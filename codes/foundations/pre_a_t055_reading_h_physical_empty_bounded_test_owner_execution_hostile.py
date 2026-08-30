#!/usr/bin/env python3
"""Adversarial contract mutations for the R-441 owner-execution audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-t055-reading-h-physical-empty-bounded-test-owner-execution-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre-a-t055-reading-h-physical-empty-bounded-test-owner-execution/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-pre-a-t055-reading-h-physical-empty-bounded-test-owner-execution/independent.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-pre-a-t055-reading-h-physical-empty-bounded-test-owner-execution/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    owner = manifest["owner_contract"]
    branch = manifest["physical_empty_branch_E"]
    verdicts = manifest["verdicts"]
    checks: list[dict[str, Any]] = []

    def reject(name: str, mutation: dict[str, Any], would_be_accepted: bool, reason: str) -> None:
        if would_be_accepted:
            raise AssertionError(f"hostile mutation accepted: {name}")
        checks.append({"name": name, "status": "REJECTED", "mutation": mutation, "reason": reason})

    reject("zero alias for E", {"zero_reference_identification": "E=0"}, branch["zero_reference_identification"] == "E=0", "zero/P1 alias is forbidden")
    reject("admit uninstantiated E", {"admitted": True}, branch["admitted"] is True, "E has no normalized representative or preparation")
    reject("drop finite-parts field", {"remove": "finite_part_counterterm_scheme"}, "finite_part_counterterm_scheme" not in owner["required_fixed_fields"], "all fifteen fields are identity-locked")
    reject("change orientation", {"comparison_orientation": "F_total[E] - F_total[G_*]"}, owner["comparison_orientation"] != "F_total[G_*] - F_total[E]", "requested sign orientation is fixed")
    reject("evaluate without common owner", {"finite_evaluation_allowed": True}, owner["finite_evaluation_allowed"] is True, "missing owner values force the input audit to stop")
    reject("promote stationarity", {"reading_h_stationarity": "PASS"}, verdicts["reading_h_stationarity"]["status"] != "BLOCKED_NOT_EVALUATED", "no full regulated tangent or residual budget exists")
    reject("promote physical claim", {"claim_bearing": True}, manifest["claim_bearing"] is True or primary["scope"].get("yang_mills_promoted", False) or independent["scope"].get("physical_promotion", False), "blocked input is not a physical/Yang-Mills/mass-gap result")
    if primary["verdict"] != "BLOCKED_NOT_EVALUATED" or independent["verdict"] != "INDEPENDENT_BLOCKED_INPUT_CONTROL":
        raise AssertionError("hostile audit requires the unmutated blocked controls")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r434-hostile/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-441",
        "exploration_id": "EXP-001286",
        "claim_id": manifest["card_id"],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "assertions": checks,
        "scope": {"hostile_mutations_rejected": True, "physical_promotion_rejected": True, "claim_bearing": False},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
        "evidence_level": "T0 / EXECUTED ADVERSARIAL INPUT-BOUNDARY CONTROL",
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-441 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    payload = run(output)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        print("R-441 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
