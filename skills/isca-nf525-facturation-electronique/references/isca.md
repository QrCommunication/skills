# ISCA — Loi anti-fraude TVA (logiciels de caisse / d'encaissement)

> Source de l'obligation : **article 286, I, 3° bis du CGI**.
> Doctrine : **BOI-TVA-DECLA-30-10-30** (BOFiP). En vigueur depuis le
> **1er janvier 2018**.

## Table des matières
1. Fondement légal et champ d'application
2. Les 4 conditions ISCA en détail
3. Mécanismes techniques attendus
4. Modes de preuve (certificat vs attestation) — état 2025/2026
5. Sanctions et contrôle inopiné
6. Anti-patterns fréquents

---

## 1. Fondement légal et champ d'application

L'article 286-I-3°bis du CGI impose à **tout assujetti à la TVA qui enregistre
les règlements de ses clients au moyen d'un logiciel ou d'un système de
caisse** d'utiliser un logiciel/système satisfaisant à des conditions
**d'inaltérabilité, de sécurisation, de conservation et d'archivage** des
données, en vue du contrôle de l'administration fiscale.

**Qui est concerné**
- Logiciels de caisse, systèmes d'encaissement, certains ERP/logiciels de
  gestion **dès lors qu'ils enregistrent les règlements clients**.
- Le déclencheur est l'**enregistrement du règlement**, pas la facturation
  seule.

**Qui ne l'est PAS (assouplissement notable)**
- Depuis la loi de finances 2018, l'obligation est **recentrée sur les
  logiciels et systèmes de CAISSE** (et non « tout logiciel comptable »).
- Les opérations exclusivement **B2B** (entre assujettis) qui donnent
  obligatoirement lieu à facture peuvent sortir du champ selon le cas — mais
  l'analyse se fait au cas par cas. **Vérifier le BOFiP au moment de l'usage.**

> Ne pas confondre avec l'obligation comptable générale de conservation des
> documents (LPF) ni avec la réforme e-invoicing 2026 (réglementation
> distincte — voir reforme-2026.md).

---

## 2. Les 4 conditions ISCA en détail

**I — Inaltérabilité**
Les données d'encaissement, une fois enregistrées, **ne peuvent plus être
modifiées ni supprimées**. Toute correction doit se faire par une **nouvelle
écriture** (annulation / opération de signe contraire / note de correction),
en conservant l'enregistrement initial. La donnée originale reste lisible et
traçable. Mécanisme typique : **chaînage de hachage** (voir §3) garantissant
que toute modification a posteriori est détectable.

**S — Sécurisation**
Les données sont **sécurisées et horodatées** de façon à garantir leur
**origine et leur intégrité**. Mécanismes : signature/empreinte de chaque
enregistrement, chaînage cryptographique, horodatage fiable, contrôle d'accès.
L'objectif : prouver qu'une donnée n'a pas été insérée, retirée ou modifiée.

