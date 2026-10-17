# Définition de conformité et matrice de traçabilité

## 1. Définition

Un système d'IA est jugé **conforme** lorsqu'il satisfait, de façon **démontrable**, aux critères ci-dessous. « Démontrable » signifie que chaque critère renvoie à une preuve vérifiable : un fichier du dépôt, un test automatisé ou un document.

Légende : ✅ mis en œuvre et testé · 🟡 partiel (limite documentée) · ⬜ action organisationnelle, **non réalisable par le code**.

Pour vérifier les preuves techniques : `pytest -q` (62 tests) et `flask --app lumen verify-audit`.

## 2. Les six critères de conformité

| # | Critère | Condition de réussite | Mise en œuvre | Preuves | Statut |
|---|---|---|---|---|---|
| 1 | **Bases légales identifiées** | Chaque finalité a une base légale écrite ; le consentement à la politique est recueilli et daté | Tableau des finalités et bases légales ; case d'acceptation avec version et horodatage | `analyse-juridique.md` §4 ; `auth.register` ; `test_policy_acceptance_required` | ✅ Documenté ; 🟡 base exacte à confirmer par l'Organisation selon la loi applicable |
| 2 | **Droits des personnes garantis** | Information, accès, export, rectification, effacement, opposition, contestation utilisables sans intervention technique | Routes en libre-service ; export complet ; suppression du compte en cascade ; contestation | `privacy.py` ; `test_export_contains_full_content`, `test_delete_account_erases_everything`, `test_rectification_and_password_change`, `test_objection_to_external_processing` | ✅ |
| 3 | **Mesures de sécurité définies** | Chiffrement, authentification robuste, protection contre les attaques web courantes, journalisation, durées de conservation appliquées | Fernet ; scrypt ; CSRF ; CSP ; limitation des tentatives ; audit chaîné ; purge automatique | `security.py`, `crypto.py`, `audit.py`, `retention.py` ; `test_security.py`, `test_audit_retention.py` | ✅ (🟡 pas de MFA) |
| 4 | **Responsabilité attribuée** | Responsable, rôles, propriétaires de risques et procédure d'incident nommés | RACI, rôles applicatifs, propriétaire par risque, procédure d'incident | `gouvernance-ia.md` §2 et §7 ; `cartographie-des-risques.md` | ✅ Cadre fourni ; ⬜ désigner les personnes réelles |
| 5 | **Risques éthiques analysés** | Registre avec échelles référencées, risques éthiques (biais, discrimination, hallucination, sur-confiance, mésusage) évalués avant et après mesures | 18 risques ; échelles ISO 31000, ISO/IEC 23894, NIST, CNIL | `methodologie-risques.md`, `cartographie-des-risques.md`, `risk_register.json` | ✅ |
| 6 | **Supervision humaine prévue** | Un humain décide de toute mesure touchant une personne ; décisions motivées ; contestation ; accès aux contenus limité et tracé | File de revue, quatre actions, justification obligatoire, contestation, suspension contestable | `admin.py`, `privacy.py` ; `test_human_oversight_and_contestation_end_to_end`, `test_admin_cannot_block_another_admin_or_read_unflagged_content` | ✅ |

## 3. Critères complémentaires

| Critère | Mise en œuvre | Preuves | Statut |
|---|---|---|---|
| **Transparence** (information sur l'IA, ses limites, le fournisseur) | Étiquette « AI-generated », parcours de la donnée, pages publiques | `ask.html`, `transparency.html`, `privacy.html` ; `test_public_pages_render_without_login` | ✅ |
| **Minimisation** | Pseudonymes ; filtre avant stockage ; IP tronquée ; relecteur limité aux contenus signalés | `compliance.py` ; `test_blocked_prompt_is_not_stored_nor_processed`, `test_audit_has_no_message_content_or_usernames`, `test_audit_ip_is_truncated` | ✅ (🟡 noms en texte libre non détectés) |
| **Limitation de conservation** | Purge toutes les 24 h, configurable | `retention.py` ; `test_retention_purge_deletes_only_expired_data` | ✅ |
| **Journalisation et traçabilité** | Audit chaîné ; fournisseur et transfert tracés par requête | `audit.py` ; `test_audit_chain_is_intact_then_detects_tampering` | ✅ |
| **Transferts hors pays** | Désactivés par défaut ; opposition ; évaluation | `ai_service.py`, `transferts-groq.md` ; `test_external_provider_opt_out_prevents_transfer` | ✅ technique ; ⬜ DPA et autorisation CNDP |
| **Analyse d'impact (AIPD)** | Document complet avec registre des traitements | `aipd-dpia.md` | ✅ ; ⬜ avis du DPO à recueillir |
| **Données sensibles** | Interdites par la politique, détectées par mots-clés et signalées pour revue | `compliance.py` ; `test_flags_sensitive_categories_without_blocking` | 🟡 détection par motifs, non exhaustive |
| **Authentification sécurisée** | scrypt, politique de mot de passe, limitation, session durcie, pas de compte par défaut | `test_no_default_admin_account`, `test_login_throttling_locks_after_repeated_failures`, `test_session_fixation_protection` | ✅ |
| **Outils open source** | Flask, SQLite, cryptography, requests, python-dotenv ; modèle Llama (poids ouverts) ; Ollama | `requirements.txt` | ✅ ; l'API Groq est un service tiers propriétaire, optionnel |

## 4. Ce qui reste à faire par l'Organisation

Ces actions conditionnent la conformité **juridique** complète ; elles ne peuvent pas être accomplies par le code ni par l'équipe de développement.

| # | Action | Référence |
|---|---|---|
| 1 | Déclaration ou autorisation CNDP (loi 09-08, art. 12) | `analyse-juridique.md` §10 |
| 2 | Si fournisseur externe : accord de sous-traitance, autorisation du transfert | `transferts-groq.md` §6 |
| 3 | Désigner un DPO ou un point de contact et recueillir son avis sur l'AIPD | `aipd-dpia.md` §8 |
| 4 | Désigner les rôles réels (responsable, relecteurs, propriétaires de risques), idéalement deux relecteurs | `gouvernance-ia.md` §2 |
| 5 | Valider ou ajuster les seuils de l'échelle de risque (appétence au risque) | `methodologie-risques.md` §5 |
| 6 | Sensibiliser les utilisateurs avant l'ouverture | `gouvernance-ia.md` §10 |
| 7 | Mettre en place la gestion des secrets, des sauvegardes chiffrées, HTTPS | `SECURITY.md` |
| 8 | Planifier `verify-audit` et la revue semestrielle | `gouvernance-ia.md` §5, §8 |

## 5. Limites connues, assumées

- Le filtre fonctionne par motifs : il ne détecte pas les noms en texte libre ni les données déguisées.
- Les biais et les erreurs des modèles de langage ne sont pas supprimés, seulement divulgués, surveillés et encadrés.
- Pas d'authentification multifacteur ni de récupération de mot de passe par e-mail (aucun e-mail n'est collecté).
- Les références juridiques marquées « à vérifier » doivent être contrôlées sur les textes officiels.

## 6. Verdict

**Conformité technique : démontrée et testée** pour les six critères. **Conformité juridique complète : conditionnée** aux actions du §4. Le dépôt ne prétend pas à plus.
