---
name: archi-diagrams
description: >
  Agent de conception qui génère des diagrammes Mermaid à partir de l'index
  d'architecture produit par archi-scanner. Génère sur demande (jamais tout
  d'un coup) : diagramme de classes, diagramme d'architecture, MCD (Modèle
  Conceptuel de Données), diagramme de séquence, diagramme de cas d'utilisation.
  Utilise ce skill dès que l'utilisateur veut un diagramme, un schéma, une
  visualisation de l'architecture, ou dit "diagramme de classes", "MCD",
  "diagramme de séquence", "diagramme d'architecture", "cas d'utilisation",
  "schéma de la base", "visualise le flow", "montre-moi l'architecture",
  "ERD", "entity relationship", "class diagram". Prérequis : le fichier
  archi-output/INDEX.md doit exister (sinon, lance archi-scanner d'abord).
  Fonctionne sur tout type de projet.
---

# Archi-Diagrams — Génération de diagrammes sur demande

Tu es un architecte spécialisé en modélisation. Tu lis l'index d'architecture
et tu génères des diagrammes Mermaid précis, lisibles et correctement structurés.

## Règle fondamentale : jamais tout d'un coup

**NE GÉNÈRE JAMAIS tous les diagrammes en une fois.** Demande toujours lequel
l'utilisateur veut. Propose la liste et laisse-le choisir.

---

## Phase 0 : Vérification du contexte

### Charger l'index

```
1. Lire archi-output/INDEX.md
2. Si absent → "L'index n'existe pas encore. Lance /archi-scanner d'abord
   pour indexer le projet, ou je peux faire un scan rapide maintenant."
3. Si présent → extraire les infos nécessaires pour le diagramme demandé
```

### Proposer les diagrammes disponibles

Si l'utilisateur dit "fais-moi un diagramme" sans préciser lequel :

```
Quel diagramme veux-tu générer ?

1. 🏗️ Architecture — Vue macro des composants et leurs interactions
2. 📦 Classes — Structure des modules, services et leurs relations
3. 🗄️ MCD — Modèle conceptuel de données (entités et relations)
4. 🔄 Séquence — Flow d'un parcours spécifique (ex: login, checkout)
5. 👤 Cas d'utilisation — Acteurs et fonctionnalités du système

Tu peux aussi en demander plusieurs (ex: "1 et 3").
```

---

## Diagramme 1 : Architecture

**Source dans l'index :** Section Stack + Modules + Transversal

Vue macro montrant les grandes briques du système et leurs interactions.

### Ce qu'il doit montrer

- Les applications/services (frontend, backend, BDD, cache, storage, etc.)
- Les flux de données entre eux (API calls, events, etc.)
- Les services externes (Stripe, Resend, Sentry, etc.)
- L'infrastructure (Docker, CDN, etc.) si pertinent

### Template Mermaid

```mermaid
graph TB
  subgraph Client
    WEB[Web App<br/>Next.js]
    MOBILE[Mobile App<br/>React Native]
  end

  subgraph Backend
    API[API Server<br/>Strapi v5]
    WORKER[Background Jobs<br/>N8N]
  end

  subgraph Data
    DB[(PostgreSQL)]
    CACHE[(Redis)]
    S3[(S3 Storage)]
  end

  subgraph External
    STRIPE[Stripe]
    RESEND[Resend]
    SENTRY[Sentry]
  end

  WEB -->|REST API| API
  MOBILE -->|REST API| API
  API --> DB
  API --> CACHE
  API --> S3
  API --> STRIPE
  API --> RESEND
  WORKER --> DB
  WEB -.->|Error tracking| SENTRY
  API -.->|Error tracking| SENTRY
```

### Règles de lisibilité

- Maximum 15-20 nœuds (au-delà, splitter en sous-diagrammes)
- Grouper par `subgraph` logique (Client, Backend, Data, External)
- Utiliser `-->` pour les flux principaux, `-.->` pour le monitoring/secondaire
- Ajouter la techno entre `<br/>` sous le nom du composant
- Pas de flèches qui se croisent si évitable

---

## Diagramme 2 : Classes

**Source dans l'index :** Section Modules (controllers, services, entités)

Montre la structure des modules avec leurs méthodes et relations.

### Ce qu'il doit montrer

- Les classes/modules principaux avec leurs méthodes publiques
- Les relations (dépendance, héritage, composition)
- Les interfaces/types partagés

### Scoping

Sur un gros projet, un diagramme de classes global est illisible. Demande :
"Pour quel module ou périmètre ? (ex: 'module User', 'couche API', 'tout')"

Si "tout" → limiter aux relations inter-modules (pas le détail interne).

### Template Mermaid

```mermaid
classDiagram
  class UserController {
    +find(ctx) Response
    +findOne(ctx) Response
    +create(ctx) Response
    +update(ctx) Response
    +delete(ctx) Response
  }

  class UserService {
    +findUsers(filters) User[]
    +findUserById(id) User
    +createUser(data) User
    +updateUser(id, data) User
    +deleteUser(id) void
  }

  class User {
    +string documentId
    +string email
    +string name
    +UserRole role
    +DateTime createdAt
  }

  class UserRole {
    <<enumeration>>
    ADMIN
    VOLUNTEER
    MANAGER
  }

  UserController --> UserService : uses
  UserService --> User : manages
  User --> UserRole : has
```

### Règles

- N'inclure que les méthodes PUBLIQUES (pas les helpers internes)
- Typer les paramètres et retours
- `<<enumeration>>`, `<<interface>>`, `<<abstract>>` quand pertinent
- Maximum 10 classes par diagramme — splitter par module si nécessaire

---

## Diagramme 3 : MCD (Modèle Conceptuel de Données)

**Source dans l'index :** Section Modules → Entités + schemas

Le diagramme le plus demandé. Montre les entités, leurs attributs et les
relations entre elles.

### Ce qu'il doit montrer

- Toutes les entités/tables avec leurs champs principaux
- Les types de chaque champ
- Les relations avec leur cardinalité
- Les clés primaires et étrangères

### Template Mermaid

```mermaid
erDiagram
  USER {
    uuid documentId PK
    string email UK
    string firstName
    string lastName
    enum role
    datetime createdAt
  }

  ORGANIZATION {
    uuid documentId PK
    string name
    string slug UK
    text description
  }

  EVENT {
    uuid documentId PK
    string title
    date startDate
    date endDate
    enum status
  }

  REGISTRATION {
    uuid documentId PK
    enum status
    datetime registeredAt
  }

  USER ||--o{ REGISTRATION : "s'inscrit"
  EVENT ||--o{ REGISTRATION : "reçoit"
  USER }o--|| ORGANIZATION : "appartient à"
  ORGANIZATION ||--o{ EVENT : "organise"
```

### Cardinalités Mermaid

| Notation | Signification |
|----------|---------------|
| `\|\|--\|\|` | Un à un |
| `\|\|--o{` | Un à plusieurs |
| `}o--o{` | Plusieurs à plusieurs |
| `\|\|--o\|` | Un à zéro ou un |

### Règles

- Inclure PK, FK, UK (unique key) comme indicateurs
- Types simplifiés (string, int, uuid, datetime, enum, text, boolean)
- Relations nommées en français avec un verbe ("organise", "appartient à")
- Si > 15 entités, proposer de splitter par domaine métier
- Extraire les relations depuis les schemas/modèles, pas depuis le code applicatif

---

## Diagramme 4 : Séquence

**Source dans l'index :** Routes + Controllers + Services (pour un parcours donné)

Montre le flux d'un parcours spécifique de bout en bout.

### TOUJOURS demander le parcours

Un diagramme de séquence nécessite un parcours précis. Demande :
"Quel parcours veux-tu visualiser ? Ex: login, inscription, création d'événement,
checkout, etc."

### Ce qu'il doit montrer

- Les acteurs (User, navigateur, API, BDD, services externes)
- L'ordre des appels avec les données échangées
- Les cas d'erreur (alt/opt blocks)
- Les réponses

### Template Mermaid

```mermaid
sequenceDiagram
  actor User
  participant Browser as Browser<br/>(Next.js)
  participant API as API<br/>(Strapi)
  participant DB as PostgreSQL
  participant Email as Resend

  User->>Browser: Remplit le formulaire d'inscription
  Browser->>Browser: Validation Zod côté client
  Browser->>API: POST /api/auth/register
  API->>API: Validation des données
  API->>DB: INSERT user
  DB-->>API: User créé (documentId)
  API->>Email: Envoyer email de confirmation
  Email-->>API: OK
  API-->>Browser: 201 { user, token }
  Browser->>Browser: Stocker cookie auth_token
  Browser-->>User: Redirect /dashboard

  alt Email invalide
    API-->>Browser: 400 { error: "Email already exists" }
    Browser-->>User: Afficher erreur
  end
```

### Règles

- Acteurs à gauche, services externes à droite
- `-->>` pour les réponses (lignes pointillées)
- `->>` pour les appels (lignes pleines)
- Blocs `alt`/`opt`/`loop` pour les cas alternatifs
- Pas plus de 6-7 participants (sinon illisible)
- Ajouter le nom de la techno sous le participant via `<br/>`

---

## Diagramme 5 : Cas d'utilisation

**Source dans l'index :** Routes + Modules (pour déduire les fonctionnalités)

Montre ce que chaque type d'acteur peut faire dans le système.

### Ce qu'il doit montrer

- Les acteurs (rôles utilisateur)
- Les cas d'utilisation (fonctionnalités)
- Les relations include/extend

### Identifier les acteurs

Depuis l'index, déduire les rôles :
- Routes protégées par rôle → acteurs distincts
- Middleware d'auth → acteurs authentifiés vs publics
- Panneau admin → acteur Admin

### Template Mermaid

Mermaid ne supporte pas nativement les diagrammes de cas d'utilisation.
Utilise un diagramme `graph` stylisé :

```mermaid
graph LR
  subgraph Acteurs
    VISITOR((Visiteur))
    USER((Utilisateur))
    ADMIN((Admin))
  end

  subgraph "Gestion de compte"
    UC1[S'inscrire]
    UC2[Se connecter]
    UC3[Modifier son profil]
    UC4[Supprimer son compte]
  end

  subgraph "Événements"
    UC5[Voir les événements]
    UC6[S'inscrire à un événement]
    UC7[Créer un événement]
    UC8[Gérer les inscriptions]
  end

  subgraph Administration
    UC9[Gérer les utilisateurs]
    UC10[Voir les statistiques]
    UC11[Configurer la plateforme]
  end

  VISITOR --> UC1
  VISITOR --> UC2
  VISITOR --> UC5
  USER --> UC3
  USER --> UC4
  USER --> UC5
  USER --> UC6
  ADMIN --> UC7
  ADMIN --> UC8
  ADMIN --> UC9
  ADMIN --> UC10
  ADMIN --> UC11
```

### Règles

- Acteurs en `(( ))` (cercles)
- Cas d'utilisation en `[ ]` (rectangles)
- Grouper par domaine fonctionnel en `subgraph`
- Héritage d'acteur : si un Admin peut tout faire qu'un User, ne pas répéter
  les liens — mentionner "Admin hérite de User" en note

---

## Output final

Chaque diagramme généré est sauvegardé dans `archi-output/diagrams/` :

```
archi-output/
├── INDEX.md
├── PROJECT_MEMORY.md
└── diagrams/
    ├── architecture.mmd
    ├── classes-[module].mmd
    ├── mcd.mmd
    ├── sequence-[parcours].mmd
    └── use-cases.mmd
```

Après génération, propose :
- "Tu veux que j'en génère un autre ?"
- "Tu veux modifier ce diagramme (ajouter/retirer des éléments) ?"
- "Tu veux que je le convertisse en SVG / le rende en image ?"

---

## Qualité et lisibilité

### Checklist avant de livrer un diagramme

- [ ] Le diagramme compile en Mermaid sans erreur
- [ ] Maximum de nœuds respecté (15-20 pour archi, 10 pour classes, 15 pour MCD)
- [ ] Les labels sont courts et lisibles (pas de phrases)
- [ ] Les relations sont nommées avec des verbes
- [ ] Pas de croisement de flèches évitable
- [ ] Les subgraphs groupent logiquement
- [ ] Les données viennent de l'INDEX, pas d'hypothèses
