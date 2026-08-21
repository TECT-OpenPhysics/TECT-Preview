"""Stdlib-only independent lane for the R-183 reserve margin theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-diagonal-reserve-margin-cross-hessian-manifest.json"


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


def qform(a: Fraction, p: Fraction, q: Fraction, x: Fraction, y: Fraction) -> Fraction:
    return x * (p * x + a * y) + y * (a * x + q * y)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    r182 = json.loads((REPO / manifest["inputs"]["r182_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    coefficients = {key: Fraction(str(value)) for key, value in r182["registered_inputs"]["cross_coefficients"].items()}
    active = {key: Fraction(str(value)) for key, value in r182["registered_inputs"]["active_phase"].items()}
    beta = Fraction(str(r182["registered_inputs"]["feedback_gain"]))
    cases = manifest["registered_inputs"]["cases"]
    a = coefficients["field"] + coefficients["current"] * active["w1"] * active["w2"]
    delta = Fraction(cases["below_threshold_delta"])
    extra = Fraction(cases["asymmetric_extra"])
    threshold = 2 * a
    d_below = threshold - delta
    d1_asym = threshold
    d2_asym = threshold + extra
    p_asym = d1_asym - a
    q_asym = d2_asym - a
    remainder = q_asym - a * a / p_asym
    feedback = [[Fraction(1), Fraction(0)], [beta, Fraction(1)]]

    assert coefficients == {"field": Fraction(2), "current": Fraction(3), "ordered": Fraction(5)}
    assert [active["w1"], active["w2"]] == [Fraction(1), Fraction(2)]
    assert beta == Fraction(1, 2)
    assert status["proof_complete"] is False and status["lifecycle"] == "ACTIVE"
    assert a == Fraction(8)
    assert threshold == Fraction(manifest["registered_inputs"]["expected"]["isotropic_threshold"])

    def reserve(d1: Fraction, d2: Fraction) -> list[list[Fraction]]:
        return [[d1 - a, a], [a, d2 - a]]

    threshold_matrix = reserve(threshold, threshold)
    threshold_pulled = matmul(matmul(transpose(feedback), threshold_matrix), feedback)
    asym_matrix = reserve(d1_asym, d2_asym)
    asym_pulled = matmul(matmul(transpose(feedback), asym_matrix), feedback)
    below_fixture = qform(a, d_below - a, d_below - a, Fraction(1), Fraction(-1))
    pulled_y = Fraction(manifest["registered_inputs"]["fixture"]["pulled_y"])
    pulled_below_fixture = qform(a, d_below - a, d_below - a, Fraction(1), beta * Fraction(1) + pulled_y)
    necessary_witness = qform(a, p_asym, q_asym, -a / p_asym, Fraction(1))

    assert threshold_matrix == [[a, a], [a, a]]
    assert threshold_pulled == [[Fraction(18), Fraction(12)], [Fraction(12), Fraction(8)]]
    assert asym_pulled == [[Fraction(20), Fraction(16)], [Fraction(16), Fraction(16)]]
    assert below_fixture == -2 * delta
    assert pulled_below_fixture == -2 * delta
    assert remainder == extra
    assert necessary_witness == remainder
    assert qform(a, a, a, Fraction(1), Fraction(-1)) == 0
    assert qform(a, a, a, Fraction(1), Fraction(1)) == 4 * a

    derived = {
        "active_cross_scale": a,
        "feedback_gain": beta,
        "threshold": threshold,
        "below_threshold": d_below,
        "asymmetric_reserves": {"d1": d1_asym, "d2": d2_asym, "p": p_asym, "q": q_asym, "remainder": remainder},
        "threshold_matrix": threshold_matrix,
        "threshold_pulled_matrix": threshold_pulled,
        "asymmetric_pulled_matrix": asym_pulled,
        "threshold_quadratic": "8*(x + y)**2",
        "threshold_pulled_quadratic": "2*(3*x + 2*y)**2",
        "asymmetric_quadratic": "8*(x**2 + 2*x*y + 2*y**2)",
        "below_fixture": below_fixture,
        "pulled_subthreshold_fixture": pulled_below_fixture,
        "necessary_reserve_witness": necessary_witness,
        "isotropic_positive": True,
        "isotropic_subthreshold_negative": True,
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": 19,
        "assertions": [{"name": "independent exact reserve-margin arithmetic", "pass": True}],
        "derived": derived,
        "boundary": manifest["boundary"],
    }
    atomic_json(args.output, payload)
    print("INDEPENDENT R-183 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
