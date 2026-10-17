# Analyse d'impact relative à la protection des données (AIPD / DPIA)

> Document pédagogique fondé sur un **déploiement de référence** de Lumen AI (RGPD art. 35 ; méthode PIA de la CNIL ; lignes directrices WP248 rév.01). L'Organisation qui déploie le système doit l'adapter, renseigner les rubriques « à compléter » et obtenir l'avis de son DPO ou point de contact avant production. Version 1.0.

| Élément | Valeur |
|---|---|
| Traitement | Assistant conversationnel Lumen AI |
| Responsable de traitement | L'Organisation (à nommer) |
| DPO / point de contact | À compléter par l'Organisation |
| Date de l'évaluation | À compléter lors de la validation |
| Conclusion | **Risque résiduel acceptable sous conditions** (voir §7) |

## 1. Description du traitement

### 1.1 Nature, portée, contexte, finalités

- **Nature.** Les utilisateurs authentifiés saisissent un texte ; le système le contrôle, le traite par un modèle de langage (local ou externe selon configuration), affiche la réponse et la conserve chiffrée.
- **Portée.** Utilisateurs internes d'une organisation (de quelques dizaines à quelques centaines de personnes). Pas de profilage, pas de décision automatisée, pas de collecte de données sensibles voulue.
- **Contexte.** Technologie innovante ; rapport de subordination possible entre l'Organisation et ses utilisateurs (étudiants, salariés).
- **Finalités.** (1) Fournir l'assistant ; (2) assurer la sécurité et la traçabilité ; (3) modérer les usages contraires à la politique avec revue humaine.

### 1.2 Données et flux

| Donnée | Catégorie | Source | Finalité | Destinataires | Conservation |
|---|---|---|---|---|---|
| Pseudonyme, rôle | Identification | Utilisateur | Authentification | Administrateurs (liste sans contenu) | Durée du compte |
| Empreinte du mot de passe (scrypt) | Authentification | Utilisateur | Authentification | Aucun (jamais affichée) | Durée du compte |
| Version de politique acceptée, date | Preuve de consentement | Système | Responsabilité | Administrateurs | Durée du compte |
| Requête et réponse (chiffrées) | Contenu libre, **potentiellement sensible** | Utilisateur / modèle | Assistant, historique | Utilisateur ; relecteurs si signalé ; fournisseur d'IA si externe | 180 jours (paramétrable) |
| Signalement et décision de revue | Modération | Système / relecteur | Supervision | Relecteurs, utilisateur concerné | 180 jours (avec la requête) ; avertissements 12 mois |
| Contestation et décision | Recours | Utilisateur / relecteur | Droits | Relecteurs, utilisateur | 12 mois après décision |
| Événements d'audit (ID pseudonyme, action, IP tronquée) | Traçabilité | Système | Sécurité, redevabilité | Administrateurs | 12 mois |
| Compteurs d'échecs de connexion (clés HMAC) | Sécurité | Système | Anti-bruteforce | Aucun | 24 heures |

### 1.3 Cycle de vie de la donnée

