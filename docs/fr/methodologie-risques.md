# Méthodologie d'évaluation des risques et échelles de référence

> Document pédagogique. Les seuils chiffrés ci-dessous sont une **proposition de calibrage** : selon l'ISO 31000, les critères de risque doivent être fixés par l'organisation elle-même (son « appétence au risque »). Elle doit les valider avant mise en production.

## 1. Pourquoi une échelle référencée

Une échelle « mineur, modéré, majeur, critique, catastrophique » est trop générique : deux évaluateurs ne placeront pas le même risque au même niveau. Chaque niveau est donc **défini par des critères mesurables** (nombre de personnes, nature des données, réversibilité, conséquence juridique) et rattaché à des référentiels reconnus.

## 2. Référentiels utilisés

| Référentiel | Usage dans ce projet |
|---|---|
| **ISO 31000:2018**, Management du risque | Processus (contexte, identification, analyse, évaluation, traitement, suivi) et obligation de définir des *critères de risque* en amont |
| **ISO/IEC 23894:2023**, Gestion des risques liés à l'IA | Adaptation de l'ISO 31000 aux systèmes d'IA (risques propres à l'apprentissage automatique, au cycle de vie du système) |
| **NIST AI RMF 1.0** (NIST AI 100-1, 2023) | Quatre fonctions : *Govern, Map, Measure, Manage*. Utilisé pour structurer la gouvernance et la mesure |
| **NIST AI 600-1** (profil IA générative, 2024) | Catalogue de risques propres à l'IA générative (confabulation, vie privée, biais, configuration humain-IA, sécurité de l'information, chaîne de valeur) |
| **ISO/IEC 27005:2022** et **ISO/IEC 27001/27002:2022** | Risques de sécurité de l'information et mesures de sécurité (numéros de contrôle cités dans le registre) |
| **ISO/IEC 29134** et **méthode PIA de la CNIL** | Gravité et vraisemblance des risques *pour les personnes* (4 niveaux CNIL : négligeable, limitée, importante, maximale) |
| **RGPD** (règlement UE 2016/679), art. 24, 25, 32, 35, 83 | Obligation d'évaluer les risques pour les droits et libertés ; barème des sanctions (art. 83) |
| **Loi marocaine 09-08**, décret 2-09-165, délibérations de la CNDP | Cadre national : droits (art. 5, 7, 8, 9), formalités (art. 12), transferts (art. 43-44), sanctions (art. 51 et suivants) |
| **Règlement UE 2024/1689** (AI Act) | Classification du système et obligations de transparence (art. 50) |
| **Méthodes de modélisation des menaces** : STRIDE (sécurité), LINDDUN (vie privée) | Aide à l'identification des scénarios |

## 3. Échelle de probabilité (1 à 5)

| Niveau | Libellé | Définition | Fréquence indicative | Probabilité annuelle indicative |
|---|---|---|---|---|
| 1 | Rare | Ne se produira que dans des circonstances exceptionnelles ; aucun précédent connu dans un contexte comparable | Moins d'une fois en 5 ans | < 5 % |
| 2 | Peu probable | Possible mais nécessite une combinaison de conditions défavorables | Une fois tous les 2 à 5 ans | 5 à 20 % |
| 3 | Possible | Peut se produire ; des cas sont documentés ailleurs | Environ une fois par an | 20 à 50 % |
| 4 | Probable | Se produira vraisemblablement ; facile à déclencher ou fréquent dans les systèmes comparables | Plusieurs fois par an | 50 à 90 % |
| 5 | Quasi certain | Se produit en usage normal, sans attaquant ni circonstance particulière | Mensuel ou plus | > 90 % |

La probabilité tient compte de la facilité d'exploitation, des motivations et de l'exposition (ISO/IEC 27005) ; pour un risque de vie privée, elle correspond à la *vraisemblance* de la méthode CNIL.

## 4. Échelle de gravité (1 à 5)

