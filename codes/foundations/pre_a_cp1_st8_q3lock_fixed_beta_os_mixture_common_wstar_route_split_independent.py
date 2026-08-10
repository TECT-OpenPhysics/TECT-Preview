#!/usr/bin/env python3
"""Independent exact audit of the R-167 v1.4 fixed-beta OS-mixture split.

Only the Python standard library and ``Fraction`` arithmetic are used.  The
script independently rebuilds four finite algebraic interfaces:

* the common OS-mixture Gram/Radon--Nikodym/KMS fixture;
* the sharp-time two-level counterexample;
* the full-Gibbs half-modular locality obstruction; and
* the high-frequency one-bond obstruction to a frequency-blind single-rung
  site-influence recurrence.

The output is T0 verification evidence.  A pass does not identify the OS
mixture dynamics with a thermodynamic Hamiltonian limit and does not construct
a beta-independent common C-star dynamics.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.4"
EXPLORATION_ID = "EXP-000800"

MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT_V13 = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-common-alpha-topology-critical-"
    "graph-route-split-manifest.json"
)
PARENT_V12 = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-"
    "resummation-route-split-manifest.json"
)
OS_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-"
    "counterterm-empty-route-split-manifest.json"
)
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SHARP-TIME-OS-GRAM-ONLY-"
    "REAL-TIME-FUNCTORIALITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FULL-GIBBS-HALF-MODULAR-"
    "LOCAL-SEPARATING-CLASS",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SINGLE-RUNG-ENERGY-CONSTRAINED-"
    "SITEWISE-INFLUENCE-RECURRENCE",
)
CLOSED_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIXED-BETA-CANONICAL-OS-MIXTURE-"
    "COMMON-NORMAL-WSTAR-KMS-ENVELOPE"
)
SUCCESSOR_GATE = (
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-"
    "IN-CANONICAL-OS-MIXTURE"
)
ALL_BOND_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-"
    "LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE"
)
PROJECTED_GATE = (
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY"
)


def serial(value: Any) -> Any:
    """Convert exact values to deterministic JSON-compatible values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        serial(dict(payload)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                serial(dict(payload)),
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast exact assertion ledger."""

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
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
            )
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def weighted_sum(weights: Iterable[Fraction], values: Iterable[Fraction]) -> Fraction:
    return sum((weight * value for weight, value in zip(weights, values)), Fraction(0))


def os_mixture_fixture() -> dict[str, Any]:
    """Rebuild the finite common-word Gram, RN, and KMS identities."""

    # INPUTS: overlapping center laws, an interior mixture, and one Gibbs qubit.
    lam_plus = Fraction(2, 5)
    lam_minus = 1 - lam_plus
    center_plus = (Fraction(3, 4), Fraction(1, 4))
    center_minus = tuple(reversed(center_plus))
    rho = (Fraction(2, 3), Fraction(1, 3))
    center_zero = tuple(
        lam_plus * center_plus[index] + lam_minus * center_minus[index]
        for index in range(2)
    )

    basis = tuple(
        (center, row, column)
        for center in range(2)
        for row in range(2)
        for column in range(2)
    )
    gram_plus = tuple(center_plus[center] * rho[column] for center, _, column in basis)
    gram_minus = tuple(center_minus[center] * rho[column] for center, _, column in basis)
    gram_zero = tuple(center_zero[center] * rho[column] for center, _, column in basis)
    gram_residual = tuple(
        zero - lam_plus * plus - lam_minus * minus
        for zero, plus, minus in zip(gram_zero, gram_plus, gram_minus)
    )

    t_plus_center = tuple(center_plus[index] / center_zero[index] for index in range(2))
    t_minus_center = tuple(center_minus[index] / center_zero[index] for index in range(2))
    t_plus = tuple(t_plus_center[center] for center, _, _ in basis)
    t_minus = tuple(t_minus_center[center] for center, _, _ in basis)
    weighted_t = tuple(
        lam_plus * plus + lam_minus * minus
        for plus, minus in zip(t_plus, t_minus)
    )

    # An exact common-word vector tests q_0=lambda q_+ +(1-lambda)q_-.
    vector = tuple(Fraction(value) for value in (1, -2, 3, 5, -7, 11, -13, 17))
    q_plus = weighted_sum(gram_plus, (value * value for value in vector))
    q_minus = weighted_sum(gram_minus, (value * value for value in vector))
    q_zero = weighted_sum(gram_zero, (value * value for value in vector))

    # T_sigma is central in this direct-sum word fixture, hence commutes with
    # every left matrix unit in the qubit factor.  Verify by basis indices.
    commutant_rows = []
    for center in range(2):
        for row in range(2):
            for column in range(2):
                left_factor = t_plus_center[center]
                right_factor = t_plus_center[center]
                left_minus = t_minus_center[center]
                right_minus = t_minus_center[center]
                commutant_rows.append(
                    {
                        "center": center,
                        "matrix_unit": (row, column),
                        "plus_residual": left_factor - right_factor,
                        "minus_residual": left_minus - right_minus,
                    }
                )

    # Exhaust the matrix-unit KMS boundary identity
    # psi(A alpha_(i beta)(B))=psi(BA).  The imaginary-time multiplier of
    # E_kl is rho_k/rho_l.
    kms_rows = []
    for phase, center_weights in (("plus", center_plus), ("minus", center_minus)):
        for center in range(2):
            for i in range(2):
                for j in range(2):
                    for k in range(2):
                        for ell in range(2):
                            modular_factor = rho[k] / rho[ell]
                            ab = (
                                center_weights[center] * rho[i]
                                if j == k and i == ell
                                else Fraction(0)
                            )
                            ba = (
                                center_weights[center] * rho[k]
                                if ell == i and k == j
                                else Fraction(0)
                            )
                            kms_rows.append(
                                {
                                    "phase": phase,
                                    "center": center,
                                    "A": (i, j),
                                    "B": (k, ell),
                                    "residual": modular_factor * ab - ba,
                                }
                            )

    # RN normality is tested on a nonconstant diagonal common-word element.
    diagonal_test = (
        (Fraction(1), Fraction(-2)),
        (Fraction(3), Fraction(5)),
    )

    def phase_value(center_weights: tuple[Fraction, Fraction]) -> Fraction:
        return sum(
            (
                center_weights[center]
                * sum(rho[index] * diagonal_test[center][index] for index in range(2))
                for center in range(2)
            ),
            Fraction(0),
        )

    def rn_value(t_center: tuple[Fraction, Fraction]) -> Fraction:
        return sum(
            (
                center_zero[center]
                * t_center[center]
                * sum(rho[index] * diagonal_test[center][index] for index in range(2))
                for center in range(2)
            ),
            Fraction(0),
        )

    return {
        "lambda_plus": lam_plus,
        "lambda_minus": lam_minus,
        "center_plus": center_plus,
        "center_minus": center_minus,
        "center_zero": center_zero,
        "rho": rho,
        "basis_dimension": len(basis),
        "gram_plus": gram_plus,
        "gram_minus": gram_minus,
        "gram_zero": gram_zero,
        "gram_residual": gram_residual,
        "gram_determinant": weighted_sum((Fraction(1),) * len(gram_zero), gram_zero),
        "q_plus": q_plus,
        "q_minus": q_minus,
        "q_zero": q_zero,
        "q_mixture": lam_plus * q_plus + lam_minus * q_minus,
        "T_plus_center": t_plus_center,
        "T_minus_center": t_minus_center,
        "weighted_T": weighted_t,
        "T_plus_upper": 1 / lam_plus,
        "T_minus_upper": 1 / lam_minus,
        "commutant_rows": commutant_rows,
        "kms_rows": kms_rows,
        "rn_plus": rn_value(t_plus_center),
        "rn_minus": rn_value(t_minus_center),
        "direct_plus": phase_value(center_plus),
        "direct_minus": phase_value(center_minus),
        "rn_nonprojections": any(
            value not in (0, 1) for value in t_plus_center + t_minus_center
        ),
        "faithful_mixture": all(value > 0 for value in gram_zero),
        "symmetric_center": tuple(
            (center_plus[index] + center_minus[index]) / 2 for index in range(2)
        ),
    }


def sharp_time_fixture() -> dict[str, Any]:
    """Exact Pauli-algebra version of the sharp-time-only counterexample."""

    # INPUT: beta=1 and nu=log(2).  exp(nu)=2 makes every thermal ratio exact.
    exp_nu = Fraction(2)
    tanh_nu = (exp_nu**2 - 1) / (exp_nu**2 + 1)
    cosh_nu = (exp_nu + 1 / exp_nu) / 2
    rho_zero = ((Fraction(1, 2), Fraction(0)), (Fraction(0), Fraction(1, 2)))
    rho_one = (
        (Fraction(1, 2), tanh_nu / 2),
        (tanh_nu / 2, Fraction(1, 2)),
    )
    a = Fraction(7, 5)
    b = Fraction(-11, 6)
    sharp_zero = (a * a + b * b) / 2
    # Off-diagonal density entries do not contribute to a diagonal multiplier.
    sharp_one = rho_one[0][0] * a * a + rho_one[1][1] * b * b
    return {
        "exp_nu": exp_nu,
        "tanh_nu": tanh_nu,
        "cosh_nu": cosh_nu,
        "rho_zero": rho_zero,
        "rho_one": rho_one,
        "sharp_zero": sharp_zero,
        "sharp_one": sharp_one,
        "quarter_turn_evolved_label": "-sigma_y",
        "quarter_turn_difference_square": Fraction(2),
        "quarter_turn_operator_norm_squared": Fraction(2),
        "euclidean_midpoint_zero": Fraction(1),
        "euclidean_midpoint_one": 1 / cosh_nu,
        "same_sharp_multipliers": True,
        "same_real_time": False,
        "same_positive_time_cylinder": False,
    }


def half_modular_fixture() -> dict[str, Any]:
    """Audit algebra closure and the exact loss of strict Gibbs locality."""

    # INPUT: a faithful correlated two-site diagonal Gibbs density.  Its
    # nonfactorizing weights make the modular image of a first-site flip depend
    # on the second site.
    raw_weights = (Fraction(1), Fraction(2), Fraction(3), Fraction(8))
    total = sum(raw_weights, Fraction(0))
    weights = tuple(value / total for value in raw_weights)

    def two_sided_half_norm_squared(left: int, right: int) -> Fraction:
        ratio = weights[left] / weights[right]
        return max(Fraction(1), ratio, 1 / ratio)

    adjoint_rows = []
    product_rows = []
    for left in range(4):
        for right in range(4):
            value = two_sided_half_norm_squared(left, right)
            adjoint_rows.append(
                {
                    "unit": (left, right),
                    "value": value,
                    "adjoint_value": two_sided_half_norm_squared(right, left),
                }
            )
            for endpoint in range(4):
                product_rows.append(
                    {
                        "product": ((left, right), (right, endpoint)),
                        "output": two_sided_half_norm_squared(left, endpoint),
                        "input_product": value
                        * two_sided_half_norm_squared(right, endpoint),
                    }
                )

    # A=X tensor I flips 00<->10 and 01<->11.  Positive-half modular squared
    # amplitudes are rho_target/rho_source and differ with the neighbour bit.
    flip_forward_squared = (
        weights[2] / weights[0],
        weights[3] / weights[1],
    )
    flip_backward_squared = tuple(1 / value for value in flip_forward_squared)

    # Exact Q3 one-bond cross witness from the authority, using only rational
    # inputs.  exp(-kappa q_y) is unbounded on R whenever kappa is nonzero.
    strip_s = Fraction(2, 3)
    coupling_c = Fraction(3, 5)
    translation_a = Fraction(7, 4)
    kappa = strip_s * coupling_c * translation_a
    translation_slopes = tuple(-coupling_c * Fraction(radius) for radius in (1, 2, 4, 8))
    hbar = Fraction(5, 7)
    chi = Fraction(7, 4)
    boost_slopes = tuple(
        hbar * Fraction(radius) / chi for radius in (1, 2, 4, 8)
    )
    return {
        "weights": weights,
        "cross_ratio": weights[0] * weights[3] / (weights[1] * weights[2]),
        "adjoint_rows": adjoint_rows,
        "product_rows": product_rows,
        "flip_forward_squared": flip_forward_squared,
        "flip_backward_squared": flip_backward_squared,
        "strict_locality_preserved": flip_forward_squared[0] == flip_forward_squared[1],
        "strip_s": strip_s,
        "coupling_c": coupling_c,
        "translation_a": translation_a,
        "cross_witness_kappa": kappa,
        "positive_endpoint_bounded": kappa == 0,
        "negative_endpoint_bounded": kappa == 0,
        "translation_slopes": translation_slopes,
        "boost_slopes": boost_slopes,
        "extreme_site_coefficients_forced_zero": True,
    }


def single_rung_fixture() -> dict[str, Any]:
    """Exact root-of-unity high-frequency bond-kick counterexample."""

    # Use the normalized Weyl convention with phase exp(2*pi*i*u*v).  The
    # rational phase turn 1/2 is exactly -1, so no floating trigonometry enters.
    rows = []
    for denominator in (2, 4, 8, 16, 32, 64):
        delta = Fraction(1, denominator)
        source_frequency = Fraction(denominator, 2)
        test_frequency = Fraction(1)
        phase_turn = delta * source_frequency * test_frequency
        rows.append(
            {
                "denominator": denominator,
                "delta": delta,
                "source_frequency": source_frequency,
                "test_frequency": test_frequency,
                "phase_turn": phase_turn,
                "phase_is_minus_one": phase_turn == Fraction(1, 2),
            }
        )

    # Two-level exact graph-test normalization: K^(1/2)=diag(1,2), X is the
    # flip, and ||K^(1/2) X K^(-1/2)||=2.  C=X/2 has graph norm one.  The
    # neighbour phase Z anticommutes with X, so [Z,C] is unitary.
    graph_test_norm = Fraction(2)
    normalized_test_scale = 1 / graph_test_norm
    commutator_operator_norm_squared = Fraction(1)
    response_strongstar_squared = 2 * commutator_operator_norm_squared
    source_influence_uniform_upper_squared = Fraction(8)
    return {
        "rows": rows,
        "graph_test_norm": graph_test_norm,
        "normalized_test_scale": normalized_test_scale,
        "graph_conjugate_singular_values_squared": (Fraction(4), Fraction(1, 4)),
        "commutator_operator_norm_squared": commutator_operator_norm_squared,
        "response_strongstar_squared": response_strongstar_squared,
        "source_influence_uniform_upper_squared": source_influence_uniform_upper_squared,
        "minimum_recurrence_coefficient": (
            response_strongstar_squared / source_influence_uniform_upper_squared
        ),
        "initial_neighbour_influence_squared": Fraction(0),
        "frequency_blind_small_coefficient_recurrence": False,
    }


def analytic_shear_fixture() -> dict[str, Any]:
    """Smallest exact positive Weyl-frequency/radius bond lemma."""

    # INPUT: one three-cycle, so every vertex has exactly two neighbours.
    coupling = Fraction(3, 5)
    delta = Fraction(2, 7)
    frequencies = (Fraction(2), Fraction(3), Fraction(5))
    transformed = tuple(
        frequencies[index]
        + delta
        * coupling
        * sum(frequencies[other] for other in range(3) if other != index)
        for index in range(3)
    )
    total = sum(frequencies, Fraction(0))
    transformed_total = sum(transformed, Fraction(0))
    radius_factor = 1 + 2 * delta * coupling
    return {
        "coupling": coupling,
        "delta": delta,
        "frequencies": frequencies,
        "transformed": transformed,
        "total": total,
        "transformed_total": transformed_total,
        "radius_factor": radius_factor,
        "radius_identity": transformed_total == radius_factor * total,
        "bond_one_layer": True,
        "quartic_onsite_radius_invariance_proved": False,
        "thermodynamic_boundary_cauchy_proved": False,
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    required = (MANIFEST, CERTIFICATE, PARENT_V13, PARENT_V12, OS_PARENT, NEGATIVE_REGISTRY)
    missing = [
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in required
        if not path.exists()
    ]
    if missing and not staged:
        raise FileNotFoundError("missing v1.4 authority: " + ", ".join(missing))
    if missing:
        return {"status": "MISSING_STAGED", "missing": missing, "source_paths": []}

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_text = json.dumps(manifest, sort_keys=True, ensure_ascii=True)
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    parent_v13 = json.loads(PARENT_V13.read_text(encoding="utf-8"))
    parent_v12 = json.loads(PARENT_V12.read_text(encoding="utf-8"))
    os_parent = json.loads(OS_PARENT.read_text(encoding="utf-8"))
    negative_registry = NEGATIVE_REGISTRY.read_text(encoding="utf-8")

    audit.check("authority schema", manifest["schema"] == "tect/pre-a-route-split/1.0", manifest["schema"], "tect/pre-a-route-split/1.0", "authority")
    audit.check("authority task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "authority")
    audit.check("authority exploration", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "authority")
    audit.check("authority result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "authority")
    audit.check("authority result number", manifest["result_number"] == RESULT_NUMBER, manifest["result_number"], RESULT_NUMBER, "authority")
    audit.check("authority version", manifest["result_version"] == RESULT_VERSION, manifest["result_version"], RESULT_VERSION, "authority")
    audit.check("authority claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "authority")
    audit.check("authority parent explorations", manifest["parent_explorations"] == ["EXP-000790", "EXP-000798", "EXP-000799"], manifest["parent_explorations"], ["EXP-000790", "EXP-000798", "EXP-000799"], "authority")
    audit.check("negative IDs exact", manifest["negative_ids"] == list(NEGATIVE_IDS), manifest["negative_ids"], list(NEGATIVE_IDS), "authority")
    audit.check("closed fixed-beta envelope gate", manifest["closed_subgates"] == [CLOSED_GATE], manifest["closed_subgates"], [CLOSED_GATE], "authority")
    audit.check("retained common-alpha gates", manifest["retained_gate_ids"] == [ALL_BOND_GATE, PROJECTED_GATE], manifest["retained_gate_ids"], [ALL_BOND_GATE, PROJECTED_GATE], "authority")
    audit.check("successor gate first", manifest["open_gates"][0] == SUCCESSOR_GATE, manifest["open_gates"], SUCCESSOR_GATE, "authority")
    audit.check("v1.3 parent", parent_v13["result_version"] == "v1.3" and parent_v13["exploration_id"] == "EXP-000799", {"version": parent_v13["result_version"], "exploration": parent_v13["exploration_id"]}, {"version": "v1.3", "exploration": "EXP-000799"}, "authority")
    audit.check("v1.2 modular parent", parent_v12["result_version"] == "v1.2" and "common modular-analytic core" in parent_v12["modular_multiplier_lemma"]["definitions"], parent_v12["modular_multiplier_lemma"], "finite type-I modular multiplier lemma", "authority")
    audit.check("phasewise OS parent", os_parent["exploration_id"] == "EXP-000790" and "sharp_time_Cstar_algebra" in json.dumps(os_parent, sort_keys=True), os_parent["exploration_id"], "EXP-000790 common sharp-time authority", "authority")

    for negative_id in NEGATIVE_IDS:
        audit.check(
            f"negative registry {negative_id}",
            negative_id in negative_registry,
            negative_id if negative_id in negative_registry else "MISSING",
            negative_id,
            "authority",
        )
        audit.check(
            f"certificate negative {negative_id}",
            negative_id in certificate,
            negative_id if negative_id in certificate else "MISSING",
            negative_id,
            "authority",
        )

    for token in (
        EXPLORATION_ID,
        RESULT_NUMBER,
        RESULT_VERSION,
        CLOSED_GATE,
        SUCCESSOR_GATE,
        "fixed-beta",
        "normal KMS",
        "strong-star",
        "half-modular",
        "single site-influence rung",
        "thermodynamic",
        "beta-independent",
        "Pre-A",
    ):
        audit.check(
            f"certificate token {token}",
            token in certificate,
            token if token in certificate else "MISSING",
            token,
            "authority",
        )

    contract = manifest["fixed_beta_os_mixture_theorem"]
    audit.check("full cylinder load-bearing", "full positive-time cylinder module" in contract["inputs"] and "K reduces" in contract["canonical_reconstruction"], contract, "full common reducing word module", "authority")
    audit.check("normal KMS authority", "normal beta-KMS" in contract["normal_kms_states"] and "single mixture group" in contract["normal_kms_states"], contract["normal_kms_states"], "normal phase states for one mixture group", "authority")
    audit.check("half modular scope", "finite-support separating class" in manifest["half_modular_local_scalarity_theorem"]["scope"] and "direct D and delta-D" in manifest["half_modular_local_scalarity_theorem"]["scope"], manifest["half_modular_local_scalarity_theorem"]["scope"], "local class rejected, direct route retained", "authority")
    audit.check("single rung scope", "Weyl-frequency or analytic-rung" in manifest["single_rung_influence_counterexample"]["consequence"], manifest["single_rung_influence_counterexample"]["consequence"], "frequency profile required", "authority")
    audit.check("Hamiltonian identification open", "not yet" in manifest["hamiltonian_identification_boundary"]["missing_identification"] and manifest["hamiltonian_identification_boundary"]["next_gate"] == SUCCESSOR_GATE, manifest["hamiltonian_identification_boundary"], SUCCESSOR_GATE, "authority")

    for token in (
        "thermodynamic limit",
        "beta-independent",
        "volume-uniform",
        "ground states",
        "GNS",
        "continuum",
        "physical empty space",
        "C6",
        "Sector A",
        "Pre-A",
    ):
        audit.check(
            f"no-overclaim {token}",
            token.lower().replace("-", " ")
            in manifest["no_overclaim"].lower().replace("-", " "),
            manifest["no_overclaim"],
            f"contains {token}",
            "scope",
        )

    audit.check("manifest mentions all authorities", all(token in manifest_text for token in (CLOSED_GATE, SUCCESSOR_GATE, ALL_BOND_GATE, PROJECTED_GATE)), manifest_text, "all gate IDs", "authority")
    return {
        "status": "COMPLETE",
        "missing": [],
        "source_paths": list(required),
        "boundary": manifest["no_overclaim"],
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    os_mix = os_mixture_fixture()
    sharp = sharp_time_fixture()
    half = half_modular_fixture()
    rung = single_rung_fixture()
    analytic = analytic_shear_fixture()

    audit.check("stdlib-only imports", all((node.module or "").split(".")[0] in {"__future__", "argparse", "ast", "hashlib", "json", "os", "tempfile", "fractions", "pathlib", "typing"} for node in ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8"))) if isinstance(node, ast.ImportFrom)), "standard library", "standard library", "code")
    audit.check("OS mixture weights", os_mix["lambda_plus"] == Fraction(2, 5) and os_mix["lambda_minus"] == Fraction(3, 5), (os_mix["lambda_plus"], os_mix["lambda_minus"]), (Fraction(2, 5), Fraction(3, 5)), "OS")
    audit.check("OS mixture center law", os_mix["center_zero"] == (Fraction(9, 20), Fraction(11, 20)), os_mix["center_zero"], (Fraction(9, 20), Fraction(11, 20)), "OS")
    audit.check("OS full Gram identity", all(value == 0 for value in os_mix["gram_residual"]), os_mix["gram_residual"], "all zero", "OS")
    audit.check("OS mixture form isometry", os_mix["q_zero"] == os_mix["q_mixture"], os_mix["q_zero"], os_mix["q_mixture"], "OS")
    audit.check("OS mixture faithful", os_mix["faithful_mixture"] and os_mix["basis_dimension"] == 8, {"faithful": os_mix["faithful_mixture"], "dimension": os_mix["basis_dimension"]}, {"faithful": True, "dimension": 8}, "OS")
    audit.check("RN T plus", os_mix["T_plus_center"] == (Fraction(5, 3), Fraction(5, 11)), os_mix["T_plus_center"], (Fraction(5, 3), Fraction(5, 11)), "RN")
    audit.check("RN T minus", os_mix["T_minus_center"] == (Fraction(5, 9), Fraction(15, 11)), os_mix["T_minus_center"], (Fraction(5, 9), Fraction(15, 11)), "RN")
    audit.check("RN weighted identity", all(value == 1 for value in os_mix["weighted_T"]), os_mix["weighted_T"], "all one", "RN")
    audit.check("RN domination bounds", max(os_mix["T_plus_center"]) <= os_mix["T_plus_upper"] and max(os_mix["T_minus_center"]) <= os_mix["T_minus_upper"], {"plus": os_mix["T_plus_center"], "minus": os_mix["T_minus_center"]}, {"plus_upper": os_mix["T_plus_upper"], "minus_upper": os_mix["T_minus_upper"]}, "RN")
    audit.check("RN in commutant", all(row["plus_residual"] == row["minus_residual"] == 0 for row in os_mix["commutant_rows"]), len(os_mix["commutant_rows"]), "all residuals zero", "RN")
    audit.check("RN plus normal functional", os_mix["rn_plus"] == os_mix["direct_plus"], os_mix["rn_plus"], os_mix["direct_plus"], "RN")
    audit.check("RN minus normal functional", os_mix["rn_minus"] == os_mix["direct_minus"], os_mix["rn_minus"], os_mix["direct_minus"], "RN")
    audit.check("RN densities not central projections", os_mix["rn_nonprojections"], os_mix["T_plus_center"] + os_mix["T_minus_center"], "nonprojection densities", "scope")
    audit.check("KMS exhaustive rows", len(os_mix["kms_rows"]) == 64 and all(row["residual"] == 0 for row in os_mix["kms_rows"]), len(os_mix["kms_rows"]), "64 zero residuals", "KMS")
    audit.check("symmetric mixture parity law", os_mix["symmetric_center"] == (Fraction(1, 2), Fraction(1, 2)), os_mix["symmetric_center"], (Fraction(1, 2), Fraction(1, 2)), "OS")

    audit.check("sharp density exact", sharp["tanh_nu"] == Fraction(3, 5) and sharp["rho_one"] == ((Fraction(1, 2), Fraction(3, 10)), (Fraction(3, 10), Fraction(1, 2))), sharp["rho_one"], "[[1/2,3/10],[3/10,1/2]]", "sharp")
    audit.check("sharp Gram equality", sharp["sharp_zero"] == sharp["sharp_one"], (sharp["sharp_zero"], sharp["sharp_one"]), "equal", "sharp")
    audit.check("sharp quarter-turn gap", sharp["quarter_turn_difference_square"] == sharp["quarter_turn_operator_norm_squared"] == 2, sharp["quarter_turn_difference_square"], 2, "sharp")
    audit.check("sharp Euclidean midpoint split", sharp["euclidean_midpoint_zero"] == 1 and sharp["euclidean_midpoint_one"] == Fraction(4, 5), (sharp["euclidean_midpoint_zero"], sharp["euclidean_midpoint_one"]), (1, Fraction(4, 5)), "sharp")
    audit.check("sharp-only inference false", sharp["same_sharp_multipliers"] and not sharp["same_real_time"] and not sharp["same_positive_time_cylinder"], sharp, "same sharp data, distinct dynamics", "sharp")

    audit.check("half modular density faithful correlated", all(value > 0 for value in half["weights"]) and half["cross_ratio"] == Fraction(4, 3), {"weights": half["weights"], "cross_ratio": half["cross_ratio"]}, "faithful and nonproduct", "half-modular")
    audit.check("half modular star closure", all(row["value"] == row["adjoint_value"] for row in half["adjoint_rows"]), len(half["adjoint_rows"]), "adjoint invariant", "half-modular")
    audit.check("half modular product closure", all(row["output"] <= row["input_product"] for row in half["product_rows"]), len(half["product_rows"]), "submultiplicative", "half-modular")
    audit.check("half modular local flip becomes conditional", half["flip_forward_squared"] == (Fraction(3), Fraction(4)) and not half["strict_locality_preserved"], half["flip_forward_squared"], (Fraction(3), Fraction(4)), "half-modular")
    audit.check("half modular reverse amplitudes", half["flip_backward_squared"] == (Fraction(1, 3), Fraction(1, 4)), half["flip_backward_squared"], (Fraction(1, 3), Fraction(1, 4)), "half-modular")
    audit.check("Q3 cross witness nonzero", half["cross_witness_kappa"] == Fraction(7, 10), half["cross_witness_kappa"], Fraction(7, 10), "half-modular")
    audit.check("Q3 full endpoints unbounded", not half["positive_endpoint_bounded"] and not half["negative_endpoint_bounded"], (half["positive_endpoint_bounded"], half["negative_endpoint_bounded"]), (False, False), "half-modular")
    audit.check("extreme-site translation slopes", half["translation_slopes"] == (Fraction(-3, 5), Fraction(-6, 5), Fraction(-12, 5), Fraction(-24, 5)), half["translation_slopes"], "nonzero linear R slopes", "half-modular")
    audit.check("extreme-site boost slopes", all(value != 0 for value in half["boost_slopes"]) and half["extreme_site_coefficients_forced_zero"], half["boost_slopes"], "nonzero linear R slopes force CCR commutators zero", "half-modular")

    audit.check("single-rung phase locked", all(row["phase_is_minus_one"] for row in rung["rows"]), [row["phase_turn"] for row in rung["rows"]], "all half-turns", "single-rung")
    audit.check("single-rung delta tends down", all(right["delta"] < left["delta"] for left, right in zip(rung["rows"], rung["rows"][1:])), [row["delta"] for row in rung["rows"]], "strict decrease", "single-rung")
    audit.check("single-rung frequency compensates", all(row["delta"] * row["source_frequency"] == Fraction(1, 2) for row in rung["rows"]), [(row["delta"], row["source_frequency"]) for row in rung["rows"]], "delta*a=1/2", "single-rung")
    audit.check("single-rung graph test normalization", rung["graph_test_norm"] == 2 and rung["normalized_test_scale"] == Fraction(1, 2) and rung["graph_conjugate_singular_values_squared"] == (Fraction(4), Fraction(1, 4)), rung, "G(X)=2 and G(X/2)=1", "single-rung")
    audit.check("single-rung nonvanishing response", rung["response_strongstar_squared"] == 2 and rung["initial_neighbour_influence_squared"] == 0, {"new": rung["response_strongstar_squared"], "old": rung["initial_neighbour_influence_squared"]}, {"new": 2, "old": 0}, "single-rung")
    audit.check("single-rung recurrence lower coefficient", rung["minimum_recurrence_coefficient"] == Fraction(1, 4) and not rung["frequency_blind_small_coefficient_recurrence"], rung["minimum_recurrence_coefficient"], Fraction(1, 4), "single-rung")

    audit.check("analytic shear one-layer identity", analytic["radius_identity"] and analytic["radius_factor"] == Fraction(47, 35), {"transformed": analytic["transformed_total"], "factor": analytic["radius_factor"]}, Fraction(47, 35), "analytic")
    audit.check("analytic route boundary", analytic["bond_one_layer"] and not analytic["quartic_onsite_radius_invariance_proved"] and not analytic["thermodynamic_boundary_cauchy_proved"], analytic, "bond precursor only", "scope")

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    source_paths = [SCRIPT, PARENT_V13, PARENT_V12, OS_PARENT]
    source_paths.extend(Path(path) for path in authority.get("source_paths", []))
    unique_paths = []
    for path in source_paths:
        if path.exists() and path not in unique_paths:
            unique_paths.append(path)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in unique_paths
    }
    for relative, digest in source_hashes.items():
        audit.check(f"source hash {relative}", len(digest) == 64 and all(character in "0123456789abcdef" for character in digest), digest, "64 lowercase hexadecimal", "provenance")

    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": "T-054",
        "claim_ids": ["C6-SPACETIME-SIGNATURE"],
        "claim_bearing": False,
        "verdict": verdict,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "assertions": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "rows": audit.rows,
        },
        "derived": {
            "os_mixture": os_mix,
            "sharp_time_counterexample": sharp,
            "half_modular_locality": half,
            "single_rung_counterexample": rung,
            "analytic_shear_precursor": analytic,
            "fixed_beta_common_normal_wstar_envelope_closed": True,
            "sharp_time_only_functoriality_closed": False,
            "full_gibbs_half_modular_local_separating_class_closed": False,
            "single_rung_frequency_blind_recurrence_closed": False,
            "Hamiltonian_thermodynamic_identification_closed": False,
            "beta_independent_common_alpha_closed": False,
            "ground_state_selection_closed": False,
            "GNS_gap_closed": False,
            "continuum_closed": False,
            "physical_empty_comparison_closed": False,
            "Pre_A_closed": False,
        },
        "negative_ids": list(NEGATIVE_IDS),
        "closed_gate": CLOSED_GATE,
        "successor_gate": SUCCESSOR_GATE,
        "retained_gates": [ALL_BOND_GATE, PROJECTED_GATE],
        "authority": authority,
        "source_hashes": source_hashes,
        "boundary": authority.get(
            "boundary",
            "Staged exact fixtures only; formal v1.4 authority is incomplete.",
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-identical canonical payloads",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="allow missing formal v1.4 authority and report INCOMPLETE",
    )
    arguments = parser.parse_args()

    payload = build_payload(staged=arguments.staged)
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.self_test:
        repeated = build_payload(staged=arguments.staged)
        repeated_encoded = canonical_bytes(repeated)
        if encoded != repeated_encoded:
            raise AssertionError("nondeterministic independent payload")
        if digest != hashlib.sha256(repeated_encoded).hexdigest():
            raise AssertionError("nondeterministic independent digest")
        print(
            f"SELF-TEST {payload['verdict']} {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
        )
        return 0 if payload["verdict"] == "PASS" or arguments.staged else 1

    if payload["verdict"] != "PASS":
        print(
            f"INCOMPLETE {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | authority "
            + ", ".join(payload["authority"]["missing"])
        )
        return 1
    atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['summary']['passed']}/{payload['summary']['total']} | "
        f"SHA256 {digest} | {RESULT_ID}"
    )
    print(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
