# SuperPDP — référence détaillée (endpoints & codes)

> Complément du `SKILL.md`. La **source de vérité** reste
> `superpdp-openapi.yaml` (grep ciblé). Ce fichier condense les paramètres
> d'usage courant et les tables de codes métier.

## Table des matières
1. Paramètres des endpoints
2. invoice_events — status codes
3. invoice_type_code
4. vat_category_code
5. payment_means_code
6. unit_code (UN/ECE Rec 20)

---

## 1. Paramètres des endpoints

### `GET /v1.beta/invoices` — lister
| Param | Valeurs | Notes |
|-------|---------|-------|
| `direction` | `in` (reçues) · `out` (émises) | |
| `date` | `YYYY` · `YYYY-MM` · `YYYY-MM-DD` | filtre période |
| `order` | `asc` (défaut) · `desc` | |
| `starting_after_id` / `ending_before_id` | id | pagination **par curseur** |
| `limit` | 1..1000 (défaut 100) | |
| `expand[]` | `en_invoice`, `en_invoice.lines`, `events`, … | hydrate la réponse |

### `POST /v1.beta/invoices` — créer
- `Content-Type: application/xml` → corps = XML CII/UBL brut.
- `Content-Type: multipart/form-data` → champ `pdf` (Factur-X) + `invoice`.
- **Jamais de JSON** sur cet endpoint.

### `POST /v1.beta/invoices/convert` — convertir (public)
- Query : `?from=<fmt>&to=<fmt>` avec `cii` · `ubl` · `en16931` · `factur-x`.
- Génération Factur-X : multipart `pdf` + `invoice` (JSON ou XML).

### `GET /v1.beta/invoices/{id}/download`
- Renvoie le fichier brut (PDF ou XML selon le format stocké).

### `GET /v1.beta/invoice_events`
- Params : `invoice_id`, `starting_after_id`, `limit` (max 1000).
- Réponse : `{ data: [...], has_after: bool }`.

### `POST /v1.beta/invoice_events`
```json
{ "invoice_id": 123, "status_code": "fr:212",
  "details": [ /* ... */ ], "attachments": [ /* ... */ ] }
```

### `POST /v1.beta/validation_reports` (public)
- Multipart : valide une ou des factures, renvoie un rapport de conformité.

### `directory_entries` (annuaire Peppol/PPF)
- `GET` liste · `POST` crée · `GET /{id}` détail · `DELETE /{id}` supprime.

---

## 2. invoice_events — status codes créables

| Code | Sens |
|------|------|
| `fr:204` … `fr:211` | Statuts métier français du cycle de vie (dépôt, mise à disposition, approbation, refus, litige, etc. — voir l'OpenAPI pour le libellé exact de chaque code) |
| `fr:212` | **Paiement** (avec `details` de montant optionnel) — remplace tout endpoint « mark-paid » |

> Il n'existe pas d'endpoint « cancel » ni « mark-paid » : tout passe par la
> création d'un `invoice_event` au bon `status_code`.

---

## 3. invoice_type_code

| Code | Description |
|------|-------------|
| 380 | Facture commerciale |
| 381 | Avoir (note de crédit) |
| 384 | Facture rectificative |
| 389 | Auto-facturation |

> Un **avoir** n'est pas une ressource séparée : c'est une facture
> `invoice_type_code: "381"`.

---

## 4. vat_category_code

| Code | Description |
|------|-------------|
| S | Taux standard |
| Z | Taux zéro |
| E | Exonéré |
| AE | Autoliquidation |
| K | Intracommunautaire |
| G | Export hors UE |
| O | Non assujetti |
| L | IGIC (Canaries) |
| M | IPSI (Ceuta/Melilla) |

---

## 5. payment_means_code

| Code | Description |
|------|-------------|
| 10 | Espèces |
| 20 | Chèque |
| 30 | Virement |
| 31 | Virement interbancaire |
| 42 | Paiement sur compte |
| 48 | Carte de crédit |
| 49 | Prélèvement |
| 58 | Carte SEPA |

---

## 6. unit_code (UN/ECE Rec 20)

| Code | Description |
|------|-------------|
| C62 | Unité (pièce) |
| HUR | Heure |
| DAY | Jour |
| MON | Mois |
| KGM | Kilogramme |
| MTR | Mètre |
| LTR | Litre |

> Liste complète des unités, devises et enums : grepper
> `superpdp-openapi.yaml`.
