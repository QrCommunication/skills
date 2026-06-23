# Skill — Conformité ISCA · NF525 · Facturation électronique (France)

> Skill Claude Code (agent IA) couvrant la conformité fiscale française des
> logiciels de caisse et de facturation : **loi anti-fraude TVA / ISCA**,
> **certification NF525/LNE**, et la **réforme de la facturation électronique
> 2026-2027** (PDP, e-invoicing, e-reporting, Factur-X / EN16931).

> ℹ️ Ce README est une documentation **humaine**. Il n'est volontairement **pas
> inclus dans le package `.skill`** distribuable (le contenu opérationnel pour
> l'agent IA vit dans `SKILL.md` + `references/`). C'est conforme aux bonnes
> pratiques de création de skills (un skill ne contient que ce dont l'agent a
> besoin).

> ⚠️ **Avertissement** : outil d'aide technique et d'audit, **pas un conseil
> juridique ou fiscal**. Le domaine réglementaire est **mouvant** (plusieurs
> revirements récents) ; toute règle doit être reconfirmée à la source
> officielle (impots.gouv.fr, BOFiP, economie.gouv.fr) au moment de l'usage.

---

## À quoi ça sert

Le skill équipe l'agent pour **trois modes** :

| Mode | Exemple de demande |
|------|--------------------|
| **Audit** | « Ce module de caisse respecte-t-il ISCA ? », « valide ce Factur-X » |
| **Implémentation** | « Ajoute le chaînage inaltérable », « génère une facture Factur-X », « intègre une PDP » |
| **Conseil** | « Quel est le calendrier 2026-2027 ? », « différence e-invoicing / e-reporting ? », « quelles mentions obligatoires ? » |

Il couvre **trois piliers distincts** (à ne pas confondre) :

1. **ISCA** — l'obligation légale (art. 286-I-3°bis du CGI) : Inaltérabilité,
   Sécurisation, Conservation, Archivage des données d'encaissement.
2. **NF525** — *une* certification (parmi d'autres : LNE) qui *prouve* le
   respect d'ISCA. C'est un moyen de preuve, pas l'obligation.
3. **Réforme e-invoicing** — obligation *séparée* : facture électronique B2B +
   e-reporting via PDP, 2026-2027.

---

## Déclenchement

L'agent charge le skill automatiquement dès qu'apparaissent des termes comme :
`ISCA`, `NF525`, `LNE`, `loi anti-fraude TVA`, `logiciel de caisse`, `chaînage
inaltérable`, `JET`, `FEC`, `facture électronique`, `e-reporting`, `PDP`,
`PPF`, `Factur-X`, `ZUGFeRD`, `EN16931`, `Chorus Pro`, `CII`, `UBL`. Aucune
invocation manuelle nécessaire.

---

## Structure

```
isca-nf525-facturation-electronique/
├── SKILL.md                      # Index : 3 piliers, arbre de décision, faits datés
├── references/                   # Chargés à la demande par l'agent
│   ├── isca.md                   # ISCA : 4 conditions, chaînage, preuve, sanctions
│   ├── nf525.md                  # NF525 : certification, JET, perpétuels, audit
│   ├── reforme-2026.md           # Calendrier, PDP/PPF, e-invoicing vs e-reporting
│   ├── formats.md                # Factur-X/UBL/CII, EN16931, profils, validation
│   └── audit-checklists.md       # Checklists 🔴🟠🟡 + grille de restitution
├── scripts/
│   ├── verify_chain.py           # Vérifie un chaînage de hachage (ISCA) — stdlib
│   ├── validate_facturx.py       # Valide un Factur-X (XSD + Schematron EN16931)
│   └── requirements.txt          # Déps de validate_facturx.py
├── README.md                     # (ce fichier — hors package)
└── .venv/                        # (local, hors package)
```

---

## Outils

### `verify_chain.py` — chaînage inaltérable (ISCA)

Aucune dépendance (stdlib). Rejoue un chaînage de hachage
`signature_n = H(données_n || signature_{n-1})` et détecte toute rupture
(donnée altérée, écriture supprimée, réordonnancement).

```bash
python3 scripts/verify_chain.py registres.json
python3 scripts/verify_chain.py registres.json --algo sha256 --seed "" --data-fields montant,date,ticket
```
Sortie : `0` = chaîne intègre · `1` = rupture détectée · `2` = erreur d'entrée.

### `validate_facturx.py` — validation de facture structurée

Extrait le XML d'un PDF **Factur-X/ZUGFeRD**, détecte flavor + profil, lance
**XSD + Schematron EN16931** (lib `factur-x`/Saxon), vérifie les Business Terms
obligatoires et les mentions « réforme ». Accepte aussi un `.xml` brut (CII ;
UBL en structurel). Parsing **durci anti-XXE**.

Installation (PEP 668 → venv) :
```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

Usage (le script se ré-exécute automatiquement dans `./.venv`) :
```bash
python3 scripts/validate_facturx.py facture.pdf
python3 scripts/validate_facturx.py facture.xml
```
Sortie : `0` = valide · `1` = non conforme (XSD/Schematron/obligatoire) ·
`2` = erreur d'entrée / déps manquantes.

**Hors périmètre** (à vérifier séparément) :
- Conformité **PDF/A-3** du conteneur → `veraPDF`.
- CIUS françaises / spécifications de la **PDP** cible.
- Cohérence couche PDF lisible ⇄ couche XML.
- Validation Schematron **UBL** (Peppol/EN16931-UBL) → `mustangproject`.

> ⚠️ Le profil Factur-X **MINIMUM** a un Schematron **laxiste** (ne contrôle pas
> l'arithmétique des totaux). « Schematron OK en MINIMUM » ≠ montants justes.
> Pour une facture B2B réelle, viser un profil **≥ BASIC**.

---

## Point réglementaire à retenir (daté)

L'auto-attestation éditeur des logiciels de caisse a fait des allers-retours :
- **LF 2025** (art. 43, loi n° 2025-127 du 14/02/2025) : **supprime**
  l'auto-attestation.
- **LF 2026** (art. 125, loi n° 2026-103 du 19/02/2026) : la **RÉTABLIT**.

Au mid-2026, les deux modes de preuve coexistent (certificat accrédité
NF525/LNE **ou** attestation éditeur). **Toujours reconfirmer.** Détail dans
`references/isca.md`.

---

## Packaging

Le `.skill` distribuable est régénéré en excluant `.venv/`, `__pycache__/`,
`.gitignore`, `README.md` et `*.skill`. Outil officiel :
`bun <meta-skill-creator>/scripts/package-skill.ts <chemin-du-skill>` (nécessite
`zip`), ou équivalent zip excluant ces chemins.
