#!/usr/bin/env python3
"""Primary structural audit for the R338 finite QFT algebra cross-check."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-lean-finite-algebra"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R338.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
MARKERS = [
    "finite_trace_cyclicity",
    "finite_thermal_four_cycle",
    "finite_os_gram_real_possemidef",
    "finite_transfer_scope",
]


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    source = LEAN.read_text(encoding="utf-8")
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001177" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001177/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and manifest["scope"]["pre_a_closed"] is False, [manifest["claim_bearing"], manifest["scope"]["pre_a_closed"]], "nonbearing/open", "scope")
    check("source language", not re.search(r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]", source), True, "no Hangul", "source")
    check("forbidden tokens", not any(re.search(rf"\b{re.escape(token)}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), True, "none", "source")
    declarations = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check("theorem markers", all(marker in declarations for marker in MARKERS), declarations, MARKERS, "source")
    entry = next((item for item in registry["entrypoints"] if item["path"] == "verification/lean/Tect/R338.lean"), None)
    check("registry entry", entry is not None, entry["path"] if entry else None, "verification/lean/Tect/R338.lean", "registry")
    actual_hash = normalized_sha256(LEAN)
    check("registry hash", entry is not None and entry["sha256"] == actual_hash, entry["sha256"] if entry else None, actual_hash, "registry")
    check("registry declarations", entry is not None and entry.get("declarations") == MARKERS, entry.get("declarations") if entry else None, MARKERS, "registry")
    check("scope firewall", all(not manifest["scope"][field] for field in ("common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), {field: manifest["scope"][field] for field in ("common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")}, "all downstream QFT gates open", "scope")
    formal = {
        "trace_cyclicity": "finite_trace_cyclicity",
        "thermal_four_cycle": "finite_thermal_four_cycle",
        "real_gram_possemidef": "finite_os_gram_real_possemidef",
        "scope_fixture": "finite_transfer_scope",
    }
    check("formal identity set", set(formal.values()) == set(MARKERS), formal, MARKERS, "formal")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LEAN-FINITE-ALGEBRA",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "formal_checks": formal,
        "source_sha256": actual_hash,
        "scope": manifest["scope"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY LEAN-FINITE-ALGEBRA PASS {payload['passed']}/{payload['assertion_count']} markers={len(payload['formal_checks'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