La gravité mesure l'impact **sur les personnes concernées** en premier lieu, puis sur l'organisation. Le niveau retenu est le plus élevé atteint sur l'un des critères.

| Niveau | Libellé | Personnes touchées (calibrage proposé) | Nature des données | Réversibilité | Conséquence juridique | Équivalent CNIL |
|---|---|---|---|---|---|---|
| 1 | Négligeable | Aucune personne identifiable | Aucune donnée personnelle ou données publiques | Immédiate | Aucune | Négligeable |
| 2 | Limitée | Moins de 10 personnes | Pseudonymes, contenu de requêtes courantes | Gêne mineure, surmontée sans difficulté | Rappel interne, correction | Limitée |
| 3 | Significative | 10 à 500 personnes | Contenu de requêtes, historiques, identifiants de compte | Surmontable avec effort (changer de mots de passe, rectifier) | Plainte possible auprès de la CNDP, mise en demeure | Importante (bas) |
| 4 | Grave | Plus de 500 personnes, ou **données sensibles** (RGPD art. 9) même peu nombreuses | Catégories particulières, identifiants officiels, données financières | Difficilement réversible (atteinte à la réputation, discrimination) | Enquête de l'autorité, sanctions administratives, atteinte aux droits fondamentaux | Importante (haut) |
| 5 | Critique | Très grand nombre, ou personnes vulnérables | Données sensibles en masse | Irréversible (perte d'emploi, de droit, préjudice psychologique ou physique grave) | Sanctions maximales : jusqu'à 20 M€ ou 4 % du CA mondial (RGPD art. 83(5)) ; sanctions pénales de la loi 09-08 (art. 51 et suivants) | Maximale |

Correspondance CNIL : niveaux 1 et 2 → négligeable et limitée ; niveaux 3 et 4 → importante ; niveau 5 → maximale.

## 5. Matrice et seuils de décision

**Score = probabilité × gravité** (1 à 25).

| Score | Niveau de risque | Décision (critère d'acceptation proposé) |
|---|---|---|
| 1 à 4 | **Faible** | Accepté ; surveillance courante |
| 5 à 9 | **Modéré** | Accepté si un propriétaire est désigné et que le risque est suivi ; revue semestrielle |
| 10 à 16 | **Élevé** | Non acceptable en l'état : plan de traitement avec échéance (3 mois maximum) et décision du responsable de traitement |
| 17 à 25 | **Critique** | Inacceptable : traitement immédiat ; pas de mise en production tant que le risque n'est pas ramené sous 17 |

Règle complémentaire : **tout risque de gravité 5** est présenté au responsable de traitement quel que soit son score, et toute gravité ≥ 4 impose de consulter le DPO (ou le point de contact protection des données).

## 6. Processus

1. **Contexte** : périmètre, acteurs, données, flux (voir `aipd-dpia.md`).
2. **Identification** : ateliers de menaces (STRIDE pour la sécurité, LINDDUN pour la vie privée), catalogue NIST AI 600-1 pour les risques propres à l'IA générative.
3. **Analyse du risque inhérent** : probabilité et gravité *sans* mesure.
4. **Traitement** : mesures techniques et organisationnelles, rattachées aux contrôles ISO/IEC 27002 et aux fonctions NIST.
5. **Risque résiduel** : réévaluation *avec* les mesures mises en œuvre.
6. **Revue** : tous les 6 mois, et à chaque changement structurant (changement de fournisseur d'IA, nouvelle donnée collectée, incident). Voir `gouvernance-ia.md`.

## 7. Limites

- Les probabilités et gravités sont des **jugements d'experts**, pas des mesures statistiques : elles doivent être discutées en groupe et documentées.
- Les seuils (10 personnes, 500 personnes, bornes de fréquence) sont à calibrer sur la taille réelle de l'organisation.
- Le biais des modèles de langage ne peut pas être éliminé par l'application : il est géré par la transparence, la supervision humaine et l'interdiction d'usages décisionnels.
