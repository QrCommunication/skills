---
name: document-format-conformance
description: >-
  Expert des spécifications de formats documentaires — PDF (ISO 32000), PDF/A
  (ISO 19005), OOXML/Office (ECMA-376 / ISO 29500 : .docx .xlsx .pptx), ODF/
  OpenOffice (ISO 26300 : .odt .ods .odp) et Factur-X/PDF-A3 (conteneur). Permet
  d'INSPECTER la structure réelle d'un fichier, de VALIDER sa conformité
  structurelle ET sémantique (qpdf, veraPDF, lxml/xmllint, factur-x), de MODIFIER
  un fichier « à la volée » en garantissant qu'il reste conforme (incremental
  update PDF signature-safe, patch de part OPC/ODF avec repackage valide), et
  d'AUDITER une codebase/un moteur qui produit ces formats contre la spec.
  À utiliser dès qu'apparaissent : conformité PDF, PDF/A, PDF/UA, ISO 32000,
  veraPDF, xref/trailer, incremental update, OOXML, ECMA-376, ISO 29500, OPC,
  [Content_Types].xml, docx/xlsx/pptx, ODF, ISO 26300, manifest.xml, mimetype,
  Factur-X, ZUGFeRD, PDF/A-3, AFRelationship, valider/réparer/modifier un PDF
  ou un document Office/OpenOffice, auditer un générateur de PDF/Office.
---

# Document Format Conformance · PDF · OOXML · ODF · Factur-X

## Overview

Boîte à outils experte pour les **spécifications** des formats documentaires et
leur **conformité**. Deux modes complémentaires :

- **Mode FICHIER** — inspecter, valider, réparer et modifier des fichiers réels
  (.pdf, .docx, .xlsx, .pptx, .odt, .ods, .odp, Factur-X) en garantissant qu'ils
  restent conformes à leur spec après modification.
- **Mode CODE** — auditer une bibliothèque / un moteur qui *produit* ces formats
  (couverture de la spec, écarts, vecteurs de test). Voir
  [references/audit-methodology.md](references/audit-methodology.md).

Principe directeur : **on n'implémente aucun parseur maison**. Les scripts sont de
fins wrappers autour des validateurs de référence (qpdf, veraPDF, lxml/xmllint,
factur-x/saxonche, pikepdf/pypdf). La conformité affichée est donc celle d'outils
faisant autorité, pas d'heuristiques.

## Setup (une seule fois)

Le skill **installe lui-même ses dépendances** (venv Python + CLI + veraPDF) :

```bash
bash scripts/setup.sh        # idempotent : relançable sans risque
python3 scripts/doctor.py    # diagnostic : que manque-t-il ?
```

