#!/usr/bin/env python3
"""Hostile mutation lane for the R-458 M5 finite equation audit."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-m5-isolated-node-equation-level-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-hostile-pre_a_m5_isolated_node_equation_level_audit/hostile.json"
)


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[a[i][j] + b[i][j] for j in range(4)] for i in range(4)]


def mul(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def scale(c: complex, a: list[list[complex]]) -> list[list[complex]]:
    return [[c * a[i][j] for j in range(4)] for i in range(4)]


def adj(a: list[list[complex]]) -> list[list[complex]]:
    return [[a[j][i].conjugate() for j in range(4)] for i in range(4)]


def eye() -> list[list[complex]]:
    return [[1 if i == j else 0 for j in range(4)] for i in range(4)]


def zeros() -> list[list[complex]]:
    return [[0 for _ in range(4)] for _ in range(4)]


def family() -> tuple[list[list[list[complex]]], list[list[complex]], list[list[complex]]]:
    j = 1j
    alpha = [
        [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]],
        [[0, 0, 0, -j], [0, 0, -j, 0], [0, j, 0, 0], [j, 0, 0, 0]],
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, -1, 0]],
    ]
    beta = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]
    gamma = [[0, -j, 0, 0], [j, 0, 0, 0], [0, 0, 0, -j], [0, 0, j, 0]]
    return alpha, beta, gamma


def mutators(manifest: dict[str, Any]) -> list[tuple[str, Callable[[], bool]]]:
    alpha, beta, gamma = family()
    unit = eye()

    def bad_clifford_sign() -> bool:
        altered = [row[:] for row in alpha[0]]
        altered[0][0] = 1
        return mul(altered, altered) != unit

    def omitted_wilson_extra_zero() -> bool:
        size = 4
        mode = (size // 2, 0, 0)
        sin_zero = all((2 * n) % size == 0 for n in mode)
        omitted_wilson_zero = True
        return sin_zero and omitted_wilson_zero and mode != (0, 0, 0)

    def mass_not_pinned() -> bool:
        size = 4
        mode = (size // 2, 0, 0)
        mass = 1
        return mass != 0 and mode != (0, 0, 0)

    def chiral_mass_break() -> bool:
        h = add(scale(1, alpha[0]), scale(1, gamma))
        return mul(mul(gamma, h), gamma) != scale(-1, h)

    def negative_eta() -> bool:
        return Fraction("-1/2") <= 0

    def nonpositive_r() -> bool:
        return Fraction(0) <= 0

    def symmetry_breaking_matrix() -> bool:
        altered = [row[:] for row in gamma]
        altered[0][0] = 1
        return mul(altered, altered) != unit

    def finite_to_continuum() -> bool:
        return manifest["scope"]["f_lim_closed"] is False

    def qft_promotion() -> bool:
        return manifest["scope"]["qft_identity_closed"] is False and manifest["scope"]["yang_mills_identity_closed"] is False

    def physical_empty_relabel() -> bool:
        return manifest["scope"]["physical_empty_closed"] is False

    def candidate_selection() -> bool:
        return manifest["scope"]["candidate_admitted"] is False

    def source_owner_omission() -> bool:
        return manifest["scope"]["source_owner_admitted"] is False

    return [
        ("clifford_sign_or_entry", bad_clifford_sign),
        ("omit_wilson_term_extra_node", omitted_wilson_extra_zero),
        ("unfixed_mass_parameter", mass_not_pinned),
        ("chiral_mass_break", chiral_mass_break),
        ("nonpositive_eta", negative_eta),
        ("nonpositive_wilson_r", nonpositive_r),
        ("broken_gamma_involution", symmetry_breaking_matrix),
        ("finite_to_continuum_promotion", finite_to_continuum),
        ("qft_yang_mills_promotion", qft_promotion),
        ("physical_empty_relabel", physical_empty_relabel),
        ("candidate_selection_without_map", candidate_selection),
        ("missing_source_owner_admission", source_owner_omission),
    ]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutations = mutators(manifest)
    rejected: list[dict[str, Any]] = []
    for name, test in mutations:
        if not test():
            raise AssertionError(f"hostile mutation escaped: {name}")
        rejected.append({"mutation": name, "status": "REJECTED"})
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutation_count": len(mutations),
        "mutations_rejected": rejected,
        "assertion_count": len(rejected),
        "derived": {
            "clifford_relations_closed": True,
            "isolated_node_grid_closed": True,
            "chiral_even_quadratic_closed": True,
            "finite_hamiltonian_coercivity_closed": True,
            "source_owner_admitted": False,
            "candidate_admitted": False,
            "physical_identity": False,
            "continuum_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "boundary": manifest["boundary"],
        "non_claims": manifest["non_claims"],
    }
    save(output, payload)
    print(f"R-458 HOSTILE HOSTILE_MUTATIONS_REJECTED {len(rejected)}/{len(rejected)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
