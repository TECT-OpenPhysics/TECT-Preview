#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001226 / R-384."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_two_scale_filter_removal_corridor"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-two-scale-filter-removal-corridor-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R384.lean"
LEAN_REGISTRY = REPO / "verification/lean/registry.json"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads(LEAN_REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    if candidate.is_file():
        return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R384.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R384.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
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
        if len(assertions) < 220:
            assertions.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001226" and manifest["result_id"] == "R-384" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001226/R-384/false")
    check("sources", all(path.is_file() for path in (PRIMARY, INDEPENDENT, LEAN, LEAN_REGISTRY)), [str(path) for path in (PRIMARY, INDEPENDENT, LEAN, LEAN_REGISTRY)], "all present")
    primary_hash = normalized_sha256(PRIMARY)
    independent_hash = normalized_sha256(INDEPENDENT)
    check("independent source", primary_hash != independent_hash, [primary_hash, independent_hash], "distinct")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = ("removal_weight_nonnegative", "low_frequency_factor_bound", "high_frequency_tail_factor", "low_m0_envelope_factor", "endpoint_low_frequency_factor", "endpoint_high_frequency_factor", "scope_fixture")
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    registry = json.loads(LEAN_REGISTRY.read_text(encoding="utf-8"))
    entries = [entry for entry in registry["entrypoints"] if entry["path"] == "verification/lean/Tect/R384.lean"]
    check("Lean registry unique", len(entries) == 1, len(entries), 1)
    check("Lean registry hash", entries[0]["sha256"] == normalized_sha256(LEAN), entries[0]["sha256"], normalized_sha256(LEAN))
    check("Lean declarations", entries[0]["declarations"] == list(markers), entries[0]["declarations"], list(markers))

    with tempfile.TemporaryDirectory(prefix="q3-two-scale-filter-removal-corridor-") as temporary:
        primary_process, primary = run_child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p = primary["derived"]
        i = independent["derived"]
        exact_fields = ("context_count", "expected_contexts", "theta", "gibbs_log_energy_identity_finite_checked", "endpoint_energy_moment_finite_checked", "quadratic_cauchy_envelope_finite_checked", "left_right_energy_moment_symmetry_finite_checked", "per_cutoff_moment_profile_finite_checked", "successive_cutoff_ratio_diagnostic_finite_checked", "filtered_endpoint_envelope_finite_checked", "filtered_m2_envelope_finite_checked", "filtered_profile_finite_checked", "low_high_split_finite_checked", "filter_removal_envelope_finite_checked", "endpoint_removal_envelope_finite_checked", "filter_removal_proved", "low_frequency_uniformity_proved", "high_frequency_tail_uniformity_proved", "cutoff_growth_warning", "source_uniformity_proved", "weighted_cutoff_uniformity_proved", "weighted_volume_uniformity_proved", "shape_uniformity_proved", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
        for field in exact_fields:
            check(f"agreement {field}", p[field] == i[field], [p[field], i[field]], "equal")
        numeric_fields = ("maximum_gibbs_log_energy_identity_error", "maximum_endpoint_orientation_error", "maximum_moment_orientation_error", "maximum_cauchy_envelope_violation", "maximum_endpoint_reconstruction_error", "maximum_endpoint_modular_moment", "maximum_endpoint_energy_first_moment", "maximum_state_weighted_m0", "maximum_state_weighted_m2", "maximum_cauchy_bound", "minimum_state_weighted_m0", "minimum_state_weighted_m2", "maximum_endpoint_to_cauchy_ratio", "maximum_bond_unitary_factorization_error", "maximum_kubo_weight_asymmetry", "minimum_kubo_weight", "maximum_successive_m0_ratio", "maximum_successive_m2_ratio", "growth_warning_ratio", "maximum_filtered_m0", "maximum_filtered_m2", "maximum_filtered_endpoint", "maximum_reference_filtered_m0", "maximum_reference_filtered_m2", "maximum_reference_filtered_endpoint", "maximum_corridor_removal_m0", "maximum_corridor_removal_m0_envelope", "maximum_corridor_endpoint_removal", "maximum_corridor_endpoint_removal_envelope", "reference_power")
        for field in numeric_fields:
            scale = 1.0 + max(abs(float(p[field])), abs(float(i[field])))
            check(f"agreement {field}", abs(float(p[field]) - float(i[field])) <= agreement * scale, [p[field], i[field]], f"within {agreement} scaled")
        check("filter power count", len(p["filter_powers"]) == len(i["filter_powers"]), [len(p["filter_powers"]), len(i["filter_powers"])], "equal")
        for filter_index, (pf, inf) in enumerate(zip(p["filter_powers"], i["filter_powers"])):
            check(f"filter {filter_index} label", pf["label"] == inf["label"], [pf["label"], inf["label"]], "equal")
            check(f"filter {filter_index} power", abs(float(pf["power"]) - float(inf["power"])) <= agreement, [pf["power"], inf["power"]], f"within {agreement}")
        check("filtered profile count", len(p["filtered_profiles"]) == len(i["filtered_profiles"]), [len(p["filtered_profiles"]), len(i["filtered_profiles"])], "equal")
        filtered_exact = ("shape", "volume", "cutoff", "filter", "contexts", "expected_contexts")
        filtered_numeric = ("power", "maximum_endpoint", "maximum_m0", "maximum_m2", "maximum_cauchy_bound", "maximum_endpoint_to_cauchy_ratio")
        for profile_index, (pp, ip) in enumerate(zip(p["filtered_profiles"], i["filtered_profiles"])):
            for field in filtered_exact:
                check(f"filtered profile {profile_index} {field}", pp[field] == ip[field], [pp[field], ip[field]], "equal")
            for field in filtered_numeric:
                scale = 1.0 + max(abs(float(pp[field])), abs(float(ip[field])))
                check(f"filtered profile {profile_index} {field}", abs(float(pp[field]) - float(ip[field])) <= agreement * scale, [pp[field], ip[field]], f"within {agreement} scaled")
        check("reference filter", abs(float(p["reference_power"]) - float(i["reference_power"])) <= agreement, [p["reference_power"], i["reference_power"]], f"within {agreement}")
        check("energy window count", len(p["energy_windows"]) == len(i["energy_windows"]), [len(p["energy_windows"]), len(i["energy_windows"])], "equal")
        for window_index, (pw, iw) in enumerate(zip(p["energy_windows"], i["energy_windows"])):
            check(f"energy window {window_index} label", pw["label"] == iw["label"], [pw["label"], iw["label"]], "equal")
            check(f"energy window {window_index} value", abs(float(pw["window"]) - float(iw["window"])) <= agreement, [pw["window"], iw["window"]], f"within {agreement}")
        check("corridor profile count", len(p["corridor_profiles"]) == len(i["corridor_profiles"]), [len(p["corridor_profiles"]), len(i["corridor_profiles"])], "equal")
        corridor_exact = ("shape", "volume", "cutoff", "window", "contexts", "expected_contexts")
        corridor_numeric = ("energy_window", "maximum_low_m0", "maximum_high_m0", "maximum_low_m2", "maximum_high_m2", "maximum_removal_m0", "maximum_removal_m0_envelope", "maximum_endpoint_removal", "maximum_endpoint_removal_envelope", "maximum_partition_error_m0", "maximum_partition_error_m2")
        for profile_index, (pp, ip) in enumerate(zip(p["corridor_profiles"], i["corridor_profiles"])):
            for field in corridor_exact:
                check(f"corridor profile {profile_index} {field}", pp[field] == ip[field], [pp[field], ip[field]], "equal")
            for field in corridor_numeric:
                scale = 1.0 + max(abs(float(pp[field])), abs(float(ip[field])))
                check(f"corridor profile {profile_index} {field}", abs(float(pp[field]) - float(ip[field])) <= agreement * scale, [pp[field], ip[field]], f"within {agreement} scaled")
        check("regime count", len(p["regimes"]) == len(i["regimes"]), [len(p["regimes"]), len(i["regimes"])], "equal")
        regime_fields = ("shape", "volume", "contexts", "expected_contexts", "maximum_endpoint", "maximum_m0", "maximum_m2")
        for index, (pr, ir) in enumerate(zip(p["regimes"], i["regimes"])):
            for field in regime_fields:
                if field in ("shape", "volume", "contexts", "expected_contexts"):
                    check(f"regime {index} {field}", pr[field] == ir[field], [pr[field], ir[field]], "equal")
                else:
                    scale = 1.0 + max(abs(float(pr[field])), abs(float(ir[field])))
                    check(f"regime {index} {field}", abs(float(pr[field]) - float(ir[field])) <= agreement * scale, [pr[field], ir[field]], f"within {agreement} scaled")
            check(f"regime {index} profile count", len(pr["cutoff_profiles"]) == len(ir["cutoff_profiles"]), [len(pr["cutoff_profiles"]), len(ir["cutoff_profiles"])], "equal")
            check(f"regime {index} filtered profile count", len(pr["filtered_profiles"]) == len(ir["filtered_profiles"]), [len(pr["filtered_profiles"]), len(ir["filtered_profiles"])], "equal")
            check(f"regime {index} corridor profile count", len(pr["corridor_profiles"]) == len(ir["corridor_profiles"]), [len(pr["corridor_profiles"]), len(ir["corridor_profiles"])], "equal")
            profile_numeric = ("maximum_endpoint", "maximum_m0", "maximum_m2", "maximum_cauchy_bound", "maximum_endpoint_to_cauchy_ratio")
            for profile_index, (pp, ip) in enumerate(zip(pr["cutoff_profiles"], ir["cutoff_profiles"])):
                for field in ("shape", "volume", "cutoff", "contexts", "expected_contexts"):
                    check(f"profile {index}/{profile_index} {field}", pp[field] == ip[field], [pp[field], ip[field]], "equal")
                for field in profile_numeric:
                    scale = 1.0 + max(abs(float(pp[field])), abs(float(ip[field])))
                    check(f"profile {index}/{profile_index} {field}", abs(float(pp[field]) - float(ip[field])) <= agreement * scale, [pp[field], ip[field]], f"within {agreement} scaled")
            filtered_by_key_p = {(item["cutoff"], item["filter"]): item for item in pr["filtered_profiles"]}
            filtered_by_key_i = {(item["cutoff"], item["filter"]): item for item in ir["filtered_profiles"]}
            check(f"regime {index} filtered keys", sorted(filtered_by_key_p) == sorted(filtered_by_key_i), [sorted(filtered_by_key_p), sorted(filtered_by_key_i)], "equal")
            for key in sorted(filtered_by_key_p):
                pp = filtered_by_key_p[key]
                ip = filtered_by_key_i[key]
                for field in ("shape", "volume", "cutoff", "filter", "contexts", "expected_contexts"):
                    check(f"filtered regime {index} {key} {field}", pp[field] == ip[field], [pp[field], ip[field]], "equal")
                for field in ("power", "maximum_endpoint", "maximum_m0", "maximum_m2", "maximum_cauchy_bound", "maximum_endpoint_to_cauchy_ratio"):
                    scale = 1.0 + max(abs(float(pp[field])), abs(float(ip[field])))
                    check(f"filtered regime {index} {key} {field}", abs(float(pp[field]) - float(ip[field])) <= agreement * scale, [pp[field], ip[field]], f"within {agreement} scaled")
            corridor_by_key_p = {(item["cutoff"], item["window"]): item for item in pr["corridor_profiles"]}
            corridor_by_key_i = {(item["cutoff"], item["window"]): item for item in ir["corridor_profiles"]}
            check(f"regime {index} corridor keys", sorted(corridor_by_key_p) == sorted(corridor_by_key_i), [sorted(corridor_by_key_p), sorted(corridor_by_key_i)], "equal")
            for key in sorted(corridor_by_key_p):
                pp = corridor_by_key_p[key]
                ip = corridor_by_key_i[key]
                for field in ("shape", "volume", "cutoff", "window", "contexts", "expected_contexts"):
                    check(f"corridor regime {index} {key} {field}", pp[field] == ip[field], [pp[field], ip[field]], "equal")
                for field in ("energy_window", "maximum_low_m0", "maximum_high_m0", "maximum_low_m2", "maximum_high_m2", "maximum_removal_m0", "maximum_removal_m0_envelope", "maximum_endpoint_removal", "maximum_endpoint_removal_envelope", "maximum_partition_error_m0", "maximum_partition_error_m2"):
                    scale = 1.0 + max(abs(float(pp[field])), abs(float(ip[field])))
                    check(f"corridor regime {index} {key} {field}", abs(float(pp[field]) - float(ip[field])) <= agreement * scale, [pp[field], ip[field]], f"within {agreement} scaled")
            check(f"regime {index} ratio count", len(pr["successive_ratios"]) == len(ir["successive_ratios"]), [len(pr["successive_ratios"]), len(ir["successive_ratios"])], "equal")
            for ratio_index, (pratio, iratio) in enumerate(zip(pr["successive_ratios"], ir["successive_ratios"])):
                check(f"ratio {index}/{ratio_index} cutoffs", [pratio["from_cutoff"], pratio["to_cutoff"]] == [iratio["from_cutoff"], iratio["to_cutoff"]], [pratio, iratio], "equal")
                for field in ("m0_ratio", "m2_ratio"):
                    if pratio[field] is None or iratio[field] is None:
                        check(f"ratio {index}/{ratio_index} {field} null", pratio[field] is None and iratio[field] is None, [pratio[field], iratio[field]], "both null")
                    else:
                        scale = 1.0 + max(abs(float(pratio[field])), abs(float(iratio[field])))
                        check(f"ratio {index}/{ratio_index} {field}", abs(float(pratio[field]) - float(iratio[field])) <= agreement * scale, [pratio[field], iratio[field]], f"within {agreement} scaled")
        open_fields = ("filter_removal_proved", "low_frequency_uniformity_proved", "high_frequency_tail_uniformity_proved", "source_uniformity_proved", "weighted_cutoff_uniformity_proved", "weighted_volume_uniformity_proved", "shape_uniformity_proved", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
        check("scope firewall", all(p[field] is False and i[field] is False for field in open_fields), "open", "all limiting/QFT flags false")
        derived = {"primary": p, "independent": i, "max_primary_independent_numeric_difference": max(abs(float(p[field]) - float(i[field])) for field in numeric_fields)}

    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-TWO-SCALE-FILTER-REMOVAL-CORRIDOR", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": assertions, "derived": derived, "lean": lean, "provenance": {"manifest_sha256": normalized_sha256(MANIFEST), "primary_sha256": primary_hash, "independent_sha256": independent_hash, "lean_sha256": normalized_sha256(LEAN), "lean_registry_sha256": normalized_sha256(LEAN_REGISTRY)}, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED TWO-SCALE-FILTER-REMOVAL-CORRIDOR PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']} diff={payload['derived']['max_primary_independent_numeric_difference']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
