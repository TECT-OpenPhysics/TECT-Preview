#!/usr/bin/env python3
"""Primary exact verifier for R-167 v2.7.

The script reconstructs the BDL admissible optimal-scale arithmetic and the
configuration-Weyl high-momentum packet algebra.  Manifest values are test
oracles, never inputs to the derivation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-fixed-ritz-gevrey-two-truncation-and-raw-configuration-weyl-c0-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
GATES = REPO / "claims/GATES.md"
RESULTS = REPO / "RESULTS-LEDGER.md"
NEGATIVES = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-primary-{SLUG}/result.json"
)


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def derive_truncation_fixture() -> dict[str, Any]:
    # Clearly labelled exact test inputs, not derived outputs.
    alpha = Fraction(1)
    beta = Fraction(1)
    gap = Fraction(1)
    eta = Fraction(1, 800)
    volume = 12
    x_squared = beta * gap / (8 * eta)
    x = math.isqrt(x_squared.numerator // x_squared.denominator)
    if Fraction(x * x) != x_squared:
        raise AssertionError("fixture x must be an exact integer square root")
    n_star = x
    rho = beta * gap / (n_star * n_star)
    ratio = eta / rho
    fixed_order = (
        2
        * alpha
        * beta
        * gap
        * volume
        * Fraction(1, n_star * n_star)
        * ratio ** (n_star + 1)
    )
    equivalent = 2 * alpha * volume * eta * ratio**n_star
    envelope = 16 * alpha * volume * eta * Fraction(1, 8) ** x
    return {
        "alpha": alpha,
        "beta": beta,
        "Gamma": gap,
        "eta": eta,
        "volume": volume,
        "x": x,
        "n_star": n_star,
        "rho": rho,
        "ratio": ratio,
        "fixed_order": fixed_order,
        "equivalent": equivalent,
        "envelope": envelope,
        "fixed_to_envelope": fixed_order / envelope,
        "smallness_beta": eta < beta * gap / 32,
        "smallness_alpha": eta < gap / (32 * alpha),
        "ground_condition": eta < rho / 4,
    }


def derive_gevrey_checks(limit: int = 40) -> dict[str, Any]:
    ratios = []
    majorant_checks = []
    geometric_checks = []
    moment_checks = []
    x = sp.symbols("x", nonnegative=True)
    s = sp.symbols("s", nonnegative=True)
    for r in range(1, limit + 1):
        coefficient_factor = (r + 1) ** (2 * r)
        exact_factorial = math.factorial(r) ** 2
        majorant_checks.append(
            coefficient_factor <= 36**r * exact_factorial
        )
        ratios.append(Fraction((r + 1) ** 2, 7))
    for order in range(0, 13):
        partial = sum((-x) ** n for n in range(order + 1))
        remainder = (-x) ** (order + 1) / (1 + x)
        geometric_checks.append(sp.simplify(1 / (1 + x) - partial - remainder) == 0)
        moment_checks.append(
            sp.integrate(sp.exp(-s) * s**order, (s, 0, sp.oo))
            == sp.factorial(order)
        )
    return {
        "checked_orders": limit,
        "majorant_checks": majorant_checks,
        "divergent_fixture_ratios_t_one_seventh": ratios,
        "last_ratio": ratios[-1],
        "geometric_checks": geometric_checks,
        "moment_checks": moment_checks,
    }


def derive_weyl_packet() -> dict[str, Any]:
    t, chi, hbar, xi2, sigma2 = sp.symbols(
        "t chi hbar xi2 sigma2", positive=True
    )
    p_parallel = chi * sp.pi / (t * xi2) - hbar / 2
    kinetic_phase = sp.simplify(t * xi2 * p_parallel / chi)
    bch_phase = hbar * t * xi2 / (2 * chi)
    total_phase = sp.simplify(kinetic_phase + bch_phase)
    gaussian_exponent = -hbar**2 * t**2 * xi2 / (4 * chi**2 * sigma2)
    packet_translation = sp.simplify(t * p_parallel / chi)
    return {
        "p_parallel": p_parallel,
        "kinetic_phase": kinetic_phase,
        "bch_phase": bch_phase,
        "total_phase": total_phase,
        "gaussian_exponent": gaussian_exponent,
        "packet_translation_at_endpoint": packet_translation,
        "free_relative_expectation": -sp.exp(gaussian_exponent),
    }


def exact_exploration_record() -> dict[str, Any] | None:
    if not EXPLORATIONS.exists():
        return None
    found = []
    for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == "EXP-000828":
            found.append(record)
    return found[0] if len(found) == 1 else None


def run(*, staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check(
        "manifest schema",
        manifest["schema"].endswith("/1.0"),
        manifest["schema"],
        "*/1.0",
        "provenance",
    )
    audit.check(
        "claim nonbearing",
        manifest["claim_bearing"] is False,
        manifest["claim_bearing"],
        False,
        "scope",
    )
    audit.check(
        "result and exploration",
        manifest["result_number"] == "R-167"
        and manifest["result_version"] == "v2.7"
        and manifest["exploration_id"] == "EXP-000828",
        (manifest["result_number"], manifest["result_version"], manifest["exploration_id"]),
        ("R-167", "v2.7", "EXP-000828"),
        "provenance",
    )

    fixture = derive_truncation_fixture()
    oracle = manifest["exact_fixture"]
    expected = {
        "x": str(fixture["x"]),
        "n_star": fixture["n_star"],
        "rho": str(fixture["rho"]),
        "ratio": str(fixture["ratio"]),
        "fixed_order_bound": str(fixture["fixed_order"]),
        "stretched_exponential_envelope": str(fixture["envelope"]),
        "fixed_to_envelope_ratio": str(fixture["fixed_to_envelope"]),
    }
    for key, value in expected.items():
        audit.check(
            f"truncation fixture {key}", oracle[key] == value, oracle[key], value, "truncation"
        )
    audit.check(
        "equivalent BDL remainder forms",
        fixture["fixed_order"] == fixture["equivalent"],
        fixture["fixed_order"],
        fixture["equivalent"],
        "truncation",
    )
    for key in ("smallness_beta", "smallness_alpha", "ground_condition"):
        audit.check(f"fixture {key}", fixture[key] is True, fixture[key], True, "truncation")

    gevrey = derive_gevrey_checks()
    audit.check(
        "Gevrey majorant sampled",
        all(gevrey["majorant_checks"]),
        all(gevrey["majorant_checks"]),
        True,
        "gevrey",
    )
    audit.check(
        "Gevrey counterseries ratio grows",
        all(
            right > left
            for left, right in zip(
                gevrey["divergent_fixture_ratios_t_one_seventh"],
                gevrey["divergent_fixture_ratios_t_one_seventh"][1:],
            )
        )
        and gevrey["last_ratio"] > 1,
        gevrey["last_ratio"],
        ">1 and increasing",
        "gevrey",
    )
    audit.check(
        "exact finite geometric remainders",
        all(gevrey["geometric_checks"]),
        all(gevrey["geometric_checks"]),
        True,
        "gevrey",
    )
    audit.check(
        "exponential moments are factorials",
        all(gevrey["moment_checks"]),
        all(gevrey["moment_checks"]),
        True,
        "gevrey",
    )

    packet = derive_weyl_packet()
    t, chi, hbar, xi2, sigma2 = sp.symbols(
        "t chi hbar xi2 sigma2", positive=True
    )
    audit.check(
        "Weyl packet phase equals pi",
        sp.simplify(packet["total_phase"] - sp.pi) == 0,
        packet["total_phase"],
        sp.pi,
        "weyl",
    )
    audit.check(
        "Gaussian exponent",
        sp.simplify(
            packet["gaussian_exponent"]
            + hbar**2 * t**2 * xi2 / (4 * chi**2 * sigma2)
        )
        == 0,
        packet["gaussian_exponent"],
        "-hbar^2*t^2*xi2/(4*chi^2*sigma2)",
        "weyl",
    )
    audit.check(
        "Galilean endpoint bounded",
        sp.limit(packet["packet_translation_at_endpoint"], t, 0, dir="+")
        == sp.pi / xi2,
        sp.limit(packet["packet_translation_at_endpoint"], t, 0, dir="+"),
        sp.pi / xi2,
        "weyl",
    )
    audit.check(
        "free relative expectation tends minus one",
        sp.limit(packet["free_relative_expectation"], t, 0, dir="+") == -1,
        sp.limit(packet["free_relative_expectation"], t, 0, dir="+"),
        -1,
        "weyl",
    )

    required_tokens = (
        manifest["closed_gate_id"],
        *manifest["negative_ids"],
        "2alpha_M|Lambda||eta|",
        "16alpha_M|Lambda||eta|",
        "Gevrey-two",
        "standard-SW",
        "lim_(t->0,t!=0)||alpha_t(W_xi)-W_xi||=2",
        "No per-lemma or intermediate PDF is issued",
    )
    for token in required_tokens:
        audit.check(
            f"certificate token {token[:48]}",
            token in certificate,
            token in certificate,
            True,
            "certificate",
        )

    scope = manifest["no_overclaim"]
    for token in (
        "neither a convergent all-order SW transformation",
        "physical-lambda-one",
        "common alpha",
        "broken-sector GNS",
        "physical Sector A",
        "Pre-A",
    ):
        audit.check(
            f"scope token {token}", token in scope, token in scope, True, "scope"
        )

    formal_missing: list[str] = []
    if not staged:
        exploration = exact_exploration_record()
        if exploration is None:
            formal_missing.append("EXP-000828")
        if manifest["closed_gate_id"] not in GATES.read_text(encoding="utf-8"):
            formal_missing.append(manifest["closed_gate_id"])
        negative_text = NEGATIVES.read_text(encoding="utf-8")
        formal_missing.extend(
            negative_id
            for negative_id in manifest["negative_ids"]
            if negative_id not in negative_text
        )
        results_text = RESULTS.read_text(encoding="utf-8")
        if "R-167 v2.7" not in results_text or "EXP-000828" not in results_text:
            formal_missing.append("R-167 v2.7")
        audit.check(
            "formal authorities present",
            not formal_missing,
            formal_missing,
            [],
            "formal",
        )

    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "result_number": "R-167",
        "result_version": "v2.7",
        "verdict": "PASS",
        "summary": {
            "passed": len(audit.rows),
            "failed": 0,
            "total": len(audit.rows),
        },
        "derived": {
            "truncation_fixture": {
                key: str(value)
                for key, value in fixture.items()
                if key
                not in {"smallness_beta", "smallness_alpha", "ground_condition"}
            },
            "gevrey_checked_orders": gevrey["checked_orders"],
            "gevrey_last_ratio_t_one_seventh": str(gevrey["last_ratio"]),
            "weyl_total_phase": str(packet["total_phase"]),
            "weyl_gaussian_exponent": str(packet["gaussian_exponent"]),
            "weyl_norm_jump": "2",
            "standard_sw_optimal_scale_transfer": False,
            "all_order_convergence": False,
            "common_alpha_closed": False,
        },
        "source_hashes": {
            path.relative_to(REPO).as_posix(): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"PASS {summary['passed']}/{summary['total']}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
