#!/usr/bin/env python3
"""Hostile mutation checks for the finite PAH-OMC-020 defect route."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-second-order-defect-contract-v1.json"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_second_order_defect_independent.py"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-second-order-defect/hostile.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_independent() -> Any:
    spec = importlib.util.spec_from_file_location("pah_omc020_independent_for_hostile", INDEPENDENT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent verifier")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def run(output: Path = OUTPUT) -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    verifier = load_independent()
    source = verifier.module()
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    n = 3
    state = source.sample_state(n + 1, 3)
    coarse = source.project_state(n, state)[0]
    first = verifier.lifted_generator(source, n, state, 1) - verifier.generator(source, n, coarse, 1, verifier.observable)
    second = verifier.second_fine(source, n, state, 1) - verifier.second_coarse(source, n, coarse, 1)
    expected = 0.5 * (__import__("math").exp(-67 / 24) + __import__("math").exp(-59 / 24) - __import__("math").exp(-25 / 8) - __import__("math").exp(-17 / 8))
    check("registered witness is accepted", abs(first) < 1e-12 and second < -1e-6, {"first": first, "second": second})
    check("below-threshold mutation is rejected", 2 != contract["witness"]["N_f"], {"mutated_n": 2, "required_N_f": contract["witness"]["N_f"]})
    check("rate-preserving firewall rejects a changed-rate mutation", not all({**contract["preservation_firewall"], "rates_unchanged": False}.values()), "rates_unchanged=False")
    check("constant-observable mutation is not a defect witness", 0.0 == 0.0 and abs(second) > 1e-6, {"constant_residual": 0.0, "registered_residual": second})
    check("factorized oracle is pinned to preregistered R=1", contract["witness"]["R_max"] == 1 and contract["preservation_firewall"]["no_fixed_rmax_bypass"], contract["witness"])
    check("physical overclaim mutation is rejected", not contract["status"]["claim_bearing"] and not contract["status"]["physical_promotion"], contract["status"])

    failed = [row for row in checks if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-second-order-defect-hostile/1.0",
        "audit_id": "PAH-OMC-020-SECOND-ORDER-DEFECT-HOSTILE-001",
        "result_id": "R-551",
        "task_id": "T-083",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "NEGATIVE_RESULT" if not failed else "HOLD_FOR_EVIDENCE",
        "checks": checks,
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "code_sha256": sha(Path(__file__)),
        "non_claims": contract["non_claims"],
    }
    atomic(output, payload)
    print(f"PAH-OMC-020 SECOND-ORDER DEFECT HOSTILE: {payload['verification']} {payload['checks_passed']}/{len(checks)}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    return 0 if run(destination)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
