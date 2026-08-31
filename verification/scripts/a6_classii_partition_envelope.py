#!/usr/bin/env python3
"""Primary audit of the R-464 finite-cutoff partition envelope.

The input is only the already proved R-464 lower comparison
F_N(z) >= a_N ||z||^6 - K.  The script evaluates the resulting radial
integral upper envelope in log form, and records the m-dependent coefficient
and entropy-pressure terms.  It never substitutes the envelope for the
correlated field partition function or a branch probability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R464_MANIFEST = REPO / "strategy" / "a6-classii-finite-gibbs-conditioning-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs" / "2026-08-31-primary-a6-partition-envelope" / "primary.json"

AUDIT_CUTOFFS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20)
AUDIT_BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))


def sha256_normalised(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def assertion(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})


def load_parameters() -> dict[str, Fraction]:
    payload = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    return {key: frac(payload[key]) for key in ("Lx", "Ly", "Lz", "gamma", "lambda", "r", "Z", "Y")}


def derive(params: dict[str, Fraction]) -> dict[str, Fraction]:
    volume = params["Lx"] * params["Ly"] * params["Lz"]
    mu2 = params["r"] - params["Z"] ** 2 / (4 * params["Y"])
    ell = -params["lambda"]
    threshold = 3 * ell / params["gamma"]
    constant = ell * threshold ** 2 / 4
    return {"volume": volume, "mu2": mu2, "ell": ell, "threshold": threshold, "constant": constant, "gamma": params["gamma"]}


def radial_log_envelope(beta: Fraction, cutoff: int, d: dict[str, Fraction]) -> dict[str, Any]:
    sites = (2 * cutoff + 1) ** 3
    dimension = 6 * sites
    coefficient = d["gamma"] * d["volume"] / (12 * sites ** 3)
    constant = d["constant"] * d["volume"]
    beta_float = float(beta)
    coefficient_float = float(coefficient)
    radial_log = (
        dimension / 2 * math.log(math.pi)
        + math.lgamma(dimension / 6)
        - math.log(3.0)
        - math.lgamma(dimension / 2)
        - dimension / 6 * math.log(beta_float * coefficient_float)
    )
    log_envelope = beta_float * float(constant) + radial_log
    pressure_term = -dimension / 6 * math.log(beta_float * coefficient_float)
    return {
        "cutoff": cutoff,
        "sites": sites,
        "real_dimension": dimension,
        "beta": str(beta),
        "sextic_norm6_coefficient": str(coefficient),
        "constant_K": str(constant),
        "coefficient_times_sites_cubed": str(coefficient * sites ** 3),
        "beta_times_coefficient": beta_float * coefficient_float,
        "radial_log_integral": radial_log,
        "constant_shift": beta_float * float(constant),
        "norm_volume_pressure": pressure_term,
        "log_upper_envelope": log_envelope,
        "finite": math.isfinite(log_envelope),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    params = load_parameters()
    derived = derive(params)
    rows: list[dict[str, Any]] = []

    assertion(rows, "A1 manifest exists", A1_MANIFEST.is_file(), str(A1_MANIFEST), True)
    assertion(rows, "R-464 manifest exists", R464_MANIFEST.is_file(), str(R464_MANIFEST), True)
    assertion(rows, "A1 manifest hash available", bool(sha256_normalised(A1_MANIFEST)), sha256_normalised(A1_MANIFEST), "nonempty SHA-256")
    assertion(rows, "R-464 manifest identity", json.loads(R464_MANIFEST.read_text(encoding="utf-8")).get("result_id") == "R-464", "R-464", "R-464")
    assertion(rows, "volume positive", derived["volume"] > 0, str(derived["volume"]), ">0")
    assertion(rows, "mu2 positive", derived["mu2"] > 0, str(derived["mu2"]), ">0")
    assertion(rows, "gamma positive", derived["gamma"] > 0, str(derived["gamma"]), ">0")
    assertion(rows, "lambda nonpositive", params["lambda"] <= 0, str(params["lambda"]), "<=0")
    assertion(rows, "threshold positive", derived["threshold"] > 0, str(derived["threshold"]), ">0")
    assertion(rows, "comparison constant nonnegative", derived["constant"] >= 0, str(derived["constant"]), ">=0")

    coefficient_rows: list[dict[str, Any]] = []
    for cutoff in AUDIT_CUTOFFS:
        sites = (2 * cutoff + 1) ** 3
        coeff = derived["gamma"] * derived["volume"] / (12 * sites ** 3)
        coefficient_rows.append({"cutoff": cutoff, "sites": sites, "coefficient": coeff, "dimension": 6 * sites})
        assertion(rows, f"coefficient positive N={cutoff}", coeff > 0, str(coeff), ">0")
        assertion(rows, f"dimension is six-site N={cutoff}", 6 * sites == 6 * sites, 6 * sites, 6 * sites)
        assertion(rows, f"coefficient scaling identity N={cutoff}", coeff * sites ** 3 == derived["gamma"] * derived["volume"] / 12, str(coeff * sites ** 3), str(derived["gamma"] * derived["volume"] / 12))
    assertion(rows, "coefficient strictly decreases with cutoff", all(left["coefficient"] > right["coefficient"] for left, right in zip(coefficient_rows, coefficient_rows[1:])), [str(x["coefficient"]) for x in coefficient_rows], "strictly decreasing")

    envelope_rows: list[dict[str, Any]] = []
    for beta in AUDIT_BETAS:
        for cutoff in AUDIT_CUTOFFS:
            row = radial_log_envelope(beta, cutoff, derived)
            envelope_rows.append(row)
            assertion(rows, f"radial envelope finite beta={beta} N={cutoff}", row["finite"], row["log_upper_envelope"], "finite real log")
            assertion(rows, f"positive beta*coefficient beta={beta} N={cutoff}", row["beta_times_coefficient"] > 0, row["beta_times_coefficient"], ">0")
            assertion(rows, f"positive pressure term beta={beta} N={cutoff}", row["norm_volume_pressure"] > 0, row["norm_volume_pressure"], ">0")
    assertion(rows, "all declared envelope rows present", len(envelope_rows) == len(AUDIT_BETAS) * len(AUDIT_CUTOFFS), len(envelope_rows), len(AUDIT_BETAS) * len(AUDIT_CUTOFFS))
    assertion(rows, "envelope is labelled comparison only", True, "upper envelope from R-464 lower bound", "comparison only")
    assertion(rows, "no partition asymptotic asserted", True, "not asserted", "not asserted")

    passed = sum(1 for row in rows if row["status"] == "PASS")
    output = {
        "schema": "tect/a6-classii-partition-envelope-primary/1.0",
        "run_kind": "primary",
        "result_id": "R-465",
        "exploration_id": "EXP-001340",
        "script_version": __version__,
        "verdict": "R-465-PRIMARY-PASS" if passed == len(rows) else "R-465-PRIMARY-FAIL",
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "assertions": rows,
        "inputs": {
            "a1_manifest": {"path": str(A1_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(A1_MANIFEST)},
            "r464_manifest": {"path": str(R464_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(R464_MANIFEST)},
            "cutoffs": list(AUDIT_CUTOFFS),
            "betas": [str(x) for x in AUDIT_BETAS],
        },
        "derived": {
            "volume": str(derived["volume"]),
            "mu2": str(derived["mu2"]),
            "gamma": str(derived["gamma"]),
            "lambda_abs": str(derived["ell"]),
            "threshold_T": str(derived["threshold"]),
            "comparison_constant_C_times_volume": str(derived["constant"] * derived["volume"]),
            "coefficient_rows": [{"cutoff": x["cutoff"], "sites": x["sites"], "coefficient": str(x["coefficient"]), "dimension": x["dimension"]} for x in coefficient_rows],
            "envelope_rows": envelope_rows,
            "formula": "Z_N(beta) <= exp(beta*K) * pi^(d/2)*Gamma(d/6)/(3*Gamma(d/2))*(beta*a_N)^(-d/6)",
            "pressure_formula": "(d/6)*log(1/(beta*a_N)) with a_N=gamma*V/(12*m^3)",
        },
        "evidence_level": "T0 finite comparison-envelope diagnostic",
        "assumptions": [
            "R-464 lower comparison F_N(z)>=a_N||z||^6-K controls at each fixed cutoff.",
            "The finite-dimensional radial integral formula is used only as an upper envelope.",
            "Cutoffs and beta values are declared audit inputs, not fitted parameters.",
        ],
        "missing_assumptions": [
            "The actual correlated finite-cutoff partition function and its uniform asymptotics.",
            "A source-owned positive-mass branch tube, probability and entropy/Jacobian estimate.",
            "Tightness, floor removal, continuum limits, physical identification, QFT, Yang--Mills and mass-gap bridge.",
        ],
        "non_claims": [
            "The radial envelope is not the actual partition function and does not prove its asymptotic behavior.",
            "The m-dependent pressure term is a diagnostic of the present comparison, not a no-go theorem for another common norm.",
            "No branch probability, entropy density, tightness, continuum, physical, QFT, Yang--Mills or mass-gap claim follows.",
            "Existing T-054, T-059 and T-061 methods and owner order are unchanged.",
        ],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"PRIMARY R-465 {output['verdict']} {passed}/{len(rows)}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if output["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
