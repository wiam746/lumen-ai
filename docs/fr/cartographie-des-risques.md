# Cartographie des risques

> Document généré par `scripts/build_risk_docs.py` à partir de `docs/risk_register.json`. Ne pas modifier à la main : modifier le registre puis régénérer.
> Échelles, seuils et référentiels : voir [`methodologie-risques.md`](methodologie-risques.md).

## 1. Synthèse

| Niveau | Risques inhérents (sans mesure) | Risques résiduels (avec mesures) |
|---|---|---|
| 🟩 Faible | 0 | 7 |
| 🟨 Modéré | 5 | 11 |
| 🟧 Élevé | 13 | 0 |
| 🟥 Critique | 0 | 0 |

18 risques identifiés. Aucun risque résiduel n'atteint le niveau élevé.

Risques résiduels les plus élevés : R06 (9), R01 (8), R05 (8), R18 (8). Ils tiennent à la nature des modèles de langage (biais, erreurs, sur-confiance), aux limites d'un filtre à motifs et à des démarches que seule l'organisation peut mener ; ils sont gérés par la transparence, la supervision humaine et l'interdiction des usages décisionnels.

## 2. Carte de chaleur : risque inhérent

| Gravité \ Probabilité | 1 Rare | 2 Peu probable | 3 Possible | 4 Probable | 5 Quasi certain |
|---|---|---|---|---|---|
| **5 Critique** | 🟨 | 🟧 | 🟧 | 🟥 | 🟥 |
| **4 Grave** | 🟩 | 🟨 R16 | 🟧 R02, R04, R09, R11, R13, R18 | 🟧 R07 | 🟥 |
| **3 Significative** | 🟩 | 🟨 | 🟨 R12, R15, R17 | 🟧 R01, R06, R08, R10 | 🟧 R03, R05 |
| **2 Limitée** | 🟩 | 🟩 | 🟨 | 🟨 R14 | 🟧 |
| **1 Négligeable** | 🟩 | 🟩 | 🟩 | 🟩 | 🟨 |

## 3. Carte de chaleur : risque résiduel

| Gravité \ Probabilité | 1 Rare | 2 Peu probable | 3 Possible | 4 Probable | 5 Quasi certain |
|---|---|---|---|---|---|
| **5 Critique** | 🟨 | 🟧 | 🟧 | 🟥 | 🟥 |
| **4 Grave** | 🟩 R13, R16 | 🟨 R18 | 🟧 | 🟧 | 🟥 |
| **3 Significative** | 🟩 R09, R12 | 🟨 R02, R04, R07, R10, R11 | 🟨 R06 | 🟧 | 🟧 |
| **2 Limitée** | 🟩 R15 | 🟩 R17 | 🟨 R03, R08 | 🟨 R01, R05 | 🟧 |
| **1 Négligeable** | 🟩 | 🟩 | 🟩 R14 | 🟩 | 🟨 |

## 4. Registre des risques

