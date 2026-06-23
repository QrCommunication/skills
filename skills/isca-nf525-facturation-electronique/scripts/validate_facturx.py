#!/usr/bin/env python3
"""
validate_facturx.py — Valide une facture électronique structurée (audit format).

Prend en entrée un PDF Factur-X/ZUGFeRD (.pdf) OU un XML brut (.xml, CII ou UBL)
et produit un rapport d'audit :
  1. Extraction du XML embarqué (pour un PDF) ;
  2. Détection du flavor (factur-x / zugferd / order-x) et du PROFIL
     (minimum → extended) ;
  3. Validation XSD (structure) ;
  4. Validation Schematron EN16931 (règles de gestion BR-*) — la vraie
     validation sémantique, via Saxon ;
  5. Contrôle de présence des Business Terms obligatoires + mentions « réforme » ;
  6. Rappels sur ce que ce script ne couvre PAS (conformité PDF/A-3 → veraPDF).

Périmètre honnête :
  - CII (Factur-X/ZUGFeRD) : XSD + Schematron EN16931 complets (lib factur-x).
  - UBL : contrôles STRUCTURELS uniquement ici ; pour la validation Schematron
    UBL (Peppol BIS / EN16931-UBL), utiliser mustangproject ou un validateur
    Peppol dédié.
  - Conformité du conteneur PDF/A-3 : NON vérifiée ici → utiliser veraPDF.

USAGE :
    python3 validate_facturx.py facture.pdf
    python3 validate_facturx.py facture.xml

Dépendances : voir scripts/requirements.txt (factur-x, lxml, pypdf, saxonche).
Le script se ré-exécute automatiquement dans ./.venv si présent à la racine du
skill.

CODE DE SORTIE : 0 = valide · 1 = non conforme (XSD/Schematron/obligatoire) ·
2 = erreur d'entrée / dépendances manquantes.
"""
from __future__ import annotations

import os
import sys


# ---------------------------------------------------------------------------
# Ré-exécution automatique dans le venv du skill (PEP 668 / externally-managed)
# ---------------------------------------------------------------------------
def _ensure_runtime() -> None:
    try:
        import facturx  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("_FACTURX_REEXEC") == "1":
        return  # déjà ré-exécuté : on laissera main() afficher l'erreur propre
    here = os.path.dirname(os.path.abspath(__file__))
    venv_py = os.path.normpath(os.path.join(here, "..", ".venv", "bin", "python"))
    # NB : comparer les chemins ABSOLUS, pas realpath() — le python du venv est
    # un symlink vers l'interpréteur système, donc realpath les confondrait et
    # empêcherait la bascule. Le flag _FACTURX_REEXEC garde contre toute boucle.
    if os.path.exists(venv_py) and os.path.abspath(venv_py) != os.path.abspath(sys.executable):
        env = dict(os.environ, _FACTURX_REEXEC="1")
        os.execve(venv_py, [venv_py, os.path.abspath(__file__), *sys.argv[1:]], env)


_ensure_runtime()

# Silence les logs INFO bavards de factur-x ; on ne garde que nos messages.
import logging  # noqa: E402
logging.getLogger("facturx").setLevel(logging.ERROR)


# ---------------------------------------------------------------------------
# Helpers XML (parcours par nom local, robuste aux versions de namespace)
# ---------------------------------------------------------------------------
def lname(el) -> str:
    return el.tag.rsplit("}", 1)[-1] if isinstance(el.tag, str) else ""


def child(el, name):
    if el is None:
        return None
    for c in el:
        if lname(c) == name:
            return c
    return None


def descend(el, *names):
    cur = el
    for n in names:
        cur = child(cur, n)
        if cur is None:
            return None
    return cur


def text(el, *names):
    node = descend(el, *names) if names else el
    if node is None or node.text is None:
        return None
    return node.text.strip()


def count_local(root, name) -> int:
    return sum(1 for el in root.iter() if lname(el) == name)


