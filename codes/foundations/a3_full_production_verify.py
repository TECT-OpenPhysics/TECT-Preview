#!/usr/bin/env python3
"""One-command verifier for the P3 full-production discretization package.

Each CPU-reproducible audit writes only to a temporary directory.  The CUDA
row is checked as the recorded, hash-bound evidence artifact rather than being
silently rerun on a non-CUDA host.  Thus this command is safe on CPU machines
and still fails if the accepted CUDA evidence is absent, stale, or incomplete.

Use --reuse-recorded-audits only to verify the accepted immutable result JSONs
and their current source hashes without redoing the expensive CPU calculations.
The default remains a clean temporary re-execution of every CPU audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

__version__ = "1.2.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"
__claims__ = ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
HARDWARE_EVIDENCE = CLAIM / "runs" / "2026-07-17-hardware-precision" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-integrated-verifier-energy-envelope" / "result.json"
AUDITS = (
    ("a3_full_production_spatial_consistency.py", "spatial_audit", "A3-FULL-SPATIAL-CONSISTENCY-PASS", "spatial.json", CLAIM / "runs" / "2026-07-17-spatial-consistency" / "result.json"),
    ("a3_full_production_finite_time_convergence.py", "finite_time_audit", "A3-FULL-FINITE-TIME-CONVERGENCE-PASS", "finite-time.json", CLAIM / "runs" / "2026-07-17-finite-time-convergence" / "result.json"),
    ("a3_full_production_hessian_ritz_convergence.py", "hessian_ritz_audit", "A3-FULL-HESSIAN-RITZ-CONVERGENCE-PASS", "hessian-ritz.json", CLAIM / "runs" / "2026-07-17-hessian-ritz-convergence" / "result.json"),
    ("a3_full_production_independent_galerkin.py", "independent_galerkin_audit", "A3-FULL-INDEPENDENT-GALERKIN-PASS", "independent-galerkin.json", CLAIM / "runs" / "2026-07-17-independent-galerkin" / "result.json"),
    ("a3_full_production_solution_ball_bound.py", "solution_ball_bound_audit", "A3-FULL-SOLUTION-BALL-BOUND-PASS", "solution-ball.json", CLAIM / "runs" / "2026-07-17-solution-ball-bound" / "result.json"),
    ("a3_full_production_energy_ball_envelope.py", "energy_ball_envelope_audit", "A3-FULL-ENERGY-BALL-ENVELOPE-PASS", "energy-ball.json", CLAIM / "runs" / "2026-07-17-energy-ball-envelope" / "result.json"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hardware(manifest: dict[str, Any]) -> tuple[bool, int, dict[str, Any]]:
    if not HARDWARE_EVIDENCE.exists():
        return False, 0, {"reason": "recorded CUDA evidence is missing"}
    evidence = json.loads(HARDWARE_EVIDENCE.read_text(encoding="utf-8"))
    rows = {row.get("configuration"): row for row in evidence.get("rows", [])}
    required = ("cpu_complex128", "cpu_complex64", "cuda_complex128", "cuda_complex64")
    source = REPO / manifest["authority"]["hardware_precision_audit"]["path"]
    source_hash_ok = sha256(source) == manifest["authority"]["hardware_precision_audit"]["sha256"]
    backend = REPO / manifest["authority"]["p1_backend"]["path"]
    backend_hash_ok = sha256(backend) == manifest["authority"]["p1_backend"]["sha256"]
    row_ok = all(rows.get(name, {}).get("status") == "PASS" for name in required)
    assertion_ok = all(item.get("status") == "PASS" for item in evidence.get("assertions", []))
    passed = bool(evidence.get("torch", {}).get("cuda_available")) and bool(evidence.get("gate_closed")) and evidence.get("verdict") == "A3-FULL-HARDWARE-PRECISION-PASS" and row_ok and assertion_ok and source_hash_ok and backend_hash_ok
    return passed, len(evidence.get("assertions", [])), {"recorded_artifact_sha256": sha256(HARDWARE_EVIDENCE), "recorded_device": evidence.get("torch", {}).get("devices", []), "source_hash_ok": source_hash_ok, "backend_hash_ok": backend_hash_ok, "rows_pass": row_ok, "assertions_pass": assertion_ok, "verdict": evidence.get("verdict")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reuse-recorded-audits", action="store_true", help="validate immutable recorded CPU audit results rather than rerunning them")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    reports: list[dict[str, Any]] = []
    assertion_total = 0
    with tempfile.TemporaryDirectory(prefix="a3-full-production-") as temporary:
        output_root = Path(temporary)
        for script_name, authority_key, expected_verdict, output_name, recorded_artifact in AUDITS:
            script = Path(__file__).resolve().parent / script_name
            source_hash_ok = sha256(script) == manifest["authority"][authority_key]["sha256"]
            if args.reuse_recorded_audits:
                completed = None
                artifact = recorded_artifact
            else:
                completed = subprocess.run([sys.executable, str(script), "--output", str(output_root / output_name)], cwd=REPO, text=True, capture_output=True, check=False)
                artifact = output_root / output_name
            result = json.loads(artifact.read_text(encoding="utf-8")) if artifact.exists() else {}
            count = int(result.get("assertion_summary", {}).get("total", 0))
            assertion_total += count
            completed_ok = args.reuse_recorded_audits or (completed is not None and completed.returncode == 0)
            passed = completed_ok and source_hash_ok and result.get("verdict") == expected_verdict and result.get("assertion_summary", {}).get("passed") == count
            reports.append({"script": script_name, "mode": "recorded" if args.reuse_recorded_audits else "temporary-reexecution", "expected_verdict": expected_verdict, "actual_verdict": result.get("verdict"), "assertions": result.get("assertion_summary"), "source_hash_ok": source_hash_ok, "recorded_artifact": str(recorded_artifact.relative_to(REPO)), "passed": passed})
            print(f"{'PASS' if passed else 'FAIL'}: {script.stem} ({result.get('assertion_summary', {}).get('passed', 0)}/{count})")
            if not passed:
                detail = "recorded artifact validation" if args.reuse_recorded_audits else f"exit={completed.returncode}; stdout={completed.stdout[-400:]!r}; stderr={completed.stderr[-400:]!r}"
                failures.append(f"{script_name}: source_hash_ok={source_hash_ok}; {detail}")
    hardware_passed, hardware_count, hardware_report = check_hardware(manifest)
    assertion_total += hardware_count
    reports.append({"script": "recorded_cuda_hardware_evidence", "assertions": {"passed": hardware_count if hardware_passed else 0, "total": hardware_count}, "passed": hardware_passed, "detail": hardware_report})
    print(f"{'PASS' if hardware_passed else 'FAIL'}: recorded_cuda_hardware_evidence ({hardware_count if hardware_passed else 0}/{hardware_count})")
    if not hardware_passed:
        failures.append(f"recorded CUDA evidence invalid: {hardware_report}")
    passed = not failures
    mode = "recorded immutable CPU audits" if args.reuse_recorded_audits else "temporary CPU re-execution"
    output = {"schema": "tect/a3-full-production-integrated-verifier-result/1.0", "claim_id": manifest["claim_id"], "script_version": __version__, "verdict": "A3-FULL-PRODUCTION-VERIFY-PASS" if passed else "A3-FULL-PRODUCTION-VERIFY-FAIL", "scope": f"{mode} of spatial, finite-time, Hessian/Ritz, independent-proxy, solution-ball-order, and energy-to-H2-envelope audits; hash validation of recorded CUDA evidence", "reports": reports, "assertion_summary": {"passed": assertion_total if passed else sum(int(report.get("assertions", {}).get("passed", 0)) for report in reports), "total": assertion_total}, "failures": failures, "not_closed_here": ["explicit positive-time H4/H6 smoothing constants", "numerical enclosure of the solution-ball constant C(R,tau,T)", "dealiased finite-time evolution bound", "historical Sector-B solver continuum validity", "independent external reproduction", "tier promotion"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"ASSERTS: {output['assertion_summary']['passed']}/{assertion_total}")
    print(output["verdict"])
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
