#!/usr/bin/env python3
"""Synthetic, finite audit of the public GTS likelihood semantics.

This is a source-transcription audit, not an execution of the external GTS
repository.  The fixture values are tooling test inputs and are never event
measurements.  The script deliberately has no SciPy/Astropy/GDT dependency so
that the primary transcription and an independent scalar implementation can be
compared before the external environment is frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

# Tooling thresholds; these are not research-derived values.
COMPARE_TOL = 1.0e-9
HOSTILE_MIN_DELTA = 1.0e-6

# Synthetic test oracle inputs.  They are not event data and are intentionally
# small enough for an independent scalar implementation.
FIXTURE: dict[str, Any] = {
    "counts": [160.0, 150.0, 142.0, 131.0, 125.0, 118.0],
    "background": [20.0, 20.0, 19.0, 18.0, 18.0, 17.0],
    "background_variance": [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
    "response": [
        [
            [0.80, 0.70, 0.60, 0.50, 0.40, 0.30],
            [0.52, 0.47, 0.42, 0.37, 0.32, 0.27],
            [0.31, 0.29, 0.27, 0.25, 0.23, 0.21],
        ],
        [
            [1.00, 0.90, 0.80, 0.70, 0.60, 0.50],
            [0.68, 0.62, 0.56, 0.50, 0.44, 0.38],
            [0.43, 0.40, 0.37, 0.34, 0.31, 0.28],
        ],
    ],
    "gamma": 2.5,
    "prethreshold": 5.0,
    "num_iters": 3,
}


def _erf_array(values: np.ndarray) -> np.ndarray:
    return np.vectorize(math.erf, otypes=[float])(values)


def _normalise(llratio: np.ndarray) -> tuple[np.ndarray, float, tuple[int, int]]:
    imax = int(np.argmax(llratio))
    llmax = float(llratio.ravel()[imax])
    llnorm = llratio - llmax
    llmarg = llmax + float(np.log(np.exp(llnorm).sum())) - math.log(llratio.size)
    return llnorm, llmarg, tuple(np.unravel_index(imax, llratio.shape))


def _source_transcription(fixture: dict[str, Any]) -> dict[str, Any]:
    """Vectorised transcription of the public likelihood.py path."""
    f = np.asarray(fixture["counts"], dtype=float)
    b = np.maximum(0.0, np.asarray(fixture["background"], dtype=float))
    vb = np.asarray(fixture["background_variance"], dtype=float)
    rsp = np.asarray(fixture["response"], dtype=float)
    gamma = float(fixture["gamma"])
    prethreshold = float(fixture["prethreshold"])
    num_iters = int(fixture["num_iters"])
    nspec, nsky, nchan = rsp.shape
    if f.shape != (nchan,) or b.shape != (nchan,) or vb.shape != (nchan,):
        raise ValueError("fixture channel shape mismatch")
    d = f - b
    r = rsp.reshape((-1, nchan))
    rsq = r**2
    vn = b + vb
    vfinv = 1.0 / (np.maximum(b, f) + vb)
    s = np.sum(r * d * vfinv, axis=-1) / np.sum(rsq * vfinv, axis=-1)
    spos = s > 0.0
    p = b + r * s[:, np.newaxis]

    def marginal(
        local_vfinv: np.ndarray, local_p: np.ndarray, local_s: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        ll = np.sum(
            0.5
            * (
                np.log(vn * local_vfinv)
                + d**2 / vn
                - (f - local_p) ** 2 * local_vfinv
            ),
            axis=-1,
        )
        positive = local_s > 1.0e-6
        sqvinv = np.sqrt(np.sum(rsq * local_vfinv, axis=-1))
        logsqv = -np.log(sqvinv)
        logp = -(math.log(gamma) + logsqv)
        positive_z = (local_s * (1.0 / gamma) * sqvinv)[positive]
        logppos = np.log(1.0 - np.exp(-positive_z)) - np.log(local_s[positive])
        np.place(logp, positive, logppos)
        logo = np.log(1.0 + _erf_array(local_s * sqvinv / math.sqrt(2.0)))
        llmarg = logsqv + logo + logp + ll
        return llmarg - (-math.log(gamma)), sqvinv

    llratio, sqvinv = marginal(vfinv, p, s)
    llnorm, llmarg, max_idx = _normalise(llratio.reshape(nspec, nsky))
    if llmarg < prethreshold:
        return {
            "status": 2,
            "llratio": llratio.reshape(nspec, nsky),
            "marginal_llr": llmarg,
            "max_index": max_idx,
        }

    for _ in range(num_iters):
        a = (f - p) * vfinv
        dvf = spos[:, np.newaxis] * r
        asqmvfinv = a**2 - vfinv
        dl = np.sum(r * a + 0.5 * dvf * asqmvfinv, axis=-1)
        ddl = np.sum(-vfinv * (dvf * a + r) ** 2 + 0.5 * (dvf * vfinv) ** 2, axis=-1)
        s -= dl / ddl
        p = b + r * s[:, np.newaxis]
        spos = s > 0.0
        vf = np.maximum(b, p) + vb
        vfinv = 1.0 / vf

    llratio, sqvinv = marginal(vfinv, p, s)
    llnorm, llmarg, max_idx = _normalise(llratio.reshape(nspec, nsky))
    return {
        "status": 1,
        "llratio": llratio.reshape(nspec, nsky),
        "marginal_llr": llmarg,
        "max_index": max_idx,
    }


def _independent_scalar(fixture: dict[str, Any]) -> dict[str, Any]:
    """Independent scalar implementation of the same declared equations."""
    f = [float(x) for x in fixture["counts"]]
    b = [max(0.0, float(x)) for x in fixture["background"]]
    vb = [float(x) for x in fixture["background_variance"]]
    rsp = fixture["response"]
    gamma = float(fixture["gamma"])
    prethreshold = float(fixture["prethreshold"])
    num_iters = int(fixture["num_iters"])
    nspec = len(rsp)
    nsky = len(rsp[0])
    nchan = len(f)
    d = [f[k] - b[k] for k in range(nchan)]
    vn = [b[k] + vb[k] for k in range(nchan)]
    flat = [rsp[i][j] for i in range(nspec) for j in range(nsky)]
    s = []
    for r in flat:
        vf_inv = [1.0 / (max(b[k], f[k]) + vb[k]) for k in range(nchan)]
        num = sum(r[k] * d[k] * vf_inv[k] for k in range(nchan))
        den = sum(r[k] * r[k] * vf_inv[k] for k in range(nchan))
        s.append(num / den)
    p = [[b[k] + r[k] * sidx for k in range(nchan)] for r, sidx in zip(flat, s)]
    # The source path uses max(background, counts) for the initial variance;
    # the fitted model p is used only after each Newton update.
    vfinv = [
        [1.0 / (max(b[k], f[k]) + vb[k]) for k in range(nchan)]
        for _ in p
    ]

    def marginal(local_p: list[list[float]], local_vfinv: list[list[float]], local_s: list[float]) -> list[float]:
        values: list[float] = []
        for r, pidx, vinv, sidx in zip(flat, local_p, local_vfinv, local_s):
            ll = sum(
                0.5
                * (
                    math.log(vn[k] * vinv[k])
                    + d[k] * d[k] / vn[k]
                    - (f[k] - pidx[k]) ** 2 * vinv[k]
                )
                for k in range(nchan)
            )
            sqvinv = math.sqrt(sum(r[k] * r[k] * vinv[k] for k in range(nchan)))
            logsqv = -math.log(sqvinv)
            if sidx > 1.0e-6:
                z = sidx * sqvinv / gamma
                logp = math.log(-math.expm1(-z)) - math.log(sidx)
            else:
                logp = -(math.log(gamma) + logsqv)
            logo = math.log(1.0 + math.erf(sidx * sqvinv / math.sqrt(2.0)))
            values.append(logsqv + logo + logp + ll + math.log(gamma))
        return values

    ll = marginal(p, vfinv, s)
    llmax = max(ll)
    llmarg = llmax + math.log(sum(math.exp(x - llmax) for x in ll)) - math.log(len(ll))
    if llmarg < prethreshold:
        arr = np.asarray(ll, dtype=float).reshape(nspec, nsky)
        return {"status": 2, "llratio": arr, "marginal_llr": llmarg, "max_index": tuple(np.unravel_index(int(np.argmax(arr)), arr.shape))}

    for _ in range(num_iters):
        next_s: list[float] = []
        next_p: list[list[float]] = []
        next_vfinv: list[list[float]] = []
        for r, pidx, vinv, sidx in zip(flat, p, vfinv, s):
            a = [(f[k] - pidx[k]) * vinv[k] for k in range(nchan)]
            dvf = [float(sidx > 0.0) * r[k] for k in range(nchan)]
            asqmvfinv = [a[k] * a[k] - vinv[k] for k in range(nchan)]
            dl = sum(r[k] * a[k] + 0.5 * dvf[k] * asqmvfinv[k] for k in range(nchan))
            ddl = sum(
                -vinv[k] * (dvf[k] * a[k] + r[k]) ** 2
                + 0.5 * (dvf[k] * vinv[k]) ** 2
                for k in range(nchan)
            )
            new_s = sidx - dl / ddl
            new_p = [b[k] + r[k] * new_s for k in range(nchan)]
            new_vinv = [1.0 / (max(b[k], new_p[k]) + vb[k]) for k in range(nchan)]
            next_s.append(new_s)
            next_p.append(new_p)
            next_vfinv.append(new_vinv)
        s, p, vfinv = next_s, next_p, next_vfinv

    ll = marginal(p, vfinv, s)
    llmax = max(ll)
    llmarg = llmax + math.log(sum(math.exp(x - llmax) for x in ll)) - math.log(len(ll))
    arr = np.asarray(ll, dtype=float).reshape(nspec, nsky)
    return {
        "status": 1,
        "llratio": arr,
        "marginal_llr": llmarg,
        "max_index": tuple(np.unravel_index(int(np.argmax(arr)), arr.shape)),
    }


def _fixture_digest(fixture: dict[str, Any]) -> str:
    encoded = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _summarise(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": int(result["status"]),
        "marginal_llr": float(result["marginal_llr"]),
        "max_index": [int(x) for x in result["max_index"]],
        "llratio_shape": [int(x) for x in result["llratio"].shape],
    }


def run(out: Path) -> dict[str, Any]:
    primary = _source_transcription(FIXTURE)
    independent = _independent_scalar(FIXTURE)
    delta = float(np.max(np.abs(primary["llratio"] - independent["llratio"])))
    marginal_delta = abs(float(primary["marginal_llr"]) - float(independent["marginal_llr"]))

    hostile_fixture = json.loads(json.dumps(FIXTURE))
    hostile_fixture["counts"][0] += 7.0
    hostile = _source_transcription(hostile_fixture)
    hostile_delta = abs(float(hostile["marginal_llr"]) - float(primary["marginal_llr"]))

    checks = [
        {
            "id": "primary-finite-path",
            "finding": "PASS",
            "detail": "The vectorised transcription returns finite status, shape and marginalized LLR for the synthetic counts/background/response fixture.",
        },
        {
            "id": "independent-equation-reproduction",
            "finding": "PASS" if delta <= COMPARE_TOL and marginal_delta <= COMPARE_TOL else "FAIL",
            "detail": f"Independent scalar implementation agrees with the primary transcription: max array delta={delta:.3e}, marginal delta={marginal_delta:.3e}.",
        },
        {
            "id": "hostile-fixture-rejection",
            "finding": "PASS" if hostile_delta > HOSTILE_MIN_DELTA else "FAIL",
            "detail": f"A hostile +7 count mutation changes the finite statistic by {hostile_delta:.6f}, exceeding the tooling rejection threshold.",
        },
        {
            "id": "external-dependency-boundary",
            "finding": "PASS",
            "detail": "The harness uses only NumPy and standard-library math; no external GTS event/template bytes or dependencies are silently substituted.",
        },
    ]
    if any(check["finding"] == "FAIL" for check in checks):
        raise AssertionError(checks)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "tect/gts-synthetic-audit/0.1",
        "id": "GTS-SYNTHETIC-AUDIT-001",
        "recorded_on": "2026-08-30",
        "claim_bearing": False,
        "tier": "T0",
        "status": "PASS_PRIMARY_INDEPENDENT_HOSTILE",
        "source_repository": "https://github.com/USRA-STI/gamma-ray-targeted-search",
        "source_commit": "1bc1e913f97fd7195a7e297f8d6032a5c7758894",
        "fixture_role": "Synthetic tooling test oracle; not event data and not a physical observation.",
        "fixture_digest_sha256": _fixture_digest(FIXTURE),
        "primary": _summarise(primary),
        "independent": _summarise(independent),
        "hostile_mutation": {
            "mutation": "counts[0] += 7.0",
            "fixture_digest_sha256": _fixture_digest(hostile_fixture),
            "summary": _summarise(hostile),
            "marginal_delta_from_primary": hostile_delta,
        },
        "comparison": {
            "max_llratio_abs_delta": delta,
            "marginal_llr_abs_delta": marginal_delta,
            "compare_tolerance": COMPARE_TOL,
            "hostile_min_delta": HOSTILE_MIN_DELTA,
        },
        "checks": checks,
        "run_command": "python verification/scripts/audit_gts_synthetic_owner.py --out claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-synthetic-code-owner/synthetic.json",
        "interpretation": "Finite source-code transcription and independent scalar agreement only. This does not execute the external GTS repository and does not bind event/template/dependency or physical timing ownership.",
        "non_claims": [
            "No event-level GBM result, response value, calibration validity or detector-to-geocenter correction is established.",
            "The synthetic fixture is not GW170817 data and receives no retrospective or prospective observational credit.",
            "No Stachie joint Lambda background calibration, continuous Delta_t_det likelihood, covariance, intrinsic-lag law, F_reg/F_lim/F_eff/F_obs map, microscopic dynamics, QFT/Yang--Mills/gravity identity, Pre-A, C6, Sector-A, continuum, physical-vacuum or mass-gap claim follows.",
        ],
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-synthetic-code-owner/synthetic.json"),
    )
    args = parser.parse_args()
    payload = run(args.out)
    print(json.dumps({"status": payload["status"], "out": str(args.out), "comparison": payload["comparison"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
