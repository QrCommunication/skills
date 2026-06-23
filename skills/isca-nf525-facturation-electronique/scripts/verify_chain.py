#!/usr/bin/env python3
"""
verify_chain.py — Vérificateur d'intégrité d'un chaînage de hachage inaltérable.

Mécanisme cœur de la condition « Inaltérabilité / Sécurisation » d'ISCA
(art. 286-I-3°bis CGI, NF525) : chaque enregistrement porte une signature
calculée à partir de SES données + la signature de l'enregistrement précédent :

    signature_n = H( canonical(données_n) || signature_{n-1} )

Toute donnée altérée, écriture supprimée ou réordonnée casse la chaîne → c'est
détectable. Cet outil rejoue la chaîne et signale la 1re rupture.

ENTRÉE : un fichier JSON = liste d'objets. Chaque objet contient ses champs
métier + un champ signature stockée (par défaut "signature"). Optionnellement
un champ de signature précédente (par défaut "previous_signature") qui, s'il
est présent, est aussi recoupé.

Le schéma exact de chaînage varie selon les éditeurs. Adapter via les options
(--algo, --seed, --sig-field, --prev-field, --data-fields, --join) pour coller
à l'implémentation auditée AVANT de conclure.

USAGE :
    python3 verify_chain.py registres.json
    python3 verify_chain.py registres.json --algo sha256 --seed ""
    python3 verify_chain.py registres.json --data-fields montant,date,ticket

CODE DE SORTIE : 0 = chaîne intègre · 1 = rupture détectée · 2 = erreur d'entrée
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys


def canonical(data: dict, sig_field: str, prev_field: str,
              data_fields: list[str] | None) -> str:
    """Sérialisation déterministe des données métier (hors champs de signature).

    La normalisation déterministe est CRITIQUE : sans format canonique stable,
    le rejeu échoue à tort (faux positifs). Ici : tri des clés, séparateurs
    fixes, UTF-8 préservé.
    """
    if data_fields is not None:
        payload = {k: data.get(k) for k in data_fields}
    else:
        payload = {k: v for k, v in data.items()
                   if k not in (sig_field, prev_field)}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def compute_signature(data: dict, prev_sig: str, algo: str, sig_field: str,
                      prev_field: str, data_fields: list[str] | None,
                      join: str) -> str:
    raw = canonical(data, sig_field, prev_field, data_fields) + join + prev_sig
    h = hashlib.new(algo)
    h.update(raw.encode("utf-8"))
    return h.hexdigest()


def verify(records: list[dict], algo: str, seed: str, sig_field: str,
           prev_field: str, data_fields: list[str] | None,
           join: str) -> list[dict]:
    """Rejoue la chaîne. Retourne un rapport par enregistrement."""
    report = []
    prev_sig = seed
    for i, rec in enumerate(records):
        stored = rec.get(sig_field)
        expected = compute_signature(rec, prev_sig, algo, sig_field,
                                     prev_field, data_fields, join)
        sig_ok = (stored == expected)

        # Recoupement optionnel de la signature précédente déclarée.
        prev_ok = True
        if prev_field in rec:
            prev_ok = (rec.get(prev_field) == prev_sig)

        report.append({
            "index": i,
            "stored": stored,
            "expected": expected,
            "signature_ok": sig_ok,
            "previous_link_ok": prev_ok,
            "ok": sig_ok and prev_ok,
        })
        # On chaîne sur la signature STOCKÉE (reflète l'état réel du système).
        prev_sig = stored if stored is not None else expected
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Vérifie un chaînage de hachage inaltérable (ISCA/NF525).")
    p.add_argument("file", help="Fichier JSON : liste d'enregistrements.")
    p.add_argument("--algo", default="sha256", help="Algorithme de hachage (défaut: sha256).")
    p.add_argument("--seed", default="", help="Signature initiale (previous du 1er enregistrement).")
    p.add_argument("--sig-field", default="signature", help="Nom du champ signature stockée.")
    p.add_argument("--prev-field", default="previous_signature", help="Nom du champ signature précédente (optionnel).")
    p.add_argument("--data-fields", default=None,
                   help="Liste de champs métier à hacher, séparés par des virgules. "
                        "Si absent : tous les champs sauf signature/previous.")
    p.add_argument("--join", default="",
                   help="Chaîne de jonction entre données et signature précédente (défaut: '').")
    p.add_argument("--quiet", action="store_true", help="N'afficher que le verdict final.")
    args = p.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            records = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERREUR lecture/JSON : {e}", file=sys.stderr)
        return 2

    if not isinstance(records, list):
        print("ERREUR : le JSON doit être une LISTE d'enregistrements.", file=sys.stderr)
        return 2

    try:
        hashlib.new(args.algo)
    except ValueError:
        print(f"ERREUR : algorithme inconnu '{args.algo}'.", file=sys.stderr)
        return 2

    data_fields = args.data_fields.split(",") if args.data_fields else None
    report = verify(records, args.algo, args.seed, args.sig_field,
                    args.prev_field, data_fields, args.join)

    first_break = next((r["index"] for r in report if not r["ok"]), None)

    if not args.quiet:
        for r in report:
            if r["ok"]:
                print(f"  [{r['index']:>5}] OK")
            else:
                flag = []
                if not r["signature_ok"]:
                    flag.append("SIGNATURE INVALIDE")
                if not r["previous_link_ok"]:
                    flag.append("LIEN PRÉCÉDENT ROMPU")
                print(f"  [{r['index']:>5}] RUPTURE — {', '.join(flag)}")
                print(f"           stockée  = {r['stored']}")
                print(f"           attendue = {r['expected']}")

    total = len(report)
    broken = sum(1 for r in report if not r["ok"])
    print("-" * 60)
    if first_break is None:
        print(f"✅ CHAÎNE INTÈGRE — {total} enregistrement(s), 0 rupture.")
        return 0
    print(f"🔴 CHAÎNE COMPROMISE — {broken}/{total} rupture(s). "
          f"Première rupture à l'index {first_break}.")
    print("   → Inaltérabilité NON garantie : une falsification existe ou le "
          "schéma de chaînage configuré ne correspond pas à l'implémentation.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
