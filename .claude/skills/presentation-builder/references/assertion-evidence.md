# Doctrine assertion–preuve

> Une diapositive n'est pas une page de manuel. Elle est une affirmation que le visuel rend indiscutable.

---

## La règle fondamentale

| Zone | Contenu | Interdit |
|------|---------|----------|
| **Titre** | Une phrase complète : sujet + verbe + affirmation. C'est le message à retenir. | Un label, un thème, un mot isolé. |
| **Corps** | Un seul visuel qui prouve l'assertion du titre. Schéma, diagramme, capture, tableau chiffré, extrait de code ciblé. | Plusieurs visuels en concurrence. Une liste de bullets. Du code intégral projeté. |
| **Détail** | Notes orateur uniquement — invisible pour le jury. | Texte de lecture qui double ce que le jury voit déjà. |

Conséquence directe : la combinaison "mur de bullets + code projeté intégralement" est structurellement impossible avec cette doctrine.

---

## Avant / après

| Avant (label) | Après (assertion) |
|---------------|-------------------|
| Sécurité | Sans mot de passe à voler : l'accès passe par un lien à usage unique. |
| Architecture logicielle | Le métier est protégé : tout dépend du domaine, qui ne dépend de rien. |
| Modèle de données | Le prix est figé en base, même si l'écriture contourne l'application. |
| Jeu d'essai | Le tunnel se comporte comme prévu, y compris quand il doit refuser. |
| Base de données | Chaque entité a une clé métier stable, indépendante de l'identifiant technique. |
| Gestion des erreurs | L'utilisateur voit toujours un message actionnable, jamais une stack trace. |

Chaque "après" est une vraie phrase : sujet identifiable, verbe conjugué, affirmation vérifiable. Ce n'est pas un titre de section — c'est une thèse que le visuel vient étayer.

---

## Ce qui va dans les notes orateur

Les notes orateur portent tout ce que le jury ne doit pas lire sur l'écran :

- **Définitions** — expliquer un terme technique sans le projeter (« DDD : Domain-Driven Design, l'idée que le code modélise le métier, pas l'inverse »).
- **Anti-sèches** — chiffres, dates, noms de librairies, valeurs de configuration que l'on cite à l'oral sans les retenir par cœur.
- **Réponses probables au jury** — anticiper les questions prévisibles et y répondre dans les notes, phrase par phrase, prêtes à lire si le stress monte.
- **Transitions** — la phrase exacte qui relie cette diapo à la suivante (« Ce choix d'architecture a une contrepartie directe sur le modèle de données — slide suivante »).

Les notes ne résument pas la diapo. Elles la prolongent vers ce que la diapo ne peut pas montrer.

---

## Le test d'une diapositive

Avant de valider une slide, appliquer ce test :

> **Projetée 20 secondes pendant que je parle, est-ce qu'elle aide ou est-ce qu'elle se lit à ma place ?**

- Si le jury lit la slide au lieu de vous écouter : elle contient trop de texte. Déplacez vers les notes.
- Si la slide peut exister sans vous : elle n'illustre rien. Remplacez le texte par un visuel.
- Si vous ne pouvez pas résumer son message en une phrase : le titre est un label, pas une assertion. Réécrivez-le.

Un visuel qui « aide » attire l'œil sur la preuve pendant que la voix porte le raisonnement. Un visuel qui « se lit à votre place » remplace la voix — et vous rend inutile sur scène.

---

## Application dans le pipeline presentation-builder

- **Étape Storyboard** : chaque carte doit avoir un titre-assertion avant de passer à l'étape suivante. Un titre sans verbe est un signal d'alarme.
- **Étape Notes** : les notes sont rédigées selon les quatre catégories ci-dessus. Aucun texte de slide ne migre vers les notes à la légère — si c'est important à dire, c'est dans les notes ; si c'est important à montrer, c'est dans le visuel.
- **Revue finale** : appliquer le test des 20 secondes sur chaque slide avant export.
