#!/usr/bin/env python3
"""doctor.py — diagnostic des validateurs requis par le skill.

Affiche l'état de chaque dépendance (venv python + CLI) et le quoi-faire si
manquant. Code retour 0 si tout l'essentiel est présent, 1 sinon.
"""
from __future__ import annotations

import importlib
import sys

import _common as C

C.reexec_in_venv()


def main() -> int:
    print("=== document-format-conformance · doctor ===")
    essential_ok = True

    print("\n[venv python]")
    py_mods = {
        "pikepdf": True, "pypdf": True, "facturx": False,
        "docx": False, "pptx": False, "openpyxl": False, "lxml": True,
    }
    for mod, essential in py_mods.items():
        try:
            m = importlib.import_module(mod)
            print(f"  ✓ {mod:10s} {getattr(m, '__version__', '?')}")
        except Exception:  # noqa: BLE001
            mark = "✗" if essential else "·"
            print(f"  {mark} {mod:10s} ABSENT" + ("  (essentiel)" if essential else "  (optionnel)"))
            if essential:
                essential_ok = False

    print("\n[CLI externes]")
    cli = {"qpdf": True, "xmllint": True, "verapdf": False}
    for tool, essential in cli.items():
        path = C.find_tool(tool)
        if path:
            print(f"  ✓ {tool:10s} {path}")
        else:
            mark = "✗" if essential else "·"
            print(f"  {mark} {tool:10s} ABSENT" + ("  (essentiel)" if essential else "  (PDF/A & Factur-X)"))
            if essential:
                essential_ok = False

    if not essential_ok:
        print(f"\n→ {C.SETUP_HINT}")
        return 1
    print("\n✓ Tous les validateurs essentiels sont présents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
