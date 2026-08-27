#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001212 / R-370."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_energy_window"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-energy-window-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R370.lean"
LEAN_REGISTRY = REPO / "verification/lean/registry.json"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads(LEAN_REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    directory = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = directory / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R370.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R370.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    agreement = float(manifest["finite_fixture"]["agreement_tolerance"])
    assertions: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(assertions) < 96:
            assertions.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001212" and manifest["result_id"] == "R-370" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001212/R-370/false")
    check("sources", all(path.is_file() for path in (PRIMARY, INDEPENDENT, LEAN, LEAN_REGISTRY)), [str(path) for path in (PRIMARY, INDEPENDENT, LEAN, LEAN_REGISTRY)], "all present")
    primary_hash = normalized_sha256(PRIMARY)
    independent_hash = normalized_sha256(INDEPENDENT)
    check("independent source", primary_hash != independent_hash, [primary_hash, independent_hash], "distinct")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = ("kubo_mori_diagonal", "arithmetic_mean_symmetry", "half_envelope", "weighted_half_envelope", "bond_translation_fixture", "square_shape_fixture", "prefix_fixture", "energy_gap_split_fixture", "energy_gap_decomposition_fixture", "scope_fixture")
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    registry = json.loads(LEAN_REGISTRY.read_text(encoding="utf-8"))
    entries = [entry for entry in registry["entrypoints"] if entry["path"] == "verification/lean/Tect/R370.lean"]
    check("Lean registry unique", len(entries) == 1, len(entries), 1)
    check("Lean registry hash", entries[0]["sha256"] == normalized_sha256(LEAN), entries[0]["sha256"], normalized_sha256(LEAN))
    check("Lean declarations", entries[0]["declarations"] == list(markers), entries[0]["declarations"], list(markers))

    with tempfile.TemporaryDirectory(prefix="q3-fractional-stress-") as temporary:
        primary_process, primary = run_child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p = primary["derived"]
        i = independent["derived"]
        exact_fields = (
            "context_count", "expected_contexts", "theta", "bond_translation_finite_checked", "source_translation_finite_checked",
            "edge_and_square_shapes_checked", "all_prefixes_finite_checked", "energy_gap_split_finite_checked",
            "energy_gap_pythagorean_decomposition_closed", "weighted_fractional_bound_closed",
            "low_gap_cutoff_uniformity_proved", "high_gap_tail_uniformity_proved",
            "weighted_cutoff_uniformity_proved", "weighted_volume_uniformity_proved", "source_uniformity_proved",
            "shape_uniformity_proved", "local_modular_dirichlet_comparison_proved", "common_core_closed", "common_alpha_closed",
            "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"
        )
        for field in exact_fields:
            check(f"agreement {field}", p[field] == i[field], [p[field], i[field]], "equal")
        numeric_fields = (
            "max_weighted_phase_error", "max_fractional_envelope_violation", "max_weighted_bound_violation",
            "maximum_weighted_fractional_norm", "maximum_weighted_fractional_bound", "maximum_weighted_to_bound_ratio",
            "minimum_nonzero_weighted_fractional_norm", "maximum_kubo_weight_asymmetry", "minimum_kubo_weight",
            "maximum_arithmetic_to_kubo_fractional_ratio", "maximum_window_decomposition_error",
            "maximum_low_gap_phase_error", "maximum_high_gap_phase_error",
            "maximum_low_gap_bound_violation", "maximum_high_gap_bound_violation",
            "maximum_low_gap_fractional_norm", "maximum_high_gap_fractional_norm",
            "maximum_low_gap_fractional_bound", "maximum_high_gap_fractional_bound",
            "maximum_high_gap_fraction", "minimum_nonzero_low_gap_fractional_norm",
            "maximum_bond_unitary_factorization_error"
        )
        for field in numeric_fields:
            scale = 1.0 + max(abs(float(p[field])), abs(float(i[field])))
            check(f"agreement {field}", abs(float(p[field]) - float(i[field])) <= agreement * scale, [p[field], i[field]], f"within {agreement} scaled")
        check("regime count", len(p["regimes"]) == len(i["regimes"]), [len(p["regimes"]), len(i["regimes"])], "equal")
        for regime_index, (pr, ir) in enumerate(zip(p["regimes"], i["regimes"])):
            for field in ("shape", "volume", "cutoffs", "sites", "bond_term_indices", "contexts", "expected_contexts"):
                check(f"regime {regime_index} {field}", pr[field] == ir[field], [pr[field], ir[field]], "equal")
            for field in ("maximum_kubo_fractional_norm", "maximum_kubo_fractional_bound"):
                scale = 1.0 + max(abs(float(pr[field])), abs(float(ir[field])))
                check(f"regime {regime_index} {field}", abs(float(pr[field]) - float(ir[field])) <= agreement * scale, [pr[field], ir[field]], f"within {agreement} scaled")
            check(f"regime {regime_index} bond row count", len(pr["bond_rows"]) == len(ir["bond_rows"]), [len(pr["bond_rows"]), len(ir["bond_rows"])], "equal")
            for bond_index, (pb, ib) in enumerate(zip(pr["bond_rows"], ir["bond_rows"])):
                for field in ("cutoff", "bond_term_index", "context_count"):
                    check(f"regime {regime_index} bond {bond_index} {field}", pb[field] == ib[field], [pb[field], ib[field]], "equal")
                for field in ("maximum_kubo_fractional_norm", "maximum_kubo_fractional_bound"):
                    scale = 1.0 + max(abs(float(pb[field])), abs(float(ib[field])))
                    check(f"regime {regime_index} bond {bond_index} {field}", abs(float(pb[field]) - float(ib[field])) <= agreement * scale, [pb[field], ib[field]], f"within {agreement} scaled")
            check(f"regime {regime_index} window row count", len(pr["window_rows"]) == len(ir["window_rows"]), [len(pr["window_rows"]), len(ir["window_rows"])], "equal")
            for row_index, (prow, irow) in enumerate(zip(pr["window_rows"], ir["window_rows"])):
                for field in ("cutoff", "energy_gap", "context_count"):
                    check(f"regime {regime_index} window row {row_index} {field}", prow[field] == irow[field], [prow[field], irow[field]], "equal")
                for field in ("maximum_low_gap_fractional_norm", "maximum_high_gap_fractional_norm", "maximum_high_gap_fraction"):
                    scale = 1.0 + max(abs(float(prow[field])), abs(float(irow[field])))
                    check(f"regime {regime_index} window row {row_index} {field}", abs(float(prow[field]) - float(irow[field])) <= agreement * scale, [prow[field], irow[field]], f"within {agreement} scaled")
        check("window summary count", len(p["window_summaries"]) == len(i["window_summaries"]), [len(p["window_summaries"]), len(i["window_summaries"])], "equal")
        for window_index, (pw, iw) in enumerate(zip(p["window_summaries"], i["window_summaries"])):
            check(f"window {window_index} energy_gap", pw["energy_gap"] == iw["energy_gap"], [pw["energy_gap"], iw["energy_gap"]], "equal")
            check(f"window {window_index} context_count", pw["context_count"] == iw["context_count"], [pw["context_count"], iw["context_count"]], "equal")
            for field in ("maximum_low_gap_fractional_norm", "maximum_high_gap_fractional_norm", "maximum_low_gap_fractional_bound", "maximum_high_gap_fractional_bound", "maximum_high_gap_fraction", "maximum_decomposition_error"):
                scale = 1.0 + max(abs(float(pw[field])), abs(float(iw[field])))
                check(f"window {window_index} {field}", abs(float(pw[field]) - float(iw[field])) <= agreement * scale, [pw[field], iw[field]], f"within {agreement} scaled")
        open_fields = (
            "low_gap_cutoff_uniformity_proved", "high_gap_tail_uniformity_proved",
            "weighted_cutoff_uniformity_proved", "weighted_volume_uniformity_proved", "source_uniformity_proved",
            "shape_uniformity_proved", "local_modular_dirichlet_comparison_proved", "common_core_closed", "common_alpha_closed",
            "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"
        )
        check("scope firewall", all(p[field] is False and i[field] is False for field in open_fields), "open", "all limiting/QFT flags false")
        derived = {"primary": p, "independent": i, "max_primary_independent_numeric_difference": max(abs(float(p[field]) - float(i[field])) for field in numeric_fields)}

    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-ENERGY-WINDOW",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": assertions,
        "derived": derived,
        "lean": lean,
        "provenance": {
            "manifest_sha256": normalized_sha256(MANIFEST),
            "primary_sha256": primary_hash,
            "independent_sha256": independent_hash,
            "lean_sha256": normalized_sha256(LEAN),
            "lean_registry_sha256": normalized_sha256(LEAN_REGISTRY)
        },
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED KUBO-MORI ENERGY-WINDOW PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']} diff={payload['derived']['max_primary_independent_numeric_difference']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