# ---------------------------------------------------------------------------
# Extraction des champs métier pour le rapport lisible
# ---------------------------------------------------------------------------
def extract_cii(root) -> dict:
    doc = child(root, "ExchangedDocument")
    txn = child(root, "SupplyChainTradeTransaction")
    agr = descend(txn, "ApplicableHeaderTradeAgreement")
    settle = descend(txn, "ApplicableHeaderTradeSettlement")
    summ = descend(settle, "SpecifiedTradeSettlementHeaderMonetarySummation")
    seller = descend(agr, "SellerTradeParty")
    buyer = descend(agr, "BuyerTradeParty")
    return {
        "BT-1 (n° facture)": text(doc, "ID"),
        "BT-3 (type code)": text(doc, "TypeCode"),
        "BT-2 (date émission)": text(doc, "IssueDateTime", "DateTimeString"),
        "BT-27 (vendeur)": text(seller, "Name"),
        "BT-31 (TVA vendeur)": text(descend(seller, "SpecifiedTaxRegistration"), "ID"),
        "BT-44 (acheteur)": text(buyer, "Name"),
        "SIREN/SIRET acheteur": text(descend(buyer, "SpecifiedLegalOrganization"), "ID"),
        "BT-5 (devise)": text(settle, "InvoiceCurrencyCode"),
        "BT-109 (total HT)": text(summ, "TaxBasisTotalAmount"),
        "BT-110 (total TVA)": text(summ, "TaxTotalAmount"),
        "BT-112 (total TTC)": text(summ, "GrandTotalAmount"),
        "_lignes": count_local(root, "IncludedSupplyChainTradeLineItem"),
        "_deliver_to": descend(txn, "ApplicableHeaderTradeDelivery", "ShipToTradeParty") is not None,
    }


def extract_ubl(root) -> dict:
    supplier = descend(root, "AccountingSupplierParty", "Party")
    customer = descend(root, "AccountingCustomerParty", "Party")
    total = child(root, "LegalMonetaryTotal")
    return {
        "BT-1 (n° facture)": text(root, "ID"),
        "BT-3 (type code)": text(root, "InvoiceTypeCode"),
        "BT-2 (date émission)": text(root, "IssueDate"),
        "CustomizationID": text(root, "CustomizationID"),
        "BT-27 (vendeur)": text(descend(supplier, "PartyLegalEntity"), "RegistrationName") or text(descend(supplier, "PartyName"), "Name"),
        "BT-44 (acheteur)": text(descend(customer, "PartyLegalEntity"), "RegistrationName") or text(descend(customer, "PartyName"), "Name"),
        "BT-5 (devise)": text(root, "DocumentCurrencyCode"),
        "BT-112 (total à payer)": text(total, "PayableAmount"),
        "_lignes": count_local(root, "InvoiceLine"),
        "_deliver_to": descend(root, "Delivery") is not None,
    }


