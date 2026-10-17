# Cadre de gouvernance de l'IA

Ce cadre organise la responsabilité, la supervision et l'amélioration continue de Lumen AI. Il s'inspire des fonctions **Govern, Map, Measure, Manage** du NIST AI RMF 1.0 et des exigences de l'ISO/IEC 42001:2023 (système de management de l'IA) et de l'ISO/IEC 23894:2023 (gestion des risques IA).

## 1. Principes

1. **L'humain décide.** L'IA informe ; elle ne sanctionne, ne note et ne classe personne.
2. **Transparence.** Les utilisateurs savent qu'ils parlent à une IA, où va leur donnée et comment contester.
3. **Minimisation.** On ne collecte et ne conserve que le nécessaire, le moins longtemps possible.
4. **Redevabilité.** Chaque décision et chaque accès sensible laisse une trace vérifiable.
5. **Proportionnalité.** Les mesures sont proportionnées aux risques identifiés ; tout changement structurant est réévalué.

## 2. Rôles et responsabilités (matrice RACI)

R = réalise · A = rend compte · C = consulté · I = informé

| Activité | Responsable de traitement | Responsable IA / comité | DPO / point de contact | Responsable technique | Relecteurs | Utilisateurs |
|---|---|---|---|---|---|---|
| Valider les finalités, les fournisseurs et les transferts | **A/R** | C | C | C | I | I |
| Tenir le registre des risques et l'AIPD | A | R | R | C | I | |
| Configurer, sécuriser et maintenir le système | I | C | C | **A/R** | | |
| Revoir les contenus signalés | I | A | C | | **R** | |
| Répondre aux contestations | A | C | C | | **R** | I |
| Répondre aux demandes de droits hors libre-service | A | | **R** | C | | I |
| Gérer un incident de sécurité ou une fuite | **A** | C | R | R | C | I |
| Former et sensibiliser | A | **R** | C | C | R | I |
| Respecter la politique d'utilisation | | | | | R | **R** |

Rôles applicatifs : `user` (utilisateur) et `admin` (relecteur et administrateur). La séparation des fonctions (exploitation, relecture, protection des données) est organisationnelle ; il est recommandé d'avoir **au moins deux relecteurs** (principe des quatre yeux), pour qu'une décision puisse être réexaminée par une autre personne que celle qui l'a prise.

## 3. Supervision humaine

**Ce qui déclenche une revue.** Un message est mis en file d'attente si le filtre détecte une catégorie sensible (santé, religion, opinion politique, orientation sexuelle, origine, casier judiciaire, syndicat, biométrie/génétique) ou un identifiant indirect (adresse, date de naissance). Les identifiants directs et secrets sont rejetés avant tout stockage et n'arrivent jamais au relecteur.

**Ce que fait le relecteur.** Il ouvre la requête signalée (accès journalisé), puis choisit :

| Décision | Effet | Justification écrite |
|---|---|---|
| Valider | Aucun | Non requise |
| Avertir | Avertissement enregistré | Obligatoire |
| Supprimer le contenu | Requête supprimée | Obligatoire |
| Suspendre le compte | Compte suspendu, contestable | Obligatoire |

Un administrateur ne peut pas suspendre un autre administrateur depuis la file de revue. Un relecteur ne peut pas ouvrir un contenu non signalé.

**Délais cibles (à valider par l'Organisation).** Revue d'un contenu signalé : 5 jours ouvrés. Cette cible est une proposition, non une exigence technique.

## 4. Procédure de contestation

1. L'utilisateur ouvre **Contester** (disponible même compte suspendu), choisit l'objet (réponse de l'IA, décision de modération, autre), indique éventuellement le numéro de requête et explique (10 à 2 000 caractères).
2. La contestation apparaît dans la file des relecteurs avec le statut *open*.
3. Un relecteur l'examine, **accepte ou rejette** avec une explication obligatoire. S'il accepte une contestation de suspension, il peut réactiver le compte immédiatement.
4. La décision et son motif sont visibles par l'utilisateur ; l'événement est consigné dans l'audit.
5. Si l'utilisateur n'est pas satisfait, il peut saisir le point de contact puis l'autorité de contrôle (CNDP ou autorité nationale).

**Délais.** Accusé immédiat à l'enregistrement. Réponse visée sous 15 jours ouvrés, **un mois au maximum** (RGPD art. 12(3)). Pour éviter qu'une décision soit réexaminée par la personne qui l'a prise, privilégier un second relecteur.

## 5. Traçabilité

- Journal d'audit en base, chaîné par hachage SHA-256 : toute modification ou suppression d'un événement passé est détectée par `flask verify-audit` (à planifier, par exemple chaque semaine).
- Contenu du journal : identifiant numérique pseudonyme, action, cible, horodatage, adresse IP tronquée (/24 en IPv4, /48 en IPv6), détails techniques. **Jamais** le texte des messages ni les noms d'utilisateur saisis.
- Chaque requête enregistre son fournisseur, son modèle et si elle a quitté l'infrastructure (`external_transfer`).
- Durée de conservation du journal : 12 mois (paramétrable).

## 6. Transparence

- Notice de confidentialité et politique d'utilisation publiques, avec numéro de version ; l'acceptation est enregistrée avec sa version.
- Page « How this AI works » : nature du système, limites, risques, garanties, responsable.
- Sur chaque requête : parcours de la donnée en quatre étapes, fournisseur actif, étiquette « AI-generated ».

## 7. Gestion des incidents

| Étape | Action | Délai cible |
|---|---|---|
| Détecter | Alerte utilisateur, `verify-audit` en échec, comportement anormal, signalement du fournisseur | n/a |
| Contenir | Désactiver le fournisseur externe (`LLM_PROVIDER=offline`), suspendre des comptes, changer les clés | Immédiat |
| Évaluer | Nature, données concernées, nombre de personnes, risque pour elles (échelle de gravité) | 24 h |
| Notifier | Autorité de contrôle si risque pour les personnes ; personnes concernées si risque élevé (RGPD art. 33-34 ; CNDP) | 72 h |
| Documenter | Fiche d'incident, causes, mesures | 5 jours |
| Corriger | Mise à jour du registre des risques et de l'AIPD | 30 jours |

## 8. Gestion du changement et revue

Une **nouvelle évaluation d'impact** est nécessaire avant : changement de fournisseur ou de modèle, nouvelle donnée collectée, ouverture à un nouveau public, ajout d'outils ou d'accès aux données pour le modèle, usage décisionnel. Autrement, revue **tous les 6 mois** du registre des risques, de l'AIPD et des indicateurs.

## 9. Indicateurs de suivi (Measure)

| Indicateur | Source | Cible proposée |
|---|---|---|
| Requêtes rejetées par le filtre (par catégorie) | audit `COMPLIANCE_BLOCK` | Suivi de tendance |
| Délai moyen de revue d'un contenu signalé | requêtes | ≤ 5 jours ouvrés |
| Contestations ouvertes depuis plus de 15 jours ouvrés | contestations | 0 |
| Part des contestations acceptées | contestations | Suivi : un taux élevé signale un problème de filtre ou de politique |
| Requêtes transférées à l'extérieur | `external_transfer` | Conforme à la décision de l'Organisation |
| Intégrité du journal | `verify-audit` | 100 % de vérifications réussies |
| Taux d'erreur sur un jeu de questions de référence | test manuel | À définir (voir R05) |

## 10. Formation et culture IA

Avant l'ouverture des comptes : présentation de la politique d'utilisation, des limites de l'IA, des règles sur les données personnelles et de la procédure de contestation (AI Act art. 4, par référence). Rappel annuel.
