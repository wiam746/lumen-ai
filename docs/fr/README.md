# Documentation de conformité (français)

Ces documents accompagnent Lumen AI. Ils décrivent le cadre juridique, les risques, la gouvernance et les garanties du système. Ils sont **pédagogiques** : l'organisation qui déploie Lumen doit les adapter et les faire valider (DPO, juriste, direction). Ils ne constituent pas un avis juridique.

## Ordre de lecture conseillé

1. [`definition-of-compliance.md`](definition-of-compliance.md) : ce qui est conforme, avec les preuves, et ce qui reste à faire
2. [`analyse-juridique.md`](analyse-juridique.md) : cadre applicable (loi 09-08, RGPD, AI Act, cybersécurité)
3. [`methodologie-risques.md`](methodologie-risques.md) : échelles de risque référencées (ISO, NIST, CNIL)
4. [`cartographie-des-risques.md`](cartographie-des-risques.md) : registre, cartes de chaleur, plan de traitement (généré)
5. [`aipd-dpia.md`](aipd-dpia.md) : analyse d'impact et registre des traitements
6. [`gouvernance-ia.md`](gouvernance-ia.md) : rôles, supervision, contestation, incidents
7. [`transferts-groq.md`](transferts-groq.md) : transfert vers un fournisseur externe
8. [`politique-utilisation.md`](politique-utilisation.md) : règles pour les utilisateurs

## Régénérer la cartographie des risques

Le registre est la source de vérité (`docs/risk_register.json`). Après modification :

```bash
python scripts/build_risk_docs.py
```

## Convention sur les références juridiques

Les références **[vérifié]** ont été confrontées à des sources publiques ; les références **[à vérifier]** reposent sur des connaissances générales et doivent être contrôlées sur le texte officiel.
