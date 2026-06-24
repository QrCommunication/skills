# Skills

A small collection of self-contained agent **skills** — portable packages that
extend an AI coding agent (Claude Code and compatible runtimes) with
specialized knowledge, workflows, and tools.

Each skill lives under [`skills/`](skills/) and is independent: a `SKILL.md`
(loaded by the agent), optional `references/`, `scripts/`, and bundled
dependencies, plus a human-facing `README.md`.

## Skills in this collection

### 🧾 [`isca-nf525-facturation-electronique`](skills/isca-nf525-facturation-electronique/)

French tax-compliance expert for cash-register and invoicing software:

- **ISCA** — the anti-VAT-fraud obligation (art. 286-I-3°bis of the CGI):
  Inalterability, Security, Conservation, Archiving of payment data.
- **NF525 / LNE** — the certification that proves ISCA compliance.
- **E-invoicing reform 2026–2027** — PDP/PPF architecture, e-invoicing vs
  e-reporting, calendar, and the structured formats (Factur-X, UBL, CII,
  EN16931).

Works in three modes — **audit**, **implementation**, **advisory** — and ships
two tested tools:

| Tool | What it does |
|------|--------------|
| `scripts/verify_chain.py` | Replays an **inalterable hash chain** (core of ISCA) and flags any break. Stdlib only. |
| `scripts/validate_facturx.py` | Extracts the XML from a **Factur-X** PDF and runs **XSD + Schematron EN16931** validation (hardened against XXE). Needs `scripts/requirements.txt`. |

> Note: a domain-specific skill (content in French) — not legal or tax advice;
> the regulatory area changes fast, so verify rules at the official source.

### 🧭 [`orchestrate`](skills/orchestrate/)

A **generic, portable** orchestration router with a tiered complexity
architecture. It refines a request, **discovers and installs** the skills a task
needs, detects the right tier (0–3), and **delegates** execution to subagents —
it never executes code itself.

- **STEP 0** — refine the request (bundled `prompt-creator`).
- **STEP 0.5** — discover installed skills; search & install missing ones
  (bundled `find-skills` + `skill-installer`).
- **Tiers** — direct (0), template pipeline (1), planned master plan (2),
  custom human-validated workflow (3).

All of its dependencies are bundled **inside** the skill
([`orchestrate/skills/`](skills/orchestrate/skills/)) so it runs anywhere with
no external setup; optional helper agents live in
[`orchestrate/agents/`](skills/orchestrate/agents/).

### 🔌 [`super-pdp`](skills/super-pdp/)

Integration expert for the **SuperPDP API** (European electronic invoicing —
Factur-X, UBL, CII, EN16931, Peppol, PPF). Everything needed to implement,
integrate and debug the API directly in a project, in any language:

- **OAuth2** auth (not a Bearer API key), the **14 `/v1.beta/` endpoints**, the
  four formats and conversion, the **EN16931 `en_invoice`** model, business
  codes, and the implementation gotchas (`POST /invoices` is XML/multipart —
  never JSON; credit notes are `invoice_type_code: "381"`; payment is an
  `invoice_event` `fr:212`).
- Bundles the full **OpenAPI v1.10.0.beta** spec
  ([`references/superpdp-openapi.yaml`](skills/super-pdp/references/superpdp-openapi.yaml))
  as the source of truth.

Distilled from the `superpdp-expert` agent into portable skill form. Pairs with
the `isca-…` skill (which covers format conformance and the FR regulatory
context).

### 📄 [`document-format-conformance`](skills/document-format-conformance/)

Specification expert for **document formats** and their **conformance** — PDF
(ISO 32000), PDF/A (ISO 19005), Office OOXML (ECMA-376 / ISO 29500: .docx .xlsx
.pptx), OpenDocument (ISO 26300: .odt .ods .odp) and Factur-X / PDF-A3
(container). Two modes: **file** (inspect, validate, modify-in-place while
staying conformant) and **code** (audit a generator/engine against the spec).

Principle: **no home-grown parsers** — the scripts are thin wrappers over the
reference validators, and the skill **self-provisions** them:

| Tool | Role |
|------|------|
| `scripts/setup.sh` | Idempotent bootstrap: `.venv` + `qpdf`/`xmllint` (apt) + **veraPDF** (headless). |
| `inspect_doc.py` / `validate.py` | Structure dump + conformance report (qpdf, veraPDF, lxml/xmllint). |
| `pdf_modify.py` | Conformant PDF edits incl. **incremental update** (signature-safe, via pypdf). |
| `opc_modify.py` | Patch a part inside OOXML/ODF with valid repackage (ODF `mimetype` rule enforced). |
| `facturx_tool.py` | Factur-X PDF/A-3 container check/extract/embed (semantics → `isca-…`). |

Covers the **PDF/A-3 mechanics** of Factur-X; the **fiscal XML semantics**
(EN16931 Schematron, business terms) live in the `isca-…` skill — no overlap.

## Repository layout

```
skills/                                    # this repo
├── README.md                              # this file
└── skills/
    ├── isca-nf525-facturation-electronique/
    │   ├── SKILL.md  ├── README.md
    │   ├── references/   └── scripts/
    ├── super-pdp/
    │   ├── SKILL.md  ├── README.md
    │   └── references/   # OpenAPI spec + code tables
    ├── document-format-conformance/
    │   ├── SKILL.md  ├── README.md
    │   ├── references/   # pdf · ooxml · odf · facturx-pdfa3 · audit-methodology
    │   └── scripts/      # setup.sh + validators (self-provisioning .venv)
    └── orchestrate/
        ├── SKILL.md  ├── README.md
        ├── skills/    # bundled dependency skills
        └── agents/    # optional helper agents
```

## Using a skill

Place a skill folder under your agent's skills directory:

| Scope | Path |
|-------|------|
| Personal (all your projects) | `~/.claude/skills/<skill-name>/` |
| Project (this repo only) | `.claude/skills/<skill-name>/` |

The agent loads each skill's `SKILL.md` automatically based on its
`description`, then pulls in `references/` and `scripts/` on demand. For
`isca-…/scripts/validate_facturx.py`, install its Python dependencies first:

```bash
cd skills/isca-nf525-facturation-electronique
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

## Conventions

- One responsibility per skill; `SKILL.md` stays lean (navigation + core), with
  detail pushed into `references/`.
- Bundled scripts are dependency-light and tested before shipping.
- READMEs are for humans and are **not** required by the agent runtime.
