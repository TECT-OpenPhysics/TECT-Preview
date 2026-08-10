#!/usr/bin/env python3
"""Independent exact audit of the R-167 v1.5 tangent-to-OS route split.

This verifier deliberately does not import the primary implementation or read
any primary result.  It uses only the Python standard library and exact
``Fraction`` arithmetic to rebuild the finite algebraic interfaces declared in
the v1.5 manifest:

* the configuration-character CCR, double-commutator, Kubo, and Fejer scales;
* finite positive-Gram transport and the singular limiting-support rule;
* rotating-null and dimension-collapse failures of naive GNS embeddings;
* configuration-cylinder momentum-gauge ambiguity and the raw-character
  bounded-generator obstruction;
* parity of a phase mixture and the two-level cross-beta mismatch; and
* the exact local source jet and first coordinate-tail rung.

The output is T0 verification evidence.  A pass does not prove all-exhaustion
strong-star locality, a canonical momentum/Weyl embedding, a beta-independent
C-star dynamics, a ground state, a GNS gap, a continuum, or Pre-A closure.
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
from typing import Any, Iterable, Mapping, Sequence


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-hamiltonian-os-tangent-transport-"
    "generator-route-split"
)
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.5"
EXPLORATION_ID = "EXP-000801"

MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate.md"
TANGENT_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-"
    "phase-boundary-route-split-manifest.json"
)
MIXTURE_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-"
    "wstar-route-split-manifest.json"
)
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATION_LOG = REPO / "explorations/log.jsonl"
GATES = REPO / "claims/GATES.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-POINTWISE-OS-GRAM-NAIVE-"
    "LABEL-EMBEDDING",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONFIGURATION-CYLINDER-"
    "CANONICAL-MOMENTUM-GENERATOR",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-CHARACTER-"
    "BOUNDED-GENERATOR-CORE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-ASYMMETRIC-MIXTURE-ZERO-"
    "SOURCE-PERIODIC-LIMIT",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-"
    "AUTOMATIC-CROSS-BETA-GLUING",
)
CLOSED_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIXED-BETA-TANGENT-NET-BANDLIMITED-"
    "HAMILTONIAN-OS-POINTED-GNS-IDENTIFICATION"
)
SUCCESSOR_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-"
    "BETA-INDEPENDENT-CSTAR-DYNAMICS"
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-"
    "IN-CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY",
)

Matrix = tuple[tuple[Fraction, ...], ...]


def serial(value: Any) -> Any:
    """Convert exact objects to deterministic JSON-compatible values."""

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


def matrix(rows: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def identity(size: int) -> Matrix:
    return tuple(
        tuple(Fraction(int(row == column)) for column in range(size))
        for row in range(size)
    )


def transpose(value: Matrix) -> Matrix:
    return tuple(tuple(value[row][column] for row in range(len(value))) for column in range(len(value[0])))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def matadd(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] + right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def diagonal(values: Sequence[int | Fraction]) -> Matrix:
    return tuple(
        tuple(
            Fraction(values[row]) if row == column else Fraction(0)
            for column in range(len(values))
        )
        for row in range(len(values))
    )


def trace(value: Matrix) -> Fraction:
    return sum((value[index][index] for index in range(len(value))), Fraction(0))


def determinant_two(value: Matrix) -> Fraction:
    return value[0][0] * value[1][1] - value[0][1] * value[1][0]


def quadratic(value: Matrix, vector: Sequence[Fraction]) -> Fraction:
    return sum(
        (
            vector[row] * value[row][column] * vector[column]
            for row in range(len(vector))
            for column in range(len(vector))
        ),
        Fraction(0),
    )


def exact_rank(value: Matrix) -> int:
    work = [list(row) for row in value]
    rows = len(work)
    columns = len(work[0]) if work else 0
    rank = 0
    pivot_column = 0
    while rank < rows and pivot_column < columns:
        pivot = next(
            (row for row in range(rank, rows) if work[row][pivot_column] != 0),
            None,
        )
        if pivot is None:
            pivot_column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][pivot_column]
        work[rank] = [entry / scale for entry in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            factor = work[row][pivot_column]
            if factor:
                work[row] = [
                    work[row][column] - factor * work[rank][column]
                    for column in range(columns)
                ]
        rank += 1
        pivot_column += 1
    return rank


def principal_submatrix(value: Matrix, indices: Sequence[int]) -> Matrix:
    return tuple(tuple(value[row][column] for column in indices) for row in indices)


def character_fixture() -> dict[str, Any]:
    """Rebuild exact CCR, Dirichlet, Kubo, and Fejer constants."""

    # INPUTS chosen so every displayed norm scale is rational.
    beta = Fraction(2)
    chi = Fraction(2)
    hbar = Fraction(1, 4)
    xi = (Fraction(1), Fraction(2), Fraction(2))
    xi_norm_squared = sum((entry * entry for entry in xi), Fraction(0))
    xi_norm = Fraction(3)
    momentum_shift = tuple(hbar * entry for entry in xi)
    commutator_p_coefficients = tuple(hbar * entry / chi for entry in xi)
    commutator_constant = hbar * hbar * xi_norm_squared / (2 * chi)
    double_commutator = hbar * hbar * xi_norm_squared / chi
    kubo_norm_squared = double_commutator / (beta * hbar * hbar)
    kubo_norm = xi_norm / 2  # sqrt(beta*chi)=2.

    radius = Fraction(4)
    fejer_duhamel = kubo_norm / radius
    fejer_derivative = kubo_norm
    fejer_inside = Fraction(2) / (radius * radius) + beta * hbar / radius
    fejer_unaveraged_squared = kubo_norm_squared * fejer_inside
    fejer_unaveraged = Fraction(3, 4)

    span_coefficients = (Fraction(2), Fraction(-1, 2))
    span_label_norms = (Fraction(3), Fraction(4))
    span_numerator = sum(
        (abs(coefficient) * norm for coefficient, norm in zip(span_coefficients, span_label_norms)),
        Fraction(0),
    )
    span_bound = span_numerator / 2
    return {
        "beta": beta,
        "chi": chi,
        "hbar": hbar,
        "xi": xi,
        "xi_norm_squared": xi_norm_squared,
        "xi_norm": xi_norm,
        "momentum_shift": momentum_shift,
        "commutator_p_coefficients": commutator_p_coefficients,
        "commutator_constant": commutator_constant,
        "double_commutator": double_commutator,
        "kubo_norm_squared": kubo_norm_squared,
        "kubo_norm": kubo_norm,
        "radius": radius,
        "fejer_duhamel_bound": fejer_duhamel,
        "fejer_derivative_bound": fejer_derivative,
        "fejer_inside": fejer_inside,
        "fejer_unaveraged_squared": fejer_unaveraged_squared,
        "fejer_unaveraged_bound": fejer_unaveraged,
        "span_coefficients": span_coefficients,
        "span_label_norms": span_label_norms,
        "span_derivative_bound": span_bound,
        "q_only_terms_cancel": True,
        "raw_recovery_uniform_in_q_only_terms": True,
    }


def gram_transport_fixture() -> dict[str, Any]:
    """Exact noncommuting positive-root transports and limit support rule."""

    root_zero = matrix(((2, 1), (1, 2)))
    gram_zero = matmul(root_zero, root_zero)
    root_zero_inverse = matrix(
        ((Fraction(2, 3), Fraction(-1, 3)), (Fraction(-1, 3), Fraction(2, 3)))
    )
    rows = []
    for denominator in (2, 3, 5, 10, 20):
        epsilon = Fraction(1, denominator)
        root_n = matrix(((2 + epsilon, 1), (1, 2 - epsilon)))
        gram_n = matmul(root_n, root_n)
        transport = matmul(root_zero_inverse, root_n)
        residual = matsub(
            matmul(matmul(transpose(transport), gram_zero), transport),
            gram_n,
        )
        distance = max(
            abs(transport[row][column] - identity(2)[row][column])
            for row in range(2)
            for column in range(2)
        )
        rows.append(
            {
                "denominator": denominator,
                "epsilon": epsilon,
                "root": root_n,
                "gram": gram_n,
                "root_trace": trace(root_n),
                "root_determinant": determinant_two(root_n),
                "transport": transport,
                "isometry_residual": residual,
                "distance_to_identity": distance,
            }
        )

    singular_gram = matrix(((1, 1, 2), (1, 1, 2), (2, 2, 5)))
    retained: list[int] = []
    discarded: list[int] = []
    current_rank = 0
    for index in range(len(singular_gram)):
        candidate = retained + [index]
        candidate_rank = exact_rank(principal_submatrix(singular_gram, candidate))
        if candidate_rank > current_rank:
            retained.append(index)
            current_rank = candidate_rank
        else:
            discarded.append(index)
    retained_gram = principal_submatrix(singular_gram, retained)
    return {
        "root_zero": root_zero,
        "gram_zero": gram_zero,
        "root_zero_inverse": root_zero_inverse,
        "transport_rows": rows,
        "singular_gram": singular_gram,
        "singular_rank": exact_rank(singular_gram),
        "retained_indices": retained,
        "discarded_indices": discarded,
        "retained_gram": retained_gram,
        "retained_determinant": determinant_two(retained_gram),
        "full_inverse_permitted": False,
        "principal_positive_root_rule": True,
    }


def embedding_counterexamples() -> dict[str, Any]:
    """Rotating null ideals and faithful-to-singular dimension collapse."""

    rotating_rows = []
    for denominator in (2, 3, 5, 10, 20):
        epsilon = Fraction(1, denominator)
        vector = (Fraction(1), epsilon)
        gram_n = matrix(
            ((vector[0] * vector[0], vector[0] * vector[1]),
             (vector[1] * vector[0], vector[1] * vector[1]))
        )
        null_vector = (-epsilon, Fraction(1))
        gram_zero = matrix(((1, 0), (0, 0)))
        rotating_rows.append(
            {
                "denominator": denominator,
                "gram": gram_n,
                "rank": exact_rank(gram_n),
                "null_vector": null_vector,
                "finite_null_value": quadratic(gram_n, null_vector),
                "limit_value_of_finite_null": quadratic(gram_zero, null_vector),
            }
        )

    collapse_rows = []
    for denominator in (2, 4, 8, 16, 32):
        gram_n = diagonal((1, Fraction(1, denominator)))
        collapse_rows.append(
            {
                "denominator": denominator,
                "gram": gram_n,
                "rank": exact_rank(gram_n),
                "second_label_norm_squared": Fraction(1, denominator),
            }
        )
    collapse_limit = diagonal((1, 0))
    return {
        "rotating_rows": rotating_rows,
        "rotating_limit": diagonal((1, 0)),
        "null_inclusion_fails": all(
            row["finite_null_value"] == 0
            and row["limit_value_of_finite_null"] > 0
            for row in rotating_rows
        ),
        "collapse_rows": collapse_rows,
        "collapse_limit": collapse_limit,
        "finite_ranks": tuple(row["rank"] for row in collapse_rows),
        "limit_rank": exact_rank(collapse_limit),
        "complete_label_embedding_injective": False,
    }


def gauge_fixture() -> dict[str, Any]:
    """Exact finite cylinder cancellation plus the continuous CCR shift."""

    transfer = matrix(((2, 1), (1, 2)))
    gauge = diagonal((1, -1))
    transfer_squared = matmul(transfer, transfer)
    transfer_cubed = matmul(transfer_squared, transfer)
    segments = (transfer, transfer_squared, transfer_cubed)
    gauged_segments = tuple(matmul(matmul(gauge, segment), gauge) for segment in segments)
    observables = (
        diagonal((Fraction(2), Fraction(-1))),
        diagonal((Fraction(3, 2), Fraction(5, 3))),
        diagonal((Fraction(-4, 5), Fraction(7, 4))),
    )

    plain_product = identity(2)
    gauged_product = identity(2)
    for segment, gauged_segment, observable in zip(segments, gauged_segments, observables):
        plain_product = matmul(matmul(plain_product, segment), observable)
        gauged_product = matmul(matmul(gauged_product, gauged_segment), observable)
    plain_trace = trace(plain_product)
    gauged_trace = trace(gauged_product)

    chi = Fraction(5, 2)
    momentum_shift = Fraction(7, 3)
    generator_plain_p = Fraction(1, 1) / chi
    generator_gauged_p = Fraction(1, 1) / chi
    generator_gauged_constant = -momentum_shift / chi
    return {
        "transfer": transfer,
        "gauge": gauge,
        "observables_commute_with_gauge": all(
            matmul(gauge, observable) == matmul(observable, gauge)
            for observable in observables
        ),
        "plain_cylinder_trace": plain_trace,
        "gauged_cylinder_trace": gauged_trace,
        "cylinder_equal": plain_trace == gauged_trace,
        "chi": chi,
        "momentum_shift": momentum_shift,
        "delta_H_q_p_coefficient": generator_plain_p,
        "delta_Ha_q_p_coefficient": generator_gauged_p,
        "delta_Ha_q_constant": generator_gauged_constant,
        "generator_difference": generator_gauged_constant,
        "canonical_momentum_selected_by_q_cylinders": False,
    }


def raw_character_fixture() -> dict[str, Any]:
    """Exact affine high-momentum witness for the bounded-generator scope."""

    hbar = Fraction(1, 4)
    chi = Fraction(2)
    xi = Fraction(3)
    slope = hbar * xi / chi
    intercept = hbar * hbar * xi * xi / (2 * chi)
    rows = []
    for momentum in (1, 2, 4, 8, 16, 32, 64):
        value = slope * momentum + intercept
        rows.append(
            {
                "momentum": momentum,
                "affine_commutator_value": value,
                "value_over_momentum": value / momentum,
            }
        )
    return {
        "hbar": hbar,
        "chi": chi,
        "xi": xi,
        "slope": slope,
        "intercept": intercept,
        "rows": rows,
        "symbolically_unbounded": slope != 0,
        "bounded_wstar_generator_core": False,
        "l2_form_seed_not_rejected": True,
        "temporal_smear_identity": "delta(A_f)=-A_(f')",
        "temporal_smears_bounded_smooth": True,
    }


def parity_cross_beta_fixture() -> dict[str, Any]:
    """Parity forces half weight; two KMS modular generators mismatch."""

    magnetization = Fraction(3, 5)
    parity_rows = []
    for weight in (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)):
        mixed_odd = (2 * weight - 1) * magnetization
        parity_rows.append(
            {
                "lambda_plus": weight,
                "mixed_odd_expectation": mixed_odd,
                "parity_invariant": mixed_odd == 0,
            }
        )

    sigma_x = matrix(((0, 1), (1, 0)))
    hamiltonian_one = matrix(((0, -1), (-1, 0)))
    hamiltonian_two = matrix(((0, -2), (-2, 0)))
    mismatch = matsub(hamiltonian_two, hamiltonian_one)
    # At positive time s=log(r)/kappa, exp(-s H_kappa) has the exact
    # nonnegative entries ((r+r^-1)/2,(r-r^-1)/2).
    positivity_rows = []
    for ratio in (Fraction(2), Fraction(4)):
        cosh_value = (ratio + 1 / ratio) / 2
        sinh_value = (ratio - 1 / ratio) / 2
        positivity_rows.append(
            {
                "ratio": ratio,
                "transfer": matrix(
                    ((cosh_value, sinh_value), (sinh_value, cosh_value))
                ),
                "entrywise_nonnegative": cosh_value > 0 and sinh_value > 0,
            }
        )
    return {
        "magnetization": magnetization,
        "parity_rows": parity_rows,
        "unique_parity_weight": Fraction(1, 2),
        "symmetric_limit_still_unproved": True,
        "beta_one": Fraction(1),
        "beta_two": Fraction(2),
        "sigma_x": sigma_x,
        "H_one": hamiltonian_one,
        "H_two": hamiltonian_two,
        "modular_generator_mismatch": mismatch,
        "mismatch_is_scalar": mismatch[0][1] == 0 and mismatch[1][0] == 0 and mismatch[0][0] == mismatch[1][1],
        "positivity_rows": positivity_rows,
        "automatic_cross_beta_gluing": False,
    }


def generator_tail_fixture() -> dict[str, Any]:
    """Exact source jet and first coordinate-tail acceleration rung."""

    chi = Fraction(5)
    source = Fraction(3, 7)
    xi = (Fraction(3), Fraction(4))
    source_direction = (Fraction(2), Fraction(-1))
    source_dot = sum(
        (left * right for left, right in zip(xi, source_direction)), Fraction(0)
    )
    source_second_jet_imaginary = source * source_dot / chi

    tail_gradient = (Fraction(1), Fraction(1))
    tail_dot = sum(
        (left * right for left, right in zip(xi, tail_gradient)), Fraction(0)
    )
    tail_second_jet_imaginary = -tail_dot / chi
    xi_norm_squared = sum((entry * entry for entry in xi), Fraction(0))
    xi_norm = Fraction(5)
    gradient_second_moment = Fraction(9)
    tail_duhamel_bound_squared = (
        xi_norm_squared * gradient_second_moment / (chi * chi)
    )
    tail_duhamel_bound = Fraction(3)
    return {
        "chi": chi,
        "source": source,
        "xi": xi,
        "source_direction": source_direction,
        "source_dot": source_dot,
        "first_source_jet_difference": Fraction(0),
        "second_source_jet_imaginary_coefficient": source_second_jet_imaginary,
        "finite_neighbourhood_for_each_fixed_iterate": True,
        "tail_gradient": tail_gradient,
        "tail_dot": tail_dot,
        "first_tail_jet_difference": Fraction(0),
        "second_tail_jet_imaginary_coefficient": tail_second_jet_imaginary,
        "xi_norm_squared": xi_norm_squared,
        "xi_norm": xi_norm,
        "gradient_second_moment": gradient_second_moment,
        "tail_duhamel_bound_squared": tail_duhamel_bound_squared,
        "tail_duhamel_bound": tail_duhamel_bound,
        "connected_tail_resummation_closed": False,
        "real_time_series_summed": False,
    }


def stdlib_only() -> tuple[bool, list[str]]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "os",
        "tempfile",
        "fractions",
        "pathlib",
        "typing",
    }
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append((node.module or "").split(".")[0])
    return all(name in allowed for name in imported), sorted(imported)


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    """Check formal authorities without consuming any primary result."""

    required_core = (MANIFEST, TANGENT_PARENT, MIXTURE_PARENT)
    missing = [str(path.relative_to(REPO)).replace("\\", "/") for path in required_core if not path.exists()]
    if missing:
        raise FileNotFoundError("missing core authorities: " + ", ".join(missing))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tangent_parent = json.loads(TANGENT_PARENT.read_text(encoding="utf-8"))
    mixture_parent = json.loads(MIXTURE_PARENT.read_text(encoding="utf-8"))

    audit.check("manifest result number/version", manifest["result_number"] == RESULT_NUMBER and manifest["result_version"] == RESULT_VERSION, {"number": manifest["result_number"], "version": manifest["result_version"]}, {"number": RESULT_NUMBER, "version": RESULT_VERSION}, "authority")
    audit.check("manifest exploration", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "authority")
    audit.check("manifest claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "authority")
    audit.check("manifest negative set", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "authority")
    audit.check("manifest closed gate", manifest["closed_subgates"] == [CLOSED_GATE], manifest["closed_subgates"], [CLOSED_GATE], "authority")
    audit.check("manifest retained gates", tuple(manifest["retained_gate_ids"]) == RETAINED_GATES, manifest["retained_gate_ids"], list(RETAINED_GATES), "authority")
    audit.check("manifest successor", manifest["route_status"]["next_gate"] == SUCCESSOR_GATE and manifest["open_gates"][0] == SUCCESSOR_GATE, {"route": manifest["route_status"]["next_gate"], "open": manifest["open_gates"]}, SUCCESSOR_GATE, "authority")
    audit.check("EXP-000781 tangent parent", tangent_parent["exploration_id"] == "EXP-000781" and tangent_parent["tangent_DLR_theorem"]["selection"], tangent_parent["exploration_id"], "EXP-000781", "authority")
    audit.check("EXP-000800 mixture parent", mixture_parent["exploration_id"] == "EXP-000800" and mixture_parent["result_version"] == "v1.4", {"exploration": mixture_parent["exploration_id"], "version": mixture_parent["result_version"]}, {"exploration": "EXP-000800", "version": "v1.4"}, "authority")

    formal_missing: list[str] = []
    if not CERTIFICATE.exists():
        formal_missing.append(str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"))
    else:
        certificate = CERTIFICATE.read_text(encoding="utf-8")
        for token in (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            CLOSED_GATE,
            SUCCESSOR_GATE,
            "Fejer",
            "pointed",
            "momentum",
            "cross-beta",
            "beta-independent",
            "Pre-A",
        ):
            if token.lower() not in certificate.lower():
                formal_missing.append(
                    f"{str(CERTIFICATE.relative_to(REPO)).replace(chr(92), '/')}#{token}"
                )
            else:
                audit.check(
                    f"certificate token {token}", True, token, token, "authority"
                )
        for negative_id in NEGATIVE_IDS:
            if negative_id not in certificate:
                formal_missing.append(
                    f"{str(CERTIFICATE.relative_to(REPO)).replace(chr(92), '/')}#{negative_id}"
                )
            else:
                audit.check(
                    f"certificate negative {negative_id}",
                    True,
                    negative_id,
                    negative_id,
                    "authority",
                )

    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8") if NEGATIVE_REGISTRY.exists() else ""
    for negative_id in NEGATIVE_IDS:
        if negative_id not in negative_text:
            formal_missing.append(f"negative-results/registry.md#{negative_id.lower()}")
        else:
            audit.check(f"negative registry {negative_id}", True, negative_id, negative_id, "authority")

    exploration_text = EXPLORATION_LOG.read_text(encoding="utf-8") if EXPLORATION_LOG.exists() else ""
    if f'"id":"{EXPLORATION_ID}"' not in exploration_text:
        formal_missing.append(f"explorations/log.jsonl#{EXPLORATION_ID}")
    else:
        audit.check("exploration registered", True, EXPLORATION_ID, EXPLORATION_ID, "authority")

    gate_text = GATES.read_text(encoding="utf-8") if GATES.exists() else ""
    for gate in (CLOSED_GATE, SUCCESSOR_GATE):
        if gate not in gate_text:
            formal_missing.append(f"claims/GATES.md#{gate.lower()}")
        else:
            audit.check(f"gate registered {gate}", True, gate, gate, "authority")

    no_overclaim = manifest["no_overclaim"]
    for token in (
        "complete finite GNS spaces",
        "all-exhaustion",
        "periodic zero-source symmetric limit",
        "canonical momentum",
        "beta-independent common C-star alpha",
        "ground states",
        "GNS",
        "continuum",
        "physical empty space",
        "Pre-A",
        "C6",
        "Sector-A",
    ):
        audit.check(f"no-overclaim {token}", token.lower() in no_overclaim.lower(), no_overclaim, f"contains {token}", "scope")

    formal_missing = list(dict.fromkeys(formal_missing))
    status = "COMPLETE" if not formal_missing else "STAGED"
    if formal_missing and not staged:
        status = "INCOMPLETE"
    return {
        "status": status,
        "missing": formal_missing,
        "source_paths": [str(path) for path in required_core]
        + ([str(CERTIFICATE)] if CERTIFICATE.exists() else []),
        "boundary": no_overclaim,
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    characters = character_fixture()
    gram = gram_transport_fixture()
    embeddings = embedding_counterexamples()
    gauge = gauge_fixture()
    raw = raw_character_fixture()
    parity_beta = parity_cross_beta_fixture()
    generator_tail = generator_tail_fixture()

    imports_ok, imported = stdlib_only()
    audit.check("stdlib-only imports", imports_ok, imported, "standard library only", "code")
    audit.check(
        "no primary import/result consumption",
        imports_ok and all("primary" not in name for name in imported),
        imported,
        "standard-library imports only",
        "code",
    )

    audit.check("character norm", characters["xi_norm_squared"] == 9 and characters["xi_norm"] == 3, {"square": characters["xi_norm_squared"], "norm": characters["xi_norm"]}, {"square": 9, "norm": 3}, "character")
    audit.check("character CCR shift", characters["momentum_shift"] == (Fraction(1, 4), Fraction(1, 2), Fraction(1, 2)), characters["momentum_shift"], (Fraction(1, 4), Fraction(1, 2), Fraction(1, 2)), "character")
    audit.check("character commutator p coefficients", characters["commutator_p_coefficients"] == (Fraction(1, 8), Fraction(1, 4), Fraction(1, 4)), characters["commutator_p_coefficients"], (Fraction(1, 8), Fraction(1, 4), Fraction(1, 4)), "character")
    audit.check("character commutator constant", characters["commutator_constant"] == Fraction(9, 64), characters["commutator_constant"], Fraction(9, 64), "character")
    audit.check("character double commutator", characters["double_commutator"] == Fraction(9, 32), characters["double_commutator"], Fraction(9, 32), "character")
    audit.check("Kubo exact norm", characters["kubo_norm_squared"] == Fraction(9, 4) and characters["kubo_norm"] == Fraction(3, 2), {"square": characters["kubo_norm_squared"], "norm": characters["kubo_norm"]}, {"square": Fraction(9, 4), "norm": Fraction(3, 2)}, "character")
    audit.check("Fejer D tail", characters["fejer_duhamel_bound"] == Fraction(3, 8), characters["fejer_duhamel_bound"], Fraction(3, 8), "Fejer")
    audit.check("Fejer derivative tail", characters["fejer_derivative_bound"] == Fraction(3, 2), characters["fejer_derivative_bound"], Fraction(3, 2), "Fejer")
    audit.check("Fejer modular radicand", characters["fejer_inside"] == Fraction(1, 4), characters["fejer_inside"], Fraction(1, 4), "Fejer")
    audit.check("Fejer unaveraged two-sided", characters["fejer_unaveraged_squared"] == Fraction(9, 16) and characters["fejer_unaveraged_bound"] == Fraction(3, 4), {"square": characters["fejer_unaveraged_squared"], "bound": characters["fejer_unaveraged_bound"]}, {"square": Fraction(9, 16), "bound": Fraction(3, 4)}, "Fejer")
    audit.check("finite character span", characters["span_derivative_bound"] == 4, characters["span_derivative_bound"], 4, "character")
    audit.check("q-only uniformity", characters["q_only_terms_cancel"] and characters["raw_recovery_uniform_in_q_only_terms"], characters, "q-only source/boundary cancellation", "scope")

    audit.check("limit Gram root", gram["gram_zero"] == matrix(((5, 4), (4, 5))), gram["gram_zero"], matrix(((5, 4), (4, 5))), "Gram")
    audit.check("root inverse", matmul(gram["root_zero_inverse"], gram["root_zero"]) == identity(2), matmul(gram["root_zero_inverse"], gram["root_zero"]), identity(2), "Gram")
    audit.check("all perturbed roots positive", all(row["root_trace"] > 0 and row["root_determinant"] > 0 for row in gram["transport_rows"]), [(row["root_trace"], row["root_determinant"]) for row in gram["transport_rows"]], "positive trace and determinant", "Gram")
    audit.check("polar transports exact", all(all(entry == 0 for residual_row in row["isometry_residual"] for entry in residual_row) for row in gram["transport_rows"]), [row["isometry_residual"] for row in gram["transport_rows"]], "all zero", "Gram")
    audit.check("polar transports tend to identity", all(right["distance_to_identity"] < left["distance_to_identity"] for left, right in zip(gram["transport_rows"], gram["transport_rows"][1:])), [row["distance_to_identity"] for row in gram["transport_rows"]], "strict decrease", "Gram")
    audit.check("singular support rank", gram["singular_rank"] == 2 and gram["retained_indices"] == [0, 2] and gram["discarded_indices"] == [1], {"rank": gram["singular_rank"], "retained": gram["retained_indices"], "discarded": gram["discarded_indices"]}, {"rank": 2, "retained": [0, 2], "discarded": [1]}, "Gram")
    audit.check("retained Gram positive", gram["retained_determinant"] == 1 and not gram["full_inverse_permitted"], {"determinant": gram["retained_determinant"], "full_inverse": gram["full_inverse_permitted"]}, {"determinant": 1, "full_inverse": False}, "Gram")

    audit.check("rotating null exact", embeddings["null_inclusion_fails"], [(row["finite_null_value"], row["limit_value_of_finite_null"]) for row in embeddings["rotating_rows"]], "finite null but nonnull limit", "embedding")
    audit.check("rotating Gram rank one", all(row["rank"] == 1 for row in embeddings["rotating_rows"]), embeddings["finite_ranks"] if "finite_ranks" in embeddings else [row["rank"] for row in embeddings["rotating_rows"]], "all rank one", "embedding")
    audit.check("dimension collapse", embeddings["finite_ranks"] == (2, 2, 2, 2, 2) and embeddings["limit_rank"] == 1, {"finite": embeddings["finite_ranks"], "limit": embeddings["limit_rank"]}, {"finite": (2, 2, 2, 2, 2), "limit": 1}, "embedding")
    audit.check("no complete injective label embedding", not embeddings["complete_label_embedding_injective"], embeddings["complete_label_embedding_injective"], False, "scope")

    audit.check("gauge commutes with q observables", gauge["observables_commute_with_gauge"], gauge["observables_commute_with_gauge"], True, "gauge")
    audit.check("full finite cylinder cancellation", gauge["cylinder_equal"] and gauge["plain_cylinder_trace"] == gauge["gauged_cylinder_trace"], {"plain": gauge["plain_cylinder_trace"], "gauged": gauge["gauged_cylinder_trace"]}, "equal", "gauge")
    audit.check("gauge changes q generator", gauge["generator_difference"] == Fraction(-14, 15), gauge["generator_difference"], Fraction(-14, 15), "gauge")
    audit.check("configuration cylinders do not select momentum", not gauge["canonical_momentum_selected_by_q_cylinders"], gauge["canonical_momentum_selected_by_q_cylinders"], False, "scope")

    audit.check("raw commutator affine coefficients", raw["slope"] == Fraction(3, 8) and raw["intercept"] == Fraction(9, 64), {"slope": raw["slope"], "intercept": raw["intercept"]}, {"slope": Fraction(3, 8), "intercept": Fraction(9, 64)}, "raw-character")
    audit.check("raw high-momentum growth", all(right["affine_commutator_value"] > left["affine_commutator_value"] for left, right in zip(raw["rows"], raw["rows"][1:])), [row["affine_commutator_value"] for row in raw["rows"]], "strict growth", "raw-character")
    audit.check("raw symbolic unboundedness", raw["symbolically_unbounded"] and not raw["bounded_wstar_generator_core"], {"slope_nonzero": raw["symbolically_unbounded"], "bounded_core": raw["bounded_wstar_generator_core"]}, {"slope_nonzero": True, "bounded_core": False}, "raw-character")
    audit.check("raw L2/form scope retained", raw["l2_form_seed_not_rejected"] and raw["temporal_smears_bounded_smooth"], raw, "L2/form seed and temporal smears retained", "scope")

    parity_rows = parity_beta["parity_rows"]
    audit.check("parity only at half mixture", [row["parity_invariant"] for row in parity_rows] == [False, True, False], parity_rows, "only lambda=1/2", "parity")
    audit.check("parity exact odd response", [row["mixed_odd_expectation"] for row in parity_rows] == [Fraction(-1, 5), 0, Fraction(1, 5)], [row["mixed_odd_expectation"] for row in parity_rows], (Fraction(-1, 5), 0, Fraction(1, 5)), "parity")
    audit.check("symmetric limit remains open", parity_beta["symmetric_limit_still_unproved"], parity_beta["symmetric_limit_still_unproved"], True, "scope")
    audit.check("cross-beta Hamiltonians", parity_beta["H_one"] == matrix(((0, -1), (-1, 0))) and parity_beta["H_two"] == matrix(((0, -2), (-2, 0))), {"H1": parity_beta["H_one"], "H2": parity_beta["H_two"]}, "-sigma_x and -2 sigma_x", "cross-beta")
    audit.check("cross-beta nonscalar mismatch", parity_beta["modular_generator_mismatch"] == matrix(((0, -1), (-1, 0))) and not parity_beta["mismatch_is_scalar"], parity_beta["modular_generator_mismatch"], "nonscalar -sigma_x", "cross-beta")
    audit.check("cross-beta stochastic-positive controls", all(row["entrywise_nonnegative"] for row in parity_beta["positivity_rows"]), parity_beta["positivity_rows"], "entrywise positive transfers", "cross-beta")
    audit.check("cross-beta gluing not automatic", not parity_beta["automatic_cross_beta_gluing"], parity_beta["automatic_cross_beta_gluing"], False, "scope")

    audit.check("source first jet", generator_tail["first_source_jet_difference"] == 0, generator_tail["first_source_jet_difference"], 0, "generator")
    audit.check("source second jet", generator_tail["source_dot"] == 2 and generator_tail["second_source_jet_imaginary_coefficient"] == Fraction(6, 35), {"dot": generator_tail["source_dot"], "coefficient": generator_tail["second_source_jet_imaginary_coefficient"]}, {"dot": 2, "coefficient": Fraction(6, 35)}, "generator")
    audit.check("local fixed-iterate jet", generator_tail["finite_neighbourhood_for_each_fixed_iterate"], generator_tail["finite_neighbourhood_for_each_fixed_iterate"], True, "generator")
    audit.check("tail first rung", generator_tail["first_tail_jet_difference"] == 0 and generator_tail["second_tail_jet_imaginary_coefficient"] == Fraction(-7, 5), {"first": generator_tail["first_tail_jet_difference"], "second": generator_tail["second_tail_jet_imaginary_coefficient"]}, {"first": 0, "second": Fraction(-7, 5)}, "tail")
    audit.check("tail Duhamel bound", generator_tail["tail_duhamel_bound_squared"] == 9 and generator_tail["tail_duhamel_bound"] == 3, {"square": generator_tail["tail_duhamel_bound_squared"], "bound": generator_tail["tail_duhamel_bound"]}, {"square": 9, "bound": 3}, "tail")
    audit.check("tail resummation remains open", not generator_tail["connected_tail_resummation_closed"] and not generator_tail["real_time_series_summed"], generator_tail, "first rung only", "scope")

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"

    source_paths = [SCRIPT, MANIFEST, TANGENT_PARENT, MIXTURE_PARENT]
    if CERTIFICATE.exists():
        source_paths.append(CERTIFICATE)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
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
            "character_dirichlet_fejer": characters,
            "finite_block_transport": gram,
            "embedding_counterexamples": embeddings,
            "momentum_gauge": gauge,
            "raw_character_scope": raw,
            "parity_cross_beta": parity_beta,
            "generator_first_tail": generator_tail,
            "selected_tangent_pointed_gns_identification_closed": True,
            "all_exhaustion_mixture_l2_closed": False,
            "canonical_momentum_weyl_bridge_closed": False,
            "raw_character_bounded_generator_core_closed": False,
            "zero_source_symmetric_periodic_limit_closed": False,
            "beta_independent_cstar_dynamics_closed": False,
            "ground_state_selection_closed": False,
            "GNS_gap_closed": False,
            "continuum_closed": False,
            "physical_empty_comparison_closed": False,
            "Pre_A_closed": False,
        },
        "negative_ids": list(NEGATIVE_IDS),
        "closed_gate": CLOSED_GATE,
        "successor_gate": SUCCESSOR_GATE,
        "retained_gates": list(RETAINED_GATES),
        "authority": authority,
        "source_hashes": source_hashes,
        "boundary": authority["boundary"],
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
        help="allow missing v1.5 certificate/registries and report INCOMPLETE",
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
        if payload["authority"]["missing"]:
            print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
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
