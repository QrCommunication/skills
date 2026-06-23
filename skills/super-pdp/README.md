# super-pdp — SuperPDP API integration skill

Everything an AI coding agent needs to **implement, integrate and debug the
SuperPDP API** for European electronic invoicing (Factur-X, UBL, CII, EN16931,
Peppol BIS 3.0, PPF) — directly inside a project, in any language.

This skill is the **portable, skill-form distillation** of the original
`superpdp-expert` Claude Code agent: the curated API knowledge plus the full
**OpenAPI specification** (the source of truth), with no standalone CLI/runtime
to install.

## What it covers

- **OAuth2** authentication (`client_credentials` and `authorization_code`) —
  SuperPDP uses OAuth2, **not** a Bearer API key.
- The **14 endpoints** under `/v1.beta/` (invoices, invoice_events,
  directory_entries, validation_reports, convert, companies).
- The four **formats** (`factur-x`, `ubl`, `cii`, `en16931`) and conversion.
- The **EN16931 `en_invoice`** JSON model (amounts are strings!).
- Business **codes** (invoice types, VAT categories, payment means, units) and
  lifecycle **status codes** for `invoice_events`.
- The **implementation gotchas** — what doesn't exist (`/v1/documents`,
  `/v1/credit-notes`, "cancel", "mark-paid"), why `POST /invoices` rejects JSON,
  and how credit notes / payments are actually modeled.

## Layout

```
super-pdp/
├── SKILL.md                        # implementation guide (auth, endpoints, model, gotchas)
├── README.md                       # this file
└── references/
    ├── superpdp-openapi.yaml       # full OpenAPI v1.10.0.beta spec — SOURCE OF TRUTH (4143 lines)
    └── api-reference.md            # endpoint params + all business-code tables
```

## How the agent uses it

The skill loads automatically when a task mentions SuperPDP, `api.superpdp.tech`,
`/v1.beta/`, `invoice_events`, Factur-X/UBL/CII/EN16931, etc. Its first rule:
**read the bundled OpenAPI spec** (`references/superpdp-openapi.yaml`) — by
targeted `grep`, not wholesale — before writing any data-structure code, since
it holds every schema, enum and required field.

```
GET  https://api.superpdp.tech/oauth2/token        # client_credentials → Bearer
POST https://api.superpdp.tech/v1.beta/invoices    # XML or multipart PDF (never JSON)
POST https://api.superpdp.tech/v1.beta/invoice_events   # lifecycle/payment status
POST https://api.superpdp.tech/v1.beta/validation_reports  # public validation
```

## Configuration (in your target project)

```
SUPERPDP_API_URL=https://api.superpdp.tech
SUPERPDP_CLIENT_ID=...
SUPERPDP_CLIENT_SECRET=...
```

## Scope & related

- **This skill** = how to **talk to the SuperPDP API** and produce conformant
  payloads.
- For French regulatory context and **format conformance** (ISCA, NF525,
  the 2026-2027 reform, Factur-X PDF/A-3 + Schematron EN16931 validation), see
  the sibling skill `isca-nf525-facturation-electronique`.

## Source

Distilled from the `superpdp-agent` package (agent `superpdp-expert`, API
v1.10.0.beta). Official docs: https://www.superpdp.tech/openapi/ · License: MIT.
