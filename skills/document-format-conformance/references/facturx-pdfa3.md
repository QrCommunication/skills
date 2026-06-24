# Factur-X / ZUGFeRD — conteneur PDF/A-3 (ISO 19005-3)

Référence pour la **conformité du conteneur** d'une facture hybride PDF+XML.

> **Périmètre & anti-duplication.** Ce skill couvre la **mécanique PDF/A-3** (le
> contenant). La **sémantique fiscale du XML** — XSD CII, Schematron EN16931,
> business terms (BT-*), réforme française 2026-2027, CII vs UBL, profils
> minimum→extended — est couverte par le skill
> **`isca-nf525-facturation-electronique`**. Pour auditer une facture de bout en
> bout : `facturx_tool.py check` (conteneur) **puis** le validateur d'`isca` (XML).

## Le principe : 1 fichier, 2 couches

Une facture Factur-X est **un PDF/A-3** qui :
- s'affiche/s'imprime comme une facture lisible (couche PDF) ;
- embarque le **même contenu en XML structuré** (couche données, profil EN16931).

PDF/A-3 (ISO 19005-3) = PDF/A-2 **+ autorisation de fichiers embarqués** de type
quelconque → c'est ce qui rend la facture hybride possible et archivable.

## Les 5 exigences de conformité du conteneur

| # | Exigence | Spec | Check `facturx_tool.py` |
|---|---|---|---|
| 1 | Le PDF est **PDF/A-3** (b/u/a) valide | ISO 19005-3 | `PDF/A-3b (veraPDF)` |
| 2 | XML embarqué nommé **`factur-x.xml`** (ZUGFeRD ≥2 : idem ; `zugferd-invoice.xml` legacy) | Factur-X 1.0.07 §6 | `XML de facture embarqué` + `nom normatif` |
| 3 | La pièce jointe porte un **`/AFRelationship`** (`Data` recommandé ; `Alternative`/`Source` tolérés) | ISO 32000-2 §7.11.3 | `/AFRelationship sur la pièce XML` |
| 4 | Le document référence ses fichiers associés via **`/AF`** (Associated Files) au niveau catalogue | ISO 32000-2 §14.13 | `/AF document-level` |
| 5 | **Métadonnées XMP Factur-X** (extension schema : `DocumentType=INVOICE`, `DocumentFileName`, `Version`, `ConformanceLevel=profil`) | Factur-X §7 | `métadonnées XMP Factur-X` |

`facturx_tool.py check` vérifie les 5 + lance un **XSD rapide** sur le XML pour
signaler une structure cassée ; il renvoie explicitement vers `isca` pour la
validation EN16931 complète.

## Profils (rappel — sémantique détaillée dans `isca`)

`MINIMUM` → `BASIC WL` → `BASIC` → `EN16931` (= « COMFORT ») → `EXTENDED`. Le
profil est porté par `GuidelineSpecifiedDocumentContextParameter/ID`
(`urn:factur-x.eu:1p0:<profil>`) et **doit** correspondre au `ConformanceLevel`
déclaré dans le XMP.

## Générer un Factur-X conforme

`facturx_tool.py embed` part d'un PDF (converti en PDF/A-3 par la lib factur-x),
embarque le XML avec le bon `/AFRelationship`, pose `/AF` + XMP, puis **revalide
en PDF/A-3b via veraPDF** :

```bash
python3 scripts/facturx_tool.py embed facture.pdf factur-x.xml \
        --out invoice.pdf --flavor factur-x --level en16931 --afrelationship data
# → "pdfa3b_verapdf": "PASS …"
```

Extraire / contrôler :
```bash
python3 scripts/facturx_tool.py extract invoice.pdf --out out.xml
python3 scripts/facturx_tool.py check   invoice.pdf      # rapport JSON des 5 exigences
```

## Écarts fréquents

| Écart | Détection |
|---|---|
| PDF normal (pas PDF/A-3) avec XML attaché | veraPDF FAIL 3b |
| XML attaché sans `/AFRelationship` | check #3 = False (Acrobat n'ouvre pas la facture comme telle) |
| Pas de `/AF` au catalogue | check #4 = False (fichier embarqué « invisible » comme associé) |
| XMP sans extension Factur-X / `ConformanceLevel` ≠ profil XML | check #5 = False / incohérence |
| Nom de pièce non normatif (`invoice.xml`) | check #2 « nom normatif » = False |
| Police non embarquée (couche PDF) | veraPDF FAIL (exigence PDF/A) |

## Outils sous-jacents
- **veraPDF** : conformité PDF/A-3.
- **factur-x** (lib Akretion) : extraction/génération XML + AF + XMP.
- **pikepdf** : inspection `/AF`, `/AFRelationship`, XMP.
- Sémantique EN16931 → **skill `isca-nf525-facturation-electronique`**.
