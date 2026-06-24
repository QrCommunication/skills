#!/usr/bin/env python3
"""opc_modify.py — lecture / modification d'une part dans un conteneur OOXML ou ODF.

Le conteneur (ZIP/OPC pour OOXML, ZIP pour ODF) est reconstruit en préservant :
  - l'ordre des entrées et leur mode de compression d'origine ;
  - pour ODF : la règle ISO 26300-3 §3.3 (mimetype = 1ère entrée, STORED, en clair).
La nouvelle valeur d'une part XML est refusée si elle n'est pas well-formed
(lxml) → impossible de produire un conteneur cassé « à la volée ».

Sous-commandes :
  list <fichier>
  get  <fichier> <partname>                       (dump la part sur stdout)
  set  <fichier> <partname> <contenu> [--out OUT]  (remplace, repackage, revalide)
"""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

import _common as C

C.reexec_in_venv()
C.harden_path()


def _wellformed(data: bytes) -> tuple[bool, str]:
    from lxml import etree
    try:
        etree.fromstring(data)
        return True, "well-formed"
    except etree.XMLSyntaxError as e:
        return False, str(e)


def cmd_list(path: str) -> None:
    with zipfile.ZipFile(path) as z:
        parts = [{"name": i.filename, "size": i.file_size,
                  "compress": "stored" if i.compress_type == zipfile.ZIP_STORED else "deflated"}
                 for i in z.infolist()]
    print(json.dumps({"file": path, "parts": parts}, indent=2, ensure_ascii=False))


def cmd_get(path: str, part: str) -> None:
    with zipfile.ZipFile(path) as z:
        if part not in z.namelist():
            C.fail(f"Part absente : {part}")
        sys.stdout.buffer.write(z.read(part))


def cmd_set(path: str, part: str, content_file: str, out: str | None) -> None:
    fmt = C.detect_format(path)
    new_data = Path(content_file).read_bytes()
    # Refuser une part XML non well-formed (garantie de conformité)
    if part.endswith(".xml") or part.endswith(".rels"):
        wf, det = _wellformed(new_data)
        if not wf:
            C.fail(f"Nouveau contenu non well-formed, modification refusée : {det}", code=1)

    out = out or path
    with zipfile.ZipFile(path) as z:
        if part not in z.namelist():
            C.fail(f"Part absente : {part}")
        entries = [(i, z.read(i.filename)) for i in z.infolist()]

    # ODF : garantir mimetype en 1ère position + STORED
    if fmt["family"] == "odf":
        entries.sort(key=lambda t: 0 if t[0].filename == "mimetype" else 1)

    tmp = out + ".tmp"
    with zipfile.ZipFile(tmp, "w") as zout:
        for info, data in entries:
            if info.filename == part:
                data = new_data
            ct = info.compress_type
            if info.filename == "mimetype":  # ODF : toujours STORED
                ct = zipfile.ZIP_STORED
            zout.writestr(_clone_info(info), data, compress_type=ct)
    shutil.move(tmp, out)

    # Post-validation : déléguer au validateur de conformité
    post = _revalidate(out, fmt)
    print(json.dumps({"operation": "set", "part": part, "outfile": out,
                      "format": fmt, "post_validation": post}, indent=2, ensure_ascii=False))
    sys.exit(0 if post.get("conformant") else 1)


def _clone_info(info: zipfile.ZipInfo) -> zipfile.ZipInfo:
    ni = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
    ni.compress_type = info.compress_type
    ni.external_attr = info.external_attr
    ni.internal_attr = info.internal_attr
    ni.create_system = info.create_system
    return ni


def _revalidate(out: str, fmt: dict) -> dict:
    """Relance scripts/validate.py et renvoie un résumé du rapport."""
    validator = str(C.SKILL_ROOT / "scripts" / "validate.py")
    r = C.run([sys.executable, validator, out])
    try:
        rep = json.loads(r.stdout)
        return {"conformant": rep.get("conformant"),
                "failed_checks": [c["check"] for c in rep.get("checks", []) if c["ok"] is False]}
    except json.JSONDecodeError:
        return {"conformant": None, "raw": (r.stdout + r.stderr)[:400]}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Lecture/modification de parts OOXML/ODF")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").add_argument("file")
    g = sub.add_parser("get"); g.add_argument("file"); g.add_argument("part")
    s = sub.add_parser("set"); s.add_argument("file"); s.add_argument("part")
    s.add_argument("content"); s.add_argument("--out")
    a = ap.parse_args()

    fmt = C.detect_format(a.file)
    if fmt["family"] not in ("ooxml", "odf"):
        C.fail(f"opc_modify n'accepte que OOXML/ODF (reçu {fmt}). Pour le PDF voir pdf_modify.py.")

    if a.cmd == "list":
        cmd_list(a.file)
    elif a.cmd == "get":
        cmd_get(a.file, a.part)
    elif a.cmd == "set":
        cmd_set(a.file, a.part, a.content, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
