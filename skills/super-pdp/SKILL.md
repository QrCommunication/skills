---
name: super-pdp
description: >-
  Expert d'intégration de l'API SuperPDP pour la facturation électronique
  européenne (Factur-X, UBL, CII, EN16931, Peppol BIS 3.0, PPF). À utiliser pour
  IMPLÉMENTER, intégrer ou déboguer des appels à l'API SuperPDP directement dans
  un projet (n'importe quel langage) : authentification OAuth2, création/envoi
  de factures, conversion entre formats, validation, synchronisation des statuts
  via invoice_events, annuaire Peppol/PPF. Déclencher dès qu'apparaissent :
  SuperPDP, api.superpdp.tech, /v1.beta/, invoice_events, validation_reports,
  directory_entries, Factur-X, UBL, CII, EN16931, Peppol, facture électronique.
---

# SuperPDP — intégration de l'API de facturation électronique

API SuperPDP **v1.10.0.beta** · Base URL `https://api.superpdp.tech/` ·
Doc en ligne : https://www.superpdp.tech/openapi/

## Règle n°1 — la spec OpenAPI est la source de vérité

**Avant toute implémentation impliquant des structures de données** (schémas,
enums, champs requis, descriptions BT-*/BG-* de EN16931), consulter la spec
bundlée :

```
Read / Grep : references/superpdp-openapi.yaml   (4143 lignes — la vérité)
```

Elle contient TOUS les schémas, enums et champs. **Grep ciblé** plutôt que
lecture intégrale, p. ex. :
```
grep -n "en_invoice:"              references/superpdp-openapi.yaml   # schéma facture
grep -n "invoice_type_code"        references/superpdp-openapi.yaml   # enum types
grep -n "/v1.beta/invoices"        references/superpdp-openapi.yaml   # endpoint
grep -nA30 "EnInvoice:"            references/superpdp-openapi.yaml   # définition complète
```
Si la spec locale est absente dans un projet, fallback :
`WebFetch https://api.superpdp.tech/openapi.json`.

## Authentification — OAuth2 (PAS de Bearer API key)

```
POST https://api.superpdp.tech/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET
```
- **Client Credentials** : accès à ses propres données (équivalent API key).
- **Authorization Code** : accès aux données d'un autre utilisateur
  (`GET /oauth2/authorize` → `POST /oauth2/token` avec `authorization_code`).
- Le token (Bearer) obtenu sert ensuite sur tous les endpoints `/v1.beta/`.
- Config type (`.env`) : `SUPERPDP_API_URL=https://api.superpdp.tech`,
  `SUPERPDP_CLIENT_ID`, `SUPERPDP_CLIENT_SECRET`.

## Les 14 endpoints (TOUS sous `/v1.beta/`)

| Méthode | Endpoint | Rôle | Auth |
|---------|----------|------|------|
| `GET` | `/v1.beta/companies/me` | Infos entreprise courante | OAuth2 |
| `GET` | `/v1.beta/invoices` | Lister (filtres direction/date/expand) | OAuth2 |
| `POST` | `/v1.beta/invoices` | **Créer/envoyer** une facture | OAuth2 |
| `GET` | `/v1.beta/invoices/{id}` | Détail facture | OAuth2 |
| `GET` | `/v1.beta/invoices/{id}/download` | Télécharger PDF/XML brut | OAuth2 |
| `POST` | `/v1.beta/invoices/convert` | Convertir entre formats | Public |
| `GET` | `/v1.beta/invoices/generate_test_invoice` | Facture test (sandbox) | OAuth2 |
| `GET` | `/v1.beta/invoice_events` | Lister événements | OAuth2 |
| `POST` | `/v1.beta/invoice_events` | **Créer un événement/statut** | OAuth2 |
| `GET` | `/v1.beta/directory_entries` | Lister annuaire (Peppol/PPF) | OAuth2 |
| `POST` | `/v1.beta/directory_entries` | Créer entrée annuaire | OAuth2 |
| `GET` | `/v1.beta/directory_entries/{id}` | Détail entrée | OAuth2 |
| `DELETE` | `/v1.beta/directory_entries/{id}` | Supprimer entrée | OAuth2 |
| `POST` | `/v1.beta/validation_reports` | Valider des factures | **Public** |

Détail des paramètres (pagination curseur, `expand[]`, filtres) :
[references/api-reference.md](references/api-reference.md).

## Pièges d'implémentation (non négociables)

**`POST /v1.beta/invoices` n'accepte PAS de JSON.**
- `application/xml` → XML CII/UBL brut.
- `multipart/form-data` → PDF Factur-X (+ `invoice`).
- Envoyer du JSON sur cet endpoint = erreur.

**Les montants sont des STRINGS** (format décimal `"1000.00"`), jamais des
numbers, dans tout le modèle `en_invoice`.

**Ce qui N'EXISTE PAS** (ne jamais appeler) :
| Faux endpoint / concept | Réalité |
|--------------------------|---------|
| `/v1/documents/` | n'existe pas |
| `/v1/credit-notes` | un avoir = une facture `invoice_type_code: "381"` |
| `/v1/validate` | c'est `POST /v1.beta/validation_reports` |
| `/v1/invoices/` (sans `.beta`) | c'est `/v1.beta/invoices/` |
| endpoint « cancel » | n'existe pas |
| endpoint « mark-paid » | `POST /v1.beta/invoice_events` `status_code: "fr:212"` |

## Formats supportés

| Format | Clé | Description |
|--------|-----|-------------|
| Factur-X | `factur-x` | PDF/A-3 + XML CII (France) |
| UBL | `ubl` | XML OASIS UBL 2.1 |
| CII | `cii` | XML UN/CEFACT |
| EN16931 | `en16931` | JSON sémantique européen |

Conversion : `POST /v1.beta/invoices/convert?from=cii&to=ubl`. Pour générer un
Factur-X : multipart `pdf` + `invoice`.

## Structure d'une facture EN16931 (`en_invoice`)

Modèle JSON minimal (montants = strings ; voir l'OpenAPI pour tous les champs) :

```json
{
  "invoice_number": "INV-2026-001",
  "issue_date": "2026-03-03",
  "due_date": "2026-04-03",
  "invoice_type_code": "380",
  "document_currency_code": "EUR",
  "buyer_reference": "PO-12345",
  "seller": { "name": "Ma Societe SAS", "street_name": "123 Rue de Paris",
    "city_name": "Paris", "postal_zone": "75001", "country_code": "FR",
    "company_id": "SIRET:12345678901234", "vat_id": "FR12345678901" },
  "buyer": { "name": "Client SARL", "street_name": "456 Avenue des Champs",
    "city_name": "Lyon", "postal_zone": "69001", "country_code": "FR",
    "company_id": "SIRET:98765432109876", "vat_id": "FR98765432109" },
  "lines": [{ "id": "1",
    "invoiced_quantity": { "value": "10", "unit_code": "C62" },
    "line_extension_amount": "1000.00",
    "item": { "name": "Service de conseil" },
    "price": { "price_amount": "100.00" },
    "line_vat_information": { "vat_category_code": "S", "vat_rate": "20.00" } }],
  "document_totals": {
    "sum_of_invoice_line_net_amount": "1000.00",
    "invoice_total_amount_without_vat": "1000.00",
    "invoice_total_amount_with_vat": "1200.00",
    "amount_due_for_payment": "1200.00" },
  "vat_break_down": [{ "vat_category_taxable_amount": "1000.00",
    "vat_category_tax_amount": "200.00", "vat_category_code": "S",
    "vat_category_rate": "20.00" }],
  "payment_instructions": { "payment_means_code": "30",
    "credit_transfer": [{ "payment_account_identifier": "FR7630001007941234567890185" }] }
}
```

## Workflow d'intégration type

1. **Auth** : obtenir un token (`client_credentials`).
2. **Créer/envoyer** : `POST /v1.beta/invoices` (XML ou multipart PDF).
3. **Valider** (optionnel, public) : `POST /v1.beta/validation_reports`.
4. **Convertir** si besoin : `POST /v1.beta/invoices/convert?from=&to=`.
5. **Suivre le cycle de vie** : poller `GET /v1.beta/invoice_events?invoice_id=…`
   et publier les statuts métier via `POST /v1.beta/invoice_events`
   (`fr:204`…`fr:211`, paiement `fr:212`).
6. **Annuaire** : gérer la présence Peppol/PPF via `directory_entries`.

## Codes métier (résumé)

`invoice_type_code` : `380` facture · `381` avoir · `384` rectificative ·
`389` auto-facturation. `vat_category_code` : `S` standard · `Z` zéro ·
`E` exonéré · `AE` autoliquidation · `K` intracommunautaire · `G` export ·
`O` non assujetti. `payment_means_code` : `30` virement · `48` carte · `49`
prélèvement · `20` chèque · `10` espèces. `unit_code` : `C62` unité · `HUR`
heure · `DAY` jour · `KGM` kg…

Tables complètes + status codes `invoice_events` :
[references/api-reference.md](references/api-reference.md).

## Références

- **Contrat de vérité** : `references/superpdp-openapi.yaml` (à grepper).
- Doc en ligne : https://www.superpdp.tech/openapi/
- EN16931 : https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/EN+16931
- Factur-X (FNFE-MPE) : https://fnfe-mpe.org/factur-x/
- Peppol BIS 3.0 : https://docs.peppol.eu/poacc/billing/3.0/

> Conformité du **format** produit (Factur-X PDF/A-3, Schematron EN16931) et
> contexte réglementaire FR (ISCA, NF525, réforme PPF) → voir le skill voisin
> `isca-nf525-facturation-electronique`.
