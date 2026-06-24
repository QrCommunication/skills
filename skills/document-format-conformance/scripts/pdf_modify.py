#!/usr/bin/env python3
"""pdf_modify.py — modification de PDF en restant conforme ISO 32000.

Toutes les opérations passent par pikepdf (moteur libqpdf, xref/trailer toujours
reconstruits valides) ou par l'incremental update de pypdf (append d'une révision
sans toucher aux octets existants → préserve les signatures). Après écriture, le
fichier de sortie est revalidé par `qpdf --check` et le verdict est inclus.

Sous-commandes :
  set-meta <in> <out> [--title T] [--author A] [--subject S] [--incremental]
  attach   <in> <out> <fichier> [--relationship Data] [--description D]
  repair   <in> <out>
  decrypt  <in> <out> [--password P]

--incremental (set-meta) : append une révision (préserve octets+signatures).
Sinon : réécriture propre complète (linéarisable, nettoyée).
"""
from __future__ import annotations

import argparse
import json
import sys

import _common as C

C.reexec_in_venv()
C.harden_path()

VALID_AFR = {"Source", "Data", "Alternative", "Supplement", "EncryptedPayload", "FormData", "Schema", "Unspecified"}


def _postcheck(out: str) -> dict:
    qpdf = C.find_tool("qpdf")
    if not qpdf:
        return {"check": "qpdf post-validation", "ok": None, "detail": "qpdf absent"}
    r = C.run([qpdf, "--check", out])
    full = (r.stdout + r.stderr).strip()
    ok, summary = C.qpdf_verdict(r.returncode, full)
    return {"check": "qpdf post-validation", "ok": ok, "detail": f"{summary} | {full[:500]}"}


def set_meta(a) -> dict:
    if a.incremental:
        from pypdf import PdfWriter
        w = PdfWriter(a.infile, incremental=True)
        meta = {}
        if a.title:   meta["/Title"] = a.title
        if a.author:  meta["/Author"] = a.author
        if a.subject: meta["/Subject"] = a.subject
        if meta:
            w.add_metadata(meta)
        with open(a.outfile, "wb") as fh:
            w.write(fh)
        return {"mode": "incremental (pypdf, octets préservés)", "set": meta}
    import pikepdf
    with pikepdf.open(a.infile) as pdf:
        with pdf.open_metadata(set_pikepdf_as_editor=False) as m:
            if a.title:   m["dc:title"] = a.title
            if a.author:  m["dc:creator"] = [a.author]
            if a.subject: m["dc:description"] = a.subject
        if a.title:   pdf.docinfo["/Title"] = a.title
        if a.author:  pdf.docinfo["/Author"] = a.author
        if a.subject: pdf.docinfo["/Subject"] = a.subject
        pdf.save(a.outfile)
    return {"mode": "réécriture pikepdf (docinfo + XMP)",
            "set": {k: v for k, v in (("title", a.title), ("author", a.author), ("subject", a.subject)) if v}}


def attach(a) -> dict:
    import pikepdf
    if a.relationship not in VALID_AFR:
        C.fail(f"--relationship doit être l'un de {sorted(VALID_AFR)} (ISO 32000-2 §7.11.3)")
    with pikepdf.open(a.infile) as pdf:
        spec = pikepdf.AttachedFileSpec.from_filepath(pdf, a.embed, description=a.description or "")
        # relationship = type d'association requis pour PDF/A-3 & Factur-X
        try:
            spec.relationship = pikepdf.Name("/" + a.relationship)
        except Exception:  # noqa: BLE001
            pass
        import os
        pdf.attachments[os.path.basename(a.embed)] = spec
        pdf.save(a.outfile)
    return {"embedded": a.embed, "AFRelationship": a.relationship,
            "note": "Pour Factur-X, viser un PDF/A-3 et utiliser scripts/facturx_tool.py qui pose XMP+AFRelationship complet."}


def repair(a) -> dict:
    qpdf = C.require_tool("qpdf")
    r = C.run([qpdf, a.infile, a.outfile])  # reconstruction xref/objets
    if r.returncode not in (0, 3):
        C.fail("qpdf repair a échoué : " + (r.stdout + r.stderr)[:500])
    return {"mode": "qpdf reconstruction", "warnings": (r.stdout + r.stderr).strip()[:400]}


def decrypt(a) -> dict:
    import pikepdf
    with pikepdf.open(a.infile, password=a.password or "") as pdf:
        pdf.save(a.outfile)
    return {"mode": "déchiffrement pikepdf"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Modification PDF conforme ISO 32000")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sm = sub.add_parser("set-meta"); sm.add_argument("infile"); sm.add_argument("outfile")
    sm.add_argument("--title"); sm.add_argument("--author"); sm.add_argument("--subject")
    sm.add_argument("--incremental", action="store_true")
    sm.set_defaults(fn=set_meta)

    at = sub.add_parser("attach"); at.add_argument("infile"); at.add_argument("outfile")
    at.add_argument("embed"); at.add_argument("--relationship", default="Data")
    at.add_argument("--description"); at.set_defaults(fn=attach)

    rp = sub.add_parser("repair"); rp.add_argument("infile"); rp.add_argument("outfile"); rp.set_defaults(fn=repair)
    dc = sub.add_parser("decrypt"); dc.add_argument("infile"); dc.add_argument("outfile")
    dc.add_argument("--password"); dc.set_defaults(fn=decrypt)

    a = ap.parse_args()
    fmt = C.detect_format(a.infile)
    if fmt["family"] != "pdf":
        C.fail(f"pdf_modify n'accepte que des PDF (reçu {fmt}). Pour OOXML/ODF voir opc_modify.py.")
    result = a.fn(a)
    post = _postcheck(a.outfile)
    print(json.dumps({"operation": a.cmd, "outfile": a.outfile, "result": result,
                      "post_validation": post}, indent=2, ensure_ascii=False))
    return 0 if post["ok"] in (True, None) else 1


if __name__ == "__main__":
    sys.exit(main())
