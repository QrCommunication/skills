# Checklists d'audit de conformité

> Checklists prêtes à l'emploi pour le **mode AUDIT**. Pour chaque constat,
> noter : **gravité** (🔴 bloquant / 🟠 majeur / 🟡 mineur) + **exigence
> violée** (article/condition) + **correction**. Ne jamais conclure « conforme »
> sur la seule présence d'un certificat/attestation : **vérifier le
> comportement réel**.

## Table des matières
1. Méthode d'audit
2. Checklist ISCA (logiciel de caisse)
3. Checklist NF525 (exigences fonctionnelles)
4. Checklist Factur-X / format structuré
5. Checklist intégration réforme / PDP
6. Grille de restitution

---

## 1. Méthode d'audit

1. **Délimiter le périmètre** : le logiciel enregistre-t-il des règlements
   clients (→ ISCA/NF525) ? émet-il des factures B2B (→ réforme) ? les deux ?
2. **Lire avant de juger** : modèles de données, services d'écriture,
   migrations, mécanisme de signature/chaînage, exports, génération de format.
3. **Tester le comportement** : tenter une modification interdite, rejouer un
   chaînage, valider un fichier produit.
4. **Tracer chaque constat** dans la grille (§6).

---

## 2. Checklist ISCA (référence : isca.md)

**Inaltérabilité**
- [ ] Aucune voie de **modification/suppression** d'une opération
  d'encaissement enregistrée (ni UI, ni API, ni script, ni accès DB
  applicatif). 🔴
- [ ] Les corrections passent **uniquement** par une écriture de **signe
  contraire** référençant l'original. 🔴
- [ ] **Chaînage de hachage** présent : `sig_n = H(data_n || sig_{n-1})`. 🔴
- [ ] Rejeu du chaînage **sans rupture** (utiliser `verify_chain.py`). 🔴
- [ ] **Normalisation déterministe** des données avant hachage (format
  canonique documenté). 🟠

**Sécurisation**
- [ ] Chaque enregistrement et chaque clôture sont **signés**. 🔴
- [ ] **Horodatage fiable** ; changements d'heure **détectés et tracés**. 🟠
- [ ] **Contrôle d'accès** / gestion des droits. 🟠

**Conservation**
- [ ] **Clôtures** journalière (Z), mensuelle, annuelle, produisant des
  **cumuls chaînés inaltérables**. 🔴
- [ ] **Grand total perpétuel** strictement croissant, **non
  réinitialisable**. 🔴
- [ ] Cohérence : cumul période = somme des opérations ; cumul annuel = somme
  des mensuels. 🟠

**Archivage**
- [ ] Procédure d'archivage produisant une archive **datée + signée/scellée**,
  **restituable**, en **format pérenne**. 🔴
- [ ] **Document/justificatif d'archivage** généré. 🟠

**Preuve de conformité**
- [ ] Certificat accrédité (NF525/LNE) **ou** attestation éditeur présent —
  **et** mécanisme réel cohérent avec le justificatif. 🔴
  (Rappel : mode de preuve admis = état du droit daté, voir isca.md.)

---

## 3. Checklist NF525 (référence : nf525.md)

- [ ] **JET** (Journal des Événements Techniques) présent, horodaté,
  **inaltérable**, couvrant démarrages, clôtures, archivages, changements de
  paramétrage, bascule formation/réel, changements d'heure. 🔴
- [ ] **Numérotation** continue, chronologique, sans trou non justifié. 🔴
- [ ] **Compteurs perpétuels** (tickets, clôtures). 🟠
- [ ] **Mode formation** marqué + **exclu** des totaux fiscaux + tracé. 🟠
- [ ] **Version certifiée** = version déployée (pas de dérive non
  re-contrôlée). 🟠
- [ ] **Multi-tenant** : périmètre fiscal **chaîné par tenant**, perpétuels non
  mélangés. 🔴 (si applicable)

---

## 4. Checklist Factur-X / format structuré (référence : formats.md)

- [ ] Conteneur = **PDF/A-3** (vérifié veraPDF), pas un PDF classique. 🔴
- [ ] XML CII **embarqué** sous le nom **`factur-x.xml`** + **XMP** déclarant le
  profil. 🔴
- [ ] XML **valide EN16931** (Schematron officiel + CIUS FR) — passe les
  `BR-*`. 🔴
- [ ] Couche **PDF lisible** et couche **XML** portent **les mêmes montants**
  (pas de divergence). 🔴
- [ ] **Profil ≥ EN16931 (COMFORT)** pour une facture détaillée (pas
  MINIMUM/BASIC WL). 🟠
- [ ] **Mentions réforme** présentes dans le XML : SIREN client, adresse de
  livraison si ≠, catégorie d'opération, option TVA débits. 🟠
- [ ] Génération via **lib dédiée** (pas de PDF/A-3 fait main). 🟡

---

## 5. Checklist intégration réforme / PDP (référence : reforme-2026.md)

- [ ] Capacité de **réception** des factures électroniques (obligatoire pour
  tous dès **1er sept. 2026**). 🔴
- [ ] **Raccordement à au moins une PDP** (le logiciel seul, en tant qu'OD, ne
  peut pas émettre/recevoir directement). 🔴
- [ ] **Résolution d'adresse via l'annuaire** (SIREN/SIRET + code routage). 🟠
- [ ] **Émission + e-reporting** pour les opérations dans le champ (selon
  taille d'entreprise et échéance). 🔴
- [ ] **E-reporting** des opérations B2C / internationales + **données de
  paiement**. 🟠
- [ ] Gestion du **cycle de vie / statuts** de facture (déposée, reçue,
  approuvée/refusée, encaissée…). 🟠
- [ ] Exemptions correctement appliquées (B2C, opérations exonérées de TVA,
  international). 🟡

---

## 6. Grille de restitution (modèle)

```
| # | Constat                                   | Gravité | Exigence violée            | Correction proposée                  |
|---|-------------------------------------------|---------|----------------------------|--------------------------------------|
| 1 | UPDATE possible sur ticket encaissé       | 🔴      | ISCA Inaltérabilité (CGI)  | Écriture de signe contraire + chaînage |
| 2 | Pas de validation Schematron EN16931      | 🔴      | EN16931 / réforme          | Valider via mustangproject + CIUS FR |
| 3 | Profil Factur-X = MINIMUM (sans lignes)   | 🟠      | EN16931 (COMFORT) attendu  | Passer en profil EN16931             |
| … |                                           |         |                            |                                      |
```

Conclure par : **synthèse** (nb de 🔴/🟠/🟡), **verdict** (conforme / non
conforme / conforme sous réserve), et **plan de remédiation priorisé** (les 🔴
d'abord). Rappeler que les points réglementaires datés doivent être
**reconfirmés** à la source officielle.
