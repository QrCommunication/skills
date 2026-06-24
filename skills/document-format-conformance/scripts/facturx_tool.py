#!/usr/bin/env python3
"""facturx_tool.py — conformité du CONTENEUR Factur-X / PDF/A-3.

Périmètre = la mécanique PDF/A-3 d'une facture hybride (ISO 32000-2 §14.13
Associated Files + ISO 19005-3 PDF/A-3 + profil XMP Factur-X) :
  - PDF/A-3b via veraPDF ;
  - pièce jointe XML présente + /AFRelationship correct ;
  - /AF au niveau document (Associated Files) ;
  - métadonnées XMP Factur-X (DocumentType/Version/ConformanceLevel).

La SÉMANTIQUE fiscale du XML (XSD, Schematron EN16931, business terms, réforme
2026) est couverte par le skill isca-nf525-facturation-electronique → on y
renvoie plutôt que de la dupliquer. `check` lance néanmoins un XSD rapide via la
lib factur-x pour signaler un XML structurellement invalide.

Sous-commandes :
  check   <pdf>
  extract <pdf> [--out facture.xml]
  embed   <pdf-base> <xml> [--out out.pdf] [--flavor factur-x] [--level en16931]
          [--afrelationship data|alternative|source] [--no-xsd]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

import _common as C

C.reexec_in_venv()
C.harden_path()
logging.getLogger("facturx").setLevel(logging.ERROR)

FX_XML_NAMES = {"factur-x.xml", "zugferd-invoice.xml", "xrechnung.xml", "order-x.xml", "factur-x.cii.xml"}
VALID_AFR = {"data", "source", "alternative", "supplement", "unspecified"}


def _embedded_info(pdf_path: str) -> dict:
    """Inspecte /Names/EmbeddedFiles + /AF document-level via pikepdf."""
    import pikepdf
    res = {"embedded_files": [], "doc_level_AF": False}
    with pikepdf.open(pdf_path) as pdf:
        res["doc_level_AF"] = "/AF" in pdf.Root
        names = pdf.Root.get("/Names")
        if names is not None and "/EmbeddedFiles" in names:
            arr = names["/EmbeddedFiles"].get("/Names", [])
            for i in range(0, len(arr) - 1, 2):
                spec = arr[i + 1]
                res["embedded_files"].append({
                    "name": str(arr[i]),
                    "AFRelationship": str(spec.get("/AFRelationship", "")) or None,
                })
        # XMP Factur-X
        try:
            with pdf.open_metadata() as m:
                xmp = str(m)
            res["xmp_facturx"] = ("urn:factur-x" in xmp) or ("fx:DocumentType" in xmp) or ("DocumentType" in xmp and "ConformanceLevel" in xmp)
        except Exception:  # noqa: BLE001
            res["xmp_facturx"] = None
    return res


def cmd_check(pdf: str) -> int:
    import facturx
    checks, tools = [], {}

    # 1. XML embarqué présent + nom normatif
    try:
        with open(pdf, "rb") as f:
            data = f.read()
        xml_name, xml_bytes = facturx.get_xml_from_pdf(data, check_xsd=False, check_schematron=False)
    except Exception as e:  # noqa: BLE001
        xml_name, xml_bytes = None, None
        checks.append(C.check("XML de facture embarqué", False, str(e)[:200]))
    if xml_bytes:
        checks.append(C.check("XML de facture embarqué", True, f"fichier: {xml_name}"))
        checks.append(C.check("nom de pièce jointe normatif", xml_name in FX_XML_NAMES,
                              f"{xml_name} (attendu ∈ {sorted(FX_XML_NAMES)})",
                              "Factur-X 1.0.07 §6"))
        # XSD rapide (structure) — sémantique complète → skill isca
        try:
            from lxml import etree
            root = etree.fromstring(xml_bytes)
            flavor = facturx.get_flavor(root)
            level = facturx.get_level(root)
            facturx.xml_check_xsd(xml_bytes, flavor=flavor, level=level)
            checks.append(C.check("XML XSD (structure)", True, f"flavor={flavor} level={level}"))
        except Exception as e:  # noqa: BLE001
            checks.append(C.check("XML XSD (structure)", False, str(e)[:300]))

    # 2. AFRelationship + /AF document-level
    emb = _embedded_info(pdf)
    fx_att = next((e for e in emb["embedded_files"] if e["name"] in FX_XML_NAMES), None)
    if fx_att:
        rel = (fx_att["AFRelationship"] or "").lstrip("/").lower()
        checks.append(C.check("/AFRelationship sur la pièce XML", rel in VALID_AFR,
                              f"AFRelationship={fx_att['AFRelationship']}",
                              "ISO 32000-2 §7.11.3 / Factur-X §6"))
    checks.append(C.check("/AF document-level (Associated Files)", emb["doc_level_AF"],
                          spec="ISO 32000-2 §14.13"))
    checks.append(C.check("métadonnées XMP Factur-X", emb.get("xmp_facturx"),
                          spec="Factur-X §7 (extension schema XMP)"))

    # 3. PDF/A-3b via veraPDF
    vera = C.find_tool("verapdf")
    if not vera:
        checks.append(C.check("PDF/A-3b (veraPDF)", None, "veraPDF absent — " + C.SETUP_HINT))
    else:
        tools["verapdf"] = C.run([vera, "--version"]).stdout.strip().split("\n")[0]
        rv = C.run([vera, "-f", "3b", "--format", "text", pdf], timeout=300)
        txt = (rv.stdout + rv.stderr).strip()
        checks.append(C.check("PDF/A-3b (veraPDF)", txt.split("\n")[0].startswith("PASS"),
                              txt[:1200], "ISO 19005-3"))

    decisive = [c["ok"] for c in checks if c["ok"] is not None]
    conformant = all(decisive) if decisive else None
    C.report(file=pdf, format={"family": "pdf", "subtype": "factur-x"},
             conformant=conformant, checks=checks, tool_versions=tools,
             extra={"note_semantique": "Validation fiscale du XML (Schematron EN16931, "
                    "business terms, réforme FR 2026) → skill isca-nf525-facturation-electronique."})


def cmd_extract(pdf: str, out: str | None) -> int:
    import facturx
    with open(pdf, "rb") as f:
        name, xml = facturx.get_xml_from_pdf(f.read(), check_xsd=False, check_schematron=False)
    if not xml:
        C.fail("Aucun XML de facture trouvé dans le PDF.", code=1)
    if out:
        with open(out, "wb") as f:
            f.write(xml)
        print(json.dumps({"extracted": name, "out": out, "bytes": len(xml)}, ensure_ascii=False))
    else:
        sys.stdout.buffer.write(xml)
    return 0


def cmd_embed(a) -> int:
    import facturx
    with open(a.pdf, "rb") as f:
        pdf_bytes = f.read()
    with open(a.xml, "rb") as f:
        xml_bytes = f.read()
    out_bytes = facturx.generate_from_binary(
        pdf_bytes, xml_bytes,
        flavor=a.flavor, level=a.level,
        check_xsd=not a.no_xsd, check_schematron=False,
        afrelationship=a.afrelationship,
    )
    out = a.out or (os.path.splitext(a.pdf)[0] + ".facturx.pdf")
    with open(out, "wb") as f:
        f.write(out_bytes)
    # Post-validation conteneur
    vera = C.find_tool("verapdf")
    pdfa = None
    if vera:
        rv = C.run([vera, "-f", "3b", "--format", "text", out], timeout=300)
        pdfa = (rv.stdout + rv.stderr).strip().split("\n")[0]
    print(json.dumps({"embedded_pdf": out, "afrelationship": a.afrelationship,
                      "flavor": a.flavor, "level": a.level,
                      "pdfa3b_verapdf": pdfa}, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Conformité conteneur Factur-X / PDF/A-3")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").add_argument("pdf")
    ex = sub.add_parser("extract"); ex.add_argument("pdf"); ex.add_argument("--out")
    em = sub.add_parser("embed"); em.add_argument("pdf"); em.add_argument("xml")
    em.add_argument("--out"); em.add_argument("--flavor", default="autodetect")
    em.add_argument("--level", default="autodetect")
    em.add_argument("--afrelationship", default="data", choices=sorted(VALID_AFR))
    em.add_argument("--no-xsd", action="store_true")
    a = ap.parse_args()

    if a.cmd == "check":
        return cmd_check(a.pdf)
    if a.cmd == "extract":
        return cmd_extract(a.pdf, a.out)
    if a.cmd == "embed":
        return cmd_embed(a)
    return 2


if __name__ == "__main__":
    sys.exit(main())