1. **Collecte** : saisie par l'utilisateur après affichage de la notice.
2. **Contrôle** : filtre sur le serveur ; rejet des identifiants et secrets (rien n'est stocké ni transmis).
3. **Traitement** : fournisseur hors ligne, local ou externe (affiché à l'utilisateur) ; masquage des identifiants dans la sortie.
4. **Stockage** : chiffrement (Fernet), base en mode 0600, clés hors base.
5. **Revue** : si signalé, relecture humaine avec accès journalisé.
6. **Suppression** : à la demande ou automatiquement à l'échéance (purge toutes les 24 h).

### 1.4 Registre des activités de traitement : voir l'annexe A.

## 2. Une AIPD est-elle nécessaire ?

Critères du G29 / CEPD (WP248 rév.01) : deux critères ou plus rendent généralement l'AIPD nécessaire.

| Critère | Applicable ? | Justification |
|---|---|---|
| Évaluation ou notation de personnes | Non | Aucune notation ; usage interdit par la politique |
| Décision automatisée à effet juridique | Non | Les décisions sont humaines |
| Surveillance systématique | Partiel | Journal d'audit, limité et pseudonymisé |
| Données sensibles ou hautement personnelles | Possible | Les utilisateurs peuvent en saisir malgré l'interdiction |
| Traitement à grande échelle | Non | Organisation unique, volume limité |
| Croisement de jeux de données | Non | |
| Personnes vulnérables ou en rapport de subordination | **Oui** | Étudiants ou salariés face à l'Organisation |
| Usage innovant ou nouvelle technologie | **Oui** | IA générative |
| Empêche l'exercice d'un droit | Non | |

**Conclusion** : deux critères remplis, auxquels s'ajoutent un transfert potentiel hors du pays et l'absence de maîtrise du contenu saisi : l'AIPD est requise, et réalisée ici.

## 3. Nécessité et proportionnalité

| Question | Réponse |
|---|---|
| Finalités déterminées, explicites, légitimes ? | Oui (§1.1) |
| Base légale ? | Mission d'intérêt public ou intérêt légitime ; consentement à la politique recueilli et horodaté (`analyse-juridique.md` §4) |
| Données adéquates et minimales ? | Pseudonyme sans nom ni e-mail ; filtre avant stockage ; pas de collecte de données d'appareil ni d'analytics |
| Exactitude ? | Rectification du nom d'utilisateur ; contestation des réponses ; avertissements sur les erreurs de l'IA |
| Durées de conservation ? | 180 jours (requêtes), 12 mois (audit, contestations) ; purge automatique testée |
| Information des personnes ? | Notice publique avant inscription ; parcours de la donnée à chaque requête |
| Exercice des droits ? | Accès, export, rectification, effacement, opposition en libre-service ; contestation |
| Sous-traitants ? | Fournisseur d'IA si externe : accord art. 28 à signer (`transferts-groq.md`) |
| Transferts hors pays ? | Désactivés par défaut ; si activés, autorisation CNDP et garanties (`transferts-groq.md`) |

## 4. Risques pour les droits et libertés des personnes

Méthode CNIL : événements redoutés (accès illégitime, modification non désirée, disparition), puis sources, impacts, gravité et vraisemblance (échelles de `methodologie-risques.md`).

| Événement redouté | Impacts possibles sur les personnes | Sources de risque | Risques liés (cartographie) | Gravité (CNIL) | Vraisemblance avant mesures |
|---|---|---|---|---|---|
| **Accès illégitime** à des requêtes | Divulgation de confidences, de données sensibles ; gêne, atteinte à la réputation | Attaquant externe, administrateur curieux, fournisseur externe | R04, R07, R10, R11, R16 | Importante (3-4) | Possible à probable |
| **Traitement non désiré ou erroné** (modification, mauvaise information) | Décision fondée sur une réponse fausse ou biaisée ; discrimination ; sur-confiance | Hallucination, biais du modèle, injection de prompt | R01, R02, R05, R06, R08, R09, R13, R17 | Limitée à importante (2-4) | Quasi certaine pour l'erreur, possible pour la discrimination |
| **Disparition ou indisponibilité** | Perte de l'historique ; service interrompu | Panne, perte de clé, indisponibilité du fournisseur | R14, R16 | Limitée (2) | Probable pour le fournisseur |
| **Collecte ou conservation excessive** | Atteinte à la vie privée, perte de maîtrise | Saisie imprudente, purge défaillante | R03, R12, R15 | Significative (3) | Quasi certaine pour la saisie imprudente |
| **Non-respect des droits ou du cadre légal** | Impossibilité de contester, de faire effacer ; sanction pour l'Organisation | Défaut d'organisation | R13, R15, R18 | Importante (3-4) | Possible |

## 5. Mesures prévues ou en place

| Mesure | Risques traités | Statut | Preuve |
|---|---|---|---|
| Filtre de conformité avant stockage et transmission | R03, R07 | ✅ Implémenté (limite : noms en texte libre) | `lumen/compliance.py`, `tests/test_compliance.py` |
| Chiffrement des requêtes et réponses, rotation de clés | R04, R16 | ✅ | `lumen/crypto.py`, `test_ask_stores_encrypted_and_never_plaintext`, `test_encryption_key_rotation` |
| Fournisseur hors ligne par défaut ; opposition individuelle ; traçage des transferts | R07 | ✅ | `lumen/ai_service.py`, `test_external_provider_opt_out_prevents_transfer` |
| Authentification : scrypt, politique de mot de passe, limitation des tentatives, cookies protégés, CSRF | R10 | ✅ (pas de MFA) | `lumen/security.py`, `tests/test_security.py` |
| CSP stricte, échappement des sorties | R08, R09 | ✅ | `test_xss_payload_is_escaped_everywhere`, `test_security_headers` |
| Revue humaine des contenus signalés, décisions justifiées, contestation | R01, R02, R13, R17 | ✅ | `lumen/admin.py`, `test_human_oversight_and_contestation_end_to_end` |
| Accès des relecteurs limité aux contenus signalés, journalisé ; journal inviolable | R11 | ✅ | `test_admin_cannot_block_another_admin_or_read_unflagged_content`, `test_audit_chain_is_intact_then_detects_tampering` |
| Purge automatique | R12 | ✅ | `lumen/retention.py`, `test_retention_purge_deletes_only_expired_data` |
| Droits en libre-service (accès, export, effacement, rectification, opposition) | R15, R18 | ✅ | `lumen/privacy.py`, `tests/test_flows.py` |
| Notice, page de transparence, politique d'utilisation | R15 | ✅ | `lumen/templates/privacy.html`, `transparency.html`, `policy.html` |
| Accord de sous-traitance, autorisation CNDP, désignation du DPO | R07, R18 | ⬜ **À réaliser par l'Organisation** | `definition-of-compliance.md` |
| Authentification multifacteur, détection de noms par NER | R03, R10 | ⬜ Évolutions prévues | README, feuille de route |
| Sensibilisation des utilisateurs | R03, R05, R06 | ⬜ **À organiser** | `gouvernance-ia.md` §10 |

## 6. Risque résiduel

Les risques résiduels (cartographie, §3) sont tous **faibles ou modérés** : aucun n'est élevé. Les plus élevés sont R06 (sur-confiance), R01 (biais), R05 (erreurs) et R18 (formalités), car ils tiennent à la technologie ou à des démarches qui échappent au code. Ils sont acceptables **sous réserve** des conditions du §7.

## 7. Conditions de mise en production

1. Désigner un DPO ou point de contact et recueillir son avis (§8).
2. Accomplir les formalités CNDP (déclaration ou autorisation, art. 12 de la loi 09-08).
3. Si un fournisseur externe est utilisé : accord de sous-traitance, autorisation du transfert, mise à jour de la notice (`transferts-groq.md`). **À défaut, rester sur `offline` ou `ollama`.**
4. Définir `LUMEN_ENV=production`, les secrets, HTTPS, `REGISTRATION_CODE` ; appliquer la checklist de `SECURITY.md`.
5. Informer et sensibiliser les utilisateurs avant l'ouverture.
6. Planifier `flask verify-audit` et la revue semestrielle de cette AIPD.

## 8. Avis et consultation (à compléter par l'Organisation)

Ces rubriques ne peuvent pas être renseignées par l'équipe de développement et sont donc laissées vides volontairement.

| Rubrique | Contenu |
|---|---|
| Avis du DPO / point de contact (RGPD art. 35(2)) | *À compléter* |
| Avis des personnes concernées ou de leurs représentants (art. 35(9)) | *À compléter, ou justification de l'absence de consultation* |
| Décision du responsable de traitement | *À compléter : valider, valider sous conditions, refuser* |
| Date, signataire | *À compléter* |

## 9. Revue

Cette AIPD est revue tous les 6 mois et avant tout changement listé dans `gouvernance-ia.md` §8.

---

## Annexe A. Fiche du registre des activités de traitement (RGPD art. 30)

| Rubrique | Contenu |
|---|---|
| Nom du traitement | Assistant conversationnel Lumen AI |
| Responsable de traitement | L'Organisation (coordonnées à compléter) ; DPO : à compléter |
| Finalités | Fournir l'assistant ; sécurité et traçabilité ; modération avec revue humaine |
| Catégories de personnes | Utilisateurs internes (étudiants, personnel) |
| Catégories de données | Pseudonyme, rôle, empreinte de mot de passe, consentement, contenus libres des requêtes et réponses, contestations, événements d'audit |
| Données sensibles | Non recherchées ; détection et signalement ; saisie interdite par la politique |
| Destinataires | Utilisateur ; relecteurs habilités (contenus signalés) ; fournisseur d'IA si externe (sous-traitant) ; hébergeur |
| Transferts hors pays | Aucun par défaut ; États-Unis si fournisseur Groq activé (voir `transferts-groq.md`) |
| Durées de conservation | Requêtes 180 j ; audit 12 mois ; contestations et avertissements 12 mois ; compteurs de connexion 24 h |
| Mesures de sécurité | Chiffrement au repos, scrypt, CSRF, CSP, limitation des tentatives, audit chaîné, accès restreint, purge (voir §5) |
| Base légale | Mission d'intérêt public ou intérêt légitime ; consentement à la politique horodaté |
| Formalité nationale | Déclaration ou autorisation CNDP (loi 09-08, art. 12) : à accomplir |

## Annexe B. Références

RGPD (règlement UE 2016/679) art. 5, 6, 9, 12-22, 24, 25, 28, 30, 32-35, 44-49, 83 · Loi marocaine 09-08 et décret 2-09-165 · Délibérations CNDP · Lignes directrices WP248 rév.01 (critères d'AIPD) · Méthode PIA de la CNIL · ISO/IEC 29134 · ISO/IEC 27002:2022 · ISO 31000:2018 · ISO/IEC 23894:2023 · NIST AI RMF 1.0 et NIST AI 600-1.
