# Réforme de la facturation électronique (France) — volet réglementaire

> Réglementation **distincte** d'ISCA/NF525. Sources : economie.gouv.fr,
> impots.gouv.fr, service-public.fr, BOFiP. **Domaine très mouvant** :
> reconfirmer le calendrier et l'architecture au moment de l'usage.

## Table des matières
1. Deux obligations : e-invoicing et e-reporting
2. Calendrier 2026-2027
3. Architecture en Y : PDP, PPF/annuaire, OD
4. Cycle de vie et statuts de facture
5. Champ d'application et exemptions
6. Mentions obligatoires nouvelles

---

## 1. Deux obligations distinctes

**E-invoicing (facturation électronique B2B domestique)**
Émettre et recevoir les factures **entre assujettis établis en France** sous
forme **électronique structurée** (Factur-X/UBL/CII — voir formats.md), via une
**PDP**. Une facture PDF « simple » par e-mail ne suffira plus.

**E-reporting (transmission de données)**
Transmettre à l'administration des **données de transaction et de paiement**
pour les opérations **hors champ e-invoicing** :
- ventes **B2C** (au consommateur),
- opérations avec des **assujettis étrangers** (export, intracommunautaire,
  import de prestations),
- données d'**encaissement** (statut de paiement) pour les opérations
  concernées.

> e-invoicing = le **flux de facture** entre entreprises FR.
> e-reporting = les **données** que l'État récupère sur ce qui échappe au
> flux e-invoicing (B2C, international) + le paiement.

---

## 2. Calendrier 2026-2027 (état mi-2026)

| Date | Obligation |
|------|------------|
| **1er sept. 2026** | **Toutes** les entreprises (toute taille) : capables de **RECEVOIR** les factures électroniques. **+ Grandes entreprises et ETI** : obligation d'**ÉMETTRE** en électronique **+ e-reporting**. |
| **1er sept. 2027** | **PME, TPE, micro-entreprises** : obligation d'**ÉMETTRE** en électronique **+ e-reporting**. |

Points clés :
- L'obligation de **réception** s'impose à **tout le monde dès sept. 2026** —
  même une micro-entreprise doit pouvoir recevoir une facture électronique via
  une PDP dès cette date.
- L'**annuaire central** a ouvert en **sept. 2025**, avec immatriculation
  automatique des assujettis TVA par la DGFiP.
- Catégories de taille = définitions de l'INSEE/réglementaires (GE / ETI /
  PME / micro). En cas de doute sur la catégorie d'une entreprise, le
  préciser.

---

## 3. Architecture en Y — qui fait quoi

**Revirement majeur (15 oct. 2024)** : le **PPF (Portail Public de
Facturation) n'est plus une plateforme gratuite d'émission/réception**. La
DGFiP l'a recentré sur deux rôles d'infrastructure. Tout le routage passe
désormais par des **PDP privées**.

| Acteur | Rôle |
|--------|------|
| **PDP** — Plateforme de Dématérialisation Partenaire | Plateforme **privée immatriculée** par la DGFiP. **Seule** habilitée à émettre/recevoir les factures électroniques et à transmettre e-invoicing + e-reporting. C'est l'intermédiaire **obligatoire**. Chaque entreprise choisit **sa** PDP. |
| **PPF** — Portail Public de Facturation | Désormais limité à : (1) **annuaire central** des assujettis TVA et de leurs adresses de facturation ; (2) **concentrateur de données** (CDD) transmettant les données fiscales à la DGFiP. **Ne route plus** les factures. |
| **OD** — Opérateur de Dématérialisation | Prestataire (ex. logiciel de facturation) **non immatriculé** qui s'interface avec une PDP. Peut produire/convertir les factures mais **doit passer par une PDP** pour l'émission/réception et l'e-reporting. |

Conséquences pratiques :
- Un éditeur de logiciel de facturation est typiquement un **OD** qui doit
  **se raccorder à une (ou plusieurs) PDP**, ou **devenir PDP** (procédure
  d'immatriculation lourde : sécurité, ISO 27001, exigences fiscales).
- L'adresse de routage d'un destinataire se résout via l'**annuaire** (PPF) :
  SIREN/SIRET + éventuel code routage → la PDP du destinataire.

---

## 4. Cycle de vie et statuts de facture

La facture électronique a un **cycle de vie** avec des **statuts** échangés via
les PDP (certains obligatoires, d'autres recommandés/libres). Statuts socle
typiques :
- **Déposée** / émise,
- **Reçue** par la plateforme du destinataire,
- **Mise à disposition** du destinataire,
- **Approuvée** / **Refusée** (rejet),
- **Encaissée** (paiement — alimente l'e-reporting de paiement),
- **Litige** / suspendue (selon implémentation).

L'implémentation doit **émettre et consommer ces statuts** via la PDP et les
journaliser. Le statut « encaissée » est important pour l'e-reporting de
paiement (notamment prestations de services soumises à la TVA sur les
encaissements).

---

## 5. Champ d'application et exemptions

**Dans le champ e-invoicing** : opérations **B2B domestiques** entre assujettis
établis en France donnant lieu à facture.

**Hors champ e-invoicing → e-reporting** : B2C, opérations avec l'étranger.

**Exonérations / hors obligation** (à reconfirmer) :
- opérations **exonérées de TVA** : santé, enseignement, opérations
  immobilières, assurance, opérations bancaires/financières, certaines
  associations à but non lucratif ;
- opérations **internationales / intracommunautaires** (relèvent de
  l'e-reporting, pas de l'e-invoicing) ;
- **B2C** (e-reporting des données, pas e-invoicing).

---

## 6. Mentions obligatoires nouvelles

En plus des mentions habituelles d'une facture, la réforme ajoute (à intégrer
dans le format structuré) :
- le **numéro SIREN** du client (pour les opérations domestiques B2B),
- l'**adresse de livraison** des biens si différente de la facturation,
- la **catégorie d'opération** : livraison de biens / prestation de services /
  mixte,
- l'option **« paiement de la TVA d'après les débits »** lorsqu'elle est
  exercée.

L'absence de ces mentions dans le flux structuré rend la facture **rejetable**
par la plateforme/le destinataire.

> Voir formats.md pour **où** placer ces mentions dans Factur-X/UBL/CII et
> comment valider le respect du socle EN16931.
