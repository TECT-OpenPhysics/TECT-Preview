#!/usr/bin/env python3
"""Execute the pinned public GTS likelihood path on a synthetic fixture.

This audit is deliberately narrower than an event-level GBM run.  It imports
``likelihood.py`` from the pinned public commit and calls ``Likelihood.calculate``
directly.  The public module imports a large ``utils`` dependency tree for
plotting and data helpers; a module stub is injected only for that import.  An
AST check proves that the calculate method does not reference ``utils``.  No
event bytes, response templates, or detector metadata are read here.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

import numpy as np

from audit_gts_synthetic_owner import FIXTURE, _fixture_digest, _source_transcription


SOURCE_COMMIT = "1bc1e913f97fd7195a7e297f8d6032a5c7758894"
LIKELIHOOD_SHA256 = "38c2059d9783d86ebbb3cd2fe3d7a6c0459db2ad0497860caae015acb0b77a1e"
COMPARE_TOL = 1.0e-9
HOSTILE_MIN_DELTA = 1.0e-6


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _calculate_uses_utils(source: str) -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "calculate":
            return any(isinstance(name, ast.Name) and name.id == "utils" for name in ast.walk(node))
    raise AssertionError("public likelihood.py has no calculate method")


def _load_public_likelihood(source_path: Path) -> Any:
    source = source_path.read_text(encoding="utf-8")
    if _sha256(source_path) != LIKELIHOOD_SHA256:
        raise AssertionError("likelihood.py hash does not match the pinned public commit")
    if _calculate_uses_utils(source):
        raise AssertionError("calculate unexpectedly references the plotting/data utils module")

    # The stub is limited to the unused plotting/data helper import.  The
    # numerical calculate path imports only NumPy, SciPy, and matplotlib.
    previous_utils = sys.modules.get("utils")
    sys.modules["utils"] = types.ModuleType("utils")
    try:
        spec = importlib.util.spec_from_file_location("gts_pinned_likelihood", source_path)
        if spec is None or spec.loader is None:
            raise AssertionError("unable to construct import specification")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous_utils is None:
            sys.modules.pop("utils", None)
        else:
            sys.modules["utils"] = previous_utils


def _execute(module: Any, fixture: dict[str, Any]) -> dict[str, Any]:
    response = np.asarray(fixture["response"], dtype=float)
    likelihood = module.Likelihood(
        response.shape[0],
        response.shape[1],
        gamma=float(fixture["gamma"]),
        num_iters=int(fixture["num_iters"]),
        prethresh=float(fixture["prethreshold"]),
    )
    likelihood.calculate(
        np.asarray(fixture["counts"], dtype=float),
        np.asarray(fixture["background"], dtype=float),
        np.asarray(fixture["background_variance"], dtype=float),
        response,
    )
    llratio = np.asarray(likelihood.llr, dtype=float)
    if not np.isfinite(llratio).all() or not np.isfinite(float(likelihood.marginal_llr)):
        raise AssertionError("public likelihood path returned a non-finite value")
    return {
        "status": int(likelihood.status),
        "marginal_llr": float(likelihood.marginal_llr),
        "llratio": llratio,
        "llratio_shape": [int(value) for value in llratio.shape],
        "max_template": int(likelihood.max_template),
        "max_location": int(likelihood.max_location),
    }


def _summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": int(result["status"]),
        "marginal_llr": float(result["marginal_llr"]),
        "llratio_shape": list(result["llratio_shape"]),
        "max_template": int(result["max_template"]),
        "max_location": int(result["max_location"]),
    }


def run(out: Path, source_root: Path) -> dict[str, Any]:
    # Keep matplotlib's cache out of the tracked tree when the public module is
    # imported on a clean operator machine.
    os.environ["MPLCONFIGDIR"] = str(Path(tempfile.gettempdir()) / "tect-gts-mpl")
    source_path = source_root / "likelihood.py"
    module = _load_public_likelihood(source_path)
    primary = _execute(module, FIXTURE)
    transcription = _source_transcription(FIXTURE)
    primary_delta = float(np.max(np.abs(primary["llratio"] - transcription["llratio"])))
    marginal_delta = abs(float(primary["marginal_llr"]) - float(transcription["marginal_llr"]))

    hostile_fixture = json.loads(json.dumps(FIXTURE))
    hostile_fixture["counts"][0] += 7.0
    hostile = _execute(module, hostile_fixture)
    hostile_delta = abs(float(hostile["marginal_llr"]) - float(primary["marginal_llr"]))

    noise_fixture = json.loads(json.dumps(FIXTURE))
    noise_fixture["counts"] = list(noise_fixture["background"])
    noise = _execute(module, noise_fixture)

    checks = [
        {
            "id": "pinned-source-hash",
            "finding": "PASS",
            "detail": "The imported likelihood.py bytes match the declared public commit source hash.",
        },
        {
            "id": "calculate-utils-isolation",
            "finding": "PASS",
            "detail": "AST inspection found no utils reference in Likelihood.calculate; the import stub cannot alter that numerical path.",
        },
        {
            "id": "public-finite-path",
            "finding": "PASS",
            "detail": "The pinned public Likelihood.calculate path returns finite status, likelihood array, and marginalized LLR.",
        },
        {
            "id": "transcription-agreement",
            "finding": "PASS" if primary_delta <= COMPARE_TOL and marginal_delta <= COMPARE_TOL else "FAIL",
            "detail": f"Direct public execution agrees with the independent repository transcription: max array delta={primary_delta:.3e}, marginal delta={marginal_delta:.3e}.",
        },
        {
            "id": "hostile-count-sensitivity",
            "finding": "PASS" if hostile_delta > HOSTILE_MIN_DELTA else "FAIL",
            "detail": f"A hostile +7 count mutation changes the direct public statistic by {hostile_delta:.6f}.",
        },
        {
            "id": "prethreshold-noise-branch",
            "finding": "PASS" if noise["status"] == 2 else "FAIL",
            "detail": f"A background-equals-counts fixture enters the public prethreshold status-2 branch (observed status={noise['status']}).",
        },
    ]
    if any(check["finding"] == "FAIL" for check in checks):
        raise AssertionError(checks)

    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "tect/gts-public-likelihood-audit/0.1",
        "id": "GTS-PUBLIC-LIKELIHOOD-001",
        "recorded_on": "2026-08-30",
        "claim_bearing": False,
        "tier": "T0",
        "status": "PASS_PINNED_PUBLIC_EXECUTION_TRANSCRIPTION_HOSTILE",
        "source_repository": "https://github.com/USRA-STI/gamma-ray-targeted-search",
        "source_commit": SOURCE_COMMIT,
        "source_file": "likelihood.py",
        "source_file_sha256": LIKELIHOOD_SHA256,
        "fixture_role": "Synthetic tooling test oracle; not event data and not a physical observation.",
        "fixture_digest_sha256": _fixture_digest(FIXTURE),
        "execution": _summary(primary),
        "independent_transcription": {
            "summary": {
                "status": int(transcription["status"]),
                "marginal_llr": float(transcription["marginal_llr"]),
                "llratio_shape": [int(value) for value in transcription["llratio"].shape],
                "max_index": [int(value) for value in transcription["max_index"]],
            },
            "max_llratio_abs_delta": primary_delta,
            "marginal_llr_abs_delta": marginal_delta,
        },
        "hostile_mutation": {
            "mutation": "counts[0] += 7.0",
            "fixture_digest_sha256": _fixture_digest(hostile_fixture),
            "summary": _summary(hostile),
            "marginal_delta_from_primary": hostile_delta,
        },
        "noise_branch": {
            "mutation": "counts := background",
            "fixture_digest_sha256": _fixture_digest(noise_fixture),
            "summary": _summary(noise),
        },
        "comparison": {
            "compare_tolerance": COMPARE_TOL,
            "hostile_min_delta": HOSTILE_MIN_DELTA,
        },
        "dependency_scope": {
            "executed": ["numpy", "scipy", "matplotlib", "pinned public likelihood.py"],
            "stubbed_only": ["utils import used by plotting/data helper methods"],
            "not_available_or_read": ["healpy", "astropy", "gdt.core", "gdt.missions.fermi.gbm", "event bytes", "response templates"],
        },
        "checks": checks,
        "run_command": "python verification/scripts/audit_gts_public_likelihood.py --out claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-public-likelihood/public_likelihood.json --source-root <pinned-public-gts-checkout>",
        "interpretation": "Direct finite execution of the pinned public likelihood module on a synthetic fixture, with independent transcription agreement and input sensitivity. This advances the code-owner candidate only at T0 and does not admit an event-level GBM likelihood or physical timing result.",
        "non_claims": [
            "No event-level GBM result, response matrix value, calibration validity, detector-to-geocenter correction, covariance model, or intrinsic-lag estimate is established.",
            "The synthetic fixture is not GW170817 data and receives no retrospective or prospective observational credit.",
            "No F_reg/F_lim/F_eff/F_obs map, microscopic dynamics, QFT/Yang--Mills/gravity identity, Pre-A, C6, Sector-A, continuum, physical-vacuum, or mass-gap claim follows.",
        ],
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-public-likelihood/public_likelihood.json"),
    )
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    payload = run(args.out, args.source_root)
    print(json.dumps({"status": payload["status"], "out": str(args.out), "comparison": payload["comparison"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