| ID | Risque | Catégorie | Inhérent (P×G) | Résiduel (P×G) | Propriétaire | Statut |
|---|---|---|---|---|---|---|
| R01 | Biais algorithmiques dans les réponses | Éthique | 🟧 4×3=12 | 🟨 4×2=8 | Responsable IA / comité de gouvernance | Partiel : le biais du modèle ne peut pas être supprimé par l'application |
| R02 | Discrimination par usage des réponses pour traiter des personnes | Éthique | 🟧 3×4=12 | 🟨 2×3=6 | Responsable de traitement | Mis en œuvre (technique + politique) |
| R03 | Saisie de données personnelles par les utilisateurs | Vie privée | 🟧 5×3=15 | 🟨 3×2=6 | DPO / point de contact | Partiel : le filtre ne détecte pas les noms en texte libre |
| R04 | Fuite de données stockées (base, sauvegardes) | Sécurité | 🟧 3×4=12 | 🟨 2×3=6 | Responsable technique | Mis en œuvre ; dépend du déploiement (HTTPS, sauvegardes chiffrées) |
| R05 | Erreurs et informations inventées (hallucinations) | Fiabilité | 🟧 5×3=15 | 🟨 4×2=8 | Responsable IA | Partiel : risque inhérent aux modèles de langage |
| R06 | Dépendance excessive à l'IA (sur-confiance) | Éthique | 🟧 4×3=12 | 🟨 3×3=9 | Comité de gouvernance | Partiel |
| R07 | Transfert de données vers un fournisseur externe (Groq, États-Unis) | Vie privée / Juridique | 🟧 4×4=16 | 🟨 2×3=6 | Responsable de traitement | Technique mis en œuvre ; actions organisationnelles à finaliser (contrat de sous-traitance, autorisation CNDP) |
| R08 | Injection de prompt et manipulation du modèle | Sécurité IA | 🟧 4×3=12 | 🟨 3×2=6 | Responsable technique | Mis en œuvre (limitation de la surface d'attaque) |
| R09 | XSS via la sortie du modèle | Sécurité | 🟧 3×4=12 | 🟩 1×3=3 | Responsable technique | Mis en œuvre et testé |
| R10 | Compromission de compte (force brute, réutilisation de mots de passe) | Sécurité | 🟧 4×3=12 | 🟨 2×3=6 | Responsable technique | Mis en œuvre ; pas d'authentification multifacteur |
| R11 | Accès abusif d'un administrateur aux contenus | Sécurité / Éthique | 🟧 3×4=12 | 🟨 2×3=6 | Responsable de traitement | Mis en œuvre |
| R12 | Conservation excessive des données (échec de la purge) | Conformité | 🟨 3×3=9 | 🟩 1×3=3 | Responsable technique | Mis en œuvre et testé |
| R13 | Décision automatisée sans intervention humaine (art. 22 RGPD) | Conformité / Éthique | 🟧 3×4=12 | 🟩 1×4=4 | Responsable de traitement | Mis en œuvre et testé |
| R14 | Indisponibilité du fournisseur d'IA | Disponibilité | 🟨 4×2=8 | 🟩 3×1=3 | Responsable technique | Mis en œuvre et testé |
| R15 | Information insuffisante des utilisateurs | Conformité | 🟨 3×3=9 | 🟩 1×2=2 | DPO / point de contact | Mis en œuvre |
| R16 | Compromission ou perte des clés de chiffrement | Sécurité | 🟨 2×4=8 | 🟩 1×4=4 | Responsable technique | Mis en œuvre ; procédure de gestion des secrets à appliquer par l'organisation |
| R17 | Mésusage par les utilisateurs (contenus illicites, notation de personnes) | Éthique | 🟨 3×3=9 | 🟩 2×2=4 | Comité de gouvernance | Mis en œuvre |
| R18 | Non-conformité réglementaire (formalités, DPO, sous-traitance) | Conformité | 🟧 3×4=12 | 🟨 2×4=8 | Responsable de traitement | À compléter par l'organisation : ces démarches ne peuvent pas être automatisées |

## 5. Fiches détaillées

### R01 : Biais algorithmiques dans les réponses

- **Scénario** : Le modèle produit des réponses stéréotypées ou défavorables à certains groupes ; un utilisateur les reprend sans esprit critique.
- **Catégorie** : Éthique · **Correspondance NIST AI 600-1** : Harmful bias and homogenization · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 4 (Probable) × gravité 3 (Significative) = **12** (Élevé)
- **Mesures en place** :
  - Mention « généré par IA » sur chaque réponse (chat.py, ask.html)
  - Page de transparence sur les biais (transparency.html)
  - Interdiction d'usage décisionnel sur des personnes (politique)
  - Contestation d'une réponse (privacy.contest)
  - Choix du modèle documenté et révisable
- **Résiduel** : probabilité 4 (Probable) × gravité 2 (Limitée) = **8** (Modéré)
- **Statut de mise en œuvre** : Partiel : le biais du modèle ne peut pas être supprimé par l'application
- **Action restante** : Évaluer périodiquement un échantillon de réponses (fonction NIST Measure) ; consigner les résultats

### R02 : Discrimination par usage des réponses pour traiter des personnes

- **Scénario** : Une réponse du système sert à classer, noter ou écarter des personnes.
- **Catégorie** : Éthique · **Correspondance NIST AI 600-1** : Harmful bias and homogenization · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 3 (Possible) × gravité 4 (Grave) = **12** (Élevé)
- **Mesures en place** :
  - Politique d'utilisation : usage décisionnel interdit
  - Toutes les sanctions décidées par un humain, avec justification obligatoire (admin.py)
  - Contestation de toute décision
  - Prompt système : « ne prend pas de décision sur des personnes »
- **Résiduel** : probabilité 2 (Peu probable) × gravité 3 (Significative) = **6** (Modéré)
- **Statut de mise en œuvre** : Mis en œuvre (technique + politique)
- **Action restante** : Rappel périodique de la politique ; audit des usages

### R03 : Saisie de données personnelles par les utilisateurs

- **Scénario** : Un utilisateur colle des identifiants, coordonnées ou données de santé dans la requête.
- **Catégorie** : Vie privée · **Correspondance NIST AI 600-1** : Data privacy · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 5 (Quasi certain) × gravité 3 (Significative) = **15** (Élevé)
- **Mesures en place** :
  - Filtre bloquant avant stockage et avant tout appel fournisseur (compliance.py)
  - Signalement des catégories sensibles RGPD art. 9 et revue humaine
  - Pseudonymes : aucun nom ni e-mail collecté (register)
  - Chiffrement et purge automatique à 180 jours
  - Information de l'utilisateur à chaque saisie (ask.html)
- **Résiduel** : probabilité 3 (Possible) × gravité 2 (Limitée) = **6** (Modéré)
- **Statut de mise en œuvre** : Partiel : le filtre ne détecte pas les noms en texte libre
- **Action restante** : Évolution prévue : détection d'entités nommées (NER) ; sensibilisation des utilisateurs

### R04 : Fuite de données stockées (base, sauvegardes)

- **Scénario** : Accès non autorisé au fichier de base de données ou à une sauvegarde.
- **Catégorie** : Sécurité · **Correspondance NIST AI 600-1** : Information security · **Contrôle ISO/IEC 27002:2022** : 8.24, 8.3, 8.12
- **Inhérent** : probabilité 3 (Possible) × gravité 4 (Grave) = **12** (Élevé)
- **Mesures en place** :
  - Chiffrement des requêtes et réponses au repos (crypto.py)
  - Clés hors base (variables d'environnement), rotation possible
  - Fichier de base en mode 0600 (db.py)
  - Accès aux contenus réservé aux relecteurs, uniquement pour les contenus signalés
  - En-têtes de sécurité et CSP strict
- **Résiduel** : probabilité 2 (Peu probable) × gravité 3 (Significative) = **6** (Modéré)
- **Statut de mise en œuvre** : Mis en œuvre ; dépend du déploiement (HTTPS, sauvegardes chiffrées)
- **Action restante** : Appliquer la checklist de durcissement (SECURITY.md)

### R05 : Erreurs et informations inventées (hallucinations)

- **Scénario** : Le modèle affirme avec assurance des faits, sources ou citations faux.
- **Catégorie** : Fiabilité · **Correspondance NIST AI 600-1** : Confabulation · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 5 (Quasi certain) × gravité 3 (Significative) = **15** (Élevé)
- **Mesures en place** :
  - Étiquette « généré par IA » et avertissement sur chaque réponse
  - Règle n° 4 du prompt système : ne pas inventer
  - Politique : vérifier les informations importantes
  - Contestation d'une réponse
  - Base de connaissances de l'organisation pour limiter les réponses hors sujet
- **Résiduel** : probabilité 4 (Probable) × gravité 2 (Limitée) = **8** (Modéré)
- **Statut de mise en œuvre** : Partiel : risque inhérent aux modèles de langage
- **Action restante** : Mesurer le taux d'erreurs sur un jeu de questions de référence

### R06 : Dépendance excessive à l'IA (sur-confiance)

- **Scénario** : Les utilisateurs acceptent les réponses sans vérification, y compris pour des sujets importants.
- **Catégorie** : Éthique · **Correspondance NIST AI 600-1** : Human-AI configuration · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 4 (Probable) × gravité 3 (Significative) = **12** (Élevé)
- **Mesures en place** :
  - Page de transparence et rappels dans l'interface
  - Politique d'utilisation
  - Limite de 30 requêtes par heure
  - Absence de mise en forme « autoritaire » (réponse étiquetée IA)
- **Résiduel** : probabilité 3 (Possible) × gravité 3 (Significative) = **9** (Modéré)
- **Statut de mise en œuvre** : Partiel
- **Action restante** : Sessions de sensibilisation (culture IA, AI Act art. 4)

### R07 : Transfert de données vers un fournisseur externe (Groq, États-Unis)

- **Scénario** : Les requêtes quittent l'organisation et le pays sans garanties suffisantes ni information des utilisateurs.
- **Catégorie** : Vie privée / Juridique · **Correspondance NIST AI 600-1** : Value chain and component integration; Data privacy · **Contrôle ISO/IEC 27002:2022** : 5.19, 5.20, 5.23
- **Inhérent** : probabilité 4 (Probable) × gravité 4 (Grave) = **16** (Élevé)
- **Mesures en place** :
  - Fournisseur par défaut hors ligne : aucun transfert sans activation explicite (config.py)
  - Alternative locale (Ollama)
  - Information affichée avant chaque requête (parcours de la donnée)
  - Droit d'opposition par utilisateur (settings)
  - Traçabilité par requête : champ external_transfer et audit
  - Filtre appliqué avant envoi ; seules les requêtes sont envoyées (ni identifiant, ni IP, ni historique)
  - Évaluation du transfert (transferts-groq.md)
- **Résiduel** : probabilité 2 (Peu probable) × gravité 3 (Significative) = **6** (Modéré)
- **Statut de mise en œuvre** : Technique mis en œuvre ; actions organisationnelles à finaliser (contrat de sous-traitance, autorisation CNDP)
- **Action restante** : Signer l'accord de traitement, obtenir l'autorisation CNDP, vérifier la politique de conservation du fournisseur

### R08 : Injection de prompt et manipulation du modèle

- **Scénario** : Un texte collé par l'utilisateur contient des instructions qui détournent le modèle (fuite du prompt système, contenu inapproprié).
- **Catégorie** : Sécurité IA · **Correspondance NIST AI 600-1** : Information security · **Contrôle ISO/IEC 27002:2022** : 8.28
- **Inhérent** : probabilité 4 (Probable) × gravité 3 (Significative) = **12** (Élevé)
- **Mesures en place** :
  - Le modèle n'a accès à aucun outil, fichier ni base de données
  - Aucun secret dans le prompt système
  - Masquage des données personnelles dans les sorties (compliance.redact)
  - Échappement des sorties (voir R09)
  - Limite de longueur de requête
- **Résiduel** : probabilité 3 (Possible) × gravité 2 (Limitée) = **6** (Modéré)
- **Statut de mise en œuvre** : Mis en œuvre (limitation de la surface d'attaque)
- **Action restante** : Ne pas donner d'outils ou d'actions au modèle sans nouvelle analyse de risque

### R09 : XSS via la sortie du modèle

- **Scénario** : La réponse contient du HTML ou du script exécuté dans le navigateur d'un utilisateur ou d'un relecteur.
- **Catégorie** : Sécurité · **Correspondance NIST AI 600-1** : Information security · **Contrôle ISO/IEC 27002:2022** : 8.28
- **Inhérent** : probabilité 3 (Possible) × gravité 4 (Grave) = **12** (Élevé)
- **Mesures en place** :
  - Échappement automatique Jinja
  - Rendu Markdown qui échappe avant de formater (app.js)
  - CSP stricte sans script ni style inline
  - Test automatisé du chemin XSS (test_xss_payload_is_escaped_everywhere)
- **Résiduel** : probabilité 1 (Rare) × gravité 3 (Significative) = **3** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre et testé
- **Action restante** : Conserver le test en intégration continue

### R10 : Compromission de compte (force brute, réutilisation de mots de passe)

- **Scénario** : Un attaquant devine ou réutilise un mot de passe et lit l'historique d'un utilisateur.
- **Catégorie** : Sécurité · **Correspondance NIST AI 600-1** : Information security · **Contrôle ISO/IEC 27002:2022** : 5.17, 8.5
- **Inhérent** : probabilité 4 (Probable) × gravité 3 (Significative) = **12** (Élevé)
- **Mesures en place** :
  - Hachage scrypt
  - Limitation des tentatives par identifiant et par IP (clés HMAC)
  - Politique de mot de passe (10 caractères, liste de mots courants)
  - Cookies HttpOnly, SameSite, Secure en production ; session de 2 h ; régénération de session
  - Jeton CSRF
- **Résiduel** : probabilité 2 (Peu probable) × gravité 3 (Significative) = **6** (Modéré)
- **Statut de mise en œuvre** : Mis en œuvre ; pas d'authentification multifacteur
- **Action restante** : Évolution prévue : authentification multifacteur (TOTP)

### R11 : Accès abusif d'un administrateur aux contenus

- **Scénario** : Un relecteur consulte des requêtes sans nécessité, ou modifie les traces pour masquer ses actes.
- **Catégorie** : Sécurité / Éthique · **Correspondance NIST AI 600-1** : Data privacy · **Contrôle ISO/IEC 27002:2022** : 5.15, 8.15
- **Inhérent** : probabilité 3 (Possible) × gravité 4 (Grave) = **12** (Élevé)
- **Mesures en place** :
  - Un relecteur n'ouvre que les contenus signalés (admin.py)
  - Chaque ouverture est journalisée
  - Journal d'audit chaîné par hachage, vérifiable (flask verify-audit)
  - Un administrateur ne peut pas suspendre un autre administrateur
  - Liste des utilisateurs sans contenu
- **Résiduel** : probabilité 2 (Peu probable) × gravité 3 (Significative) = **6** (Modéré)
- **Statut de mise en œuvre** : Mis en œuvre
- **Action restante** : Recommander deux relecteurs (principe des quatre yeux) et une vérification régulière du journal

### R12 : Conservation excessive des données (échec de la purge)

- **Scénario** : Les requêtes restent stockées au-delà de la durée annoncée.
- **Catégorie** : Conformité · **Correspondance NIST AI 600-1** : Data privacy · **Contrôle ISO/IEC 27002:2022** : 8.10
- **Inhérent** : probabilité 3 (Possible) × gravité 3 (Significative) = **9** (Modéré)
- **Mesures en place** :
  - Purge automatique toutes les 24 h (retention.py)
  - Commande flask purge
  - Durées configurables et documentées
  - Test automatisé de la purge
  - Suppression à la demande par l'utilisateur
- **Résiduel** : probabilité 1 (Rare) × gravité 3 (Significative) = **3** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre et testé
- **Action restante** : Surveiller l'événement d'audit RETENTION_PURGE

### R13 : Décision automatisée sans intervention humaine (art. 22 RGPD)

- **Scénario** : Une sanction ou un refus est prononcé par le système sans examen humain ni possibilité de contestation.
- **Catégorie** : Conformité / Éthique · **Correspondance NIST AI 600-1** : Human-AI configuration · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 3 (Possible) × gravité 4 (Grave) = **12** (Élevé)
- **Mesures en place** :
  - Le système n'attribue aucune sanction : seul un humain avertit, supprime ou suspend (admin.py)
  - Justification écrite obligatoire
  - Procédure de contestation ; un compte suspendu peut encore contester, exporter et supprimer
  - Le filtre ne fait que rejeter une saisie, sans effet sur le compte
- **Résiduel** : probabilité 1 (Rare) × gravité 4 (Grave) = **4** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre et testé
- **Action restante** : Respecter le délai de réponse aux contestations (15 jours ouvrés visés, 1 mois maximum)

### R14 : Indisponibilité du fournisseur d'IA

- **Scénario** : Le fournisseur est indisponible ou change de modèle.
- **Catégorie** : Disponibilité · **Correspondance NIST AI 600-1** : Value chain and component integration · **Contrôle ISO/IEC 27002:2022** : 5.23
- **Inhérent** : probabilité 4 (Probable) × gravité 2 (Limitée) = **8** (Modéré)
- **Mesures en place** :
  - Basculement vers l'assistant hors ligne avec note explicite à l'utilisateur
  - Délais d'attente (5 s connexion, 45 s lecture)
  - Modèle paramétrable
- **Résiduel** : probabilité 3 (Possible) × gravité 1 (Négligeable) = **3** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre et testé
- **Action restante** : Surveiller les dépréciations de modèles du fournisseur

### R15 : Information insuffisante des utilisateurs

- **Scénario** : Les utilisateurs ne savent pas où vont leurs données ni comment exercer leurs droits.
- **Catégorie** : Conformité · **Correspondance NIST AI 600-1** : Data privacy · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 3 (Possible) × gravité 3 (Significative) = **9** (Modéré)
- **Mesures en place** :
  - Notice de confidentialité publique avant inscription
  - Parcours de la donnée affiché sur la page de requête
  - Consentement à la politique enregistré avec la version
  - Pages « Mes données » et « Réglages »
- **Résiduel** : probabilité 1 (Rare) × gravité 2 (Limitée) = **2** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre
- **Action restante** : Mettre à jour la notice à chaque changement de traitement

### R16 : Compromission ou perte des clés de chiffrement

- **Scénario** : La clé de chiffrement est volée avec la base, ou perdue (historique illisible).
- **Catégorie** : Sécurité · **Correspondance NIST AI 600-1** : Information security · **Contrôle ISO/IEC 27002:2022** : 8.24
- **Inhérent** : probabilité 2 (Peu probable) × gravité 4 (Grave) = **8** (Modéré)
- **Mesures en place** :
  - Clés séparées de la base
  - Rotation par clés multiples (MultiFernet, testée)
  - Clé obligatoire en production, jamais générée silencieusement
  - Sauvegarde de la clé dans un gestionnaire de secrets (procédure)
- **Résiduel** : probabilité 1 (Rare) × gravité 4 (Grave) = **4** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre ; procédure de gestion des secrets à appliquer par l'organisation
- **Action restante** : Documenter la sauvegarde et la rotation annuelle des clés

### R17 : Mésusage par les utilisateurs (contenus illicites, notation de personnes)

- **Scénario** : Un utilisateur sollicite le système pour des contenus illicites ou pour évaluer des personnes.
- **Catégorie** : Éthique · **Correspondance NIST AI 600-1** : Human-AI configuration · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 3 (Possible) × gravité 3 (Significative) = **9** (Modéré)
- **Mesures en place** :
  - Politique d'utilisation acceptée à l'inscription
  - Revue humaine des contenus signalés
  - Échelle de sanctions graduée et contestable
  - Limite de débit
- **Résiduel** : probabilité 2 (Peu probable) × gravité 2 (Limitée) = **4** (Faible)
- **Statut de mise en œuvre** : Mis en œuvre
- **Action restante** : Revue semestrielle des cas traités

### R18 : Non-conformité réglementaire (formalités, DPO, sous-traitance)

- **Scénario** : Le traitement est exploité sans déclaration ou autorisation préalable de la CNDP, sans accord de sous-traitance, ou sans avis du DPO.
- **Catégorie** : Conformité · **Correspondance NIST AI 600-1** : Govern · **Contrôle ISO/IEC 27002:2022** : 5.34
- **Inhérent** : probabilité 3 (Possible) × gravité 4 (Grave) = **12** (Élevé)
- **Mesures en place** :
  - AIPD et registre des traitements fournis
  - Analyse juridique et liste d'actions
  - Définition de conformité avec statut par critère
- **Résiduel** : probabilité 2 (Peu probable) × gravité 4 (Grave) = **8** (Modéré)
- **Statut de mise en œuvre** : À compléter par l'organisation : ces démarches ne peuvent pas être automatisées
- **Action restante** : Déclarer ou obtenir l'autorisation CNDP (loi 09-08, art. 12), désigner un point de contact, signer les accords de sous-traitance

## 6. Plan de traitement des actions restantes

| ID | Action | Propriétaire |
|---|---|---|
| R06 | Sessions de sensibilisation (culture IA, AI Act art. 4) | Comité de gouvernance |
| R01 | Évaluer périodiquement un échantillon de réponses (fonction NIST Measure) ; consigner les résultats | Responsable IA / comité de gouvernance |
| R05 | Mesurer le taux d'erreurs sur un jeu de questions de référence | Responsable IA |
| R18 | Déclarer ou obtenir l'autorisation CNDP (loi 09-08, art. 12), désigner un point de contact, signer les accords de sous-traitance | Responsable de traitement |
| R02 | Rappel périodique de la politique ; audit des usages | Responsable de traitement |
| R03 | Évolution prévue : détection d'entités nommées (NER) ; sensibilisation des utilisateurs | DPO / point de contact |
| R04 | Appliquer la checklist de durcissement (SECURITY.md) | Responsable technique |
| R07 | Signer l'accord de traitement, obtenir l'autorisation CNDP, vérifier la politique de conservation du fournisseur | Responsable de traitement |
| R08 | Ne pas donner d'outils ou d'actions au modèle sans nouvelle analyse de risque | Responsable technique |
| R10 | Évolution prévue : authentification multifacteur (TOTP) | Responsable technique |
| R11 | Recommander deux relecteurs (principe des quatre yeux) et une vérification régulière du journal | Responsable de traitement |
| R13 | Respecter le délai de réponse aux contestations (15 jours ouvrés visés, 1 mois maximum) | Responsable de traitement |
| R16 | Documenter la sauvegarde et la rotation annuelle des clés | Responsable technique |
| R17 | Revue semestrielle des cas traités | Comité de gouvernance |
| R09 | Conserver le test en intégration continue | Responsable technique |
| R12 | Surveiller l'événement d'audit RETENTION_PURGE | Responsable technique |
| R14 | Surveiller les dépréciations de modèles du fournisseur | Responsable technique |
| R15 | Mettre à jour la notice à chaque changement de traitement | DPO / point de contact |

## 7. Revue

Revue tous les 6 mois et à chaque changement structurant (voir `gouvernance-ia.md`). La date et l'auteur de chaque revue sont consignés dans le registre de gouvernance de l'organisation.
