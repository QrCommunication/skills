# Skill — Document Format Conformance (PDF · OOXML · ODF · Factur-X)

> A Claude Code (AI agent) skill: a **specification expert** for document
> formats and their **conformance**. It inspects, validates, modifies "on the
> fly", and audits PDF (ISO 32000 / PDF/A), Office OOXML (ECMA-376 / ISO 29500:
> `.docx .xlsx .pptx`), OpenDocument (ISO 26300: `.odt .ods .odp`), and
> Factur-X / PDF-A3 files.

> ℹ️ This README is **human** documentation. It is not part of the operational
> content the agent loads (`SKILL.md` + `references/`).

---

## Core principle: no home-grown parsers

Every operation is a thin wrapper over a **reference validator**, so the
"conformant / not conformant" verdict carries the authority of the tool, not a
home-made heuristic:

| Domain | Validator |
|--------|-----------|
| PDF structure, repair, linearization | `qpdf`, `pikepdf` (libqpdf bindings) |
| PDF/A & PDF/UA conformance | **veraPDF** (the consortium's reference validator) |
| Incremental update (signature-safe) | `pypdf` |
| OOXML / ODF (well-formed, XSD, RelaxNG) | `lxml`, `xmllint` |
| Factur-X / ZUGFeRD (container) | `factur-x` (+ `saxonche`), `pikepdf`, `veraPDF` |

## Two modes

| Mode | Example request |
|------|-----------------|
| **File** | "validate this PDF/A-3", "is this `.docx` OPC-conformant?", "change the metadata without breaking the signature", "repair this PDF", "edit a part inside this `.odt` and keep it valid" |
| **Code** | "audit my custom PDF engine against ISO 32000", "does my `.xlsx` exporter emit conformant output?" → see [`references/audit-methodology.md`](references/audit-methodology.md) |

## What it checks, per format

| Format | Spec | Structural (always) | Semantic (strong) |
|--------|------|---------------------|-------------------|
| **PDF** | ISO 32000-2 | header, xref/trailer integrity, `startxref`, no damage/reconstruction | — |
| **PDF/A / PDF/UA** | ISO 19005 / 14289 | (above) | veraPDF profile `1b/2b/3b/3u/ua1/ua2` |
| **OOXML** | ECMA-376 / ISO 29500 | ZIP/OPC, `[Content_Types].xml`, `_rels` targets resolve, parts well-formed | XSD via `--xsd <dir>` (`xmllint`) |
| **ODF** | ISO 26300 | `mimetype` 1st-entry/STORED/value, `manifest.xml`, `content.xml` | RelaxNG via `--rng <schema>` |
| **Factur-X** | ISO 19005-3 + Factur-X 1.0.07 | PDF/A-3b (veraPDF), embedded `factur-x.xml`, `/AFRelationship`, document-level `/AF`, Factur-X XMP | fast XSD; full EN16931 → `isca-…` skill |

## Installation — the skill self-provisions

The skill installs its own dependencies. One idempotent command:

```bash
bash scripts/setup.sh        # .venv + qpdf/xmllint (apt) + veraPDF (headless, ~/.local)
python3 scripts/doctor.py    # diagnostic: what is present / missing
```

`setup.sh` is safe to re-run: each step detects what is already installed and
skips it. The Python scripts auto-detect `./.venv` and **re-exec** into it, so
running `python3 scripts/<x>.py …` is all you need. If a validator is missing, a
script reports it and points back to `setup.sh` — never a silent failure.

> Add `~/.local/bin` to your `PATH` if `verapdf` is not found.

Manual equivalent (no `setup.sh`):

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
sudo apt-get install -y qpdf libxml2-utils          # qpdf + xmllint
# veraPDF: https://verapdf.org/software/ (Java required; setup.sh automates this)
```

## Scripts

| Script | Role | Underlying tools |
|--------|------|------------------|
| `inspect_doc.py <f>` | Read-only structural dump (JSON) | pikepdf, zipfile, lxml |
| `validate.py <f> [--pdfa P] [--xsd DIR] [--rng FILE]` | Conformance report (JSON; exit 0/1/2) | qpdf, veraPDF, lxml, xmllint |
| `pdf_modify.py <set-meta\|attach\|repair\|decrypt>` | Conformant PDF edits | pikepdf, pypdf (incremental), qpdf |
| `opc_modify.py <list\|get\|set>` | Read/patch a part inside OOXML/ODF | zipfile, lxml + revalidation |
| `facturx_tool.py <check\|extract\|embed>` | Factur-X PDF/A-3 container | factur-x, pikepdf, veraPDF |
| `doctor.py` | Validator diagnostic | — |
| `setup.sh` | Idempotent bootstrap | venv, apt, veraPDF |

### Examples

```bash
# Inspect then validate
python3 scripts/inspect_doc.py invoice.pdf
python3 scripts/validate.py    invoice.pdf --pdfa 3b
python3 scripts/validate.py    report.docx
python3 scripts/validate.py    sheet.odt   --rng OpenDocument-v1.3-schema.rng

# Modify a PDF while staying conformant
python3 scripts/pdf_modify.py set-meta in.pdf out.pdf --title "Q3 Report" --incremental   # signature-safe
python3 scripts/pdf_modify.py attach  in.pdf out.pdf data.xml --relationship Data
python3 scripts/pdf_modify.py repair  damaged.pdf fixed.pdf

# Patch a part inside an OOXML/ODF container (repackage stays valid)
python3 scripts/opc_modify.py get rapport.docx word/document.xml > document.xml
#   …edit document.xml…
python3 scripts/opc_modify.py set rapport.docx word/document.xml document.xml --out out.docx

# Factur-X container
python3 scripts/facturx_tool.py check   invoice.pdf
python3 scripts/facturx_tool.py extract invoice.pdf --out invoice.xml
python3 scripts/facturx_tool.py embed   base.pdf factur-x.xml --out invoice.pdf --level en16931
```

## The conformance gate (non-negotiable)

Any modification is rejected or flagged non-conformant if it would break the
spec:

- `opc_modify set` **refuses** an XML part that is not well-formed (no file is
  produced).
- `pdf_modify` and `facturx embed` **re-run** qpdf / veraPDF on the output and
  report the verdict.

Never ship a file whose post-validation isn't green.

### Format gotchas baked into the tools

- **PDF** — the safe way to change a PDF is an **incremental update** (append a
  revision, original bytes untouched → existing signatures stay valid):
  `pdf_modify set-meta --incremental`. A file that qpdf had to *reconstruct*
  (rebuilt xref) is reported **not byte-clean** — distinct from a benign `/Size`
  warning.
- **OOXML** — three OPC invariants: `[Content_Types].xml` declares every part,
  every `*.rels` target resolves, all XML parts are well-formed.
- **ODF** — `mimetype` must be the **first ZIP entry, STORED (uncompressed)**,
  with the exact value; `opc_modify` re-guarantees this on every repackage.
- **Factur-X** — PDF/A-3b + embedded `factur-x.xml` + `/AFRelationship` +
  document-level `/AF` + Factur-X XMP.

## Scope & complementarity

This skill owns the **PDF/A-3 container mechanics** of Factur-X. The **fiscal XML
semantics** (EN16931 Schematron, business terms, French 2026 reform, CII vs UBL)
live in the **`isca-nf525-facturation-electronique`** skill — no duplication,
cross-linked both ways.

## Layout

```
SKILL.md                     router + workflow + setup (loaded by the agent)
references/
  pdf.md                     ISO 32000 / PDF/A: structure, xref, incremental, veraPDF
  ooxml.md                   ECMA-376 / OPC: content-types, relationships, XSD
  odf.md                     ISO 26300: mimetype STORED, manifest, RelaxNG
  facturx-pdfa3.md           PDF/A-3 hybrid: AF / AFRelationship / XMP (semantics → isca)
  audit-methodology.md       code mode: audit a generator against the spec
scripts/
  setup.sh  doctor.py  _common.py
  inspect_doc.py  validate.py  pdf_modify.py  opc_modify.py  facturx_tool.py
  requirements.txt
```

## Dependencies

- **Python (`.venv`)**: pikepdf, pypdf, factur-x (+ lxml, saxonche), python-docx,
  python-pptx, openpyxl, lxml — see [`scripts/requirements.txt`](scripts/requirements.txt).
- **CLI**: `qpdf`, `xmllint` (apt: `qpdf`, `libxml2-utils`), **veraPDF** (Java).
- Optional: `soffice`/`libreoffice` for conversion and round-trip fixtures.

The `.venv` is **not** committed or packaged — it is regenerated from
`requirements.txt` by `setup.sh` at the install location.

## Disclaimer

A technical audit/validation aid. A validator's "PASS" is scoped to the tested
profile — always confirm the **target** profile matches the requirement (PDF/A
level, OOXML Strict vs Transitional, ODF version, EN16931 profile) before relying
on the result.
