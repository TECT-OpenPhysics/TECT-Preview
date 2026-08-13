#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v2.8 fixed-cluster theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-fixed-cluster-large-n-physical-point-and-cb-multiplier-c0-boundary"
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

CLOSED_GATE = "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FIXED-COMPLETE-SPECTRAL-CLUSTER-RITZ-LARGE-N-PHYSICAL-LAMBDA-ONE-LOCAL-SW-STRETCHED-EXPONENTIAL-EXTENSIVE-REMAINDER"
NEGATIVE_ID = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0"


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

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
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


def derive_large_n_fixture() -> dict[str, Any]:
    # Clearly labelled test inputs. All other numbers are derived here.
    alpha = sp.Integer(1)
    beta = sp.Integer(1)
    lattice_scale = sp.Integer(74)
    coordination = sp.Integer(6)
    onsite_dimension = sp.Integer(8)
    coordinate_offset = sp.Rational(5, 4)
    coordinate_constant = onsite_dimension * coordinate_offset
    bond_base = 2 * coordinate_constant
    strength_base = coordination * bond_base
    strength_ceiling = strength_base + 1
    local_strength = strength_ceiling
    smallness_factor = 32 * strength_ceiling
    order_denominator = 8 * strength_ceiling
    envelope_prefactor = 16 * strength_ceiling
    gap_lower = lattice_scale**2 / sp.sqrt(2)
    x_squared = sp.simplify(beta * gap_lower / (8 * local_strength))
    n_star = int(sp.floor(sp.sqrt(x_squared)))
    rho = sp.simplify(beta * gap_lower / n_star**2)
    ratio = sp.simplify(local_strength / rho)
    fixed_order = sp.simplify(2 * alpha * local_strength * ratio**n_star)
    square_margin = (lattice_scale**2 // 4) ** 2 - 2 * (smallness_factor // 4) ** 2
    return {
        "coordination": coordination,
        "coordinate_constant": coordinate_constant,
        "bond_base": bond_base,
        "strength_base": strength_base,
        "strength_ceiling": strength_ceiling,
        "smallness_factor": smallness_factor,
        "order_denominator": order_denominator,
        "envelope_prefactor": envelope_prefactor,
        "gap_lower": gap_lower,
        "x_squared": x_squared,
        "n_star": n_star,
        "rho": rho,
        "ratio": ratio,
        "fixed_order": fixed_order,
        "square_margin": square_margin,
    }


def derive_multiplier_fixture() -> dict[str, Any]:
    # A one-dimensional real C_b witness for the approximate-identity step.
    variance = 2 * sp.log(2)
    x = sp.Integer(0)
    y = sp.pi
    convolution_x = sp.simplify(sp.exp(-variance / 2) * sp.cos(x))
    convolution_y = sp.simplify(sp.exp(-variance / 2) * sp.cos(y))
    smoothed_gap = sp.simplify(convolution_x - convolution_y)
    range_supremum = sp.Integer(1)
    range_infimum = -sp.Integer(1)
    oscillation = range_supremum - range_infimum
    return {
        "variance": variance,
        "convolution_x": convolution_x,
        "convolution_y": convolution_y,
        "smoothed_gap": smoothed_gap,
        "oscillation": oscillation,
    }


def exact_exploration_record() -> dict[str, Any] | None:
    for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("id") == "EXP-000831":
            return record
    return None


def run(staged: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    audit = Audit()
    fixture = derive_large_n_fixture()
    multiplier = derive_multiplier_fixture()

    audit.check("schema", manifest["schema"].endswith("/1.0"), manifest["schema"], "*/1.0", "identity")
    audit.check("result version", manifest["result_version"] == "v2.8", manifest["result_version"], "v2.8", "identity")
    audit.check("exploration", manifest["exploration_id"] == "EXP-000831", manifest["exploration_id"], "EXP-000831", "identity")
    audit.check("closed gate exact", manifest["closed_gate_id"] == CLOSED_GATE, manifest["closed_gate_id"], CLOSED_GATE, "identity")
    audit.check("negative exact", manifest["negative_ids"] == [NEGATIVE_ID], manifest["negative_ids"], [NEGATIVE_ID], "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    y = sp.symbols("y", nonnegative=True)
    coordinate_difference = sp.expand((y - 1) ** 2 + sp.Rational(5, 4) - y)
    audit.check("coordinate square identity", sp.expand(coordinate_difference - (y - sp.Rational(3, 2)) ** 2) == 0, coordinate_difference, (y - sp.Rational(3, 2)) ** 2, "large-N")
    audit.check("eight-coordinate constant", 8 * sp.Rational(5, 4) == fixture["coordinate_constant"], 8 * sp.Rational(5, 4), 10, "large-N")
    audit.check("bond base", fixture["bond_base"] == 20, fixture["bond_base"], 20, "large-N")
    audit.check("periodic strength base", fixture["strength_base"] == 120, fixture["strength_base"], 120, "large-N")
    audit.check("strength ceiling", fixture["strength_ceiling"] == 121, fixture["strength_ceiling"], 121, "large-N")
    audit.check("smallness factor", fixture["smallness_factor"] == 3872, fixture["smallness_factor"], 3872, "large-N")
    audit.check("order denominator", fixture["order_denominator"] == 968, fixture["order_denominator"], 968, "large-N")
    audit.check("envelope prefactor", fixture["envelope_prefactor"] == 1936, fixture["envelope_prefactor"], 1936, "large-N")
    audit.check("synthetic threshold margin", fixture["square_margin"] == 113, fixture["square_margin"], 113, "fixture")
    audit.check("synthetic admissible order", fixture["n_star"] == 2, fixture["n_star"], 2, "fixture")
    audit.check("synthetic ratio below one eighth", sp.simplify(sp.Rational(1, 8) - fixture["ratio"]) > 0, fixture["ratio"], "<1/8", "fixture")
    audit.check("synthetic fixed-order fraction", fixture["fixed_order"] == sp.Rational(7086244, 1874161), fixture["fixed_order"], sp.Rational(7086244, 1874161), "fixture")
    audit.check("manifest fixture fraction", manifest["exact_fixture"]["fixed_order_bound"] == "7086244/1874161 |Lambda|", manifest["exact_fixture"]["fixed_order_bound"], "7086244/1874161 |Lambda|", "fixture")

    audit.check("cosine convolution left", multiplier["convolution_x"] == sp.Rational(1, 2), multiplier["convolution_x"], sp.Rational(1, 2), "multiplier")
    audit.check("cosine convolution right", multiplier["convolution_y"] == -sp.Rational(1, 2), multiplier["convolution_y"], -sp.Rational(1, 2), "multiplier")
    audit.check("cosine smoothed gap", multiplier["smoothed_gap"] == 1, multiplier["smoothed_gap"], 1, "multiplier")
    audit.check("cosine oscillation", multiplier["oscillation"] == 2, multiplier["oscillation"], 2, "multiplier")
    audit.check("multiplier lower theorem token", "diam f(R^d)" in manifest["configuration_multiplier_boundary"]["lower_bound"], manifest["configuration_multiplier_boundary"]["lower_bound"], "diam f(R^d)", "multiplier")
    audit.check("real exact theorem token", "equals osc(f)" in manifest["configuration_multiplier_boundary"]["real_case"], manifest["configuration_multiplier_boundary"]["real_case"], "equals osc(f)", "multiplier")

    required_tokens = (
        CLOSED_GATE,
        NEGATIVE_ID,
        "Pi_(M,N)",
        "P_(0,N)",
        "D_M>e_well+C_M",
        "J_(M,N)<=121",
        "3872sqrt(2)",
        "968sqrt(2)",
        "1936alpha_M|Lambda|",
        "7086244/1874161",
        "liminf_(t->0,t!=0)||alpha_t(M_f)-M_f||",
        "lim_(t->0,t!=0)||alpha_t(M_f)-M_f||=osc(f)",
        "No per-lemma or intermediate v2.8 PDF is issued",
    )
    audit.check("certificate exact token ledger", all(token in certificate for token in required_tokens), [token for token in required_tokens if token not in certificate], [], "certificate")
    ritz_firewall = (
        "It is not the SW low block" in certificate
        and "whole finite-dimensional\nonsite Ritz Hilbert space" in certificate
    )
    audit.check("Ritz role firewall", ritz_firewall, ritz_firewall, True, "certificate")
    physical_firewall = "not a\nphysical-world parameter claim" in certificate
    audit.check("physical word firewall", physical_firewall, physical_firewall, True, "scope")
    full_oscillator_firewall = "not\nfull-oscillator cutoff removal" in certificate
    audit.check("no full oscillator", full_oscillator_firewall, full_oscillator_firewall, True, "scope")
    audit.check("all parents open", "All five parent gates remain OPEN" in certificate, "All five parent gates remain OPEN" in certificate, True, "scope")

    if not staged:
        missing: list[str] = []
        exploration = exact_exploration_record()
        if exploration is None:
            missing.append("EXP-000831")
        if CLOSED_GATE not in GATES.read_text(encoding="utf-8"):
            missing.append(CLOSED_GATE)
        if NEGATIVE_ID not in NEGATIVES.read_text(encoding="utf-8"):
            missing.append(NEGATIVE_ID)
        results_text = RESULTS.read_text(encoding="utf-8")
        if "R-167 v2.8" not in results_text or "EXP-000831" not in results_text:
            missing.append("R-167 v2.8")
        audit.check("formal authorities present", not missing, missing, [], "formal")

    derived_fixture = {
        "coordinate_constant": str(fixture["coordinate_constant"]),
        "bond_base": str(fixture["bond_base"]),
        "strength_ceiling": str(fixture["strength_ceiling"]),
        "smallness_factor": str(fixture["smallness_factor"]),
        "order_denominator": str(fixture["order_denominator"]),
        "envelope_prefactor": str(fixture["envelope_prefactor"]),
        "threshold_square_margin": str(fixture["square_margin"]),
        "n_star": fixture["n_star"],
        "rho": str(fixture["rho"]),
        "ratio": str(fixture["ratio"]),
        "fixed_order_bound": f"{fixture['fixed_order']} |Lambda|",
    }
    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "result_number": "R-167",
        "result_version": "v2.8",
        "verdict": "PASS",
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "derived": {
            "large_n_fixture": derived_fixture,
            "multiplier_fixture": {
                "variance": str(multiplier["variance"]),
                "convolution_x": str(multiplier["convolution_x"]),
                "convolution_y": str(multiplier["convolution_y"]),
                "smoothed_gap": str(multiplier["smoothed_gap"]),
                "real_oscillation": str(multiplier["oscillation"]),
            },
            "uniform_in_M": False,
            "full_oscillator_cutoff_removed": False,
            "standard_sw_growing_order": False,
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
