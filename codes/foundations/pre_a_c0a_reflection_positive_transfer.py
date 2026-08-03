#!/usr/bin/env python3
"""Primary exact certificate for PA-C0A-RPTM-FS-v0.

The candidate is a finite-state reflection-positive transfer benchmark.  A
positive reversible Markov transfer operator and a discrete time spacing are
declared as C0-A primitives; the script reconstructs their unique positive
self-adjoint generator and tests the sharp negative-eigenvalue boundary.  It
does not claim that time, locality, or a causal cone has emerged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0A-RPTM-FS-v0"
SLUG = "pre-a-c0a-reflection-positive-transfer"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, col]) for col in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
                "group": group,
            }
        )


def projector_transfer(pi: sp.Matrix, alpha: sp.Expr) -> tuple[sp.Matrix, sp.Matrix]:
    identity = sp.eye(pi.rows)
    projector = sp.ones(pi.rows, 1) * pi.T
    transfer = sp.simplify(alpha * identity + (1 - alpha) * projector)
    return projector, transfer


def weighted_adjoint(operator: sp.Matrix, weight: sp.Matrix) -> sp.Matrix:
    return sp.simplify(weight.inv() * operator.conjugate().T * weight)


def derive() -> dict[str, Any]:
    audit = Audit()

    pi = sp.Matrix([sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(1, 6)])
    weight = sp.diag(*pi)
    identity = sp.eye(3)
    ones = sp.ones(3, 1)
    alpha = sp.Rational(2, 3)
    projector, transfer = projector_transfer(pi, alpha)
    complement = identity - projector

    audit.check(
        "probability vector is normalized",
        sum(pi) == 1 and all(value > 0 for value in pi),
        (sum(pi), list(pi)),
        "positive normalized probability",
        "transfer",
    )
    static_energy = sp.Matrix([sp.log(2), sp.log(3), sp.log(6)])
    boltzmann_weights = static_energy.applyfunc(lambda value: sp.exp(-value))
    audit.check(
        "static energy representative reproduces the probability",
        boltzmann_weights == pi,
        boltzmann_weights,
        pi,
        "static_boundary",
    )
    audit.check(
        "stationary projector is idempotent",
        projector * projector == projector,
        projector * projector,
        projector,
        "transfer",
    )
    audit.check(
        "stationary projector preserves constants",
        projector * ones == ones,
        projector * ones,
        ones,
        "transfer",
    )
    audit.check(
        "transfer is stochastic",
        transfer * ones == ones and all(entry >= 0 for entry in transfer),
        transfer * ones,
        ones,
        "transfer",
    )
    audit.check(
        "detailed balance",
        weight * transfer == transfer.T * weight,
        weight * transfer,
        transfer.T * weight,
        "transfer",
    )
    audit.check(
        "stationary measure",
        sp.simplify(transfer.T * pi) == pi,
        sp.simplify(transfer.T * pi),
        pi,
        "transfer",
    )
    eigenvalues = transfer.eigenvals()
    audit.check(
        "positive transfer spectrum",
        eigenvalues == {sp.Integer(1): 1, alpha: 2},
        eigenvalues,
        {sp.Integer(1): 1, alpha: 2},
        "transfer",
    )

    # Operator positivity and entrywise Markov positivity are independent
    # requirements.  This exact control has P1=1 and 0<P<=I but one negative
    # transition entry, so it is not a Markov kernel.
    uniform = sp.Matrix([sp.Rational(1, 3)] * 3)
    uniform_weight = sp.diag(*uniform)
    contrast = sp.Matrix([1, 1, -2])
    positive_non_markov = identity - sp.Rational(1, 10) * contrast * contrast.T
    positive_non_markov_eigenvalues = positive_non_markov.eigenvals()
    audit.check(
        "operator-positive row-preserving control is not entrywise Markov",
        positive_non_markov * ones == ones
        and uniform_weight * positive_non_markov
        == positive_non_markov.T * uniform_weight
        and positive_non_markov_eigenvalues
        == {sp.Integer(1): 2, sp.Rational(2, 5): 1}
        and min(positive_non_markov) == sp.Rational(-1, 10),
        (
            positive_non_markov * ones,
            positive_non_markov_eigenvalues,
            min(positive_non_markov),
        ),
        (ones, {sp.Integer(1): 2, sp.Rational(2, 5): 1}, sp.Rational(-1, 10)),
        "transfer_boundary",
    )
    audit.check(
        "transfer projector decomposition",
        sp.simplify(transfer - (projector + alpha * complement)) == sp.zeros(3),
        transfer,
        projector + alpha * complement,
        "transfer",
    )

    # The generator follows by spectral functional calculus.  The time spacing
    # is an explicit positive input and is not derived.
    time_spacing = sp.symbols("a", positive=True)
    gap = (sp.log(3) - sp.log(2)) / time_spacing
    generator = sp.simplify(gap * complement)
    reconstructed_transfer = sp.simplify(
        projector + sp.exp(-time_spacing * gap) * complement
    )
    audit.check(
        "projector logarithm reconstructs the transfer",
        reconstructed_transfer == transfer,
        reconstructed_transfer,
        transfer,
        "generator",
    )
    audit.check(
        "generator is weighted-self-adjoint",
        weighted_adjoint(generator, weight) == generator,
        weighted_adjoint(generator, weight),
        generator,
        "generator",
    )
    generator_eigenvalues = generator.eigenvals()
    generator_nonzero = [
        value for value in generator_eigenvalues if sp.simplify(value) != 0
    ]
    audit.check(
        "generator spectrum and gap",
        generator_eigenvalues.get(sp.Integer(0)) == 1
        and len(generator_nonzero) == 1
        and generator_eigenvalues[generator_nonzero[0]] == 2
        and sp.simplify(generator_nonzero[0] - gap) == 0,
        generator_eigenvalues,
        {sp.Integer(0): 1, gap: 2},
        "generator",
    )
    audit.check(
        "generator kernel is one-dimensional span of constants",
        (generator * ones).applyfunc(sp.simplify) == sp.zeros(3, 1)
        and len(generator.nullspace()) == 1,
        ((generator * ones).applyfunc(sp.simplify), len(generator.nullspace())),
        (sp.zeros(3, 1), 1),
        "generator",
    )

    # Exact weighted variance form proves positivity of H without relying on a
    # floating eigenvalue calculation.
    f0, f1, f2 = sp.symbols("f0 f1 f2", real=True)
    vector = sp.Matrix([f0, f1, f2])
    variance_form = sp.expand((vector.T * weight * complement * vector)[0])
    pair_form = sp.expand(
        pi[0] * pi[1] * (f0 - f1) ** 2
        + pi[0] * pi[2] * (f0 - f2) ** 2
        + pi[1] * pi[2] * (f1 - f2) ** 2
    )
    audit.check(
        "weighted complement is exactly the variance form",
        sp.expand(variance_form - pair_form) == 0,
        variance_form,
        pair_form,
        "generator",
    )

    # Spectral-projector unitary reconstruction.  z and zbar are an exact
    # algebraic fixture with zbar*z=1.
    phase, phase_bar = sp.symbols("z zbar")
    unitary = projector + phase * complement
    unitary_adjoint = projector + phase_bar * complement
    unitary_product = sp.expand(unitary_adjoint * unitary).subs(phase_bar * phase, 1)
    audit.check(
        "spectral-projector real-time group is unitary",
        sp.simplify(unitary_product - identity) == sp.zeros(3),
        sp.simplify(unitary_product),
        identity,
        "generator",
    )

    # Two distinct positive transfers share the same static marginal but have
    # different generators.  F=-log(pi) is therefore insufficient to select P.
    alpha_alt = sp.Rational(1, 2)
    _, transfer_alt = projector_transfer(pi, alpha_alt)
    gap_alt = sp.log(2) / time_spacing
    audit.check(
        "same static probability supports distinct positive transfers",
        transfer_alt != transfer and transfer_alt.T * pi == pi,
        (transfer_alt != transfer, transfer_alt.T * pi),
        (True, pi),
        "static_boundary",
    )
    audit.check(
        "same static probability supports distinct gaps",
        sp.simplify(gap_alt - gap) != 0,
        (gap_alt, gap),
        "different",
        "static_boundary",
    )

    # Site-reflection positivity is a conditional-square identity.  A finite
    # exact Gram fixture checks it, and a link-reflection Gram uses <f,Pg>_pi.
    tests = sp.Matrix(
        [
            [1, 0],
            [2, 3],
            [-1, 2],
        ]
    )
    site_gram = sp.simplify(tests.T * weight * tests)
    link_gram = sp.simplify(tests.T * weight * transfer * tests)
    audit.check(
        "site-reflection Gram fixture is positive definite",
        site_gram[0, 0] > 0 and site_gram.det() > 0,
        (site_gram[0, 0], site_gram.det()),
        "positive leading principal minors",
        "reflection_positivity",
    )
    audit.check(
        "link-reflection Gram fixture is positive definite",
        link_gram[0, 0] > 0 and link_gram.det() > 0,
        (link_gram[0, 0], link_gram.det()),
        "positive leading principal minors",
        "reflection_positivity",
    )

    # Sharp negative control: detailed balance and nonnegative transition
    # entries alone do not imply operator positivity or a real positive log.
    alpha_bad = sp.Rational(-1, 10)
    _, transfer_bad = projector_transfer(pi, alpha_bad)
    bad_eigenvalues = transfer_bad.eigenvals()
    zero_mean = sp.Matrix([1, sp.Rational(-3, 2), 0])
    zero_mean_check = (pi.T * zero_mean)[0]
    bad_link_form = sp.simplify(
        (zero_mean.T * weight * transfer_bad * zero_mean)[0]
    )

    # The zero-spectrum boundary is link-reflection positive but has no finite
    # self-adjoint logarithmic generator: exp(-aH) is strictly positive for
    # every finite self-adjoint H.
    transfer_zero = projector
    zero_eigenvalues = transfer_zero.eigenvals()
    zero_link_form = sp.simplify(
        (zero_mean.T * weight * transfer_zero * zero_mean)[0]
    )
    audit.check(
        "zero-spectrum control is Markov and link-positive but not strictly positive",
        transfer_zero * ones == ones
        and all(entry > 0 for entry in transfer_zero)
        and weight * transfer_zero == transfer_zero.T * weight
        and zero_eigenvalues == {sp.Integer(1): 1, sp.Integer(0): 2}
        and zero_link_form == 0,
        (transfer_zero * ones, zero_eigenvalues, zero_link_form),
        (ones, {sp.Integer(1): 1, sp.Integer(0): 2}, 0),
        "zero_spectrum_boundary",
    )
    audit.check(
        "negative-control transfer remains stochastic and reversible",
        transfer_bad * ones == ones
        and all(entry >= 0 for entry in transfer_bad)
        and weight * transfer_bad == transfer_bad.T * weight,
        (transfer_bad * ones, min(transfer_bad), weight * transfer_bad == transfer_bad.T * weight),
        (ones, ">=0", True),
        "negative_control",
    )
    audit.check(
        "negative-control transfer has a negative eigenvalue",
        bad_eigenvalues == {sp.Integer(1): 1, alpha_bad: 2},
        bad_eigenvalues,
        {sp.Integer(1): 1, alpha_bad: 2},
        "negative_control",
    )
    audit.check(
        "negative-control link-reflection form is negative",
        zero_mean_check == 0 and bad_link_form < 0,
        (zero_mean_check, bad_link_form),
        (0, "<0"),
        "negative_control",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "C0A-REFLECTION-POSITIVE-FINITE-STATE-TRANSFER",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 C0-A benchmark certificate; not a TECT claim, physical time-emergence theorem, or cosmology",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "primitive_inputs": {
            "state_space": "three finite states",
            "static_probability": pi,
            "static_energy_representative": static_energy,
            "transfer": transfer,
            "transfer_conditions": "entrywise-nonnegative row-stochastic, detailed-balanced, and strictly positive with P<=I on L2(pi)",
            "time_spacing": "a>0",
            "time_order_and_reflection": "declared C0-A primitives",
        },
        "exact_results": {
            "stationary_projector": projector,
            "transfer_spectrum": eigenvalues,
            "positive_weighted_self_adjoint_transfer": True,
            "generator": "H_a=log(3/2)*(I-Pi_pi)/a",
            "generator_spectrum": generator_eigenvalues,
            "ground_kernel": "span{constant function 1}",
            "gap": gap,
            "transfer_reconstruction": "P=exp(-a H_a)",
            "unitary_group": "U(t)=exp(-it H_a)=Pi_pi+exp(-it log(3/2)/a)*(I-Pi_pi)",
            "site_reflection_positivity": "stationary reversible Markov conditional-square identity",
            "link_reflection_positivity": "requires P>=0 on L2(pi)",
            "same_static_marginal_distinct_transfer_parameters": [alpha, alpha_alt],
            "same_static_marginal_distinct_gaps": [gap, gap_alt],
            "negative_control_alpha": alpha_bad,
            "negative_control_spectrum": bad_eigenvalues,
            "negative_control_link_form": bad_link_form,
            "zero_spectrum_control_spectrum": zero_eigenvalues,
            "zero_spectrum_control_link_form": zero_link_form,
            "operator_positive_non_markov_control_spectrum": positive_non_markov_eigenvalues,
            "operator_positive_non_markov_negative_entry": sp.Rational(-1, 10),
        },
        "lane_verdict": "ADVANCE AS A C0-A TEMPORAL CALIBRATION: positive reflection-compatible transfer data reconstruct a positive self-adjoint generator and unitary group; time order and spacing remain declared primitives, while causal structure is absent",
        "scope": {
            "c0_a_temporal_transfer_benchmark_instantiated": True,
            "c0_a_causal_structure_instantiated": False,
            "time_order_and_spacing_inserted": True,
            "markov_entrywise_nonnegative_input": True,
            "static_functional_selects_transfer": False,
            "positive_self_adjoint_generator_reconstructed": True,
            "unitary_group_reconstructed": True,
            "site_reflection_positive": True,
            "link_reflection_requires_positive_transfer": True,
            "reversibility_alone_implies_positive_generator": False,
            "spatial_locality_derived": False,
            "causal_cone_derived": False,
            "lorentzian_signature_derived": False,
            "physical_quantum_dynamics_selected": False,
            "preferred_hadamard_state_selected": False,
            "pa_h1_state_supplied": False,
            "pa_m2_composition": False,
            "tect_c0_branch_selected": False,
            "pre_a_complete": False,
        },
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This finite-state C0-A benchmark reconstructs a positive self-adjoint generator and a unitary group "
            "only after a positive reversible transfer, time ordering, reflection, and spacing are supplied. It "
            "does not derive time, an arrow, spatial locality, Lorentzian signature, a null cone, light speed, a "
            "physical quantum theory, a Hadamard state, gravity, an event horizon, cosmic cooling, the PA-H1 to "
            "PA-M2 interface, or Pre-A completion."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"{CANDIDATE_ID} | positive transfer reconstruction"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
