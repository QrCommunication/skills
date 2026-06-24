# OOXML / Office — ECMA-376 / ISO-IEC 29500 (.docx .xlsx .pptx)

Référence pour valider/modifier les formats Microsoft Office (OPC).

## Sommaire
- OPC : le conteneur (Part 2)
- Parts principales par type de document
- Relationships
- Conformité : invariants + XSD (Part 1)
- Obtenir les schémas XSD officiels
- Écarts fréquents
- Commandes du skill

## OPC — Open Packaging Conventions (ISO 29500-2)

Un `.docx`/`.xlsx`/`.pptx` est un **ZIP** (« package ») contenant des **parts**
(fichiers) et des **relationships**. Invariants obligatoires :

- **`[Content_Types].xml`** à la racine : déclare le type MIME de chaque part,
  par `Default` (extension) ou `Override` (PartName précis). Toute part doit avoir
  un content-type résoluble (ISO 29500-2 §10.1.2).
- **`_rels/.rels`** : relations de package (pointent vers la part racine du
  document, core/app properties…).
- Pour chaque part `dir/x.xml` ayant des relations : **`dir/_rels/x.xml.rels`**.

Les noms de parts sont des chemins ZIP en `/` (jamais `\`), sans `.` / `..`.

## Parts principales par type

| Type | Part racine | Content-type Override |
|---|---|---|
| Word (.docx) | `word/document.xml` | `…wordprocessingml.document.main+xml` |
| Excel (.xlsx) | `xl/workbook.xml` (+ `xl/worksheets/sheetN.xml`, `xl/sharedStrings.xml`, `xl/styles.xml`) | `…spreadsheetml.sheet.main+xml` |
| PowerPoint (.pptx) | `ppt/presentation.xml` (+ `ppt/slides/slideN.xml`) | `…presentationml.presentation.main+xml` |

Métadonnées communes : `docProps/core.xml` (Dublin Core), `docProps/app.xml`.

## Relationships (ISO 29500-2 §9.3)

Chaque `*.rels` contient des `<Relationship Id Type Target [TargetMode]>`. Les
cibles **internes** (TargetMode ≠ `External`) sont résolues **relativement au
dossier parent du dossier `_rels`** et **doivent exister** dans le package. Les
`Id` (`rId1`…) sont référencés dans le XML (`r:embed`, `r:id`).

## Conformité

### Structurelle (toujours, sans schéma)
1. ZIP valide, `[Content_Types].xml` présent + well-formed.
2. Chaque part XML déclarée et résoluble en content-type.
3. `_rels/.rels` présent ; toutes les relations internes résolues.
4. Toutes les parts `.xml`/`.rels` **well-formed**.

→ `validate.py` couvre ces 4 points (lxml).

### Sémantique forte (XSD ECMA-376 Part 1)
ISO 29500-1 fournit les schémas XSD (WordprocessingML, SpreadsheetML,
PresentationML, shared, OPC). « Transitional » vs « Strict » : valider contre le
jeu correspondant au document.

```bash
# 1. extraire la part
unzip -p fichier.docx word/document.xml > /tmp/document.xml
# 2. valider contre le XSD (xmllint résout imports/includes du dossier de schémas)
xmllint --noout --schema /chemin/ECMA-376/wml.xsd /tmp/document.xml
```

`validate.py --xsd <dir>` route vers cette procédure (voir le détail ci-dessus :
le multi-fichiers XSD se fait via `xmllint --schema`, lxml seul ne suit pas
toujours les imports relatifs).

### Obtenir les schémas XSD officiels
- ECMA-376 (gratuit) : page « Standards » d'ECMA International → archive
  « Office Open XML File Formats » → dossier des schémas XSD (Transitional +
  Strict).
- Alternative pratique : les XSD sont aussi distribués avec certains SDK
  (ex : DocumentFormat.OpenXml). Placer le dossier et pointer `--xsd` dessus.

## Écarts fréquents

| Écart | Détection |
|---|---|
| Part référencée par une relation mais absente | `validate.py` : « relations internes résolues » = False |
| Part non déclarée dans `[Content_Types].xml` | content-type non résoluble → Office « répare » / refuse |
| XML non well-formed (édition manuelle) | `validate.py` : « parts XML well-formed » = False |
| `\` dans un nom de part | non conforme OPC |
| Strict validé contre schéma Transitional (ou l'inverse) | XSD FAIL |

## Modifier une part en restant conforme

`opc_modify.py set` **refuse** un nouveau XML non well-formed (aucun fichier
produit), préserve l'ordre/compression des autres parts et **revalide** la sortie
via `validate.py`.

```bash
python3 scripts/opc_modify.py list f.docx
python3 scripts/opc_modify.py get  f.docx word/document.xml > document.xml
#   … éditer document.xml …
python3 scripts/opc_modify.py set  f.docx word/document.xml document.xml --out out.docx
```

Pour de la sémantique métier (texte, styles, cellules), `python-docx`,
`openpyxl`, `python-pptx` (dans `.venv`) sont préférables au patch XML brut.

## Outils sous-jacents
- **zipfile** (stdlib) : structure OPC.
- **lxml** : well-formedness + XSD.
- **xmllint** : XSD multi-fichiers (imports/includes).
- **python-docx / openpyxl / python-pptx** : sémantique par type de document.
