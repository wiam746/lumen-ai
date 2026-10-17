# Évaluation du transfert de données vers Groq

> Lumen peut envoyer les requêtes à l'API de **Groq** (modèles Llama hébergés aux États-Unis). Ce n'est **pas** une IA locale : c'est un transfert de données personnelles potentielles vers un tiers situé hors du Maroc et hors de l'Union européenne. Ce document décrit le flux, l'analyse juridique, les garanties techniques en place et les actions que l'Organisation doit encore accomplir. Les points signalés **[à vérifier]** n'ont pas pu être confirmés auprès du fournisseur et ne doivent pas être tenus pour acquis.

## 1. Résumé

| Question | Réponse |
|---|---|
| Le transfert est-il actif par défaut ? | **Non.** Le fournisseur par défaut est `offline`. Il faut définir `LLM_PROVIDER=groq` et une clé API |
| Que quitte l'infrastructure ? | Le texte de la requête, le prompt système et, s'il existe, le contenu de `config/knowledge_base.md` |
| Que ne quitte pas l'infrastructure ? | Nom d'utilisateur, identifiant, adresse IP, historique, autres requêtes |
| L'utilisateur est-il informé ? | Oui : parcours de la donnée à chaque requête, notice de confidentialité, étiquette du fournisseur dans l'historique |
| Peut-il s'y opposer ? | Oui : réglage « ne pas envoyer mes messages à un fournisseur externe » |
| Alternative locale ? | Oui : `LLM_PROVIDER=ollama` (aucune donnée ne sort) |
| Peut-on l'utiliser en production aujourd'hui ? | **Seulement après** les actions du §6 |

## 2. Description du flux

1. L'utilisateur envoie un message ; le filtre de conformité rejette les identifiants directs et secrets **avant** tout appel (rien n'est transmis).
2. `ai_service._chat_completion` envoie en HTTPS une requête `chat/completions` à `https://api.groq.com/openai/v1` avec la clé API de l'Organisation (en-tête `Authorization`), un délai de 5 s (connexion) et 45 s (lecture). Contenu : prompt système, éventuelle base de connaissances, message de l'utilisateur.
3. La réponse est reçue, **les identifiants éventuels sont masqués**, puis le texte est chiffré et stocké localement. La requête est marquée `external_transfer = 1`.
4. Aucun message ni aucune réponse n'est écrit dans les journaux de l'application ; en cas d'échec, seul le type d'erreur est journalisé, puis l'assistant hors ligne répond (sans transfert).

Le modèle (Llama) est publié avec des poids ouverts, mais **son exécution sur l'infrastructure de Groq est un service tiers propriétaire**. Ouvert ne signifie pas local.

## 3. Rôles

| Acteur | Rôle proposé | Observation |
|---|---|---|
| L'Organisation | Responsable de traitement | Décide d'activer le fournisseur |
| Groq | **Sous-traitant** (RGPD art. 28) | À confirmer par contrat : agit sur instruction, sans usage propre des données [à vérifier] |
| Meta (modèle Llama) | Tiers sans accès aux données | Fournit seulement les poids du modèle |

## 4. Analyse juridique

### 4.1 Droit marocain

La loi 09-08 encadre le transfert de données vers un pays étranger (art. 43-44) : il suppose un niveau de protection suffisant dans le pays destinataire, apprécié par la CNDP, ou une autorisation de celle-ci. La CNDP rappelle que tout transfert à l'étranger doit être préalablement notifié ou autorisé (délibération D-02-2023) ; l'hébergement à l'étranger sans autorisation a été relevé comme manquement lors de contrôles. Le transfert illicite est sanctionné pénalement (art. 60-61 selon une synthèse publique, [à vérifier]). **[vérifié pour les art. 43-44 et le principe d'autorisation préalable]**

**Conséquence** : l'Organisation doit obtenir l'autorisation ou accomplir la notification de la CNDP avant d'activer Groq en production.

### 4.2 RGPD (si applicable, et à titre de référence)

Chapitre V : un transfert vers un pays tiers requiert (a) une décision d'adéquation (art. 45) : le cadre UE-États-Unis de protection des données (Data Privacy Framework) a fait l'objet d'une décision d'adéquation en 2023, qui ne bénéficie qu'aux entreprises certifiées ; **la certification de Groq est à vérifier** ; (b) à défaut, des garanties appropriées (art. 46) comme les clauses contractuelles types, accompagnées d'une évaluation d'impact du transfert (TIA, arrêt Schrems II) ; (c) ou une dérogation (art. 49), interprétée restrictivement et inadaptée à un usage systématique.

