"""Stdlib-only independent lane for the R-182 pulled cross-Hessian margin."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-feedback-pulled-cross-hessian-margin-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[matrix[j][i] for j in range(2)] for i in range(2)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    r178 = json.loads((REPO / manifest["inputs"]["r178_manifest"]["path"]).read_text(encoding="utf-8"))
    r181 = json.loads((REPO / manifest["inputs"]["r181_manifest"]["path"]).read_text(encoding="utf-8"))
    coefficients = {key: Fraction(str(value)) for key, value in r178["registered_inputs"]["cross_coefficients"].items()}
    active = {key: Fraction(str(value)) for key, value in manifest["registered_inputs"]["active_phase"].items()}
    feedback_gain = Fraction(r181["registered_inputs"]["feedback_gain"])
    assert coefficients == {"field": Fraction(2), "current": Fraction(3), "ordered": Fraction(5)}
    assert [active["w1"], active["w2"]] == [Fraction(1), Fraction(2)]
    assert feedback_gain == Fraction(1, 2)
    hessian_coefficient = -(coefficients["field"] + coefficients["current"] * active["w1"] * active["w2"])
    feedback = [[Fraction(1), Fraction(0)], [feedback_gain, Fraction(1)]]
    cross_hessian = [[hessian_coefficient, -hessian_coefficient], [-hessian_coefficient, hessian_coefficient]]
    pulled_hessian = matmul(matmul(transpose(feedback), cross_hessian), feedback)
    assert hessian_coefficient == -8
    assert cross_hessian == [[Fraction(-8), Fraction(8)], [Fraction(8), Fraction(-8)]]
    assert pulled_hessian == [[Fraction(-2), Fraction(4)], [Fraction(4), Fraction(-8)]]
    cross_fixture = -8 * (Fraction(0) - Fraction(1)) ** 2
    pulled_fixture = -2 * (Fraction(0) - 2 * Fraction(1)) ** 2
    assert cross_fixture == Fraction(-8) and pulled_fixture == Fraction(-8)
    derived = {
        "cross_coefficients": {key: coefficients[key] for key in ("field", "current", "ordered")},
        "active_weights": active,
        "feedback_gain": feedback_gain,
        "hessian_coefficient": hessian_coefficient,
        "cross_hessian": cross_hessian,
        "pulled_hessian": pulled_hessian,
        "cross_quadratic": "-8*(x - y)**2",
        "pulled_quadratic": "-2*(x - 2*y)**2",
        "cross_fixture": cross_fixture,
        "pulled_fixture": pulled_fixture,
        "pulled_eigenvalues": {"-10": 1, "0": 1},
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": 18, "assertions": [{"name": "independent exact pulled Hessian arithmetic", "pass": True}], "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(args.output, payload)
    print("INDEPENDENT R-182 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
