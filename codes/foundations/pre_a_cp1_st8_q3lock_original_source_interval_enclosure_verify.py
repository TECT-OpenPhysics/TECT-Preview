#!/usr/bin/env python3
"""Integrated verifier for the R-433 original-source interval enclosure."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-enclosure-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_enclosure.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_enclosure_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_enclosure_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R433.lean"
SLUG = "original_source_interval_enclosure"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-integrated-{SLUG}" / "integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-433" and manifest["exploration_id"] == "EXP-001278" and manifest["claim_bearing"] is False and manifest["status"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-433/EXP-001278/false/ORIGINAL_SOURCE_INTERVAL_CERTIFIED", "provenance")
    scope = manifest["scope"]
    required_true = ["original_source_interval_certified", "exact_original_hamiltonian_certified", "gibbs_kernel_interval_propagated", "corrected_row_interval_propagated", "residual_interval_certified", "r422_separation_certified", "r426_direct_separation_certified", "no_new_negative_result", "no_tier_change"]
    required_false = ["residual_reuse_closed_for_original_source", "cutoff_uniform_coarse_schur_closed", "volume_uniform_coarse_schur_closed", "phase_uniform_coarse_schur_closed", "exhaustion_uniform_coarse_schur_closed", "common_core_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"]
    check("scope firewall", all(scope[key] for key in required_true) and not any(scope[key] for key in required_false), {key: scope[key] for key in sorted(scope)}, "finite source flags true and all promotion flags false", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-433 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")

    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R433.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    p = primary["derived"]
    i = independent["derived"]
    max_width = Decimal(str(p["maximum_residual_matrix_interval_width"]))
    bracket_width = Decimal(str(p["bracket_width"]))
    check("primary interval certificate", primary["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED" and primary["assertion_count"] == 40 and p["source_interval_certified"] is True and p["exact_original_hamiltonian_certified"] is True and p["gibbs_kernel_interval_propagated"] is True and p["corrected_row_interval_propagated"] is True and p["residual_interval_certified"] is True and p["r422_separation_certified"] is True and p["r426_direct_separation_certified"] is True and p["residual_reuse_closed_for_original_source"] is False and max_width < Decimal("1e-8") and bracket_width < Decimal("3e-7"), {key: p[key] for key in ("hamiltonian_residual_upper", "hamiltonian_gram_upper", "maximum_residual_matrix_interval_width", "rayleigh_interval", "bracket_width", "r422_separation_margin", "r426_separation_margin")}, "40/40 finite interval checks, width<1e-8, bracket<3e-7 and both reference separations", "primary")
    check("independent finite control", independent["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS" and independent["assertion_count"] == 12 and i["residual_gap_double"] > float(manifest["source_contract"]["r422_reference"]) + float(manifest["source_contract"]["comparison_tolerance"]), {key: i[key] for key in ("residual_gap_double", "r422_separation_margin_double", "tail_split")}, "independent source/row/residual control with R-422 sign separation", "independent")
    check("hostile controls", hostile["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and hostile["assertion_count"] == 7 and hostile["scope"]["hostile_mutations_rejected"] is True and hostile["scope"]["physical_promotion_rejected"] is True, hostile["scope"], "all seven mutations rejected", "hostile")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r433-integrated/1.0",
        "result_id": "R-433",
        "exploration_id": "EXP-001278",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": "ORIGINAL_SOURCE_INTERVAL_CERTIFIED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "fixed_row": p["fixed_row"],
            "symmetry_block_sizes": p["symmetry_block_sizes"],
            "hamiltonian_residual_upper": p["hamiltonian_residual_upper"],
            "hamiltonian_gram_upper": p["hamiltonian_gram_upper"],
            "maximum_residual_matrix_interval_width": p["maximum_residual_matrix_interval_width"],
            "rayleigh_interval": p["rayleigh_interval"],
            "bracket_width": p["bracket_width"],
            "r422_separation_margin": p["r422_separation_margin"],
            "r426_separation_margin": p["r426_separation_margin"],
            "independent_residual_gap_double": i["residual_gap_double"],
            "hostile_mutation_count": hostile["assertion_count"],
            "lean": "PASS",
            "source_interval_certified": True,
            "residual_reuse_closed_for_original_source": False,
            "outputs": outputs,
        },
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": "Finite V=2, d=16, beta=8 original-source row only; all uniform, physical-empty, Yang-Mills and mass-gap flags remain false.",
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-433 INTEGRATED ORIGINAL_SOURCE_INTERVAL_CERTIFIED {len(checks)}/{len(checks)} bracket={p['rayleigh_interval']} Lean=PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
