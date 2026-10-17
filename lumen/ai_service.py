"""AI provider layer.

Providers
  offline  built-in rule-based answers (default). Nothing leaves the server.
  ollama   local open-weights model served by Ollama. Nothing leaves your infrastructure.
  groq     Llama models via Groq's hosted API (USA). This is an EXTERNAL transfer: it must be
           documented, authorised and disclosed to users (see docs/fr/transferts-groq.md).

Only the user's prompt is ever sent to a provider: no username, ID, IP or history.
Prompts are never written to application logs.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import requests
from flask import current_app

logger = logging.getLogger("lumen.ai")

PROVIDER_META = {
    "offline": {"label": "Built-in assistant (offline)", "external": False, "where": "this server"},
    "ollama": {"label": "Local model (Ollama)", "external": False, "where": "your organization's infrastructure"},
    "groq": {"label": "Groq (Llama 3.1)", "external": True, "where": "Groq servers, United States"},
}

SYSTEM_PROMPT = """You are Lumen, an AI assistant for internal users of {org}.

Rules:
1. You are an AI. Say so if asked, and remind users that answers may contain errors and that important matters must be verified with a human.
2. Never ask for, repeat, or process personal data (names, contact details, ID numbers, health or other sensitive information). If a user shares some, tell them to remove it.
3. Do not make decisions about people. You may inform and explain; humans decide.
4. If you do not know, say so. Never invent facts, sources, or quotations.
5. Stay within a professional, educational scope. Politely refuse harmful requests.
6. Reply in the language of the user's message, clearly and concisely.
{knowledge}"""


@dataclass
class AIResult:
    text: str
    provider: str
    model: str
    external: bool
    note: str = ""


def describe_provider(optout: bool = False) -> dict:
    """What the UI tells the user about where their message will be processed."""
    name = current_app.config["LLM_PROVIDER"]
    meta = dict(PROVIDER_META.get(name, PROVIDER_META["offline"]))
    if name == "groq" and not current_app.config["GROQ_API_KEY"]:
        meta = dict(PROVIDER_META["offline"])
    if meta["external"] and optout:
        meta = dict(PROVIDER_META["offline"], note="You opted out of external processing.")
    return meta


def _system_prompt() -> str:
    cfg = current_app.config
    knowledge = ""
    path = Path(cfg["KNOWLEDGE_BASE_PATH"])
    if path.is_file():
        knowledge = "\nOrganization knowledge base (authoritative, answer from it when relevant):\n" + path.read_text(encoding="utf-8")[:12000]
    return SYSTEM_PROMPT.format(org=cfg["ORG_NAME"], knowledge=knowledge)


def _chat_completion(base_url: str, model: str, prompt: str, api_key: str = "") -> str:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers=headers,
        json={"model": model, "max_tokens": 1024, "temperature": 0.3,
              "messages": [{"role": "system", "content": _system_prompt()},
                           {"role": "user", "content": prompt}]},
        timeout=(5, 45),
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_response(prompt: str, *, allow_external: bool = True) -> AIResult:
    cfg = current_app.config
    name = cfg["LLM_PROVIDER"]
    try:
        if name == "groq" and cfg["GROQ_API_KEY"]:
            if not allow_external:
                return _offline(prompt, note="Processed locally because you opted out of external processing.")
            text = _chat_completion("https://api.groq.com/openai/v1", cfg["GROQ_MODEL"], prompt, cfg["GROQ_API_KEY"])
            return AIResult(text, "groq", cfg["GROQ_MODEL"], external=True)
        if name == "ollama":
            text = _chat_completion(cfg["OLLAMA_BASE_URL"], cfg["OLLAMA_MODEL"], prompt)
            return AIResult(text, "ollama", cfg["OLLAMA_MODEL"], external=False)
    except (requests.RequestException, KeyError, ValueError) as exc:
        # Never log the prompt or the provider response body.
        logger.warning("AI provider '%s' failed (%s); using offline assistant", name, type(exc).__name__)
        return _offline(prompt, note="The configured AI provider is unavailable; the built-in assistant answered instead.")
    return _offline(prompt)


def _offline(prompt: str, note: str = "") -> AIResult:
    org = current_app.config["ORG_NAME"]
    p = prompt.lower()
    if any(w in p for w in ("privacy", "personal data", "gdpr", "09-08", "my data", "confidential", "données")):
        text = (f"**How {org} handles your data with Lumen**\n\n"
                "- Messages are scanned for personal data before anything else; flagged identifiers are rejected, not stored.\n"
                "- Stored messages are encrypted and deleted automatically after the retention period.\n"
                "- You can read, export or delete everything from the *My data* page, at any time.\n\n"
                "See the privacy notice for the full details.")
    elif any(w in p for w in ("contest", "appeal", "human", "review", "complain", "wrong", "error")):
        text = ("**Human oversight**\n\nLumen never makes decisions about you. Flagged messages are reviewed by a person, "
                "and you can contest any AI answer or moderation decision from the *Contest* page; a human answers every contest.")
    elif any(w in p for w in ("model", "provider", "where", "external", "groq", "ollama", "local", "send")):
        text = ("**Where your message is processed**\n\nThis deployment runs the built-in offline assistant: your message "
                "stays on this server. Administrators may connect a local model (Ollama) or an external provider; "
                "the *Ask* page always shows which one is active, and you may opt out of external processing in *Settings*.")
    elif any(w in p for w in ("who are you", "what are you", "how do you work", "how does", "about", "limit")):
        text = (f"**About Lumen**\n\nLumen is an AI assistant for {org}. It can summarise or explain text and answer general "
                "questions. It can be wrong, it cannot verify facts, and it must not be used to make decisions about people. "
                "Read *How this AI works* for its limits and risks.")
    else:
        text = ("**Built-in assistant (offline mode)**\n\nNo language model is connected, so I can only answer questions about "
                "Lumen itself: privacy, human oversight, where data is processed, and my limits.\n\n"
                "An administrator can enable a local or hosted model for full answers.")
    return AIResult(text, "offline", "rules-v1", external=False, note=note)
