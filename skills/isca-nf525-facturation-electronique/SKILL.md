---
name: isca-nf525-facturation-electronique
description: >-
  Expert français en conformité fiscale des logiciels de caisse et de
  facturation. Couvre la loi anti-fraude TVA / conditions ISCA (Inaltérabilité,
  Sécurisation, Conservation, Archivage — art. 286-I-3°bis du CGI), la
  certification NF525 / LNE / Infocert, et la réforme de la facturation
  électronique 2026-2027 (PDP, PPF/annuaire, e-invoicing, e-reporting,
  Factur-X, UBL, CII, profils EN16931). À utiliser pour AUDITER la conformité
  d'un logiciel (caisse, facturation, ERP), IMPLÉMENTER du code conforme
  (chaînage inaltérable, signatures, clôtures, exports FEC, génération
  Factur-X, intégration PDP) ou répondre à une QUESTION réglementaire
  (calendrier, obligations, formats, mentions obligatoires). Déclencher dès
  qu'apparaissent : ISCA, NF525, LNE, loi anti-fraude TVA, logiciel de caisse,
  chaînage inaltérable, JET, FEC, facture électronique, e-reporting, PDP, PPF,
  Factur-X, ZUGFeRD, Chorus Pro, EN16931, Factur-X CII/UBL.
---

# Conformité ISCA · NF525 · Facturation électronique (France)

## Avertissement — domaine réglementaire mouvant (lire en premier)

Ce domaine **change vite** et a déjà subi plusieurs revirements. Toute date,
obligation ou architecture citée ici porte une **source datée**. Avant de
livrer un conseil engageant ou du code de production, **vérifier la source
officielle au moment de l'usage** (impots.gouv.fr, BOFiP, economie.gouv.fr,
service-public.fr). Ne JAMAIS présenter une règle réglementaire sans sa date
d'effet et son fondement légal.

**Revirement majeur à connaître** : la **loi de finances 2025** (art. 43,
loi n° 2025-127 du 14/02/2025) avait **supprimé** l'auto-attestation éditeur
pour les logiciels de caisse. La **loi de finances 2026** (art. 125, loi
n° 2026-103 du 19/02/2026) l'a **RÉTABLIE**. Au moment de l'écriture
(juin 2026), les **deux** modes de preuve coexistent à nouveau : certificat
d'organisme accrédité (LNE / Infocert, ex. NF525) **OU** attestation
individuelle de l'éditeur. Détail : [references/isca.md](references/isca.md).

## Les trois piliers (à ne pas confondre)

