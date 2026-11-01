# Relevé d'orientation (prototype)

Taux d'accès, insertion professionnelle, salaires et métiers par formation, sur une seule fiche, avec un comparateur. Le prototype n'utilise que des données publiques. Chaque chiffre affiche sa source, sa date et sa licence. Aucune école ne paie pour apparaître.

> **Statut : prototype.** Les chiffres embarqués sont **fictifs** (marqués `EXEMPLE`). Ils reprennent la structure et les ordres de grandeur des jeux officiels. Seul le mode « Parcoursup en direct » affiche des données réelles.

## Installation

Aucune dépendance.

```bash
open index.html            # macOS (ou double-clic sur le fichier)
```

Ou avec un petit serveur local (recommandé pour l'appel à l'API) :

```bash
python3 -m http.server 8000
```

Puis ouvrir http://localhost:8000.

Le code source est dans `src/app.html`. `index.html` est généré par :

```bash
./build.sh
```

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Page autonome à ouvrir (générée) |
| `src/app.html` | Source : styles, contenu, jeu d'exemple, logique |
| `build.sh` | Ajoute l'en-tête HTML et produit `index.html` |
| `ARCHITECTURE.md` | Composants, flux de données, choix techniques |

## Fonctionnalités (MVP)

| # | Fonctionnalité | État |
|---|---|---|
| 1 | Recherche (intitulé, métier, établissement, ville) + filtre par type + tri | ✅ Exemple et direct |
| 2 | Taux d'accès, places, vœux, profil des admis (bac, mention, boursiers, filles, académie) | ✅ Exemple et direct |
| 3 | Insertion : emploi à 6/12/18/30 mois, salaire médian, emploi stable, poursuite d'études | ✅ Exemple · ⏳ direct (voir plus bas) |
| 4 | Comparateur de 2 ou 3 formations, sans désigner de « gagnant » | ✅ |
| 5 | Métiers associés (codes ROME) | ✅ Exemple · liste indicative en direct |

