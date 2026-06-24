#!/usr/bin/env python3
"""inspect_doc.py — dump structurel d'un document (PDF / OOXML / ODF) en JSON.

Lecture seule. S'appuie sur pikepdf (PDF) et zipfile/lxml (conteneurs OPC/ODF).
Étape 1 de tout audit : comprendre la structure réelle avant de valider/modifier.

Usage : python inspect_doc.py <fichier>
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import _common as C

C.reexec_in_venv()
C.harden_path()


def inspect_pdf(path: str) -> dict:
    import pikepdf

    raw = Path(path).read_bytes()
    info: dict = {
        "pdf_version": raw[5:8].decode("latin1", "ignore"),
        "size_bytes": len(raw),
        "eof_markers": raw.count(b"%%EOF"),  # >1 ⇒ mises à jour incrémentales
        "incremental_updates": max(0, raw.count(b"%%EOF") - 1),
        "linearized": raw[:2048].find(b"/Linearized") != -1,
    }
    pdf = pikepdf.open(path)
    try:
        info.update(
            pages=len(pdf.pages),
            encrypted=pdf.is_encrypted,
            has_acroform="/AcroForm" in pdf.Root,
            has_xmp_metadata="/Metadata" in pdf.Root,
        )
        names = pdf.Root.get("/Names")
        embedded = []
        if names is not None and "/EmbeddedFiles" in names:
            arr = names["/EmbeddedFiles"].get("/Names", [])
            for i in range(0, len(arr) - 1, 2):
                spec = arr[i + 1]
                embedded.append({
                    "name": str(arr[i]),
                    "AFRelationship": str(spec.get("/AFRelationship", "")) or None,
                })
        info["embedded_files"] = embedded
    finally:
        pdf.close()
    return info


def inspect_opc(path: str, fmt: dict) -> dict:
    from lxml import etree

    info: dict = {"parts": [], "content_types": [], "rels_files": 0}
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        for zi in infos:
            info["parts"].append({
                "name": zi.filename,
                "size": zi.file_size,
                "compress": "stored" if zi.compress_type == zipfile.ZIP_STORED else "deflated",
            })
        names = set(z.namelist())
        if "[Content_Types].xml" in names:
            try:
                root = etree.fromstring(z.read("[Content_Types].xml"))
                ns = {"ct": "http://schemas.openxmlformats.org/package/2006/content-types"}
                info["content_types"] = [
                    {"part": el.get("PartName"), "type": el.get("ContentType")}
                    for el in root.findall("ct:Override", ns)
                ]
            except etree.XMLSyntaxError as e:
                info["content_types_error"] = str(e)
        if fmt["family"] == "odf":
            first = infos[0] if infos else None
            info["mimetype"] = fmt.get("mimetype")
            info["mimetype_first_entry"] = bool(first and first.filename == "mimetype")
            info["mimetype_stored"] = bool(first and first.compress_type == zipfile.ZIP_STORED)
        info["rels_files"] = sum(1 for n in names if n.endswith(".rels"))
    return info


def main() -> int:
    if len(sys.argv) != 2:
        C.fail("Usage: python inspect_doc.py <fichier>")
    path = sys.argv[1]
    fmt = C.detect_format(path)
    if fmt["family"] == "pdf":
        details = inspect_pdf(path)
    elif fmt["family"] in ("ooxml", "odf"):
        details = inspect_opc(path, fmt)
    else:
        C.fail(f"Format non supporté pour inspect : {fmt}")
    print(json.dumps({"file": path, "format": fmt, "structure": details}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
