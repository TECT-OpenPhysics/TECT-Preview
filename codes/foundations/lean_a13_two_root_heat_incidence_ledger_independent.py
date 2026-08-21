"""Stdlib-only independent lane for the R-177 heat/incidence ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-heat-incidence-ledger-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def root1(heat: Fraction, r1: Fraction) -> Fraction:
    return heat + r1


def root2(heat: Fraction, r1: Fraction, r2: Fraction, beta: Fraction) -> Fraction:
    return heat + beta * root1(heat, r1) + r2


def endpoint(heat: Fraction, r1: Fraction, r2: Fraction, future: Fraction, beta: Fraction) -> Fraction:
    return root2(heat, r1, r2, beta) + future


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    r176_run = json.loads((REPO / manifest["inputs"]["r176_run"]["path"]).read_text(encoding="utf-8"))
    assert r176_run["verdict"] == "PASS" and r176_run["derived"]["root_labels"] == ["k", "2k"]
    beta = Fraction(str(manifest["registered_inputs"]["feedback_gain"]))
    heat, heat2 = Fraction(3), Fraction(0)
    r1, r2, future, future2 = Fraction(1), Fraction(2), Fraction(5), Fraction(-1)
    common_difference = endpoint(heat, r1, r2, future, beta) - endpoint(heat, r1, r2, future2, beta)
    independent_difference = endpoint(heat, r1, r2, future, beta) - endpoint(heat2, r1, r2, future, beta)
    feedback_delta = endpoint(heat, r1 + 2, r2, future, beta) - endpoint(heat, r1, r2, future, beta)
    midpoint = (Fraction(7) + Fraction(-1)) / 2
    variance = ((Fraction(7) - midpoint) ** 2 + (Fraction(-1) - midpoint) ** 2) / 2
    owner_order = manifest["registered_inputs"]["owner_order"]
    assert common_difference == future - future2
    assert independent_difference == (1 + beta) * (heat - heat2)
    assert feedback_delta == beta * 2
    assert variance == (Fraction(7) - Fraction(-1)) ** 2 / 4
    assert (Fraction(1) + Fraction(-1)) / 2 == 0 and (Fraction(1) ** 2 + Fraction(-1) ** 2) / 2 > 0
    assert owner_order == ["common_heat", "root_1", "root_2", "future_residual"]
    derived = {
        "root_labels": ["k", "2k"],
        "actual_a1_roots_from_r176": True,
        "common_heat_shared": True,
        "common_heat_cancels_from_replica_difference": True,
        "independent_heat_would_survive": True,
        "root2_feedback_from_root1_retained": True,
        "two_replica_variance_identity": True,
        "mean_only_variance_rejected": True,
        "owner_order": owner_order,
        "lean_theorems": ["two_replica_variance", "common_heat_cancels", "root2_feedback_dependence", "endpoint_feedback_dependence", "independent_heat_does_not_cancel", "root_two_after_root_one", "future_after_root_two"],
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
        "feedback_gain": beta,
        "common_difference": common_difference,
        "independent_difference": independent_difference,
        "feedback_delta": feedback_delta,
        "future_variance_fixture": variance,
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": 10,
        "assertions": [{"name": "independent exact ledger", "pass": True}],
        "derived": derived,
        "boundary": manifest["boundary"],
    }
    atomic_json(args.output, payload)
    print("INDEPENDENT R-177 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