Données manquantes : chaque absence est expliquée (secret statistique, diplôme trop récent, formation qui ne mène pas directement à l'emploi comme le PASS ou la CPGE, salaire non publié par InserJeunes).

## Sources de données

⚠️ Mon environnement de développement n'avait pas accès à ces sites : le pare-feu a bloqué data.enseignementsup-recherche.gouv.fr, data.gouv.fr et opendata.onisep.fr. Les formats et licences ci-dessous viennent de la documentation publique connue. **Vérifiez-les sur chaque page de jeu de données avant la mise en production.**

| Source | Jeu / accès | Format | Licence | Limites |
|---|---|---|---|---|
| **Parcoursup** (MESR-SIES) | [`fr-esr-parcoursup`](https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/) via l'API Opendatasoft v2.1 | JSON (API), CSV/Parquet (exports) | Licence Ouverte 2.0 (Etalab) | Une ligne par formation × établissement et par session. 100 lignes max par appel `records` (pagination `offset`), exports complets via `/exports/csv`. Noms de champs susceptibles de changer d'une session à l'autre : l'adaptateur `mapLive()` essaie plusieurs noms et recalcule les pourcentages à partir des effectifs si besoin. |
| **InserSup** (MESR-SIES) | [`fr-esr-insersup`](https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-insersup/) | idem | Licence Ouverte 2.0 | Publié par diplôme, discipline et établissement, pas par formation Parcoursup. Indicateurs masqués quand l'effectif est trop faible. Salaires disponibles seulement pour certains diplômes : à compléter avec les enquêtes d'insertion master, licence pro et DUT/BUT du même portail. |
| **InserJeunes** (DEPP/Dares) | [inserjeunes.education.gouv.fr](https://www.inserjeunes.education.gouv.fr), jeux sur data.education.gouv.fr | CSV / API | Licence Ouverte 2.0 | Couvre la voie professionnelle et les BTS. Pas de salaire. |
| **ONISEP** | [opendata.onisep.fr](https://opendata.onisep.fr) | CSV / JSON / API | **À vérifier par jeu.** Selon les jeux, ONISEP a publié sous Licence Ouverte ou sous ODbL. L'ODbL impose le partage à l'identique des bases dérivées. | Liens formation ↔ métier ↔ code ROME. |

### Ce qui est branché

- **Parcoursup en direct** : au chargement, la page teste l'API. Si elle répond, le bouton « Parcoursup en direct » devient actif. Les recherches interrogent alors `records?where="<texte>"`, et la date de mise à jour du jeu s'affiche sous les chiffres. Dans le navigateur d'un utilisateur, ce mode devrait fonctionner tel quel. Je n'ai pas pu le tester depuis mon environnement : à vérifier en priorité, y compris les noms de champs.

### Comment brancher les autres sources

1. **InserSup** : écrire `mapInsersup()` sur le modèle de `mapLive()` et construire une table de passage entre la formation Parcoursup (code UAI de l'établissement + intitulé ou code de formation) et le couple diplôme/discipline InserSup (codes SISE). Ce croisement relève d'un traitement côté serveur, détaillé dans `ARCHITECTURE.md`.
2. **InserJeunes** : jointure par UAI + code formation diplôme (BTS).
3. **ONISEP** : remplacer `METIERS_PAR_MOT` par la table formation → métiers (codes ROME) du jeu ONISEP correspondant.
4. Retirer les badges `EXEMPLE` une fois chaque bloc branché : c'est automatique, car le badge dépend du champ `origine` des données.

## Exigences du cahier des charges

- **Neutralité visible dès le premier écran** : trois engagements (aucune école payante, chiffres sourcés et datés, aucune coordonnée demandée). Tri alphabétique par défaut. Le comparateur ne désigne aucune « meilleure » formation.
- **Source et date sous chaque bloc chiffré**, avec lien vers le jeu de données et sa licence. Une liste récapitulative figure en pied de page.
- **Accessibilité** : liens d'évitement, navigation clavier complète, focus visible, focus déplacé vers la fiche ouverte, annonces `aria-live`, graphiques avec texte équivalent, tableaux avec en-têtes, contrastes conformes au niveau AA, mouvements réduits respectés, police Atkinson Hyperlegible.
- **Mobile** : une seule colonne sous 860 px, sans défilement horizontal. Le comparateur défile dans son propre cadre.
- **RGPD** : aucun cookie, aucun stockage, aucune mesure d'audience, aucun formulaire. En mode direct, seul le texte recherché part vers l'API du ministère.

## Analyse rapide de l'existant

| Outil | Ce qu'il fait bien | Ce qui manque |
|---|---|---|
| Parcoursup | Données d'admission officielles | Peu d'insertion et de salaires, comparaison difficile |
| ONISEP | Catalogue formations et métiers complet et neutre | Peu de chiffres de résultats |
| InserJeunes | Insertion officielle voie pro et BTS par établissement | Ne couvre pas le supérieur général, ni admission ni salaires |
| Diplomeo | Interface simple, avis, beaucoup d'écoles privées | Financé en partie par les écoles (visibilité, mise en relation), chiffres peu sourcés |

**Ce qui distingue le prototype** : les trois questions (puis-je entrer ? trouverai-je un emploi ? pour quel salaire ?) sont réunies sur une fiche, chaque chiffre est relié à sa source publique, et l'outil n'a aucun lien commercial avec les établissements. Si le service devient payant pour les familles, ce modèle préserve sa neutralité : il ne dépend d'aucune école.

## Limites connues

- Chiffres d'exemple **fictifs**. Les établissements nommés sont inventés.
- Mode direct non testé depuis l'environnement de développement (réseau bloqué). Les noms de champs Parcoursup sont à confirmer.
- Pas d'insertion ni de salaire en mode direct tant que la table de passage Parcoursup ↔ InserSup n'existe pas.
- Les chiffres d'insertion portent parfois sur la filière au niveau national (anciens DUT pour les BUT) et non sur l'établissement. La fiche l'indique.
- Le PASS et les CPGE n'ont pas d'indicateur de résultat standard en open data (taux de passage en études de santé, taux d'intégration en école).
- Recherche simple par mots-clés, sans tolérance aux fautes de frappe.

## Prochaines étapes

1. Tester le mode direct dans un navigateur et confirmer les noms de champs Parcoursup.
2. Construire la table de passage Parcoursup ↔ InserSup et un petit service de jointure mis en cache chaque nuit.
3. Brancher InserJeunes (BTS) et la table formations → métiers d'ONISEP, en vérifiant sa licence.
4. Ajouter la recherche géographique (académie, distance) et la pagination.
5. Tester avec 5 lycéens et 5 parents le critère « valeur comprise en moins de 30 secondes ».
6. Faire un audit RGAA complet.

## Vérifier les sources réelles

Une fois l'accès réseau ouvert :

```bash
python3 scripts/verifier_sources.py
```

Le script enregistre dans `data/sources-verifiees.json` la licence, la date de mise à jour et la liste des champs de chaque jeu. Il signale aussi les champs attendus par `mapLive()` qui manqueraient.
