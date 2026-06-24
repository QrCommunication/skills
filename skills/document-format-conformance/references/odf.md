# ODF / OpenOffice — ISO/IEC 26300 (OASIS ODF) (.odt .ods .odp)

Référence pour valider/modifier les formats OpenDocument (LibreOffice/OpenOffice).

## Sommaire
- Conteneur ZIP & règle du mimetype
- Parts XML principales
- Manifest
- Conformité : invariants + RelaxNG
- Obtenir le schéma RelaxNG
- Écarts fréquents
- Commandes du skill

## Conteneur ZIP & règle du `mimetype` (ISO 26300-3 §3.3)

Un fichier ODF est un **ZIP** avec une contrainte forte, distinctive d'ODF :

> Si le package contient une entrée `mimetype`, elle **DOIT être la PREMIÈRE
> entrée du ZIP**, stockée **non compressée (STORED)** et **sans extra field**.
> Son contenu = la chaîne MIME exacte du type de document.

Cela permet à un outil de lire le type en lisant les premiers octets du ZIP sans
le décompresser. **Casser cette règle = fichier non conforme** (même si LibreOffice
le récupère). `opc_modify.py` la **re-garantit** à chaque repackage.

Valeurs `mimetype` :

| Type | Extension | mimetype |
|---|---|---|
| Texte | .odt | `application/vnd.oasis.opendocument.text` |
| Classeur | .ods | `application/vnd.oasis.opendocument.spreadsheet` |
| Présentation | .odp | `application/vnd.oasis.opendocument.presentation` |
| Dessin | .odg | `application/vnd.oasis.opendocument.graphics` |

## Parts XML principales

| Part | Rôle |
|---|---|
| `content.xml` | contenu du document (`<office:document-content>`) |
| `styles.xml` | styles & styles de page |
| `meta.xml` | métadonnées (Dublin Core + ODF) |
| `settings.xml` | réglages applicatifs (non normatifs au rendu) |
| `META-INF/manifest.xml` | **liste toutes les entrées** du package + media-type (+ infos de chiffrement éventuelles) |
| `Pictures/…`, `Thumbnails/…` | médias, vignette |

Namespaces ODF (préfixes usuels) : `office:`, `text:`, `table:`, `draw:`,
`style:`, `fo:`, `manifest:`. Tout XML well-formed doit déclarer ses préfixes.

## Manifest (ISO 26300-3 §3.4)

`META-INF/manifest.xml` (`<manifest:manifest>`) référence chaque fichier du
package via `<manifest:file-entry manifest:full-path="…" manifest:media-type="…"/>`,
dont l'entrée racine `full-path="/"` portant le media-type du document. Une entrée
présente dans le ZIP mais absente du manifest (ou inversement) est un écart.

## Conformité

### Structurelle (toujours)
1. `mimetype` = 1ère entrée, **STORED**, valeur ODF reconnue.
2. `META-INF/manifest.xml` présent + well-formed.
3. `content.xml` présent + well-formed.

→ `validate.py` couvre ces points (lxml + zipfile).

### Sémantique forte (RelaxNG)
ODF est spécifié en **RelaxNG** (pas XSD). Schéma `OpenDocument-v1.3-schema.rng`
(et `…-manifest-schema.rng`).

```bash
unzip -p f.odt content.xml > /tmp/content.xml
xmllint --noout --relaxng OpenDocument-v1.3-schema.rng /tmp/content.xml
```

`validate.py --rng OpenDocument-v1.3-schema.rng f.odt` route vers cette validation.

### Obtenir le schéma RelaxNG officiel
- OASIS : page de la spec ODF 1.3 → archive « OpenDocument-v1.3 » → fichiers
  `*-schema.rng` (schema, manifest, dsig). Les versions 1.2/1.3 sont
  rétro-compatibles pour la plupart des documents.

## Écarts fréquents

| Écart | Détection |
|---|---|
| `mimetype` compressé ou pas en 1ère position | `validate.py` : checks mimetype = False (cause n°1 après repackage naïf) |
| `mimetype` absent alors que ZIP ODF | type non détectable sans décompression |
| Entrée ZIP non listée dans le manifest | incohérence manifest ⇄ package |
| `content.xml` mal formé (édition manuelle) | `validate.py` : well-formed = False |
| Préfixe de namespace non déclaré | XML invalide (vu lors d'un patch partiel) |

## Modifier en restant conforme

```bash
python3 scripts/opc_modify.py list f.odt
python3 scripts/opc_modify.py get  f.odt content.xml > content.xml
#   … éditer …
python3 scripts/opc_modify.py set  f.odt content.xml content.xml --out out.odt
```

`set` réordonne `mimetype` en 1ʳᵉ position STORED automatiquement, refuse un XML
cassé, et revalide la sortie. Pour générer/convertir depuis d'autres formats,
`soffice --headless --convert-to odt …` (LibreOffice) est disponible.

## Outils sous-jacents
- **zipfile** (stdlib) : conteneur + règle mimetype.
- **lxml** : well-formedness.
- **xmllint** : validation RelaxNG.
- **soffice/libreoffice** : conversion / round-trip.
