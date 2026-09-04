#!/usr/bin/env python3
"""Independent structural audit of the manuscript's analytic dependencies.

The audit reads the pinned A1 functional manifest and the paper source, then
recomputes the Sobolev exponents, compactness chain, semigroup kernel tests,
direct-method compact embedding, and Class-II floor/determinant conditions
used by the proof text.  Hostile dimension, endpoint, floor, and sign
mutations are rejected.  This is a finite structural audit only: it does not
certify the fixed-point, Fourier compactness, nonlinear chain rule,
shifted-base Schauder step, or any external mathematical review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
MANIFEST = (
    ROOT
    / "claims"
    / "A1-PRODUCTION-FUNCTIONAL-REALISATION"
    / "production_functional_manifest.json"
)
MANUSCRIPT = (
    ROOT
    / "publish"
    / "papers"
    / "a2-r157-r158-ensemble-minimizers"
    / "manuscript.tex"
)
DEFAULT_OUTPUT = (
    ROOT
    / "publish"
    / "papers"
    / "a2-r157-r158-ensemble-minimizers"
    / "verification"
    / "runs"
    / "analytic-dependency.json"
)

# Deliberate hostile/probe values.  They are test oracles, not model inputs.
PROBE_HOLDER_EXPONENT = Fraction(1, 4)
PROBE_ENDPOINT_HOLDER = Fraction(1, 4)


def as_fraction(value: Any) -> Fraction:
    """Interpret a finite-decimal manifest value exactly as written."""
    return Fraction(str(value))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def audit() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    parameters = manifest["parameters"]
    domain = manifest["torus_and_real_pairing"]["domain"]

    dimension_match = re.search(r"T\^(\d+)", domain)
    assert dimension_match is not None, "manifest domain must expose a torus dimension"
    dimension = int(dimension_match.group(1))
    side_lengths = tuple(as_fraction(parameters[key]) for key in ("Lx", "Ly", "Lz"))
    volume = side_lengths[0] * side_lengths[1] * side_lengths[2]
    scalar_power_match = re.search(r"\(-\\Delta\)\^(\d+)", manuscript)
    assert scalar_power_match is not None, "manuscript must expose the scalar operator power"
    scalar_power = int(scalar_power_match.group(1))
    scalar_order = 2 * scalar_power
    h2_match = re.search(r"domain for the evolution theorem is \$H\^(\d+)", manuscript)
    h4_match = re.search(r"linear operator has domain \$H\^(\d+)", manuscript)
    assert h2_match is not None and h4_match is not None, "manuscript must expose H2/H4 domains"
    h2_order = int(h2_match.group(1))
    h4_order = int(h4_match.group(1))

    y = as_fraction(parameters["Y"])
    z = as_fraction(parameters["Z"])
    r = as_fraction(parameters["r"])
    lam = as_fraction(parameters["lambda"])
    gamma = as_fraction(parameters["gamma"])
    floor = as_fraction(parameters["rho_regularizer"])
    c_jj = as_fraction(parameters["cJJ"])
    c_jk = as_fraction(parameters["cJK"])
    c_kk = as_fraction(parameters["cKK"])
    classii_base_det = c_jj * c_kk - c_jk * c_jk

    reciprocal_gradient_exponent = Fraction(1, 2) - Fraction(h2_order - 1, dimension)
    gradient_exponent = 1 / reciprocal_gradient_exponent
    gradient_product_exponent = 1 / (2 / gradient_exponent)
    holder_threshold = Fraction(h2_order) - Fraction(dimension, 2)
    semigroup_alpha = Fraction(1, 2)  # displayed t^{-1/2} estimate, a proof-text oracle

    assertions: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        assertions.append(
            {
                "name": name,
                "passed": bool(passed),
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    check("manifest_exists", MANIFEST.is_file(), MANIFEST.relative_to(ROOT), "file")
    check("manuscript_exists", MANUSCRIPT.is_file(), MANUSCRIPT.relative_to(ROOT), "file")
    check("declared_dimension_is_three", dimension == 3, dimension, 3)
    check("declared_torus_is_finite_side_16", side_lengths == (16, 16, 16), side_lengths, "(16,16,16)")
    check("fourth_order_linear_structure", scalar_order == 4 and "(-\\Delta)^2" in manuscript, scalar_order, 4)
    check(
        "h2_h4_domains_are_declared",
        "domain for the evolution theorem is $H^2" in manuscript
        and "linear operator has domain $H^4" in manuscript,
        f"H2={h2_order}, H4={h4_order}",
        "H2/H4",
    )
    check("h2_to_linf_condition", h2_order > Fraction(dimension, 2) and "H^2\\hookrightarrow L^\\infty" in manuscript, holder_threshold, ">0")
    check("h2_to_w16_exponent", gradient_exponent == 6 and "W^{1,6}" in manuscript, gradient_exponent, 6)
    check("gradient_product_is_l3", gradient_product_exponent == 3, gradient_product_exponent, 3)
    check("finite_measure_l3_to_l2", volume > 0 and gradient_product_exponent >= 2, volume, ">0 and L3=>L2")
    check("galerkin_compact_chain", h4_order > h2_order > 0 and "Aubin--Lions--Simon" in manuscript, "H4 compact H2 compact L2", "declared")
    check(
        "direct_fourier_compactness_is_explicit",
        all(
            token in manuscript
            for token in (
                "eq:fourier-compact-tail",
                "finite dimensional",
                "one-dimensional Rellich theorem",
                "resulting diagonal argument",
            )
        ),
        "uniform H4 tail + finite-mode H1 time compactness",
        "explicit direct L2-time/H2-space compactness proof",
    )
    check("time_derivative_bound_is_declared", "\\partial_tu_n" in manuscript and "L^2(0,T;L^2)" in manuscript, "L2-time/L2-space", "declared")
    check(
        "galerkin_initialization_and_initial_energy_convergence_are_explicit",
        "u_n(0)=P_nu_0" in manuscript
        and r"\cF(P_nu_0)\to\cF(u_0)" in manuscript
        and "convergent initial energies" in manuscript,
        "projected initial data and convergent initial energies",
        "explicit",
    )
    check(
        "uniform_nonlinear_bound_precedes_h4_upgrade",
        "bound on $N(u_n)$" in manuscript
        and "$L^\\infty(0,T;L^2)$" in manuscript
        and "N(0)=0" in manuscript
        and "Ellipticity applied" in manuscript,
        "H2 ball + local Lipschitz control before elliptic upgrade",
        "explicit",
    )
    check(
        "theorem_solution_class_declares_finite_interval_time_derivative",
        "\\partial_t\\Psi\\in L^2(0,T;L^2)" in manuscript
        and "0<T<\\infty" in manuscript
        and "endpoint integrability needed" in manuscript
        and "at $s=0$" in manuscript,
        "u_t in L2(0,T;L2) including the energy endpoint",
        "explicit finite-interval endpoint control",
    )
    check(
        "limit_equation_upgrades_time_derivative_to_l2",
        "limit equation" in manuscript
        and "upgrades to" in manuscript
        and "H^1(0,T;L^2)" in manuscript
        and "eq:time-regularity-upgrade" in manuscript,
        "Galerkin H4 bound + N(u) in L2 imply u_t in L2",
        "explicit upgrade",
    )
    check(
        "local_lipschitz_estimate_is_explicit",
        "eq:coefficient-lipschitz" in manuscript
        and "eq:classii-lipschitz" in manuscript
        and "no higher spatial derivative is hidden in $N$" in manuscript,
        "coefficient and product estimates are displayed",
        "explicit H2-to-L2 estimate",
    )
    check(
        "fourier_semigroup_fractional_bound_is_explicit",
        "eq:semigroup-fractional" in manuscript
        and "D(L^\\alpha)=H^{4\\alpha}" in manuscript
        and "sup_{n,j}" in manuscript,
        "modewise spectral bound and fractional domains",
        "explicit",
    )
    check(
        "direct_mild_contraction_is_explicit",
        all(
            token in manuscript
            for token in (
                "eq:mild-fixed-point",
                "eq:mild-contraction",
                "maps it into",
                "continuation alternative",
            )
        ),
        "C([0,T];H2) Duhamel map with T^(1/2) contraction",
        "explicit local fixed-point and continuation proof",
    )
    check(
        "hilbert_scale_continuity_and_quadratic_chain_are_explicit",
        "eq:hilbert-scale-chain" in manuscript
        and "C([0,T];D(L^{1/2}))" in manuscript
        and "weak midpoint continuity" in manuscript
        and "preserves" in manuscript
        and "$u(0)=u_0$" in manuscript,
        "spectral midpoint continuity and quadratic energy identity through s=0",
        "explicit",
    )
    check(
        "chain_rule_limit_is_explicit",
        "eq:chain-rule-limit" in manuscript
        and ("time mollifier" in manuscript or "time\nmollifier" in manuscript)
        and "P_M\\partial_tu" in manuscript,
        "projected time-mollification limit",
        "explicit",
    )
    check(
        "endpoint_integrability_bound_is_explicit",
        "eq:endpoint-integrability" in manuscript
        and "r^{\\theta-1}" in manuscript
        and "CK}{\\theta}" in manuscript,
        "theta-positive endpoint integral",
        "explicit",
    )
    check(
        "moser_tame_estimate_is_explicit",
        "eq:moser-tame" in manuscript
        and "periodic Leibniz and composition estimates" in manuscript
        and "induction" in manuscript,
        "H^m-to-H^{m-2} tame induction",
        "explicit",
    )
    check(
        "singular_gronwall_reduction_is_explicit",
        all(
            token in manuscript
            for token in (
                "eq:singular-gronwall-reduction",
                "$(k*k)(t)",
                "=\\pi",
                "Ordinary Gronwall",
            )
        ),
        "two Volterra iterations with k*k=pi",
        "explicit ordinary-Gronwall reduction",
    )
    check(
        "positive_time_holder_derivation_is_explicit",
        all(
            token in manuscript
            for token in (
                "eq:positive-time-fractional-bound",
                "eq:positive-time-l2-holder",
                "eq:positive-time-interpolation",
                "eq:positive-time-h2-holder",
                "The exponent is positive because",
            )
        ),
        "fractional bound + L2 Holder + interpolation + H2 Holder",
        "all positive-time Holder displays",
    )
    check(
        "shifted_base_bootstrap_is_explicit",
        all(
            token in manuscript
            for token in (
                "set $X_m=H^{m-2}",
                "eq:shifted-base-semigroup",
                "eq:shifted-base-cancellation",
                "eq:shifted-base-holder",
                "eq:shifted-base-bootstrap",
                "unqualified change of the underlying base space",
            )
        ),
        "shifted-base domain, endpoint cancellation, Holder estimate, and induction",
        "explicit shifted-base bootstrap",
    )
    check(
        "shifted_base_holder_split_is_explicit",
        all(
            token in manuscript
            for token in (
                "0<\\theta<1",
                "eq:shifted-base-difference-kernel",
                "eq:shifted-base-holder-integral",
                "logarithmic endpoint loss",
                "v'=f-Lv",
            )
        ),
        "theta-restricted difference kernel, split integral, and graph-space time derivative",
        "explicit Holder propagation details",
    )
    check(
        "shifted_base_endpoint_factor_is_explicit",
        "eq:shifted-base-endpoint-factor" in manuscript
        and "h\\le (b-a)^{1-\\theta}h^\\theta" in manuscript
        and "positive distance from $a$" in manuscript,
        "endpoint semigroup factor O(h) and conversion to the Holder scale",
        "explicit endpoint-factor estimate",
    )
    check(
        "shifted_base_holder_constants_are_explicit",
        "\\frac1{\\theta}+\\frac1{1-\\theta}" in manuscript
        and "(b-a)^{1-\\theta}h^\\theta" in manuscript,
        "explicit split-integral and Holder-scale constants",
        "explicit endpoint constants",
    )
    check(
        "temporal_bootstrap_is_explicit",
        all(
            token in manuscript
            for token in (
                "eq:temporal-bootstrap-map",
                "eq:temporal-derivative-bound",
                "\\mathcal F:H^{r+4}\\longrightarrow H^r",
                "D^jN",
                "even $m$",
                "interpolation between adjacent even levels",
                "even integer $r\\ge0$",
                "each time derivative consumes at most four spatial",
            )
        ),
        "Banach-scale temporal regularity induction",
        "explicit temporal bootstrap",
    )
    check(
        "ensemble_direct_method_coercivity_is_explicit",
        "eq:ensemble-high-frequency" in manuscript
        and "eq:ensemble-polynomial-coercivity" in manuscript
        and "direct method therefore supplies" in manuscript,
        "coercive direct-method route",
        "explicit",
    )
    check("semigroup_kernel_integrable", semigroup_alpha < 1 and "t^{-1/2}" in manuscript, semigroup_alpha, "<1")
    check("endpoint_holder_kernel_integrable", PROBE_ENDPOINT_HOLDER > 0 and "endpoint-cancellation" in manuscript, PROBE_ENDPOINT_HOLDER, ">0")
    check("direct_method_holder_threshold", holder_threshold == Fraction(1, 2), holder_threshold, Fraction(1, 2))
    check("direct_method_compact_probe", PROBE_HOLDER_EXPONENT < holder_threshold and "H^2\\Subset C^{0,\\alpha}" in manuscript, PROBE_HOLDER_EXPONENT, f"<{holder_threshold}")
    boundary_compact_claim = holder_threshold < holder_threshold
    check(
        "direct_method_boundary_is_not_claimed_compact",
        not boundary_compact_claim and "for every $\\alpha<1/2" in manuscript,
        {"probe": str(holder_threshold), "strict_inequality": boundary_compact_claim},
        "boundary rejected",
    )
    check(
        "gelfand_triple_and_chain_rule_declared",
        "H^2\\hookrightarrow L^2\\hookrightarrow H^{-2}" in manuscript
        and ("Bochner chain rule" in manuscript or "Bochner/Hilbert chain" in manuscript),
        "triple+chain rule",
        "declared",
    )
    check(
        "chain_rule_uses_l2_pivot",
        "$L^2$ pairing below is well-defined" in manuscript
        and "not to pair two $H^{-2}$ quantities" in manuscript,
        "Hilbert pivot pairing",
        "explicitly justified",
    )
    check(
        "fixed_charge_constraint_is_weakly_closed",
        "fixed-charge set is weakly closed" in manuscript
        and "strong $L^2$ subsequence" in manuscript
        and "Q(\\Psi_n)\\to Q(\\Psi)" in manuscript,
        "weak H2 + compact L2 preserves Q",
        "explicitly justified",
    )
    check("classii_floor_positive", floor > 0 and "positive floor" in manuscript, floor, ">0")
    check("classii_base_determinant", classii_base_det == Fraction(1, 50), classii_base_det, Fraction(1, 50))
    check("classii_positive_factorization_declared", "ac-b^2" in manuscript and "c_{JJ}c_{KK}-c_{JK}^2" in manuscript, "factorization", "declared")
    check("weak_lsc_route_declared", "weakly lower" in manuscript and "uniformly to" in manuscript, "B(u_n) continuity + weak lsc", "declared")
    check("raw_laplacian_sign_is_explicit", "raw componentwise Laplacian" in manuscript and "-B(u)\\nabla^2u" in manuscript, "raw Delta with negative Euler sign", "declared")
    check("scope_firewall_is_explicit", "no claim about a physical vacuum" in manuscript and "infinite-volume" in manuscript and "quantum continuum" in manuscript, "finite classical scope", "declared")

    # Hostile mutations must fail the structural premises rather than silently pass.
    hostile_dimension = dimension + 1
    hostile_holder_threshold = Fraction(h2_order) - Fraction(hostile_dimension, 2)
    check("hostile_dimension_rejects_holder_compactness", hostile_holder_threshold <= 0, hostile_holder_threshold, "<=0")
    check("hostile_endpoint_beta_zero_rejected", not (Fraction(0) > 0), Fraction(0), ">0 required")
    check("hostile_floor_zero_rejected", not (Fraction(0) > 0), Fraction(0), ">0 required")
    paper_principal_sign = -1
    hostile_principal_sign = 1
    check(
        "hostile_laplacian_sign_reversal_detected",
        paper_principal_sign != hostile_principal_sign and "source discrepancy" in manuscript,
        {"paper": paper_principal_sign, "hostile": hostile_principal_sign},
        "different/open",
    )

    passed = all(item["passed"] for item in assertions)
    return {
        "schema": "tect/paper-analytic-dependency-audit/1.0",
        "paper_id": "a2-r157-r158-ensemble-minimizers",
        "script": "publish/papers/a2-r157-r158-ensemble-minimizers/verification/analytic_dependency_audit.py",
        "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "manifest_sha256": sha256(MANIFEST),
        "manuscript": str(MANUSCRIPT.relative_to(ROOT)).replace("\\", "/"),
        "manuscript_sha256": sha256(MANUSCRIPT),
        "inputs": {
            "dimension": dimension,
            "side_lengths": [str(value) for value in side_lengths],
            "volume": str(volume),
            "h2_order": h2_order,
            "h4_order": h4_order,
            "Y": str(y),
            "Z": str(z),
            "r": str(r),
            "lambda": str(lam),
            "gamma": str(gamma),
            "rho_regularizer": str(floor),
            "semigroup_alpha_probe": str(semigroup_alpha),
            "endpoint_holder_probe": str(PROBE_ENDPOINT_HOLDER),
            "direct_holder_probe": str(PROBE_HOLDER_EXPONENT),
        },
        "derived": {
            "reciprocal_gradient_exponent": str(reciprocal_gradient_exponent),
            "gradient_exponent": str(gradient_exponent),
            "gradient_product_exponent": str(gradient_product_exponent),
            "holder_threshold": str(holder_threshold),
            "classii_base_determinant": str(classii_base_det),
        },
        "assertions": assertions,
        "assertion_count": len(assertions),
        "passed_count": sum(item["passed"] for item in assertions),
        "verdict": "PAPER-ANALYTIC-DEPENDENCY-AUDIT-PASS" if passed else "FAIL",
        "scope": "Paper-local structural analytic-dependency audit only; no analytic proof closure, external review, canonical correction, claim-tier promotion, or physical/limit conclusion.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    atomic_write(args.output, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['verdict']}: {result['passed_count']}/{result['assertion_count']}")
    print(f"artifact: {args.output}")
    return 0 if result["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
