# Architecture (prototype v0.1)

## Principe

Une seule page web statique, sans serveur ni compilation. Le navigateur lit les données publiques directement, ou utilise un jeu d'exemple embarqué si l'API ne répond pas.

```
┌──────────────────────── Navigateur ────────────────────────┐
│                                                            │
│  Interface (HTML + CSS)                                    │
│   ├─ Bandeau de neutralité + recherche + filtres           │
│   ├─ Liste de résultats ──► Fiche formation                │
│   │                           ├─ Admission (Parcoursup)    │
│   │                           ├─ Insertion (InserSup /     │
│   │                           │   InserJeunes)             │
│   │                           └─ Métiers (ONISEP / ROME)   │
│   └─ Barre comparateur ──► Tableau de comparaison (≤ 3)    │
│                                                            │
│  Logique (JS sans dépendance)                              │
│   ├─ SOURCES : registre nom / producteur / millésime /     │
│   │            date / licence (affiché sous chaque bloc)   │
│   ├─ Adaptateur « exemple » : SAMPLE (13 formations)       │
│   ├─ Adaptateur « direct »  : API Opendatasoft v2.1 ───────┼──► data.enseignementsup-recherche.gouv.fr
│   │     mapLive() normalise un enregistrement Parcoursup   │     /api/explore/v2.1/catalog/datasets/
│   │     loadInsertion() ajoute la ligne InserSup nationale │     fr-esr-parcoursup et fr-esr-insersup
│   │     du même diplôme (à l'ouverture de la fiche)        │
│   └─ Rendu : renderResults / renderSheet / renderCompare   │
└────────────────────────────────────────────────────────────┘
```

## Modèle de données commun

Les deux adaptateurs produisent le même objet, et l'interface ne lit que celui-ci :

```js
{
  id, origine: "exemple" | "direct", type, intitule, etab, ville, statut, selective,
  ps:  { capa, voeux, acces, bac:{g,t,p}, mention:{tb,b,ab,s}, boursiers, femmes, academie },
  ins: { src, perimetre, promo, emploi:{6,12,18,30}, salaire, salaireRaison, stable, poursuite, note } | null,
  insRaison,          // explication affichée quand ins est null
  metiers: [{ c: "M1805", n: "Développeur…" }] | null
}
```

Une valeur absente vaut `null` : l'interface affiche alors « non disponible » avec la raison, jamais une case vide ni un zéro.

## Flux

1. Au chargement, la page affiche le jeu d'exemple : une fiche ouverte et deux formations dans le comparateur. L'écran est donc rempli dès l'arrivée.
2. En parallèle, `probeLive()` interroge le catalogue Parcoursup (délai max. 6 s). Si l'API répond, le bouton « Parcoursup en direct » s'active et la date de mise à jour (`metas.default.modified`) alimente les mentions de source.
3. En mode direct, une recherche appelle `records?where="<texte>" AND fili in (...)&limit=30`. Une erreur ou un délai dépassé affiche un message clair, puis on revient au jeu d'exemple.
4. À l'ouverture d'une fiche réelle, `loadInsertion()` interroge InserSup (ligne « National » du même type de diplôme et du même intitulé), met le résultat en cache et complète la fiche. Pendant le chargement, la fiche l'indique ; en cas d'échec, elle explique pourquoi.

## Choix techniques

| Choix | Raison |
|---|---|
| Page HTML autonome, JS natif, aucune bibliothèque | S'ouvre par double-clic, s'héberge sur n'importe quel serveur statique, rien à installer. Le périmètre MVP ne justifie pas de framework. |
| Appel direct à l'API Opendatasoft depuis le navigateur | Les API du portail MESR acceptent les requêtes d'autres sites (CORS) : pas de serveur à maintenir pour un prototype. |
| Adaptateurs + modèle commun | Brancher InserSup ou ONISEP revient à écrire un `mapXxx()` de plus, sans toucher au rendu. |
| Registre `SOURCES` unique | Garantit que chaque bloc chiffré affiche sa source, sa date et sa licence. |
| Graphiques en HTML/CSS | Légers, lisibles au lecteur d'écran (libellés textuels), cohérents en thème clair et sombre. |
| Aucun stockage (ni cookie, ni localStorage) | Respect du RGPD par conception : rien à déclarer, aucun bandeau de consentement. |

## Étape suivante : petite API intermédiaire

Pour croiser Parcoursup et InserSup en production, ajouter un service léger (par exemple Python/FastAPI ou fonction serverless) qui :

- télécharge les exports CSV chaque nuit, depuis la même API (`/exports/csv`) ;
- applique une table de passage formation Parcoursup ↔ diplôme/discipline InserSup (codes SISE, UAI de l'établissement) ;
- sert un JSON déjà joint au front, avec mise en cache.
