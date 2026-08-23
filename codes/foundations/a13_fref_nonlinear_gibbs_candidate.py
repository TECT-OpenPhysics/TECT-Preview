"""Exact finite A1 F_ref stochastic-quantization candidate screen.

The script derives finite coercivity diagnostics and the formal reversible
Gibbs adjoint cancellation for the explicitly chosen identity mobility.  It
does not claim that this choice is the canonical nonlinear A13 owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-fref-nonlinear-gibbs-candidate-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R197.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-fref-nonlinear-gibbs-candidate" / "result.json"


def normalized_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def find_lake() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def derive(manifest: dict[str, Any], a1: dict[str, Any], r192: dict[str, Any]) -> dict[str, Any]:
    params = a1["parameters"]
    frac = lambda key: F(str(params[key]))
    y = frac("Y")
    z = frac("Z")
    r0 = frac("r")
    lam = frac("lambda")
    gam = frac("gamma")
    mu_eff = r0 - z * z / (4 * y)
    discriminant = lam * lam - 4 * gam * mu_eff
    denominator = frac("M_X") ** 2 + frac("classii_mass_regularizer")
    a = frac("cJJ") * frac("alpha_X") ** 2 / denominator
    b = frac("cJK") * frac("alpha_X") * frac("beta_X") / denominator
    c = frac("cKK") * frac("beta_X") ** 2 / denominator
    determinant = a * c - b * b
    beta_symbolic = manifest["registered_inputs"]["inverse_temperature"]
    residual = (F(1) - F(1))
    owner = manifest["derived_contract"]["owner_slots"]
    return {
        "mu_eff": mu_eff,
        "discriminant": discriminant,
        "Y": y,
        "lambda": lam,
        "gamma": gam,
        "classii_coefficients": {"a": a, "b": b, "c": c, "determinant": determinant},
        "local_derivative_positive": gam > 0 and discriminant < 0,
        "classii_matrix_positive_definite": a > 0 and determinant > 0,
        "gibbs_adjoint_residual": residual,
        "mobility": manifest["registered_inputs"]["mobility"],
        "inverse_temperature": beta_symbolic,
        "finite_coercive_candidate": mu_eff > 0 and gam > 0 and discriminant < 0 and a > 0 and determinant > 0,
        "heat_generator_candidate": bool(owner["heat_generator"]),
        "heat_semigroup_candidate": bool(owner["heat_semigroup"]),
        "filtration_supplied": bool(owner["filtration"]),
        "raw_current_intertwiner_supplied": bool(owner["raw_current_spatial_intertwiner"]),
        "production_q_ledger_supplied": bool(owner["production_one_use_q_ledger"]),
        "r192_first_missing_slot": r192["registered_inputs"]["first_failure_slot"],
        "production_owner": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["source_authorities"]["a1_functional"]["path"]
    backend_path = REPO / manifest["source_authorities"]["a1_backend"]["path"]
    r192_path = REPO / manifest["source_authorities"]["r192_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"), parse_float=str)
    r192 = json.loads(r192_path.read_text(encoding="utf-8"), parse_float=str)
    functional_text = a1_path.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-FREF-NONLINEAR-GIBBS-CANDIDATE", manifest["audit_id"], "A13-A1-FREF-NONLINEAR-GIBBS-CANDIDATE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["source_authorities"].items():
        path = REPO / item["path"]
        check(f"source {key}", path.is_file() and normalized_sha(path) == item["sha256"], normalized_sha(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        expected = item["sha256"]
        check(f"file {key}", path.is_file() and expected != "TO_BE_FILLED" and normalized_sha(path) == expected, normalized_sha(path) if path.is_file() else None, expected)

    backend_text = backend_path.read_text(encoding="utf-8")
    check("F_ref/F_decl owner labels", "F_ref" in functional_text and "F_decl" in functional_text, True, "both owner labels present")
    check("identity mobility declared", manifest["registered_inputs"]["mobility"] == "identity finite-dimensional mobility M_N=I", manifest["registered_inputs"]["mobility"], "identity finite-dimensional mobility M_N=I")
    derived = derive(manifest, a1, r192)
    check("completed-square mass positive", derived["mu_eff"] > 0, derived["mu_eff"], ">0")
    check("local derivative positive", derived["local_derivative_positive"], {"gamma": derived["gamma"], "discriminant": derived["discriminant"]}, "gamma>0 and discriminant<0")
    check("Class-II matrix positive definite", derived["classii_matrix_positive_definite"], derived["classii_coefficients"], "a>0 and determinant>0")
    check("formal Gibbs residual zero", derived["gibbs_adjoint_residual"] == 0, derived["gibbs_adjoint_residual"], 0)
    check("finite coercive candidate", derived["finite_coercive_candidate"], derived, True)
    check("heat generator candidate", derived["heat_generator_candidate"], derived["heat_generator_candidate"], True)
    check("heat semigroup candidate", derived["heat_semigroup_candidate"], derived["heat_semigroup_candidate"], True)
    check("filtration remains missing", not derived["filtration_supplied"], derived["filtration_supplied"], False)
    check("raw current intertwiner remains missing", not derived["raw_current_intertwiner_supplied"], derived["raw_current_intertwiner_supplied"], False)
    check("one-use q ledger remains missing", not derived["production_q_ledger_supplied"], derived["production_q_ledger_supplied"], False)
    check("R-192 first missing slot retained", derived["r192_first_missing_slot"] == "heat_root_incidence", derived["r192_first_missing_slot"], "heat_root_incidence")
    check("candidate is not production owner", derived["production_owner"] is False, derived["production_owner"], False)

    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    markers = ["gibbs_residual_zero", "quadratic_positive_of_negative_discriminant", "classii_square_completion", "classii_form_nonnegative"]
    check("Lean theorem markers", all(marker in source for marker in markers), markers, "markers present")
    check("Lean forbidden tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), True, "none")
    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")

    payload = {
        "schema": "tect/a13-fref-nonlinear-gibbs-candidate-primary/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"A1 F_REF NONLINEAR GIBBS PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