MANDATORY = ["BT-1 (n° facture)", "BT-3 (type code)", "BT-2 (date émission)",
             "BT-27 (vendeur)", "BT-44 (acheteur)", "BT-5 (devise)"]


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------
def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if "-h" in sys.argv or "--help" in sys.argv else 2

    path = sys.argv[1]
    try:
        import facturx
        import lxml.etree as ET
    except ImportError:
        print("ERREUR : dépendances manquantes. Installer :", file=sys.stderr)
        print("  python3 -m venv .venv && "
              ".venv/bin/pip install -r scripts/requirements.txt", file=sys.stderr)
        return 2

    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"ERREUR lecture : {e}", file=sys.stderr)
        return 2

    is_pdf = data[:5] == b"%PDF-" or path.lower().endswith(".pdf")

    print("=" * 64)
    print(f"AUDIT FORMAT — {os.path.basename(path)}")
    print("=" * 64)

    # 1. Obtenir le XML (extraction si PDF)
    xml_filename = os.path.basename(path)
    if is_pdf:
        try:
            xml_filename, xml_bytes = facturx.get_xml_from_pdf(
                data, check_xsd=False, check_schematron=False)
        except Exception as e:
            print("🔴 Aucun XML de facture exploitable trouvé dans le PDF.")
            print(f"   Détail : {str(e)[:200]}")
            print("   → Ce n'est pas un Factur-X/ZUGFeRD valide, ou la pièce "
                  "jointe XML est absente/mal nommée.")
            return 1
        if not xml_bytes:
            print("🔴 PDF sans XML embarqué (pas un Factur-X). "
                  "Pièce jointe `factur-x.xml` attendue.")
            return 1
        print(f"📎 XML embarqué extrait : {xml_filename}")
    else:
        xml_bytes = data
        print("📄 Entrée XML brute (pas de couche PDF — conteneur PDF/A-3 non "
              "applicable).")

    # 2. Parser + détecter flavor/profil
    # Parseur DURCI : le XML provient potentiellement d'un tiers (facture reçue).
    # Désactiver entités externes + réseau + DTD → anti-XXE et anti-billion-laughs.
    try:
        safe_parser = ET.XMLParser(
            resolve_entities=False, no_network=True, load_dtd=False,
            dtd_validation=False, huge_tree=False)
        root = ET.fromstring(xml_bytes, parser=safe_parser)
    except ET.XMLSyntaxError as e:
        print(f"🔴 XML mal formé ou rejeté (entités/DTD interdites) : {e}")
        return 1

    syntax = lname(root)  # CrossIndustryInvoice (CII) | Invoice (UBL)
    is_cii = syntax == "CrossIndustryInvoice"
    is_ubl = syntax == "Invoice"

    flavor = level = None
    if is_cii:
        try:
            flavor = facturx.get_flavor(root)
            level = facturx.get_level(root)
        except Exception:
            pass
    print(f"🧬 Syntaxe : {'CII' if is_cii else 'UBL' if is_ubl else syntax}"
          + (f" | flavor : {flavor} | profil : {level}" if flavor else ""))

    failures = 0

    # 3-4. Validation XSD + Schematron (CII uniquement via factur-x)
    if is_cii:
        for label, fn in (("XSD (structure)", "xml_check_xsd"),
                          ("Schematron EN16931 (règles BR-*)", "xml_check_schematron")):
            try:
                getattr(facturx, fn)(xml_bytes, flavor="factur-x",
                                     level=level or "autodetect")
                print(f"✅ {label} : VALIDE")
            except Exception as e:
                failures += 1
                msg = str(e).strip().splitlines()
                print(f"🔴 {label} : NON VALIDE")
                for line in msg[:8]:
                    print(f"     {line}")
                if len(msg) > 8:
                    print(f"     … (+{len(msg) - 8} ligne(s))")
    elif is_ubl:
        print("🟠 UBL détecté : validation Schematron NON couverte par ce "
              "script.")
        print("   → Valider via mustangproject ou un validateur Peppol/EN16931-UBL.")
    else:
        print(f"🟠 Racine inattendue '{syntax}' : ni CII ni UBL reconnu.")

    # 5. Champs métier + obligatoires + mentions réforme
    fields = extract_cii(root) if is_cii else extract_ubl(root) if is_ubl else {}
    if fields:
        print("\n— Champs extraits —")
        for k, v in fields.items():
            if k.startswith("_"):
                continue
            mark = "" if v else "  ⟵ ABSENT"
            print(f"   {k:<24}: {v if v else '∅'}{mark}")

        missing = [k for k in MANDATORY if k in fields and not fields[k]]
        if missing:
            failures += 1
            print("\n🔴 Business Terms OBLIGATOIRES manquants : "
                  + ", ".join(missing))

        # Cohérence profil / lignes
        lines = fields.get("_lignes", 0)
        if level in ("basic", "en16931", "extended") and lines == 0:
            print("🟠 Profil détaillé sans aucune ligne de facture "
                  "(IncludedSupplyChainTradeLineItem).")
        if level in ("minimum", "basicwl"):
            print(f"🟡 Profil « {level} » : pas de lignes de détail "
                  "(souvent insuffisant pour une facture B2B conforme).")

        # Mentions « réforme » (best-effort)
        if is_cii and not fields.get("SIREN/SIRET acheteur"):
            print("🟡 Réforme : SIREN/SIRET acheteur absent (mention requise "
                  "en B2B domestique).")
        if not fields.get("_deliver_to"):
            print("🟡 Réforme : adresse de livraison non renseignée (requise si "
                  "≠ adresse de facturation).")

    # 6. Rappels hors périmètre
    print("\n— Hors périmètre de ce script (à vérifier séparément) —")
    if is_pdf:
        print("   • Conformité PDF/A-3 du conteneur → veraPDF "
              "(`verapdf --flavour 3b facture.pdf`).")
    print("   • CIUS françaises / spécifications DGFiP de la PDP cible.")
    print("   • Cohérence couche PDF lisible ⇄ couche XML (mêmes montants).")

    # Verdict
    print("\n" + "-" * 64)
    if failures == 0 and (is_cii or is_ubl):
        print("✅ VALIDE — aucune anomalie bloquante détectée par ce script.")
        return 0
    print(f"🔴 NON CONFORME — {failures} contrôle(s) bloquant(s) en échec.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
