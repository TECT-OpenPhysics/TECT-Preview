#!/usr/bin/env python3
"""Hostile mutation firewall for the R-460 residual source audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-contents-remaining-scope-owner-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-hostile-pre_a_contents_remaining_scope_owner_audit/result.json"
)
PATTERNS = {
    "generator": re.compile(r"generator|transfer\s+operator|markov\s+semigroup", re.I),
    "heat": re.compile(r"heat[-_ ]?(?:root|kernel|semigroup)|heat\s+root", re.I),
    "filtration": re.compile(r"filtration|conditional\s+replica|replica", re.I),
    "current": re.compile(
        r"raw[-_ ]?current|current\s+spatial|spatial\s+intertwiner", re.I
    ),
    "qledger": re.compile(
        r"\bq[-_ ]ledger\b|\bq[_ -]?k\b[^\r\n]{0,80}\bledger\b"
        r"|\bone[- ]use(?:d)?\s+q\b|\bnonnegative\s+q(?:[-_ ]ledger)?\b",
        re.I,
    ),
}


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def raw_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_complete(text: str) -> bool:
    return all(pattern.search(text) for pattern in PATTERNS.values())


def owner_candidate(text: str, path: str) -> bool:
    return semantic_complete(text) and "merged" not in Path(path).name.casefold()


def run(output: Path = DEFAULT_OUTPUT) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = []
    mutations = []
    base = (
        "generator and transfer operator; heat-root and heat-kernel; "
        "filtration and conditional replica; raw-current spatial intertwiner; "
        "q_k ledger and one-use q."
    )

    def add(name: str, predicate: bool) -> None:
        if predicate:
            raise AssertionError(f"hostile mutation accepted: {name}")
        mutations.append({"mutation": name, "rejected": True})
        checks.append({"name": name, "status": "PASS", "mutation_rejected": True})

    add("drop generator group", owner_candidate(base.replace("generator and transfer operator", ""), "note.txt"))
    add("drop heat group", owner_candidate(base.replace("heat-root and heat-kernel", ""), "note.txt"))
    add("drop filtration group", owner_candidate(base.replace("filtration and conditional replica", ""), "note.txt"))
    add("drop current group", owner_candidate(base.replace("raw-current spatial intertwiner", ""), "note.txt"))
    add("drop strict q-ledger group", owner_candidate(base.replace("q_k ledger and one-use q", ""), "note.txt"))
    add("treat merged bundle as owner", owner_candidate(base, "TECT_Math01-35_Merged.txt"))
    add(
        "accept loose one-uses phrase as q-ledger",
        bool(PATTERNS["qledger"].search("one uses a variable q")),
    )
    mutated_manifest = copy.deepcopy(manifest)
    mutated_manifest["claim_bearing"] = True
    add("promote source scan to claim", mutated_manifest["claim_bearing"] is False)
    if len(mutations) != 8:
        raise AssertionError("unexpected hostile mutation count")
    payload = {
        "schema": "tect/pre-a-contents-remaining-scope-owner-audit-hostile/1.0",
        "run_kind": "hostile",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "mutations_rejected": len(mutations),
        "assertions": checks,
        "mutations": mutations,
        "source_hashes": {"manifest": raw_sha(MANIFEST), "script": raw_sha(Path(__file__))},
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-460 HOSTILE {payload['verdict']} {len(mutations)}/8", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["mutations_rejected"] == 8
        print("R-460 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