`setup.sh` crée `./.venv` (pikepdf, pypdf, factur-x, python-docx, python-pptx,
openpyxl, lxml), installe `qpdf` + `xmllint` (apt) et **veraPDF** (headless dans
`~/.local`). Les scripts Python détectent `./.venv` et s'y **ré-exécutent** seuls —
les lancer avec `python3 scripts/<x>.py …` suffit. Si un validateur manque, le
script le signale et renvoie vers `setup.sh` (jamais d'échec silencieux).

> Ajouter `~/.local/bin` au `PATH` si `verapdf` n'est pas trouvé.

## Choix du format (router)

`detect_format()` reconnaît le format par magic bytes (`%PDF`, `PK` + mimetype/
parts). En général, **lancer directement le script** : il route seul.

| Si le fichier est… | Famille | Spec | Référence à lire |
|---|---|---|---|
| `.pdf` | `pdf` | ISO 32000-2 (+ ISO 19005 PDF/A) | [references/pdf.md](references/pdf.md) |
| `.docx` `.xlsx` `.pptx` | `ooxml` | ECMA-376 / ISO 29500 (OPC) | [references/ooxml.md](references/ooxml.md) |
| `.odt` `.ods` `.odp` | `odf` | ISO 26300 (ODF) | [references/odf.md](references/odf.md) |
| Factur-X / ZUGFeRD | `pdf` (PDF/A-3) | ISO 19005-3 + Factur-X | [references/facturx-pdfa3.md](references/facturx-pdfa3.md) |

## Workflow standard (mode FICHIER)

1. **Inspecter** la structure réelle avant tout :
   `python3 scripts/inspect_doc.py <fichier>`
2. **Valider** la conformité (rapport JSON, exit 0/1/2) :
   `python3 scripts/validate.py <fichier> [--pdfa 3b] [--xsd DIR] [--rng SCHEMA]`
3. **Modifier** en restant conforme, puis la modif est **revalidée** automatiquement :
   - PDF : `python3 scripts/pdf_modify.py <set-meta|attach|repair|decrypt> …`
   - OOXML/ODF : `python3 scripts/opc_modify.py <list|get|set> …`
   - Factur-X : `python3 scripts/facturx_tool.py <check|extract|embed> …`

**Gate de conformité (NON-NÉGOCIABLE)** : toute modification est rejetée ou
signalée non conforme si elle casse la spec — un `opc_modify set` refuse un XML
non well-formed (aucun fichier produit) ; un `pdf_modify`/`facturx embed` relance
qpdf/veraPDF sur la sortie. Ne jamais livrer un fichier dont la post-validation
n'est pas verte.

## Scripts (cheat-sheet)

| Script | Rôle | Outils sous-jacents |
|---|---|---|
| `inspect_doc.py <f>` | dump structurel JSON (lecture seule) | pikepdf, zipfile, lxml |
| `validate.py <f> [--pdfa] [--xsd] [--rng]` | rapport de conformité | qpdf, veraPDF, lxml, xmllint |
| `pdf_modify.py …` | set-meta / attach / repair / decrypt | pikepdf, pypdf (incremental), qpdf |
| `opc_modify.py …` | list / get / set d'une part OOXML/ODF | zipfile, lxml + revalidation |
| `facturx_tool.py …` | check / extract / embed Factur-X | factur-x, pikepdf, veraPDF |
| `doctor.py` | diagnostic des validateurs | — |
| `setup.sh` | bootstrap idempotent | venv, apt, veraPDF |

### Points de conformité clés (mémo)

- **PDF** : modifier sans casser = **incremental update** (`pdf_modify set-meta
  --incremental` : append d'une révision, octets d'origine préservés → signatures
  intactes). Un fichier « réparé » par qpdf (xref reconstruit) est signalé
  **non byte-clean** (≠ warning bénin `/Size`).
- **OOXML** : 3 invariants OPC = `[Content_Types].xml` déclare chaque part, les
  `*.rels` pointent vers des parts existantes, parts XML well-formed.
- **ODF** : `mimetype` doit être la **1ère entrée du ZIP, STORED (non compressée)**,
  valeur exacte — `opc_modify` le re-garantit à chaque repackage.
- **Factur-X** : PDF/A-3b (veraPDF) + XML embarqué nommé `factur-x.xml` +
  `/AFRelationship` + `/AF` document-level + XMP Factur-X. La **sémantique fiscale**
  du XML (Schematron EN16931, business terms, réforme FR 2026) relève du skill
  `isca-nf525-facturation-electronique` — ne pas la dupliquer ici.

## Mode CODE (audit d'un générateur)

Pour auditer une codebase qui produit ces formats (ex : un moteur PDF maison, un
exporteur docx), suivre [references/audit-methodology.md](references/audit-methodology.md) :
inventaire des features de la spec → matrice de couverture → génération de fixtures
→ validation des sorties avec les mêmes scripts → table d'écarts priorisée.

## Obtenir les schémas officiels (validation sémantique forte)

La validation XSD ECMA-376 et RelaxNG ODF nécessite les schémas officiels (non
redistribués ici). Procédure d'obtention + commandes `xmllint --schema/--relaxng`
dans [references/ooxml.md](references/ooxml.md) et [references/odf.md](references/odf.md).
