import pytest

from lumen.compliance import check_compliance, redact


@pytest.mark.parametrize("text", [
    "Contact me at jane.doe@example.com please",
    "my mail is jane [at] example dot com",
    "Call 0612345678 tomorrow",
    "Call 06 12 34 56 78 tomorrow",
    "Reach me on +212 661 234 567",
    "My CIN is AB123456",
    "card 4111 1111 1111 1111",
    "IBAN FR76 3000 6000 0112 3456 7890 189",
    "password: hunter2hunter2",
    "mot de passe est azerty123",
    "key gsk_abcdefghijklmnopqrstuvwxyz123456",
    "position 33.5731, -7.5898",
    "j\u200bane@exam\u200bple.com",
])
def test_blocks_direct_identifiers(text):
    result = check_compliance(text)
    assert result.blocked, text


@pytest.mark.parametrize("text", [
    "Explain how the Python API handles Flask SQL queries",
    "Summarise the history of machine learning in 5 bullet points",
    "What is the difference between TCP and UDP?",
    "Order number 1234567890123 is not a card (fails Luhn)",
    "Write a note about the political situation in 1990",
    "Version 2.0.1 was released on 12/03/2024",
])
def test_does_not_block_ordinary_text(text):
    assert not check_compliance(text).blocked, text


def test_flags_sensitive_categories_without_blocking():
    result = check_compliance("Explain the rules for processing health data under GDPR")
    assert result.flagged and not result.blocked
    assert "health data" in result.categories


def test_flags_french_sensitive_terms():
    assert check_compliance("Quelles sont les règles sur le casier judiciaire ?").flagged


def test_redact_masks_identifiers_in_output():
    assert "jane@example.com" not in redact("Write to jane@example.com")
    assert redact("plain text") == "plain text"