## 5. Garanties techniques et organisationnelles implémentées

| Garantie | Où |
|---|---|
| Désactivé par défaut (privacy by default) | `config.py` : `LLM_PROVIDER=offline` |
| Filtre avant transmission ; seuls les messages « propres » partent | `chat.py`, `compliance.py` |
| Minimisation : seul le texte de la requête est envoyé | `ai_service.py` |
| Information en amont et à chaque requête | `ask.html`, `privacy.html` |
| Droit d'opposition individuel | `privacy.ai_processing`, test `test_external_provider_opt_out_prevents_transfer` |
| Traçabilité par requête et dans l'audit (`external_transfer`) | `schema.sql`, `audit.py` |
| Basculement hors ligne en cas de panne (sans transfert) | `test_provider_failure_falls_back_to_offline` |
| Masquage des identifiants dans la sortie | `compliance.redact` |
| Copie locale chiffrée | `crypto.py` |
| Pas de journalisation des messages | `ai_service.py`, `audit.py` |
| Alternative locale sans transfert | `LLM_PROVIDER=ollama` |

## 6. Points à vérifier auprès du fournisseur et actions de l'Organisation

| # | Point | Statut |
|---|---|---|
| 1 | Accord de traitement des données (DPA) disponible et signé | ⬜ À faire [à vérifier auprès de Groq] |
| 2 | Politique de conservation des requêtes côté fournisseur (durée, journalisation) | ⬜ À vérifier |
| 3 | Utilisation des requêtes pour entraîner des modèles : exclue contractuellement ? | ⬜ À vérifier |
| 4 | Lieu(x) de traitement, sous-traitants ultérieurs | ⬜ À vérifier |
| 5 | Certification au cadre UE-États-Unis, ou clauses contractuelles types | ⬜ À vérifier |
| 6 | Mesures de sécurité du fournisseur (certifications) | ⬜ À vérifier |
| 7 | Autorisation ou notification de la CNDP pour le transfert | ⬜ À faire |
| 8 | Mise à jour de la notice de confidentialité et de l'inventaire des traitements | ✅ Notice dynamique ; inventaire à mettre à jour par l'Organisation |
| 9 | Avis du DPO ou point de contact | ⬜ À faire |
| 10 | Gestion de la clé API (secret, rotation, pas dans le dépôt) | ✅ `.env` ignoré par git ; à appliquer |

## 7. Alternatives étudiées

| Option | Transfert | Qualité des réponses | Coût / effort | Recommandation |
|---|---|---|---|---|
| `offline` (règles intégrées) | Non | Très limitée | Nul | Par défaut, démonstration |
| `ollama` (modèle local) | Non | Bonne selon le matériel | Machine adaptée | **Recommandé** si des données sensibles peuvent être saisies |
| Fournisseur hébergé dans l'UE, avec DPA | Non hors UE | Bonne | Contrat | À privilégier si un service externe est nécessaire |
| `groq` | **Oui, États-Unis** | Bonne, rapide | Clé API | Acceptable **sous les conditions** du §8 |

## 8. Décision et conditions

L'activation de Groq en production est **conditionnée** à :

1. DPA signé et points 2 à 6 du §6 vérifiés et jugés satisfaisants ;
2. autorisation ou notification de la CNDP obtenue ;
3. avis du DPO consigné dans l'AIPD ;
4. politique d'utilisation rappelée aux utilisateurs : aucune donnée sensible ni personnelle dans les requêtes ;
5. revue annuelle de cette évaluation et à chaque changement de conditions du fournisseur.

Sans ces conditions : `LLM_PROVIDER=offline` ou `ollama`.

## 9. Risque résiduel

Risque R07 de la cartographie : **inhérent 16 (élevé), résiduel 6 (modéré)** une fois les garanties techniques en place et sous réserve que les actions organisationnelles du §6 soient accomplies. Sans elles, le risque doit être considéré comme élevé.

## Annexe. Mention d'information à destination des utilisateurs

> « Lorsque cette option est activée par votre organisation, vos messages sont envoyés à Groq, aux États-Unis, pour générer la réponse. Aucun identifiant de compte ni adresse IP n'est transmis. Ne saisissez pas de données personnelles ou sensibles. Vous pouvez vous y opposer à tout moment dans *Settings* : Lumen répond alors avec l'assistant intégré, qui ne transmet rien. »
