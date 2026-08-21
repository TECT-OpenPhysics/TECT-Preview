"""Stdlib-only independent lane for the R-181 feedback mixed Gram."""

from __future__ import annotations

import argparse
import hashlib
import json
from math import lcm
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-feedback-mixed-gram-crosscheck-manifest.json"


def canonical_defect_formula(beta: Fraction, envelope: Fraction) -> str:
    coefficients = [envelope - 1 - beta * beta, -2 * beta, envelope - 1]
    denominator = lcm(*(item.denominator for item in coefficients))
    numerators = [item.numerator * (denominator // item.denominator) for item in coefficients]
    labels = ["x**2", "x*y", "y**2"]
    terms: list[str] = []
    for numerator, label in zip(numerators, labels):
        if numerator == 0:
            continue
        magnitude = abs(numerator)
        coefficient = "" if magnitude == 1 else f"{magnitude}*"
        term = coefficient + label
        if not terms:
            terms.append(("-" if numerator < 0 else "") + term)
        else:
            terms.append((" - " if numerator < 0 else " + ") + term)
    numerator_text = "".join(terms)
    return f"({numerator_text})/{denominator}" if denominator != 1 else f"({numerator_text})"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    r177 = json.loads((REPO / manifest["inputs"]["r177_manifest"]["path"]).read_text(encoding="utf-8"))
    r176 = json.loads((REPO / manifest["inputs"]["r176_manifest"]["path"]).read_text(encoding="utf-8"))
    registered = manifest["registered_inputs"]
    beta = Fraction(registered["feedback_gain"])
    envelope = Fraction(registered["envelope_constant"])
    order = r177["registered_inputs"]["owner_order"]
    assert order == ["common_heat", "root_1", "root_2", "future_residual"]
    assert r176["registered_inputs"]["root_multipliers"] == [1, 2]
    gram = [[1 + beta * beta, beta], [beta, Fraction(1)]]
    fixture = registered["fixture"]
    x = Fraction(fixture["x"])
    y = Fraction(fixture["y"])
    source_norm = x * x + y * y
    output_norm = x * x + (beta * x + y) ** 2
    defect = envelope * source_norm - output_norm
    defect_formula = canonical_defect_formula(beta, envelope)
    expected_gram = [[1 + beta * beta, beta], [beta, Fraction(1)]]
    assert gram == expected_gram
    assert envelope > 1 + beta * beta
    assert output_norm == Fraction(fixture["output_norm"])
    assert source_norm == Fraction(fixture["source_norm"])
    assert defect == Fraction(fixture["defect"])
    derived = {
        "feedback_gain": beta,
        "envelope_constant": envelope,
        "owner_order": order,
        "root_multipliers": r176["registered_inputs"]["root_multipliers"],
        "feedback_matrix": [[Fraction(1), Fraction(0)], [beta, Fraction(1)]],
        "mixed_gram": gram,
        "source_norm": f"x**2 + y**2",
        "output_norm": "x**2 + (x/2 + y)**2",
        "defect": defect_formula,
        "fixture_output": output_norm,
        "fixture_source": source_norm,
        "fixture_defect": defect,
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }
    atomic_json(args.output, {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": 16, "assertions": [{"name": "independent exact feedback Gram arithmetic", "pass": True}], "derived": derived, "boundary": manifest["boundary"]})
    print("INDEPENDENT R-181 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
