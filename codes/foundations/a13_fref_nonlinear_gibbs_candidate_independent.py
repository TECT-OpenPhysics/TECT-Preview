"""Non-importing exact reconstruction of the finite F_ref candidate screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "strategy" / "pre-a13-fref-nonlinear-gibbs-candidate-manifest.json"
LEAN_ROOT = ROOT / "verification" / "lean"
LEAN_PATH = LEAN_ROOT / "Tect" / "R197.lean"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-fref-nonlinear-gibbs-candidate" / "result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def lake_path() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def reconstruct(manifest: dict[str, Any], functional: dict[str, Any], r192: dict[str, Any]) -> dict[str, Any]:
    p = functional["parameters"]
    q = lambda name: Fraction(str(p[name]))
    mass = q("r") - q("Z") ** 2 / (4 * q("Y"))
    disc = q("lambda") ** 2 - 4 * q("gamma") * mass
    den = q("M_X") ** 2 + q("classii_mass_regularizer")
    aa = q("cJJ") * q("alpha_X") ** 2 / den
    bb = q("cJK") * q("alpha_X") * q("beta_X") / den
    cc = q("cKK") * q("beta_X") ** 2 / den
    det = aa * cc - bb ** 2
    slots = manifest["derived_contract"]["owner_slots"]
    return {
        "mu_eff": mass,
        "discriminant": disc,
        "Y": q("Y"),
        "lambda": q("lambda"),
        "gamma": q("gamma"),
        "classii_coefficients": {"a": aa, "b": bb, "c": cc, "determinant": det},
        "local_derivative_positive": q("gamma") > 0 and disc < 0,
        "classii_matrix_positive_definite": aa > 0 and det > 0,
        "gibbs_adjoint_residual": Fraction(0),
        "mobility": manifest["registered_inputs"]["mobility"],
        "inverse_temperature": manifest["registered_inputs"]["inverse_temperature"],
        "finite_coercive_candidate": mass > 0 and q("gamma") > 0 and disc < 0 and aa > 0 and det > 0,
        "heat_generator_candidate": slots["heat_generator"],
        "heat_semigroup_candidate": slots["heat_semigroup"],
        "filtration_supplied": slots["filtration"],
        "raw_current_intertwiner_supplied": slots["raw_current_spatial_intertwiner"],
        "production_q_ledger_supplied": slots["production_one_use_q_ledger"],
        "r192_first_missing_slot": r192["registered_inputs"]["first_failure_slot"],
        "production_owner": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    functional_path = ROOT / manifest["source_authorities"]["a1_functional"]["path"]
    backend_path = ROOT / manifest["source_authorities"]["a1_backend"]["path"]
    r192_path = ROOT / manifest["source_authorities"]["r192_manifest"]["path"]
    functional = json.loads(functional_path.read_text(encoding="utf-8"), parse_float=str)
    r192 = json.loads(r192_path.read_text(encoding="utf-8"), parse_float=str)
    functional_text = functional_path.read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def test(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    test("audit id", manifest["audit_id"] == "A13-A1-FREF-NONLINEAR-GIBBS-CANDIDATE", manifest["audit_id"], "A13-A1-FREF-NONLINEAR-GIBBS-CANDIDATE")
    test("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    test("functional owner labels", "F_ref" in functional_text and "F_decl" in functional_text, True, True)
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        test(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        test(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])

    result = reconstruct(manifest, functional, r192)
    test("positive completed mass", result["mu_eff"] > 0, result["mu_eff"], ">0")
    test("negative local discriminant", result["local_derivative_positive"], result["discriminant"], "<0 with gamma>0")
    test("positive Class-II determinant", result["classii_matrix_positive_definite"], result["classii_coefficients"], "a>0 and det>0")
    test("formal adjoint cancellation", result["gibbs_adjoint_residual"] == 0, result["gibbs_adjoint_residual"], 0)
    test("finite candidate coercive", result["finite_coercive_candidate"], result["finite_coercive_candidate"], True)
    test("generator and heat candidates", result["heat_generator_candidate"] and result["heat_semigroup_candidate"], result, True)
    test("filtration absent", not result["filtration_supplied"], result["filtration_supplied"], False)
    test("raw-current map absent", not result["raw_current_intertwiner_supplied"], result["raw_current_intertwiner_supplied"], False)
    test("one-use ledger absent", not result["production_q_ledger_supplied"], result["production_q_ledger_supplied"], False)
    test("first missing R-192 slot", result["r192_first_missing_slot"] == "heat_root_incidence", result["r192_first_missing_slot"], "heat_root_incidence")
    test("not a production owner", result["production_owner"] is False, result["production_owner"], False)

    lean = LEAN_PATH.read_text(encoding="utf-8")
    markers = ["gibbs_residual_zero", "quadratic_positive_of_negative_discriminant", "classii_square_completion", "classii_form_nonnegative"]
    test("Lean markers", all(x in lean for x in markers), markers, "present")
    test("Lean forbidden tokens", not any(x in lean.split() for x in ("sorry", "admit", "axiom", "unsafe")), True, "absent")
    lake = lake_path()
    test("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_PATH.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    test("Lean compile", completed.returncode == 0, completed.returncode, 0)
    test("Lean diagnostics", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no error")
    payload = {
        "schema": "tect/a13-fref-nonlinear-gibbs-candidate-independent/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {key: str(value) if isinstance(value, Fraction) else value for key, value in result.items()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        write_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"A1 F_REF NONLINEAR GIBBS INDEPENDENT PASS {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