| Sujet | Ce que c'est | Qui est concerné | Référence |
|-------|--------------|------------------|-----------|
| **ISCA** | Obligation légale (CGI) que tout logiciel **enregistrant les règlements clients** soit Inaltérable, Sécurisé, Conservé, Archivé | Assujettis TVA avec logiciel de caisse/encaissement | [isca.md](references/isca.md) |
| **NF525** | **Une** certification (parmi d'autres : LNE) prouvant le respect d'ISCA. C'est un moyen de preuve, pas l'obligation elle-même | Éditeurs de logiciels de caisse | [nf525.md](references/nf525.md) |
| **Réforme e-invoicing** | Obligation **distincte** : facturation électronique B2B + e-reporting via PDP, 2026-2027 | Tous les assujettis TVA établis en France | [reforme-2026.md](references/reforme-2026.md) |

**Piège conceptuel n°1** : ISCA/NF525 (anti-fraude à l'encaissement, depuis
2018) et la réforme e-invoicing (depuis 2026) sont **deux réglementations
indépendantes**. Un logiciel peut être concerné par l'une, l'autre, ou les deux.
Ne pas mélanger « chaînage inaltérable NF525 » et « format Factur-X ».

**Piège conceptuel n°2** : NF525 ≠ ISCA. ISCA est l'obligation (la loi).
NF525 est un certificat qui l'atteste. D'autres certificats existent (LNE).

## Arbre de décision — quel chemin suivre

```
Demande utilisateur
│
├─ « Est-ce conforme ? » / audit / revue de code / "vérifie que..."
│     → MODE AUDIT : charger references/audit-checklists.md
│       + la référence du domaine (isca / nf525 / formats)
│       + utiliser scripts/verify_chain.py pour rejouer un chaînage
│
├─ « Implémente / génère / ajoute... » (chaînage, signature, clôture,
│   export FEC, Factur-X, intégration PDP)
│     → MODE IMPLÉMENTATION : charger la référence du domaine concerné.
│       Choisir la stack d'après le contexte projet (Laravel/PHP, Node/TS,
│       agnostique). Respecter les invariants de chaque référence.
│
└─ « Quand / dois-je / quelles obligations / quel format... »
      → MODE CONSEIL : charger reforme-2026.md (calendrier/obligations)
        ou isca.md/nf525.md (logiciel de caisse). Toujours dater + sourcer.
```

## Fiches de référence (charger à la demande)

- **[references/isca.md](references/isca.md)** — Loi anti-fraude TVA, art.
  286-I-3°bis CGI. Les 4 conditions ISCA en détail, mécanismes techniques
  (chaînage de hachage, signature, journal, clôtures, données de référence),
  modes de preuve (certificat vs attestation, état 2025/2026), sanctions,
  contrôle inopiné. **Pilier 1.**
- **[references/nf525.md](references/nf525.md)** — La certification NF525
  (AFNOR/Infocert), périmètre, exigences fonctionnelles (JET, grand total
  perpétuel, clôtures Z, traçabilité), alternative LNE, ce qu'un auditeur
  vérifie concrètement. **Pilier 2.**
- **[references/reforme-2026.md](references/reforme-2026.md)** — Réforme
  facturation électronique : calendrier 2026-2027, architecture en Y, PDP vs
  PPF (annuaire/concentrateur), e-invoicing vs e-reporting, cycle de vie et
  statuts de facture, exemptions, mentions obligatoires nouvelles. **Pilier 3
  (volet réglementaire).**
- **[references/formats.md](references/formats.md)** — Formats structurés :
  Factur-X (CII embarqué dans PDF/A-3), UBL, CII, socle EN16931, profils
  Factur-X (MINIMUM → EXTENDED), mapping des champs clés, validation
  (Schematron EN16931), pièges PDF/A-3. **Pilier 3 (volet technique).**
- **[references/audit-checklists.md](references/audit-checklists.md)** —
  Checklists prêtes à l'emploi pour auditer un logiciel : ISCA, NF525,
  Factur-X, intégration PDP. Anti-patterns à détecter dans le code.

## Outils (dossier `scripts/`)

- **[scripts/verify_chain.py](scripts/verify_chain.py)** — *(stdlib, zéro
  dépendance)* Vérifie l'intégrité d'un **chaînage de hachage inaltérable**
  (mécanisme cœur de la condition « Inaltérabilité » d'ISCA). Prend un fichier
  JSON de lignes/écritures, recalcule la chaîne (`signature_n = H(données_n +
  signature_{n-1})`) et signale toute rupture (donnée altérée, écriture
  supprimée, chaîne réordonnée). Usage : `python3 scripts/verify_chain.py
  <fichier.json> [--algo sha256]`. Indispensable en audit pour prouver qu'une
  falsification serait détectable.
- **[scripts/validate_facturx.py](scripts/validate_facturx.py)** — *(deps :
  `scripts/requirements.txt`)* Audite une **facture électronique structurée**.
  Extrait le XML d'un PDF **Factur-X/ZUGFeRD**, détecte flavor + profil
  (minimum → extended), et lance **validation XSD + Schematron EN16931**
  (règles `BR-*`, via la lib `factur-x`/Saxon), plus contrôle des Business
  Terms obligatoires et mentions « réforme ». Accepte aussi un `.xml` brut
  (CII ; UBL en structurel). Usage : `python3 scripts/validate_facturx.py
  <facture.pdf|.xml>`. Parsing **durci anti-XXE**. Le script se ré-exécute
  automatiquement dans `./.venv` s'il existe.
  - **Installation** : `python3 -m venv .venv && .venv/bin/pip install -r
    scripts/requirements.txt` (PEP 668 / systèmes « externally managed »).
  - **Hors périmètre** : conformité **PDF/A-3** du conteneur → `veraPDF` ;
    CIUS françaises spécifiques → specs DGFiP/PDP.

## Règles de conduite (toujours)

1. **Dater et sourcer** chaque affirmation réglementaire.
2. **Distinguer** obligation (loi) et moyen de preuve (certificat).
3. **Ne pas mélanger** les trois piliers.
4. En audit : un constat = sa gravité (bloquant / majeur / mineur) + l'article
   ou l'exigence violée + la correction.
5. En implémentation : respecter les **invariants** (chaînage non rcompromis,
   pas de modification rétroactive, traçabilité des corrections par écriture
   de signe contraire — jamais par UPDATE/DELETE).
6. Si la règle a changé récemment ou est incertaine → **vérifier en ligne**
   avant de conclure, et le dire à l'utilisateur.
