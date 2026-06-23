# Formats de facture électronique structurée

> Volet technique de la réforme. Les trois formats **socle** admis en France :
> **Factur-X**, **UBL**, **CII**. Tous reposent sur la norme sémantique
> européenne **EN16931**.

## Table des matières
1. EN16931 — le socle sémantique
2. Factur-X (PDF/A-3 + CII embarqué)
3. UBL et CII (XML pur)
4. Profils Factur-X (MINIMUM → EXTENDED)
5. Champs clés et mentions réforme — où les placer
6. Validation (Schematron EN16931) et pièges PDF/A-3
7. Anti-patterns techniques

---

## 1. EN16931 — le socle sémantique

**EN16931** est la norme européenne définissant le **modèle sémantique** d'une
facture (les *Business Terms*, codés `BT-x`, regroupés en *Business Groups*
`BG-x`) et un ensemble de **règles de gestion** (`BR-*`) + règles TVA
(`BR-CO-*`, `BR-AE-*`…). Deux **syntaxes** sont retenues pour la transposer :
**UBL 2.1** et **UN/CEFACT CII** (Cross Industry Invoice). Factur-X utilise CII.

Conséquence : quel que soit le format, une facture conforme doit satisfaire les
**règles EN16931** (un montant TVA cohérent, un total = somme des lignes ±
remises ± taxes, des catégories de TVA valides, etc.). La validation se fait
via le **Schematron EN16931** officiel (+ règles CIUS nationales le cas
échéant).

---

## 2. Factur-X (le format « hybride » privilégié en France)

Factur-X (= équivalent franco-allemand de **ZUGFeRD**) est un **PDF/A-3**
contenant **un fichier XML CII embarqué** :
- **Couche lisible** : le PDF/A-3 (lisible par un humain).
- **Couche structurée** : un XML CII (EN16931) **embarqué en pièce jointe**,
  nom de fichier réglementaire **`factur-x.xml`** (ZUGFeRD historique :
  `zugferd-invoice.xml`), avec une relation AFRelationship = **`Data`** (ou
  `Alternative` selon version) et des métadonnées XMP déclarant le profil.

Avantages : un seul fichier sert l'humain **et** la machine → adoption facile.

Exigences techniques **non négociables** :
- Le conteneur **doit être un PDF/A-3** (pas un PDF classique) — sinon non
  conforme.
- Le XML doit être déclaré dans les **métadonnées XMP** (`fx:DocumentType`,
  `fx:DocumentFileName`, `fx:Version`, `fx:ConformanceLevel` = le profil).
- L'**embedded file** doit porter le bon nom et la bonne relation.

Génération : utiliser une **bibliothèque dédiée** plutôt que bricoler le
PDF/A-3 à la main.
- PHP : `atgp/factur-x`, `easybill/php-factur-x`, ou via `horstoeko/zugferd`.
- Node/TS : `node-zugferd`, ou pipeline (génération XML CII + embarquement
  PDF/A-3 via une lib PDF/A capable, ex. Ghostscript/veraPDF en validation).
