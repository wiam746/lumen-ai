"""Generate docs/fr/cartographie-des-risques.md from docs/risk_register.json.

Scores and risk levels are computed here (probability x severity), so the document can never
contradict the register. Run:  python scripts/build_risk_docs.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANDS = [(4, "Faible", "🟩"), (9, "Modéré", "🟨"), (16, "Élevé", "🟧"), (25, "Critique", "🟥")]
P_LABELS = {1: "Rare", 2: "Peu probable", 3: "Possible", 4: "Probable", 5: "Quasi certain"}
S_LABELS = {1: "Négligeable", 2: "Limitée", 3: "Significative", 4: "Grave", 5: "Critique"}


def band(score):
    return next((name, icon) for limit, name, icon in BANDS if score <= limit)


def heatmap(risks, p_key, s_key):
    lines = ["| Gravité \\ Probabilité | " + " | ".join(f"{p} {P_LABELS[p]}" for p in range(1, 6)) + " |",
             "|---|" + "---|" * 5]
    for s in range(5, 0, -1):
        cells = []
        for p in range(1, 6):
            ids = ", ".join(r["id"] for r in risks if r[p_key] == p and r[s_key] == s)
            icon = band(p * s)[1]
            cells.append(f"{icon} {ids}".strip() if ids else icon)
        lines.append(f"| **{s} {S_LABELS[s]}** | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    data = json.loads((ROOT / "docs" / "risk_register.json").read_text(encoding="utf-8"))
    risks = data["risks"]
    for r in risks:
        r["inh"], r["res"] = r["p_inh"] * r["s_inh"], r["p_res"] * r["s_res"]
    counts = lambda key: {name: sum(1 for r in risks if band(r[key])[0] == name) for _, name, _ in BANDS}
    inh, res = counts("inh"), counts("res")
    out = [
        "# Cartographie des risques",
        "",
        "> Document généré par `scripts/build_risk_docs.py` à partir de `docs/risk_register.json`. Ne pas modifier à la main : modifier le registre puis régénérer.",
        "> Échelles, seuils et référentiels : voir [`methodologie-risques.md`](methodologie-risques.md).",
        "",
        "## 1. Synthèse",
        "",
        "| Niveau | Risques inhérents (sans mesure) | Risques résiduels (avec mesures) |",
        "|---|---|---|",
    ]
    out += [f"| {icon} {name} | {inh[name]} | {res[name]} |" for _, name, icon in BANDS]
    top = sorted(risks, key=lambda r: (-r["res"], r["id"]))[:4]
    verdict = ("Aucun risque résiduel n'atteint le niveau élevé." if res["Élevé"] + res["Critique"] == 0
               else "Des risques résiduels restent au niveau élevé ou critique : ils doivent être traités avant mise en production.")
    out += ["", f"{len(risks)} risques identifiés. {verdict}", "",
            "Risques résiduels les plus élevés : " + ", ".join(f"{r['id']} ({r['res']})" for r in top) + ". "
            "Ils tiennent à la nature des modèles de langage (biais, erreurs, sur-confiance), aux limites d'un filtre à motifs "
            "et à des démarches que seule l'organisation peut mener ; ils sont gérés par la transparence, la supervision humaine "
            "et l'interdiction des usages décisionnels.", "",
            "## 2. Carte de chaleur : risque inhérent", "", heatmap(risks, "p_inh", "s_inh"), "",
            "## 3. Carte de chaleur : risque résiduel", "", heatmap(risks, "p_res", "s_res"), "",
            "## 4. Registre des risques", "",
            "| ID | Risque | Catégorie | Inhérent (P×G) | Résiduel (P×G) | Propriétaire | Statut |",
            "|---|---|---|---|---|---|---|"]
    for r in risks:
        out.append(f"| {r['id']} | {r['title']} | {r['category']} | {band(r['inh'])[1]} {r['p_inh']}×{r['s_inh']}={r['inh']} | "
                   f"{band(r['res'])[1]} {r['p_res']}×{r['s_res']}={r['res']} | {r['owner']} | {r['status']} |")
    out += ["", "## 5. Fiches détaillées", ""]
    for r in risks:
        out += [f"### {r['id']} : {r['title']}", "",
                f"- **Scénario** : {r['scenario']}",
                f"- **Catégorie** : {r['category']} · **Correspondance NIST AI 600-1** : {r['nist']} · **Contrôle ISO/IEC 27002:2022** : {r['iso27002']}",
                f"- **Inhérent** : probabilité {r['p_inh']} ({P_LABELS[r['p_inh']]}) × gravité {r['s_inh']} ({S_LABELS[r['s_inh']]}) = **{r['inh']}** ({band(r['inh'])[0]})",
                "- **Mesures en place** :"]
        out += [f"  - {c}" for c in r["controls"]]
        out += [f"- **Résiduel** : probabilité {r['p_res']} ({P_LABELS[r['p_res']]}) × gravité {r['s_res']} ({S_LABELS[r['s_res']]}) = **{r['res']}** ({band(r['res'])[0]})",
                f"- **Statut de mise en œuvre** : {r['status']}",
                f"- **Action restante** : {r['action']}", ""]
    out += ["## 6. Plan de traitement des actions restantes", "",
            "| ID | Action | Propriétaire |", "|---|---|---|"]
    out += [f"| {r['id']} | {r['action']} | {r['owner']} |" for r in sorted(risks, key=lambda x: -x["res"])]
    out += ["", "## 7. Revue", "", "Revue tous les 6 mois et à chaque changement structurant (voir `gouvernance-ia.md`). La date et l'auteur de chaque revue sont consignés dans le registre de gouvernance de l'organisation.", ""]
    (ROOT / "docs" / "fr" / "cartographie-des-risques.md").write_text("\n".join(out), encoding="utf-8")
    print(f"{len(risks)} risks -> inherent {inh}, residual {res}")


if __name__ == "__main__":
    main()
