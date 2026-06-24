# Mode CODE — auditer un générateur de PDF/Office/ODF contre la spec

Méthodologie pour le 2ᵉ mode du skill : vérifier qu'une **codebase / un moteur**
qui *produit* (ou parse) ces formats respecte la spec — par opposition à valider
un fichier isolé.

S'applique à : un moteur PDF maison, un exporteur `.docx`/`.xlsx`, un générateur
Factur-X, un convertisseur HTML→PDF, etc.

## Principe : valider les SORTIES, pas (seulement) le code

On ne « lit » pas la spec dans le code à l'œil. On fait **produire des fichiers**
au générateur sur un panel d'entrées, puis on **valide ces fichiers** avec les
mêmes scripts que le mode FICHIER. Un écart de sortie = un écart d'implémentation
localisable.

## Procédure en 5 étapes

### 1. Inventaire des features de la spec ciblée
Lister ce que le générateur est censé couvrir, depuis la référence du format
([pdf.md](pdf.md) / [ooxml.md](ooxml.md) / [odf.md](odf.md) /
[facturx-pdfa3.md](facturx-pdfa3.md)). Exemple PDF : xref classique **et** xref
stream ? incremental update ? linéarisation ? polices embarquées ? PDF/A ?
chiffrement ? images (filtres) ? annotations ? formulaires ?

### 2. Matrice de couverture
Tableau *feature × statut* : `implémentée` / `partielle` / `absente` / `non
testée`. Repérer dans le code les points d'émission (écriture xref, génération
trailer, embed de police…) avec `grep`/lecture ciblée pour étayer chaque ligne.

### 3. Génération de fixtures
Faire produire par le générateur un fichier **par feature** (et des cas limites :
document vide, multi-pages, image bitmap, unicode/CJK, très grand, rotation,
caractères spéciaux). Conserver les entrées pour reproductibilité.

### 4. Validation des sorties (mêmes scripts)
```bash
for f in out/*.pdf;  do python3 scripts/validate.py "$f" --pdfa 3b; done
for f in out/*.docx out/*.odt; do python3 scripts/validate.py "$f"; done
python3 scripts/inspect_doc.py out/cas-limite.pdf      # corréler structure ⇄ feature
```
Chaque `conformant:false` + le `detail` du check pointent la feature défaillante.

### 5. Table d'écarts priorisée
Pour chaque non-conformité : feature, sévérité (bloquant rendu / interop /
archivage), preuve (sortie de check), localisation probable dans le code, fix
proposé. Prioriser : corruption structurelle > non-conformité PDF/A > warning bénin.

## Vecteurs de test recommandés par format

| Format | Cas qui cassent le plus souvent les générateurs |
|---|---|
| PDF | xref stream vs table ; `/Length` exact ; incremental sans corrompre `/Prev` ; police embarquée + ToUnicode ; images (filtres) ; PDF/A (OutputIntent, pas de transparence non gérée) |
| OOXML | content-type de **chaque** part ; relations cibles existantes ; Strict vs Transitional ; échappement XML ; ordre des éléments imposé par le XSD |
| ODF | `mimetype` 1ère entrée STORED ; manifest exhaustif ; namespaces déclarés ; RelaxNG du content |
| Factur-X | PDF/A-3b (police, pas de chiffrement) ; `/AF` + `/AFRelationship` ; XMP ⇄ profil XML ; nom `factur-x.xml` |

## Régression

Intégrer ces validations en CI : faire générer les fixtures par le build, lancer
`validate.py` sur chacune, **échouer le pipeline** si une sortie redevient non
conforme. C'est le filet anti-régression d'un moteur de documents.

## Anti-patterns d'audit

| Anti-pattern | Correction |
|---|---|
| Conclure « conforme » en ouvrant juste le fichier dans une visionneuse | Les visionneuses **réparent** silencieusement. Valider avec qpdf/veraPDF/xmllint |
| Auditer le code sans produire de sortie | Faire générer des fixtures et valider les artefacts réels |
| Tester un seul cas nominal | Couvrir les cas limites (vide, unicode, image, grand, rotation) |
| Traiter tous les warnings comme bloquants (ou aucun) | Distinguer corruption réelle vs warning bénin (cf. verdict qpdf) |
| Valider un PDF/A contre le mauvais niveau/partie | Choisir le profil veraPDF correspondant à la cible (1b/2b/3b/3u/ua1) |