**C — Conservation**
Les données sont **conservées dans le temps**, avec des **clôtures
périodiques** obligatoires : clôture **journalière (Z)**, **mensuelle** et
**annuelle** (a minima), produisant des **données récapitulatives cumulatives,
elles-mêmes inaltérables et chaînées**. Le **grand total perpétuel**
(cumul de tous les encaissements depuis l'origine) en est l'illustration : il
ne peut que croître, jamais être remis à zéro.

**A — Archivage**
Les données sont **archivées** afin de figer leur valeur probante et de
permettre la lecture par l'administration. L'archive est **datée**, donne lieu
à un **document/justificatif d'archivage** (souvent signé/scellé) et doit
rester **exploitable** dans le temps (format pérenne, restitution possible).
L'archivage purge le système opérationnel tout en garantissant la
restitution.

**Mnémonique** : **I**naltérabilité · **S**écurisation · **C**onservation ·
**A**rchivage.

---

## 3. Mécanismes techniques attendus

### Chaînage de hachage (cœur de l'inaltérabilité/sécurisation)
Chaque enregistrement (ligne, ticket, clôture) porte une **signature/empreinte**
calculée à partir de **ses propres données + la signature de l'enregistrement
précédent** :

```
signature_n = H( données_normalisées_n  ||  signature_{n-1} )
```

Propriétés :
- Modifier une donnée passée casse toutes les signatures suivantes → **détectable**.
- Supprimer un enregistrement rompt la continuité → **détectable**.
- Réordonner → **détectable**.

Choix d'implémentation usuels : `H = SHA-256` (ou supérieur). La
**normalisation déterministe** des données avant hachage est critique (ordre
des champs, formats de date, séparateurs, encodage) — sinon le rejeu d'audit
échoue à tort. L'outil [scripts/verify_chain.py](../scripts/verify_chain.py)
rejoue ce chaînage.

> Pour un système multi-tenant, **chaîner par périmètre fiscal** (par
> établissement / par séquence fiscale), pas globalement, pour éviter
> couplage et fuites inter-tenants. Voir aussi les règles globales sur les
> séquences fiscales et triggers PostgreSQL.

### Numérotation séquentielle continue, sans trou
Tickets/factures numérotés en **séquence continue, chronologique, sans rupture
ni doublon**. Un trou doit être **justifiable** (annulation tracée), jamais
silencieux.

### Corrections par écriture de signe contraire
Une erreur ne se corrige **jamais** par `UPDATE`/`DELETE`. On crée une
**opération d'annulation** (montant négatif / contre-passation) qui référence
l'original. Les deux écritures restent dans le journal.

### Journal des événements (JET — Journal des Événements Techniques)
Trace **horodatée et inaltérable** des événements significatifs : démarrage,
clôtures, ouvertures de tiroir, modifications de paramétrage, exports,
incidents, changements d'heure, mode formation/réel. C'est une exigence forte
de NF525 (voir nf525.md).

### Clôtures et grand total perpétuel
- **Clôture Z journalière** : fige la journée, produit un cumul, incrémente le
  grand total perpétuel.
- Cumuls **mensuels** et **annuels** chaînés.
- **Grand total perpétuel** : strictement croissant, jamais réinitialisable.

### Mode formation
Si un mode « école/formation » existe, ses opérations doivent être
**clairement marquées et exclues** des totaux fiscaux, mais **tracées** au JET.

---

## 4. Modes de preuve — état 2025/2026 (À VÉRIFIER au moment de l'usage)

La conformité ISCA se prouve par **l'un** des modes suivants :
1. **Certificat délivré par un organisme accrédité** (ex. **NF525** via
   Infocert/AFNOR Certification, ou **LNE**).
2. **Attestation individuelle de l'éditeur** (auto-attestation).

**Chronologie des revirements (essentielle)** :

| Date | Texte | Effet |
|------|-------|-------|
| 2018-01-01 | LF 2016, art. 88 → art. 286-I-3°bis CGI | Entrée en vigueur de l'obligation ISCA. Preuve par **certificat OU attestation éditeur**. |
| 2025-02-16 | **LF 2025, art. 43** (loi n° 2025-127 du 14/02/2025) | **Supprime** l'attestation éditeur. Seul le **certificat accrédité** admis. Périodes transitoires jusqu'au 31/08/2026 (certificat OU demande de certification en cours). |
| 2026-02-19 | **LF 2026, art. 125** (loi n° 2026-103 du 19/02/2026) | **RÉTABLIT l'auto-attestation** éditeur. Annule la suppression. |

**État au moment de l'écriture (juin 2026)** : les **deux** modes coexistent à
nouveau (certificat accrédité **ou** attestation éditeur). **Toujours
reconfirmer** sur impots.gouv.fr / BOFiP avant de conseiller un client, car ce
point a déjà fait l'objet de plusieurs allers-retours.

> Conséquence pratique pour un éditeur : viser la **certification NF525/LNE**
> reste le choix le plus robuste (valeur probante maximale, indépendante des
> revirements législatifs sur l'auto-attestation).

---

## 5. Sanctions et contrôle inopiné

- **Amende de 7 500 €** par logiciel/système non conforme (à défaut de
  certificat ou d'attestation justifiant la conformité), assortie de
  l'obligation de se mettre en conformité sous 60 jours, sous peine de
  nouvelle amende.
- **Contrôle inopiné** : l'administration peut intervenir sans préavis dans les
  locaux pour faire constater la détention du justificatif (certificat/
  attestation) et le fonctionnement conforme.
- L'éditeur qui fournit un logiciel permettant la fraude (permissif) s'expose à
  des sanctions spécifiques (solidarité, amendes).

---

## 6. Anti-patterns fréquents (à détecter en audit)

| Anti-pattern | Pourquoi c'est non conforme | Correction |
|--------------|------------------------------|------------|
| `UPDATE`/`DELETE` sur une écriture d'encaissement | Viole l'**Inaltérabilité** | Écriture de signe contraire référençant l'original |
| Pas de chaînage de hachage (signatures indépendantes) | Suppression/réordonnancement non détectables → **Sécurisation** KO | Chaîner : `sig_n = H(data_n || sig_{n-1})` |
| Numérotation avec trous non justifiés | Séquence fiscale rompue | Séquence continue + annulations tracées |
| Grand total perpétuel réinitialisable | Viole **Conservation** | Cumul strictement croissant, non remis à zéro |
| Clôture Z modifiable a posteriori | Clôture non inaltérable | Figer la clôture + la chaîner |
| Normalisation non déterministe avant hachage | Rejeu d'audit échoue à tort, ou collisions exploitables | Spécifier un format canonique strict |
| Mode formation mélangé aux totaux réels | Données fiscales polluées | Marquage + exclusion + trace JET |
| Pas de JET (journal d'événements) | Exigence NF525 absente | Journaliser événements techniques horodatés |
| Archive sans justificatif daté/scellé | Valeur probante non figée | Document d'archivage signé + format pérenne |
| Conclure « conforme » sur la seule présence d'une attestation, sans vérifier le mécanisme réel | Une attestation ne vaut que si le logiciel fait vraiment ISCA | Auditer le code/comportement, pas le PDF |
