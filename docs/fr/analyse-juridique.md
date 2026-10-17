# Analyse juridique

> **Avertissement.** Document pédagogique et de travail, rédigé pour un déploiement de référence de Lumen AI. Il ne constitue pas un avis juridique. Les références marquées **[vérifié]** ont été confrontées à des sources publiques (textes ou publications de la CNDP) ; celles marquées **[à vérifier]** reposent sur des connaissances générales et doivent être contrôlées sur le texte officiel avant toute décision. Les dates d'application de certains textes européens ont pu évoluer.

## 1. Objet et périmètre

Lumen AI est un assistant conversationnel destiné aux utilisateurs internes d'une organisation (« l'Organisation »). Il traite :

- des **données de compte** (pseudonyme, empreinte de mot de passe, rôle, version de la politique acceptée) ;
- des **requêtes et réponses** (texte libre, chiffré au repos) ;
- des **traces d'audit** (identifiant numérique pseudonyme, action, horodatage, adresse IP tronquée).

Il ne collecte ni nom, ni e-mail, ni cookie publicitaire ou de mesure d'audience. Il n'est pas conçu pour traiter des données sensibles ; il les détecte et les écarte ou les signale. Selon la configuration, les requêtes sont traitées localement (par défaut) ou transmises à un fournisseur externe (voir `transferts-groq.md`).

## 2. Cadre juridique applicable

### 2.1 Droit marocain

| Texte | Pertinence | Statut |
|---|---|---|
| **Loi n° 09-08** (dahir 1-09-15 du 18 février 2009) relative à la protection des personnes physiques à l'égard du traitement des données à caractère personnel, et **décret 2-09-165** du 21 mai 2009 | Texte de référence si le traitement est opéré au Maroc. Instaure la CNDP | [vérifié] |
| Art. 5, 7, 8, 9 : droits d'information, d'accès, de rectification, d'opposition | Implémentés (voir §6) | [vérifié] |
| Art. 12 : déclaration préalable ou autorisation de la CNDP ; le §1, f) vise notamment les transferts à l'étranger | Formalité à accomplir par l'Organisation | [vérifié] |
| Art. 43-44 : transfert de données vers l'étranger (niveau de protection suffisant, autorisation) | Applicable à l'usage d'un fournisseur hors du Maroc | [vérifié] |
| Art. 51 et suivants : sanctions ; art. 53 (refus des droits), art. 55 (peines d'emprisonnement et amendes pour certains manquements) | Mesure de la gravité (échelle de gravité 5) | [vérifié] |
| Art. 3 (qualité des données), art. 4 (consentement et exceptions), art. 21-22 (données sensibles), art. 23 (sécurité) | Principes de minimisation, base légale, données sensibles, sécurité | [à vérifier] |
| **CNDP** : délibérations, notamment la délibération D-02-2023 sur le transfert de données | Un transfert à l'étranger est soumis à notification ou autorisation préalable | [vérifié] |
| **Loi 05-20** relative à la cybersécurité et directive nationale de sécurité des systèmes d'information (DNSSI, DGSSI) | Cadre de sécurité de référence ; contraignant pour certaines entités (administrations, infrastructures d'importance vitale) | [à vérifier] |

### 2.2 Droit européen (référence et applicabilité conditionnelle)

Le **RGPD** (règlement UE 2016/679) s'applique de plein droit si l'Organisation est établie dans l'Union ou cible des personnes qui s'y trouvent (art. 3). Hors de ce cas, il sert de **référentiel de bonnes pratiques** reconnu internationalement et sert ici de socle de conception (art. 5, 6, 9, 12 à 22, 24, 25, 28, 30, 32, 33-34, 35, 44 à 49). Les contrôles techniques de Lumen satisfont donc aux deux cadres ; les formalités administratives diffèrent (déclaration CNDP au Maroc, pas de déclaration en France).

Le **règlement (UE) 2024/1689** (AI Act) :

