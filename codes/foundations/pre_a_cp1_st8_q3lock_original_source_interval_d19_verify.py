#!/usr/bin/env python3
"""Integrated verifier for the R-438 d=19 finite interval package."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d19-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_d19.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_d19_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_d19_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R438.lean"
SLUG = "original_source_interval_d19"
RUN_ROOT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
PRIMARY_OUTPUT = RUN_ROOT / f"2026-08-30-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = RUN_ROOT / f"2026-08-30-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = RUN_ROOT / f"2026-08-30-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = RUN_ROOT / f"2026-08-30-integrated-{SLUG}" / "integrated.json"
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
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-438" and manifest["exploration_id"] == "EXP-001283" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-438/EXP-001283/false", "provenance")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-438 artifacts", "provenance")
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
            completed = command([os.fspath(Path(sys.executable)), "-X", "utf8", os.fspath(script), "--self-test"], ROOT)
            outputs[script.name] = (completed.stdout + completed.stderr).strip()
            check(f"run {script.name}", completed.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lean = command([os.fspath(LAKE), "env", "lean", "Tect/R438.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1200:], "exit 0 without errors", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    p = primary["derived"]
    i = independent["derived"]
    scope = manifest["scope"]
    check("primary interval certificate", primary["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED" and primary["assertion_count"] == 59 and p["finite_positive_gap_certified"] is True and Decimal(p["maximum_residual_matrix_interval_width"]) < Decimal(manifest["interval_contract"]["maximum_matrix_interval_width"]) and Decimal(p["bracket_width"]) < Decimal(manifest["interval_contract"]["maximum_bracket_width"]), {key: p[key] for key in ("rayleigh_interval", "maximum_residual_matrix_interval_width", "bracket_width")}, "59/59 finite interval checks and bounded bracket", "primary")
    check("primary finite probes", Decimal(p["rayleigh_interval"][0]) > Decimal(manifest["interval_contract"]["lower_probe"]) and Decimal(p["rayleigh_interval"][1]) < Decimal(manifest["interval_contract"]["upper_probe"]), p["rayleigh_interval"], "inside fixed probes", "primary")
    check("primary row split", p["tail_split"] == {"core": manifest["source_contract"]["core_indices"], "tail": manifest["source_contract"]["tail_indices"]}, p["tail_split"], "manifest split", "primary")
    check("independent control", independent["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS" and independent["assertion_count"] == 12 and Decimal(str(i["residual_gap_double"])) > Decimal(manifest["interval_contract"]["lower_probe"]) and Decimal(str(i["residual_gap_double"])) < Decimal(manifest["interval_contract"]["upper_probe"]), {key: i[key] for key in ("residual_gap_double", "tail_split")}, "12/12 finite independent control", "independent")
    check("hostile controls", hostile["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and hostile["assertion_count"] == 8 and hostile["scope"]["hostile_mutations_rejected"] and hostile["scope"]["physical_promotion_rejected"], hostile["scope"], "all eight mutations rejected", "hostile")
    check("scope firewall", scope["original_source_interval_certified"] and scope["finite_positive_gap_certified"] and not any(scope[key] for key in ("residual_reuse_closed_for_original_source", "cutoff_uniform_coarse_schur_closed", "volume_uniform_coarse_schur_closed", "phase_uniform_coarse_schur_closed", "exhaustion_uniform_coarse_schur_closed", "common_core_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), scope, "finite flags true and all promotion flags false", "scope")
    payload = {
        "schema": "tect/pre-a-r438-integrated/1.0",
        "result_id": "R-438",
        "exploration_id": "EXP-001283",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": "ORIGINAL_SOURCE_INTERVAL_CERTIFIED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"fixed_row": p["fixed_row"], "block_sizes": p["symmetry_block_sizes"], "rayleigh_interval": p["rayleigh_interval"], "bracket_width": p["bracket_width"], "maximum_residual_matrix_interval_width": p["maximum_residual_matrix_interval_width"], "independent_residual_gap_double": i["residual_gap_double"], "hostile_mutation_count": hostile["assertion_count"], "lean": "PASS", "finite_positive_gap_certified": True, "residual_reuse_closed_for_original_source": False, "outputs": outputs},
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-438 INTEGRATED ORIGINAL_SOURCE_INTERVAL_CERTIFIED {len(checks)}/{len(checks)} bracket={p['rayleigh_interval']} Lean=PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
