# Les 7 couches — substance générique

Fichier append-only. Chaque couche : principe, pattern générique (sans stack imposée),
piège à ne pas rejouer. Ajouter des notes par stack en sous-section datée quand une
implémentation concrète apporte un détail non couvert par le générique — ne jamais
réécrire le principe pour coller à une seule stack.

## 1. Identité — token personnel

**Principe** : un utilisateur = un secret opaque, révocable, jamais rejouable en clair.
Pas de secret partagé (un seul `API_TOKEN` pour tout le monde) : il ne s'isole pas,
il ne se révoque pas sans casser tout le monde.

**Pattern générique** :
- Génération : aléatoire cryptographique (pas un UUID prévisible), préfixé pour
  identifier la famille de secret au premier coup d'œil dans les logs (`xxx_<random>`).
- Stockage : hash à sens unique (le secret brut n'existe qu'à l'émission, jamais en base).
- Résolution : le serveur retrouve l'identité à partir du hash du bearer reçu, jamais
  d'un identifiant déclaré dans la requête (sinon usurpation triviale — l'appelant
  déclare "je suis Alice" au lieu que le token le prouve).
- Rotation = régénération : un seul secret actif par identité, l'ancien meurt à l'émission
  du nouveau.

**Piège à ne pas rejouer** : si un identifiant (userId, tenantId...) reste dans le
schéma d'un tool "pour compatibilité", il permet de contourner l'identité dérivée du
token. Le supprimer partout, pas seulement là où c'est visible.

## 2. Délégation tierce — OAuth 2.1

**Principe** : le token personnel (couche 1) suppose que l'utilisateur peut copier un
secret dans la config de son agent. Un connecteur tiers (client web/mobile d'un
éditeur, app grand public) ne peut pas ; il lui faut un flux d'autorisation standard.

**Pattern générique** :
- Clients publics uniquement (pas de secret client à protéger côté client) + PKCE
  obligatoire (S256) — c'est le remplacement du secret client.
- Enregistrement dynamique (DCR) ouvert : ce n'est PAS le registre qui protège, c'est
  l'écran de consentement par utilisateur au moment de l'autorisation.
- `redirect_uri` vérifié en correspondance EXACTE (pas de préfixe, pas de wildcard) ;
  HTTPS obligatoire sauf loopback local.
- Tokens courts (accès) + rotation stricte au refresh (l'ancienne paire access+refresh
  meurt d'un bloc à chaque rotation — un refresh rejoué doit tout révoquer).
- Erreurs opaques côté client (`invalid_grant` sans détail) ; jamais de redirection
  vers une URI non enregistrée, même en cas d'erreur.
- Les deux mécanismes (token perso + OAuth) doivent résoudre la MÊME identité interne
  — aucune logique métier dupliquée entre les deux chemins d'auth.

**Piège à ne pas rejouer** : le endpoint de découverte/metadata émet déjà les en-têtes
standards attendus par les clients (ex. pointeur vers les métadonnées dans un challenge
d'auth) — ne pas les réécrire à la main si le framework/lib utilisé les fournit déjà.
Un reverse proxy ou middleware générique placé devant l'API doit explicitement exclure
les routes de découverte OAuth (souvent sous un chemin `.well-known` ou équivalent),
sinon le flux casse silencieusement pour les clients tiers.

## 3. Cloisonnement — authz par tool

**Principe** : l'identité résolue (couche 1/2) ne sert à rien si un tool charge une
ressource par son seul id sans vérifier qu'elle appartient à l'appelant.

**Pattern générique** :
- Toute lecture/écriture d'une ressource cloisonnée passe par une garde qui combine
  `id` ET l'identité résolue (ex. `find(id, owner=identité)` qui échoue proprement
  plutôt qu'un `find(id)` suivi d'une vérification a posteriori qu'on peut oublier).
- Une garde par TYPE de ressource, factorisée une seule fois, réutilisée par tous les
  tools qui touchent ce type — jamais réécrite tool par tool.
- Pour les sous-ressources (une tâche qui appartient à un projet qui appartient à un
  tenant), la garde remonte toute la chaîne, pas seulement le premier niveau.

**Piège à ne pas rejouer** (le plus coûteux des 7, vérifié deux fois sur CRM_TEAM) :
corriger une fonction d'une CLASSE de bug ne suffit pas. Après tout fix de
cloisonnement, GREP systématiquement toutes les fonctions de la même forme sur la
même entité (create/get/update/delete/send...) dans TOUT le codebase — le bug se
reproduit presque toujours sur la fonction sœur qu'on n'avait pas sous les yeux au
moment du premier fix.

## 4. Anti-abus — rate-limit par identité

**Principe** : un secret qui fuit (couche 1 ou 2) ne doit pas donner un usage illimité.

**Pattern générique** :
- Algorithme token bucket (capacité + taux de recharge) : tolère les rafales
  légitimes, borne le débit soutenu.
- Clé du bucket = **identité résolue**, jamais le token brut ni l'adresse IP seule —
  un token qui fuit partage alors le même plafond que l'usage légitime, ce qui est le
  comportement voulu (pas un blocage total, juste un plafond).
- Un seul conteneur/instance de limiteur par processus de vie du serveur (singleton
  créé au chargement, pas par requête) — sinon chaque appel repart avec un bucket
  plein et le rate-limit ne sert à rien.
- Paramètres (capacité, taux) réglables sans redéploiement de code (config/env).
- En mémoire est acceptable pour un garde-fou anti-abus mono-instance ; passer à un
  store partagé (type Redis) seulement si plusieurs instances du serveur coexistent.

**Piège à ne pas rejouer** : placer le check de rate-limit HORS de la portée du
logging (couche 5) — un rejet de rate-limit doit apparaître dans les logs comme un
appel de tool en erreur, sinon un abus en cours passe inaperçu.

## 5. Observabilité — logging des appels de tool

**Principe** : sans trace par appel, une couche 3 ou 4 mal réglée ne se voit qu'à
l'incident.

**Pattern générique** : logger au minimum identité, nom du tool, succès/échec, et le
motif d'échec si rejeté (authz, rate-limit...). Le logging enveloppe TOUTES les
couches précédentes (il doit voir un rejet de cloisonnement ou de rate-limit comme un
échec de tool, pas comme un cas à part).

## 6. Isolation — mode sandbox

**Principe** : les tools à effet de bord réel (envoi d'email, paiement, suppression)
ont besoin d'un mode d'exécution qui ne déclenche pas l'effet, pour tester le reste de
la chaîne (identité → cloisonnement → rate-limit → logging) sans conséquence externe.

**Pattern générique** : un flag de contexte (config serveur ou par requête selon le
niveau de confiance voulu) qui fait courir le tool jusqu'à l'effet de bord puis
retourne un résultat simulé cohérent, sans jamais appeler le service externe réel.

## 7. Exposition — bearer sur le manifeste/discovery

**Principe** : le manifeste qui décrit les tools disponibles à un agent est lui-même
une fuite d'information (noms de tools, schémas, parfois structure interne) s'il est
public.

**Pattern générique** : exiger le même bearer que les appels de tool pour accéder au
manifeste/à la découverte — un appelant anonyme ne doit rien apprendre de la surface
disponible avant de prouver une identité.