- Lumen est un **système à risque limité** : il interagit avec des personnes (art. 50 : informer qu'elles interagissent avec une IA) et n'entre pas dans les catégories à haut risque de l'annexe III tant qu'il n'est pas utilisé pour évaluer des personnes (éducation, emploi, accès à des services). **La politique interdit explicitement ces usages** ; en cas de changement d'usage, le classement devra être refait.
- Art. 4 (maîtrise de l'IA par le personnel) : couvert par la page de transparence et par les actions de sensibilisation prévues en gouvernance.
- Les dates d'application de chaque obligation sont échelonnées et ont fait l'objet d'ajustements : [à vérifier] au moment du déploiement.

## 3. Acteurs et responsabilités

| Rôle | Qui | Fondement |
|---|---|---|
| **Responsable de traitement** | L'Organisation qui déploie Lumen : détermine finalités et moyens | RGPD art. 4(7), 24 ; loi 09-08 (définition du responsable) |
| **Sous-traitant** | Fournisseur d'IA externe si activé (ex. Groq) ; hébergeur | RGPD art. 28 : contrat obligatoire |
| **DPO / point de contact** | Désigné par l'Organisation | RGPD art. 37-39. La loi 09-08 n'impose pas de DPO à notre connaissance [à vérifier] ; la désignation est recommandée |
| **Personnes concernées** | Utilisateurs (rapport de subordination possible : étudiants, salariés) | |
| **Relecteurs** | Administrateurs habilités à examiner les contenus signalés | Habilitation et traçabilité (gouvernance) |
| **Autorité de contrôle** | CNDP (Maroc) ; autorité nationale (UE) | |

## 4. Finalités et base légale

| Finalité | Base légale proposée | Remarque |
|---|---|---|
| Fournir l'assistant (traiter la requête, afficher l'historique) | Mission d'intérêt public de l'Organisation ou intérêt légitime (RGPD art. 6(1)(e) ou (f)) | Si la loi 09-08 est seule applicable : consentement ou exception de l'art. 4 [à vérifier] ; le consentement à la politique est de toute façon recueilli et horodaté |
| Sécurité et traçabilité (audit, anti-bruteforce) | Intérêt légitime (art. 6(1)(f)) ; obligation de sécurité (art. 32) | Données pseudonymisées, durée limitée |
| Modération (revue humaine des contenus signalés) | Intérêt légitime ; respect de la politique acceptée | Accès limité, journalisé |
| Transfert vers un fournisseur externe | Activation par l'Organisation + information + droit d'opposition ; autorisation CNDP | Voir `transferts-groq.md` |

Aucune finalité secondaire (profilage, publicité, entraînement de modèles) n'est poursuivie.

## 5. Principes de l'article 5 RGPD et mise en œuvre

| Principe | Mise en œuvre dans Lumen |
|---|---|
| Licéité, loyauté, transparence | Notice de confidentialité publique, parcours de la donnée affiché avant chaque requête, étiquette « généré par IA » |
| Limitation des finalités | Finalités documentées ; pas de réutilisation ; usages décisionnels interdits |
| Minimisation | Pseudonyme sans nom ni e-mail ; filtre rejetant les identifiants avant stockage ; l'administrateur n'ouvre que les contenus signalés ; IP tronquée |
| Exactitude | Rectification du nom d'utilisateur ; contestation des réponses de l'IA ; avertissement sur les erreurs possibles |
| Limitation de la conservation | Purge automatique (180 jours par défaut), suppression à la demande |
| Intégrité et confidentialité | Chiffrement au repos, hachage scrypt, CSRF, CSP, limitation des tentatives, journal inviolable |
| Responsabilité (art. 5(2), 24) | Audit chaîné, documentation (AIPD, registre, gouvernance), tests automatisés |

Protection des données dès la conception (art. 25) : fournisseur **hors ligne par défaut**, collecte minimale, chiffrement activé d'office.

## 6. Droits des personnes

| Droit | RGPD | Loi 09-08 | Fonctionnalité |
|---|---|---|---|
| Information | 12-14 | art. 5 | `/privacy`, `/transparency`, parcours de la donnée |
| Accès | 15 | art. 7 | `/my-data` |
| Portabilité | 20 | n/a | `/my-data/export` (JSON complet : contenus, avertissements, contestations) |
| Rectification | 16 | art. 8 | `/settings` (nom d'utilisateur, mot de passe) ; contestation d'une réponse |
| Effacement | 17 | art. 8 (suppression) [à vérifier] | Suppression d'une requête, de l'historique, du compte (cascade) |
| Opposition | 21 | art. 9 | Option « ne pas envoyer mes messages à un fournisseur externe » |
| Décision automatisée | 22 | n/a | Aucune décision automatisée à effet significatif ; contestation (voir §7) |

Le délai de réponse visé est d'**un mois** maximum (RGPD art. 12(3)) ; les demandes qui ne passent pas par les fonctions en libre-service sont adressées au point de contact. Le refus d'un droit expose à des sanctions pénales au Maroc (art. 53) [vérifié].

## 7. Décision automatisée et supervision humaine (art. 22)

- Le filtre de conformité **rejette une saisie** mais ne produit **aucun effet sur le compte** de la personne.
- Les mesures qui touchent une personne (avertissement, suppression de contenu, suspension) sont **décidées par un relecteur humain**, avec **justification écrite obligatoire**, et consignées dans l'audit.
- La personne peut **contester** toute réponse ou décision ; même suspendue, elle conserve l'accès à la contestation, à l'export et à l'effacement.
- Le système ne se présente jamais comme décisionnaire : sanction et notation de personnes par l'IA sont interdites par la politique.

Conclusion : le traitement ne relève pas de l'art. 22 ; les garanties de l'art. 22(3) sont néanmoins appliquées par prudence.

## 8. Transferts hors du Maroc / de l'UE

Si un fournisseur externe est activé, chaque requête traverse la frontière. Le Maroc soumet le transfert à l'appréciation du niveau de protection du pays de destination et à l'autorisation ou à la notification préalable de la CNDP (art. 43-44, délibération D-02-2023) [vérifié]. Le RGPD exige un fondement au chapitre V (décision d'adéquation art. 45, garanties appropriées art. 46, dérogations art. 49). L'analyse détaillée est dans [`transferts-groq.md`](transferts-groq.md). **Sans cette autorisation et sans accord de sous-traitance, la configuration externe ne doit pas être activée en production.**

## 9. Sécurité

L'obligation de sécurité (RGPD art. 32 ; loi 09-08 art. 23 [à vérifier]) est traduite en mesures concrètes, rattachées à l'ISO/IEC 27002:2022 dans le registre des risques : contrôle d'accès (5.15, 8.3), authentification (5.17, 8.5), cryptographie (8.24), journalisation (8.15), suppression (8.10), développement sécurisé (8.28), fournisseurs (5.19, 5.20, 5.23). Au Maroc, la DNSSI et la loi 05-20 fournissent le cadre national de référence [à vérifier].

**Violation de données.** RGPD art. 33-34 : notification à l'autorité sous 72 heures et information des personnes en cas de risque élevé. La loi 09-08 ne prévoit pas, à notre connaissance, de délai équivalent [à vérifier], mais la CNDP traite la fuite de données comme un manquement ; la procédure interne retient donc le délai de 72 heures (voir `gouvernance-ia.md`).

## 10. Formalités et documentation obligatoires

| Élément | Statut dans le dépôt | Responsable |
|---|---|---|
| Déclaration ou autorisation CNDP (art. 12) | **À accomplir par l'Organisation** | Responsable de traitement |
| Autorisation du transfert (si fournisseur externe) | **À accomplir** | Responsable de traitement |
| Registre des traitements (RGPD art. 30) | Fourni : annexe A de `aipd-dpia.md` | DPO |
| AIPD / DPIA (RGPD art. 35) | Fournie : `aipd-dpia.md` | DPO + responsable |
| Accord de sous-traitance (art. 28) | **À signer** si fournisseur externe | Responsable de traitement |
| Désignation d'un DPO ou point de contact | **À désigner** | Direction |
| Notice d'information | Fournie (`/privacy`) | DPO |

## 11. Risques juridiques propres à l'IA générative

- **Exactitude et responsabilité** : le fournisseur de la réponse n'en garantit pas l'exactitude ; l'Organisation répond de l'usage qu'elle en fait. Mesures : étiquetage, avertissements, politique de vérification.
- **Propriété intellectuelle** : la titularité des contenus générés et le risque de reproduction d'œuvres protégées sont des questions encore ouvertes selon les juridictions ; la politique impose de ne pas présenter la sortie brute comme œuvre vérifiée ou originale lorsque la divulgation est requise. [à vérifier]
- **Contenus illicites** : couverts par la politique d'utilisation et la modération humaine.
- **Biais et discrimination** : voir R01 et R02 dans la cartographie des risques.

## 12. Conclusion

Sur le plan technique, Lumen met en œuvre les principes de protection des données et les droits des personnes de manière testée. La conformité **juridique complète** dépend d'actions de l'Organisation que le code ne peut pas accomplir : déclaration ou autorisation CNDP, accord de sous-traitance et autorisation de transfert si un fournisseur externe est utilisé, désignation d'un point de contact, validation de l'AIPD. Elles sont suivies dans [`definition-of-compliance.md`](definition-of-compliance.md).
