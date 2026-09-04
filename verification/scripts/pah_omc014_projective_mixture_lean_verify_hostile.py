#!/usr/bin/env python3
"""Hostile mutation firewall for the PAH-OMC-014 R500 support packet.

All attacks are in-memory.  The unchanged conditional packet must be accepted,
while source-law injection, promotion, hash tampering and hypothesis weakening
must be rejected.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-projective-mixture-lean-manifest.json"
LEAN = ROOT / "verification/lean/Tect/R500.lean"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-projective-mixture-lean/hostile.json"
AUDIT_ID = "PAH-OMC-014-PROJECTIVE-MIXTURE-LEAN-HOSTILE-001"
LEAN_PIN = "2afe710dee80fe6a11ed5a0e97199f396d76fd301618697d6629eb40c740a2c1"
DECLARATIONS = [
    "coarse_weight_nonnegative",
    "coarse_weight_normalized",
    "projective_mixture_identity",
    "projective_mixture_preserves_probability",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", newline="", closefd=True) as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        Path(tmp_name).replace(path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def accepts(packet: dict[str, Any]) -> bool:
    provenance = packet.get("provenance", {})
    status = packet.get("status", {})
    lean = packet.get("lean", {})
    contract = packet.get("theorem_contract", {})
    assumptions = contract.get("assumptions", [])
    missing = contract.get("not_supplied", [])
    nonclaims = packet.get("non_claims", [])
    text = json.dumps(packet, ensure_ascii=True).lower()
    return (
        provenance.get("source_law_present") is False
        and provenance.get("claim_bearing") is False
        and provenance.get("physical_authority") is False
        and provenance.get("model_change") is False
        and provenance.get("parent_mutation") is False
        and status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("classification") == "CONDITIONAL_SUPPORT_ONLY"
        and status.get("active_gate_change") is False
        and status.get("physical_promotion") is False
        and lean.get("sha256") == LEAN_PIN
        and lean.get("declarations") == DECLARATIONS
        and len(assumptions) == 5
        and any("kernel" in item.lower() for item in assumptions)
        and any("row" in item.lower() for item in assumptions)
        and any("push-forward" in item.lower() for item in assumptions)
        and any("weights" in item.lower() for item in assumptions)
        and any("source-owned" in item.lower() for item in missing)
        and any("gibbs" in item.lower() for item in missing)
        and any("cauchy" in item.lower() for item in missing)
        and any("r-484" in item.lower() for item in missing)
        and any("r-488" in item.lower() for item in missing)
        and any("physical pre-a" in item.lower() for item in nonclaims)
        and "no source-owned" in text
        and "does not prove exact projectivity" in text
        and "full-q gibbs state exists" not in text
    )


def main() -> int:
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    before = digest(MANIFEST)
    source_before = digest(LEAN)
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    check("unchanged packet accepted", accepts(original), True, True)
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("inject source law", lambda p: p["provenance"].update(source_law_present=True)),
        ("promote claim bearing", lambda p: p["provenance"].update(claim_bearing=True)),
        ("declare model change", lambda p: p["provenance"].update(model_change=True)),
        ("mutate parent", lambda p: p["provenance"].update(parent_mutation=True)),
        ("promote verdict", lambda p: p["status"].update(verdict="MAINLINE_ADVANCE", classification="CLAIM_BEARING")),
        ("mark physical promotion", lambda p: p["status"].update(physical_promotion=True)),
        ("tamper Lean hash", lambda p: p["lean"].update(sha256="0" * 64)),
        ("drop kernel hypothesis", lambda p: p["theorem_contract"].update(assumptions=p["theorem_contract"]["assumptions"][:-1])),
        ("erase missing source law", lambda p: p["theorem_contract"].update(not_supplied=[x for x in p["theorem_contract"]["not_supplied"] if "source-owned" not in x])),
        ("rewrite conclusion as full-Q proof", lambda p: p["theorem_contract"].update(conclusion="A full-Q Gibbs state exists and is projectively consistent.")),
    ]
    outcomes = {}
    for label, mutate in mutations:
        candidate = copy.deepcopy(original)
        mutate(candidate)
        accepted = accepts(candidate)
        outcomes[label] = accepted
        check(f"rejects {label}", not accepted, accepted, False)

    check("manifest unchanged after attacks", digest(MANIFEST) == before, digest(MANIFEST), before)
    check("Lean source unchanged", digest(LEAN) == source_before == LEAN_PIN, digest(LEAN), source_before)
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", LEAN.read_text(encoding="utf-8"))
    check("source declarations remain exact", all(name in declared for name in DECLARATIONS), declared, DECLARATIONS)
    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-projective-mixture-lean-hostile/1.0",
        "run_kind": "hostile_mutation_firewall",
        "audit_id": AUDIT_ID,
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "result_id": None,
        "exploration_id": None,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "CONDITIONAL_SUPPORT_ONLY",
        "claim_bearing": False,
        "active_gate_change": False,
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "mutation_acceptance": outcomes,
        "source_hashes": {"manifest": before, "R500": source_before},
        "assumptions": ["All mutations are in-memory copies.", "Original source and manifest bytes remain hash-pinned."],
        "missing_assumptions": ["Source-owned cross-Q kernel, component Gibbs push-forward, weight recursion, topology, Cauchy estimate, and stationarity domain."],
        "non_claims": ["No PAH full-Q state, omega, physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap, cosmology, or TOE conclusion follows."],
        "next_question": "Can a source owner provide the exact kernel and component push-forward premises without any rejected mutation?",
    }
    atomic_json(OUTPUT, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; claim_bearing={payload['claim_bearing']}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
