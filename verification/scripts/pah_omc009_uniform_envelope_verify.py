#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-009 uniform-envelope obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope"
PRIMARY = RUN_DIR / "primary.json"
INDEPENDENT = RUN_DIR / "independent.json"
HOSTILE = RUN_DIR / "hostile.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-manifest.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN = ROOT / "verification/lean/Tect/R489.lean"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"

AUDIT_ID = "PAH-OMC-009-UNIFORM-ENVELOPE-INTEGRATED-001"
EXPLORATION_ID = "EXP-001434"
RESULT_ID = "R-489"
TASK_ID = "T-054"

REQUIRED_DECLARATIONS = {
    "delta_formula",
    "exponent_formula",
    "rate_quadratic_coefficient_positive",
    "exponent_step_growth",
    "mobility_square_exact",
    "root_weight_positive",
    "non_promotion_firewall",
}

# Test oracles are the exact rational witness values declared by PAH-OMC-009;
# they are not hidden production constants or fitted rate parameters.
TEST_ORACLE = {
    "degree": 4,
    "vertex": [1, 0],
    "support": [[0, 0], [1, 0], [1, 1], [2, 0], [2, 1]],
    "weight": 6,
    "quadratic": Fraction(-7, 24),
    "constant": Fraction(-5, 8),
    "rate_quadratic": Fraction(7, 48),
    "mobility_square": Fraction(1, 2),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def lake_path(registry: dict[str, Any]) -> Path | None:
    configured = registry.get("toolchain", {}).get("lake_executable")
    candidates = [Path(configured)] if configured else []
    candidates.append(Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe")
    return next((path for path in candidates if path.exists()), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source, geometry, start, contract, manifest = (load(path) for path in (SOURCE, GEOMETRY, START, CONTRACT, MANIFEST))
    primary, independent, hostile, registry = (load(path) for path in (PRIMARY, INDEPENDENT, HOSTILE, REGISTRY))
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(CONTRACT),
        "PAH-OMC-009-MANIFEST": sha(MANIFEST),
    }
    runs = (primary, independent, hostile)
    check("source-hashes", all(run.get("source_hashes") == hashes for run in runs), hashes)
    check(
        "manifest-pins",
        manifest.get("contract", {}).get("sha256") == hashes["PAH-OMC-009"]
        and manifest.get("functional_source", {}).get("sha256") == hashes["PAH-001"]
        and manifest.get("geometric_source", {}).get("sha256") == hashes["PAH-OMC-004"]
        and manifest.get("starting_contract", {}).get("sha256") == hashes["PAH-OMC-008"]
        and manifest.get("no_parent_mutation") is True,
        manifest,
    )
    check(
        "identity",
        all(
            run.get("result_id") == RESULT_ID
            and run.get("exploration_id") == EXPLORATION_ID
            and run.get("task_id") == TASK_ID
            for run in runs
        ),
    )
    check("lane-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS" and hostile.get("verification") == "PASS")
    check("lane-assertions", primary.get("failed") == 0 and independent.get("failed") == 0 and hostile.get("failed") == 0)
    check(
        "hostile-rejections",
        hostile.get("all_mutations_rejected") is True
        and hostile.get("mutations_rejected") == hostile.get("mutations_attempted")
        and hostile.get("mutations_attempted") == 6,
        hostile.get("mutations"),
    )
    check(
        "preservation-firewall",
        all(contract.get("preservation_firewall", {}).get(key) is True for key in (
            "parent_functional_unchanged",
            "parent_move_families_unchanged",
            "parent_mobility_unchanged",
            "parent_projection_unchanged",
            "parent_regulator_rule_unchanged",
            "parent_limit_order_unchanged",
            "no_new_hamiltonian",
            "no_counterterm",
            "no_averaging",
            "no_rate_fitting",
            "no_physical_identification",
        )),
    )
    exact_scope = contract.get("exact_scope", {})
    path = exact_scope.get("regulator_path", {})
    check("cofinal-scope", "n>=2" in exact_scope.get("carrier_family", "") and "R tending to infinity" in str(path.get("R_max", "")), exact_scope.get("carrier_family"))
    functional_text = exact_scope.get("functional", "")
    check(
        "displayed-functional",
        all(token in functional_text for token in ("lambda_s(s_v-1)^2/2", "kappa_D", "J_e(s)=2/(s_v+s_w)", "kappa_g", "no added term")),
        functional_text,
    )
    check("displayed-rate", "exp[-beta(F_rho(r omega)-F_rho(omega))/2]" in exact_scope.get("rate_coefficients", ""), exact_scope.get("rate_coefficients"))
    witness = primary.get("witness", {})
    independent_derived = independent.get("derived", {})
    primary_local_assertion = next((item for item in primary.get("assertions", []) if item.get("name") == "full-energy-local-polynomial"), {})
    independent_mobility_assertion = next((item for item in independent.get("assertions", []) if item.get("name") == "mobility-and-weight"), {})
    check("witness-incidence", witness.get("degree") == TEST_ORACLE["degree"] and witness.get("vertex") == TEST_ORACLE["vertex"] and independent_derived.get("degree_b") == TEST_ORACLE["degree"], witness)
    check("support-and-weight", witness.get("support") == TEST_ORACLE["support"] and witness.get("weight") == TEST_ORACLE["weight"] and independent_derived.get("support") == TEST_ORACLE["support"] and independent_derived.get("weight") == TEST_ORACLE["weight"], {"primary": witness, "independent": independent_derived})
    check(
        "exact-polynomial",
        fraction(witness.get("quadratic_coefficient")) == TEST_ORACLE["quadratic"]
        and fraction(witness.get("constant")) == TEST_ORACLE["constant"]
        and fraction(independent_derived.get("quadratic_coefficient")) == TEST_ORACLE["quadratic"]
        and fraction(independent_derived.get("constant")) == TEST_ORACLE["constant"]
        and primary_local_assertion.get("passed") is True,
        {"primary": witness, "independent": independent_derived},
    )
    deltas = witness.get("delta_F", {})
    polynomial_ok = all(fraction(deltas[str(R)]) == TEST_ORACLE["quadratic"] * R * R + TEST_ORACLE["constant"] for R in (0, 1, 2, 4, 8))
    check("sequence-polynomial", polynomial_ok, deltas)
    rate_exponents = witness.get("rate_exponent", {})
    exponent_ok = all(fraction(rate_exponents[str(R)]) == -(
        TEST_ORACLE["quadratic"] * R * R + TEST_ORACLE["constant"]
    ) / 2 for R in (1, 2, 4, 8))
    check("rate-growth-coefficient", exponent_ok and fraction(independent_derived.get("rate_exponent", {}).get("8")) == Fraction(463, 48), rate_exponents)
    check("mobility-and-positive-weight", fraction(witness.get("mobility_square")) == TEST_ORACLE["mobility_square"] and int(witness.get("weight", 0)) > 0 and fraction(independent_mobility_assertion.get("detail", {}).get("mobility_square")) == TEST_ORACLE["mobility_square"] and int(independent_mobility_assertion.get("detail", {}).get("weight", 0)) > 0, {"primary": witness, "independent": independent_mobility_assertion})
    logs = witness.get("weighted_rate_log", {})
    check("weighted-growth", all(float(logs[str(a)]) < float(logs[str(b)]) for a, b in ((1, 2), (2, 4), (4, 8))), logs)
    check(
        "negative-verdict-firewall",
        all(run.get("verdict") == "NEGATIVE_RESULT_RMAX_UNIFORM_ENVELOPE" for run in runs)
        and all(run.get("stage2_status") == "HOLD_FOR_EVIDENCE" for run in runs)
        and all(run.get("claim_bearing") is False and run.get("physical_progress") is False for run in runs)
        and primary.get("eventual_intertwining", {}).get("status") == "NOT_DECIDED_AFTER_ENVELOPE_FAILURE",
    )

    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R489.lean"), {})
    check("lean-registry", entry.get("sha256") == normalized_sha(LEAN) and REQUIRED_DECLARATIONS <= set(entry.get("declarations", [])), entry)
    lean_text = LEAN.read_text(encoding="utf-8")
    check("lean-source-firewall", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    lake = lake_path(registry)
    if lake is None:
        lean_ok, lean_detail = False, "pinned lake executable missing"
    else:
        process = subprocess.run([str(lake), "env", "lean", "Tect/R489.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("lean-compile", lean_ok, lean_detail[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc009-uniform-envelope-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "NEGATIVE_RESULT_RMAX_UNIFORM_ENVELOPE",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "verification_summary": {
            "primary": f"{primary.get('passed', 0)}/{primary.get('assertion_count', 0)}",
            "independent": f"{independent.get('passed', 0)}/{independent.get('assertion_count', 0)}",
            "hostile": f"{hostile.get('mutations_rejected', 0)}/{hostile.get('mutations_attempted', 0)} mutations rejected",
            "lean": "PASS" if lean_ok else "FAIL",
        },
        "witness": witness,
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
        "reproduction": {
            "primary": "python codes/foundations/pah_omc009_uniform_envelope.py",
            "independent": "python codes/foundations/pah_omc009_uniform_envelope_independent.py",
            "hostile": "python codes/foundations/pah_omc009_uniform_envelope_hostile.py",
            "integrated": "python verification/scripts/pah_omc009_uniform_envelope_verify.py",
            "lean": "Set-Location verification/lean; lake env lean Tect/R489.lean",
        },
    }
    atomic_json(args.output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; Lean={'PASS' if lean_ok else 'FAIL'}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
