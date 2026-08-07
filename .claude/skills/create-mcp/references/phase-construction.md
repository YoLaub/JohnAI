# Phase construction — bâtir ou durcir un serveur MCP

Pour un serveur MCP neuf ou existant, à sécuriser couche par couche dans l'ordre de
`SKILL.md` (identité → délégation tierce → cloisonnement → anti-abus → observabilité
→ isolation → exposition). Chaque couche est une itération TDD complète, pas une
case à cocher.

## Avant de commencer

1. Vérifier ce qui existe déjà (une couche déjà solide ne se refait pas) : lister les
   tools MCP actuels et leur mécanisme d'auth actuel, s'il y en a un.
2. Décider par question fermée (AskUserQuestion) les couches réellement nécessaires :
   - Couche 2 (OAuth) n'a de sens QUE s'il existe ou existera un connecteur tiers
     (client web/mobile d'un éditeur) qui ne peut pas porter un token statique. Un
     usage interne/agent-only n'en a pas besoin — l'ajouter quand même est de la
     sur-ingénierie.
   - Couche 3 (cloisonnement) ne s'applique que s'il y a un multi-tenant/multi-
     utilisateur réel. Un serveur mono-utilisateur n'a rien à cloisonner.
   - Couche 6 (sandbox) est surtout utile s'il existe des tools à effet de bord
     externe irréversible (email, paiement, appel API tiers facturé).

## Par couche

1. Lire la section correspondante de `references/couches.md`.
2. Tests d'abord sur la logique pure (génération/hash de token, calcul du bucket de
   rate-limit, garde de cloisonnement) — indépendante du transport HTTP/MCP.
3. Implémenter en respectant le pattern générique de la couche ; adapter au
   framework/lib MCP utilisé sans copier une stack spécifique dans ce fichier.
4. Vérification end-to-end réelle de la couche (pas seulement les tests unitaires) :
   un appel réel sans identité → rejeté ; avec identité → accepté ; le cas limite de
   la couche (rotation de token, refresh OAuth, franchissement du plafond de
   rate-limit...) reproduit et vérifié.
5. Si un piège générique apparaît, l'ajouter à `references/couches.md` (section de la
   couche). Si le piège est spécifique à une stack, l'ajouter à `references/pieges.md`.
6. Documenter la décision (pourquoi cette couche, quels paramètres) si le projet tient
   un index de décisions (ex. fiche OKF) — ce skill ne prescrit pas de format
   particulier, il s'insère dans celui du projet hôte.

## Ordre non négociable

Ne jamais implémenter une couche avant celles qui la précèdent dans `SKILL.md` :
implémenter le rate-limit (4) avant l'identité (1) n'a pas de clé sur laquelle
compter ; implémenter le cloisonnement (3) avant l'identité revient à cloisonner sur
une valeur déclarée par l'appelant, donc contournable.
