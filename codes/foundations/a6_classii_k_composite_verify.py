#!/usr/bin/env python3
"""One-command verifier for the A6 Class-II K-composite package."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A6-CLASSII-K-COMPOSITE-DEFINITION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / "classii_k_composite_manifest.json"
PRIMARY = REPO / "codes" / "foundations" / "a6_classii_k_composite.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a6_classii_k_composite_independent.py"
PRIMARY_RESULT = CLAIM_DIR / "runs" / "2026-07-20-primary-k-composite" / "result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs" / "2026-07-20-independent-k-composite" / "result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-integrated-k-composite" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(name: str, condition: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append(
        {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected}
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary_run = subprocess.run(
        [sys.executable, str(PRIMARY), "--output", str(PRIMARY_RESULT)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    independent_run = subprocess.run(
        [sys.executable, str(INDEPENDENT), "--output", str(INDEPENDENT_RESULT)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8")) if PRIMARY_RESULT.exists() else {}
    independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8")) if INDEPENDENT_RESULT.exists() else {}
    assertions: list[dict[str, Any]] = []

    add("primary_subprocess_passes", primary_run.returncode == 0, primary_run.returncode, 0, assertions)
    add("independent_subprocess_passes", independent_run.returncode == 0, independent_run.returncode, 0, assertions)
    add("primary_verdict_passes", primary.get("verdict") == "A6-CLASSII-K-COMPOSITE-PRIMARY-PASS", primary.get("verdict"), "A6-CLASSII-K-COMPOSITE-PRIMARY-PASS", assertions)
    add("independent_verdict_passes", independent.get("verdict") == "A6-CLASSII-K-COMPOSITE-INDEPENDENT-PASS", independent.get("verdict"), "A6-CLASSII-K-COMPOSITE-INDEPENDENT-PASS", assertions)

    source_paths = {
        "primary_audit": PRIMARY,
        "independent_audit": INDEPENDENT,
        "one_command_verifier": Path(__file__).resolve(),
        "a6_uv_source": REPO / manifest["authority"]["a6_uv_source"]["path"],
        "proof_note": REPO / manifest["authority"]["proof_note"]["path"],
        "proof_pdf": REPO / manifest["authority"]["proof_pdf"]["path"],
    }
    for key, path in source_paths.items():
        expected = manifest["authority"][key]["sha256"]
        add(f"{key}_hash_matches", sha256(path) == expected, sha256(path), expected, assertions)

    if primary and independent:
        p_area = float(primary["derived"]["area_lift"]["reference_variance"])
        i_area = float(independent["derived"]["area_lift"]["reference_variance"])
        area_error = abs(p_area - i_area) / p_area
        add("independent_area_reference_agrees", area_error < float(manifest["integrated_audit"]["area_reference_relative_tolerance"]), area_error, manifest["integrated_audit"]["area_reference_relative_tolerance"], assertions)

        p_counter = primary["derived"]["counterterm"]
        i_counter = independent["derived"]["counterterm"]
        for key in ("w_infinity", "lower_bound_coefficient"):
            error = abs(float(p_counter[key]) - float(i_counter[key]))
            add(f"independent_{key}_agrees", error < 1.0e-14, error, "<1e-14", assertions)
        p_instability = float(p_counter["homogeneous_instability"]["energy_density_over_N_3_2_limit"])
        i_instability = float(i_counter["energy_density_over_N_3_2_limit"])
        add("independent_naive_subtraction_no_go_agrees", abs(p_instability - i_instability) < 1.0e-14 and p_instability < 0.0, {"primary": p_instability, "independent": i_instability}, "same negative coefficient", assertions)

        p_mean = float(primary["derived"]["local_proxies"]["mean_contraction_proxy"]["rescaled_mean_t_s"])
        p_exact = float(primary["derived"]["local_proxies"]["derivative_integrated_proxy"]["rescaled_mean_t_s"])
        i_mean = float(independent["derived"]["local_proxy_quadrature"]["mean_proxy"]["mean"])
        i_exact = float(independent["derived"]["local_proxy_quadrature"]["derivative_proxy"]["mean"])
        add("independent_mean_proxy_limit_agrees", abs(p_mean - i_mean) / p_mean < 1.0e-10, {"primary": p_mean, "independent": i_mean}, "relative error <1e-10", assertions)
        add("independent_derivative_proxy_limit_agrees", abs(p_exact - i_exact) / p_exact < 1.0e-10, {"primary": p_exact, "independent": i_exact}, "relative error <1e-10", assertions)

        anomaly = float(independent["derived"]["asymmetric_negative_control"][-1]["split_phase"])
        add("negative_control_blocks_unrestricted_scheme_independence", abs(anomaly) > 1.0e-4 and "common real-even scalar Fourier multipliers" in manifest["admissible_regulators"], anomaly, "nonzero outside declared class", assertions)

    add("counterterm_gate_remains_open", "A6-CLASSII-COUNTERTERM-CLOSURE" in manifest["open_followups"], manifest["open_followups"], "counterterm closure listed", assertions)
    add("bare_full_field_gate_remains_open", "A6-CLASSII-FULL-FIELD-BARE-CONCENTRATION" in manifest["open_followups"], manifest["open_followups"], "full-field bare gate listed", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    primary_total = int(primary.get("assertion_summary", {}).get("total", 0))
    independent_total = int(independent.get("assertion_summary", {}).get("total", 0))
    aggregate = primary_total + independent_total + len(assertions)
    verdict = "A6-CLASSII-K-COMPOSITE-INTEGRATED-PASS" if passed == len(assertions) and primary_run.returncode == independent_run.returncode == 0 else "A6-CLASSII-K-COMPOSITE-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a6-classii-k-composite-integrated-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": verdict,
        "subprocesses": {
            "primary": {"returncode": primary_run.returncode, "stdout": primary_run.stdout, "stderr": primary_run.stderr},
            "independent": {"returncode": independent_run.returncode, "stdout": independent_run.stdout, "stderr": independent_run.stderr},
        },
        "source_reports": {
            "manifest_sha256": sha256(MANIFEST),
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "verifier_sha256": sha256(Path(__file__).resolve()),
            "primary_result_sha256": sha256(PRIMARY_RESULT) if PRIMARY_RESULT.exists() else None,
            "independent_result_sha256": sha256(INDEPENDENT_RESULT) if INDEPENDENT_RESULT.exists() else None,
        },
        "assertions": assertions,
        "assertion_summary": {
            "integrated_passed": passed,
            "integrated_total": len(assertions),
            "primary_total": primary_total,
            "independent_total": independent_total,
            "aggregate_total": aggregate,
        },
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: primary ({primary.get('assertion_summary', {}).get('passed', 0)}/{primary_total})" if primary_run.returncode == 0 else "FAIL: primary")
    print(f"PASS: independent ({independent.get('assertion_summary', {}).get('passed', 0)}/{independent_total})" if independent_run.returncode == 0 else "FAIL: independent")
    print(f"ASSERTS: {aggregate}/{aggregate}" if verdict.endswith("INTEGRATED-PASS") else f"INTEGRATED ASSERTS: {passed}/{len(assertions)}")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if verdict.endswith("INTEGRATED-PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
