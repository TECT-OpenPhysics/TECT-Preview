"""Non-importing stdlib Fraction lane for the A1 Class-II owner mismatch."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a1-classii-owner-mismatch-lean-crosscheck-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_manifest"]["path"]
    lean_path = REPO / manifest["inputs"]["lean_entrypoint"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    inputs = manifest["lean_inputs"]
    params = a1["parameters"]
    values = {key: Fraction(str(params[inputs[key]])) for key in ("alpha_key", "beta_key", "mass_key", "mass_regularizer_key", "cjk_key", "ckk_key")}
    declared_num = values["ckk_key"] * values["beta_key"] ** 2
    residual_num = values["cjk_key"] * values["alpha_key"] * values["beta_key"]
    denominator = values["mass_key"] ** 2 + values["mass_regularizer_key"]
    declared = declared_num / denominator
    residual = residual_num / denominator
    assert sha256(a1_path) == manifest["inputs"]["a1_manifest"]["sha256"]
    assert sha256(lean_path) == manifest["inputs"]["lean_entrypoint"]["sha256"]
    for name, key in (("alpha", "alpha_key"), ("beta", "beta_key"), ("mass", "mass_key"), ("mass_regularizer", "mass_regularizer_key"), ("cjk", "cjk_key"), ("ckk", "ckk_key")):
        assert values[key] == Fraction(str(inputs[name]))
    assert declared_num == Fraction(str(inputs["expected_declared_numerator"]))
    assert residual_num == Fraction(str(inputs["expected_residual_numerator"]))
    assert declared_num - residual_num == Fraction(str(inputs["expected_numerator_difference"]))
    assert denominator > 0
    assert declared != residual
    payload = {
        "schema": "tect/a1-classii-owner-mismatch-lean-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "derived": {
            "alpha": f"{values['alpha_key'].numerator}/{values['alpha_key'].denominator}",
            "beta": f"{values['beta_key'].numerator}/{values['beta_key'].denominator}",
            "mass": f"{values['mass_key'].numerator}/{values['mass_key'].denominator}",
            "mass_regularizer": f"{values['mass_regularizer_key'].numerator}/{values['mass_regularizer_key'].denominator}",
            "cjk": f"{values['cjk_key'].numerator}/{values['cjk_key'].denominator}",
            "ckk": f"{values['ckk_key'].numerator}/{values['ckk_key'].denominator}",
            "declared_numerator": f"{declared_num.numerator}/{declared_num.denominator}",
            "residual_numerator": f"{residual_num.numerator}/{residual_num.denominator}",
            "numerator_difference": f"{(declared_num - residual_num).numerator}/{(declared_num - residual_num).denominator}",
            "mass_denominator": f"{denominator.numerator}/{denominator.denominator}",
            "declared_coefficient": f"{declared.numerator}/{declared.denominator}",
            "residual_coefficient": f"{residual.numerator}/{residual.denominator}",
            "coefficient_difference": f"{(declared - residual).numerator}/{(declared - residual).denominator}",
            "mass_denominator_positive": denominator > 0,
            "coefficients_are_not_equal": declared != residual,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("INDEPENDENT A1 CLASS-II LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