- Python : `factur-x` (lib de référence d'Alexis de Lattre / Akretion).
- Choisir d'après la stack du projet (cf. contexte).

---

## 3. UBL et CII (XML pur, sans PDF)

- **UBL 2.1** (OASIS) : XML, racine `<Invoice>` (namespace UBL). Très utilisé en
  Europe (Peppol BIS Billing 3.0 repose sur UBL).
- **CII** (UN/CEFACT Cross Industry Invoice) : XML, racine
  `<rsm:CrossIndustryInvoice>`. C'est le XML **embarqué dans Factur-X**.

Ces formats sont **purement structurés** (pas de couche PDF). Ils conviennent
aux flux 100 % machine entre PDP. Le choix Factur-X vs UBL/CII dépend du canal
et de l'accord d'interopérabilité entre PDP (le socle garantit que les trois
sont acceptés).

> **Peppol** : réseau d'interopérabilité international ; la France l'utilise
> notamment pour les flux transfrontaliers / certains raccordements PDP. Peppol
> BIS Billing 3.0 = profil UBL conforme EN16931.

---

## 4. Profils Factur-X (du plus pauvre au plus riche)

| Profil | Contenu | Usage |
|--------|---------|-------|
| **MINIMUM** | En-tête + totaux, **pas** les lignes de détail | Données minimales (souvent jugé insuffisant pour une vraie facture conforme) |
| **BASIC WL** (Without Lines) | Comme MINIMUM + plus de données d'en-tête, **sans lignes** | Comptabilité agrégée |
| **BASIC** | Socle EN16931 **avec lignes** | Facture conforme « courante » |
| **EN 16931 (COMFORT)** | Couverture **complète** du socle EN16931 | Recommandé par défaut |
| **EXTENDED** | EN16931 + extensions (cas métiers complexes) | Besoins avancés |

**Recommandation par défaut** : viser au moins **EN 16931 (COMFORT)** pour une
facture B2B conforme et autoporteuse. MINIMUM/BASIC WL ne portent pas les
lignes → souvent inadaptés à une facture réelle.

---

## 5. Champs clés et mentions « réforme » — où les placer

Mapping des mentions ajoutées par la réforme (voir reforme-2026.md §6) vers les
Business Terms EN16931 :

| Mention réforme | Business Term EN16931 (indicatif) |
|-----------------|-----------------------------------|
| SIREN/SIRET du client (B2B FR) | Identifiant légal de l'acheteur — `BT-47` (Buyer legal registration identifier), schéma `0009` (SIRET) |
| Adresse de livraison si ≠ facturation | Groupe **Deliver to** `BG-15` (`BT-75`…`BT-80`) |
| Catégorie d'opération (biens/services/mixte) | Porté par les codes type/`BT` dédiés + cohérence des lignes ; à mapper selon les spécifications DGFiP/PDP en vigueur |
| Option « TVA d'après les débits » | Mention/note + cohérence des règles TVA (`BG-23`) |
| Numéro de facture | `BT-1` |
| Date d'émission | `BT-2` |
| TVA acheteur/vendeur | `BT-31` (Seller VAT), `BT-48` (Buyer VAT) |
| Total HT / TVA / TTC | `BT-109` / `BT-110` / `BT-112` |

> Les codes exacts et les CIUS françaises évoluent : se référer aux
> **spécifications externes DGFiP / au guide de la PDP cible**. Toujours
> **valider** le résultat (cf. §6) plutôt que de présumer le mapping.

---

## 6. Validation et pièges PDF/A-3

**Valider la sémantique (EN16931)**
- Passer le XML (CII ou UBL) dans le **Schematron EN16931 officiel** + les
  règles **CIUS FR** applicables. Outils : `mustangproject` (Java, validateur
  ZUGFeRD/Factur-X), validateurs Schematron, services de la PDP.
- Un XML qui « s'ouvre » n'est PAS un XML valide : il doit passer les `BR-*`.
- **Outil intégré au skill** :
  [scripts/validate_facturx.py](../scripts/validate_facturx.py) extrait le XML
  d'un PDF Factur-X, détecte flavor + profil, et lance **XSD + Schematron
  EN16931** (via la lib `factur-x`/Saxon). Usage :
  `python3 scripts/validate_facturx.py facture.pdf` (ou `.xml`). Voir
  `scripts/requirements.txt` pour l'installation (venv).

> **Piège « profil MINIMUM » (vérifié)** : le Schematron du profil **MINIMUM**
> est **laxiste** — il vérifie la présence/codes (BR-08 adresse vendeur, BR-09
> code pays, codes devise/type) mais **PAS la cohérence arithmétique des
> totaux** (ex. `GrandTotal = TaxBasis + TaxTotal`, BR-CO-15, n'y est pas
> contrôlée). Une facture MINIMUM avec un TTC incohérent passe la validation.
> Conclusion d'audit : « Schematron OK en MINIMUM » ne garantit pas des montants
> justes. Pour une vraie facture B2B, exiger un profil **≥ BASIC** (qui
> enforce les règles `BR-CO-*`).

**Valider le conteneur (PDF/A-3)**
- Vérifier la conformité **PDF/A-3** avec **veraPDF**.
- Vérifier que le XML est bien **embarqué** sous le nom réglementaire et que
  les **métadonnées XMP** déclarent le bon profil.

**Pièges récurrents**
- Générer un PDF classique au lieu d'un **PDF/A-3** → rejet.
- XML embarqué mais **XMP absent/incohérent** (profil non déclaré) → outils de
  réception qui ne détectent pas la couche structurée.
- **Désynchronisation** entre la couche visible (PDF) et la couche XML (montants
  différents) → fraude/rejet. Les deux doivent refléter **les mêmes** données.
- Profil **MINIMUM** envoyé là où des **lignes** sont attendues.
- Mauvaise relation `AFRelationship` sur la pièce jointe.

---

## 7. Anti-patterns techniques (à détecter en audit)

| Anti-pattern | Correction |
|--------------|------------|
| Factur-X = PDF classique (pas PDF/A-3) | Conteneur PDF/A-3 validé veraPDF |
| XML non validé contre le Schematron EN16931 | Valider systématiquement (mustangproject / Schematron + CIUS FR) |
| Couche PDF et couche XML divergentes (montants ≠) | Générer les deux depuis **la même** source de données |
| Construire le PDF/A-3 « à la main » | Utiliser une lib dédiée (atgp/factur-x, mustang, factur-x py, node-zugferd) |
| Profil MINIMUM pour une facture détaillée | Viser EN16931 (COMFORT) au minimum |
| Mentions réforme absentes du XML (SIREN client, adresse livraison…) | Mapper sur les BT EN16931 + valider |
| Présumer le mapping CIUS FR sans le vérifier | Confronter aux specs DGFiP/PDP + valider le flux |
| Confondre Factur-X (FR) et ZUGFeRD (DE) comme incompatibles | Même socle technique ; noms de fichier/versions à aligner |
