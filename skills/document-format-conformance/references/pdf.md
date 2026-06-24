# PDF — ISO 32000 (+ PDF/A ISO 19005, PDF/UA)

Référence structurelle pour valider/modifier des PDF de façon conforme.

## Sommaire
- Structure physique d'un fichier
- Objets, xref, trailer
- Incremental update (modification spec-fidèle)
- Linéarisation
- PDF/A (ISO 19005) & PDF/UA
- Validations & écarts fréquents
- Commandes du skill

## Structure physique (ISO 32000-2 §7.5)

Un PDF est composé de 4 sections, dans cet ordre :

1. **Header** : `%PDF-1.x` (ou `%PDF-2.0`) sur la 1ère ligne. Une 2ᵉ ligne de
   commentaire binaire (`%âãÏÓ`) signale un contenu binaire aux outils.
2. **Body** : suite d'**objets indirects** numérotés (`12 0 obj … endobj`).
3. **Cross-reference table (xref)** : index des offsets octet de chaque objet.
   Soit une table classique (`xref` + sous-sections), soit un **cross-reference
   stream** (`/Type /XRef`, PDF 1.5+, souvent dans un ObjStm).
4. **Trailer** : dictionnaire (`/Root`, `/Size`, `/Info`, `/ID`, `/Prev`…) suivi
   de `startxref <offset>` puis `%%EOF`. `startxref` donne l'offset de la xref.

Le parseur lit le fichier **de la fin vers le début** : `%%EOF` → `startxref` →
xref → trailer → `/Root` (catalogue) → arbre des pages.

## Objets (ISO 32000-2 §7.3)

8 types : Boolean, Numeric, String (`(...)` ou `<hex>`), Name (`/Name`), Array
(`[...]`), Dictionary (`<< >>`), Stream (`<<dict>> stream … endstream`), Null.
Les **streams** portent un `/Length` et un ou plusieurs `/Filter`
(`/FlateDecode`, `/DCTDecode`, `/ASCII85Decode`…). Les **object streams**
(`/Type /ObjStm`, 1.5+) compactent plusieurs objets non-stream dans un seul
stream compressé.

Catalogue (`/Root`) → `/Pages` (arbre de `/Type /Pages` et `/Page`). Chaque page :
`/MediaBox`, `/Contents` (stream(s)), `/Resources`, `/Rotate`, `/Annots`.

## Incremental update (ISO 32000-2 §7.5.6) — modification SANS casser

C'est LE mécanisme pour modifier un PDF en restant conforme **et** en préservant
les signatures : on **n'édite jamais les octets existants**. On **append** :

```
<octets d'origine inchangés>
<nouveaux objets / objets modifiés>
xref            ← nouvelle section (uniquement les objets changés)
trailer         ← avec /Prev = offset de la xref précédente
startxref <offset de la nouvelle xref>
%%EOF           ← un 2ᵉ %%EOF (chaque révision en ajoute un)
```

Compter les `%%EOF` = nombre de révisions. Une signature numérique couvre une
plage d'octets (`/ByteRange`) : tout réécrire (rewrite complet) **invalide** la
signature ; un incremental update la **préserve**.

→ `pdf_modify.py set-meta --incremental` fait exactement cela (via pypdf). Le
mode par défaut (pikepdf) fait une **réécriture propre** (xref reconstruit,
linéarisable) : à préférer quand il n'y a pas de signature à préserver.

## Linéarisation (ISO 32000-2 Annexe F)

PDF « Fast Web View » : structure réorganisée pour afficher la 1ère page avant
téléchargement complet. Marqueur `/Linearized` dans le 1er objet. `qpdf
--linearize` produit un PDF linéarisé. Non requis pour la conformité de base.

## PDF/A (ISO 19005) — archivage

Sous-ensemble contraint, **autosuffisant** (polices embarquées, pas de JS, pas de
chiffrement, couleurs gérées par OutputIntent/ICC, métadonnées XMP obligatoires).
Niveaux : **b** (basic, apparence visuelle), **u** (Unicode mapping), **a**
(accessible/tagged). Parties : PDF/A-1 (sur PDF 1.4), A-2 (PDF 1.7), **A-3** (=
A-2 + **fichiers embarqués autorisés** → base de Factur-X).

Validation = **veraPDF** (validateur de référence du consortium) :
```bash
verapdf -f 3b --format text fichier.pdf     # PASS/FAIL + violations
verapdf -f 2b fichier.pdf                    # PDF/A-2b
verapdf -f ua1 fichier.pdf                   # PDF/UA-1 (accessibilité)
```
→ `validate.py fichier.pdf --pdfa 3b` enveloppe veraPDF dans le rapport JSON.

## PDF/UA (ISO 14289) — accessibilité

PDF taggé (arbre de structure logique, `/MarkInfo`, `/StructTreeRoot`, langue,
ordre de lecture). Profils veraPDF `ua1` / `ua2`.

## Écarts fréquents (à détecter)

| Écart | Symptôme / détection |
|---|---|
| `startxref` faux / xref absente | qpdf : « can't find startxref », « reconstruct cross-reference » |
| `/Length` de stream incorrect | objets illisibles, qpdf warnings |
| Fichier « réparé » servi comme conforme | xref reconstruit = **non byte-clean** (≠ warning `/Size` bénin) |
| Police non embarquée | PDF/A FAIL (veraPDF), rendu non fiable |
| Chiffrement | interdit en PDF/A ; `inspect_doc.py` → `encrypted: true` |
| Signature cassée par rewrite | utiliser **incremental update**, pas un rewrite |

## Commandes du skill

```bash
python3 scripts/inspect_doc.py f.pdf                       # version, pages, xref/EOF, AcroForm, embedded
python3 scripts/validate.py    f.pdf                       # qpdf + pikepdf (intégrité)
python3 scripts/validate.py    f.pdf --pdfa 3b             # + veraPDF PDF/A-3b
python3 scripts/pdf_modify.py  set-meta in.pdf out.pdf --title T --incremental
python3 scripts/pdf_modify.py  attach  in.pdf out.pdf data.xml --relationship Data
python3 scripts/pdf_modify.py  repair  bad.pdf fixed.pdf   # qpdf reconstruction
```

## Outils sous-jacents
- **qpdf** : intégrité structurelle (`--check`), réparation, linéarisation.
- **pikepdf** (libqpdf) : lecture/écriture objet, métadonnées XMP, pièces jointes.
- **pypdf** : incremental update (préservation signatures).
- **veraPDF** : conformité PDF/A et PDF/UA (autorité).
