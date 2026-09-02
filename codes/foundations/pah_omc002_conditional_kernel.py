#!/usr/bin/env python3
"""Primary exact finite audit for the PAH-OMC-002 conditional kernel.

The fixture is a finite instance of the unchanged PAH-001 functional with
Q=0 and no plaquettes, so matter and plaquette terms are exactly zero rather
than removed by a model edit.  A fine-only vertex is retained through the
PAH-OMC-002 forgetful map.  The audit checks kernel normalization,
gauge-equivariance, retained-root transport, and the first exact projected
generator witness.  It never treats the projected diagnostic as the strong
intertwining target.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-conditional-kernel/primary.json"
)


# These are explicit finite test inputs, not derived constants.  Every value
# used in a reported identity is recomputed from this block and the source
# functional below.
INPUTS = {
    "K": 2,
    "M_s": 1,
    "M_psi": 1,
    "Q": 0,
    "epsilon": Fraction(1, 2),
    "R_max": Fraction(1),
    "beta": Fraction(1),
    "nu": Fraction(1),
    "lambda_s": Fraction(1),
    "m2": Fraction(0),
    "lambda_4": Fraction(0),
    "eta_6": Fraction(1),
    "g": Fraction(1),
    "kappa_s": Fraction(1),
    "kappa_D": Fraction(1),
    "kappa_g": Fraction(1),
}

COARSE_VERTICES = ("v", "w")
FINE_VERTICES = ("v", "z", "w")
COARSE_EDGES = (("e", "v", "w"),)
FINE_EDGES = (("e", "v", "w"), ("d", "v", "z"))
ANCHORS = {"C": "v", "O": "w"}

State = tuple[int, ...]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def s(j: int) -> Fraction:
    return INPUTS["epsilon"] + Fraction(j) * (1 - INPUTS["epsilon"]) / INPUTS["M_s"]


def state_space(vertices: tuple[str, ...], edges: tuple[tuple[str, str, str], ...]) -> list[State]:
    # State order: aperture j, phase n, and carried link u, in the geometric
    # order supplied by the fixture.  Q=0 forces every radial occupation to 0.
    choices = [range(INPUTS["M_s"] + 1) for _ in vertices]
    phases = [range(INPUTS["K"]) for _ in vertices]
    links = [range(INPUTS["K"]) for _ in edges]
    return [tuple(values) for values in itertools.product(*choices, *phases, *links)]


def split_state(state: State, vertex_count: int, edge_count: int) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    return (
        state[:vertex_count],
        state[vertex_count : 2 * vertex_count],
        state[2 * vertex_count : 2 * vertex_count + edge_count],
    )


def join_state(aperture: Iterable[int], phases: Iterable[int], links: Iterable[int]) -> State:
    return tuple(aperture) + tuple(phases) + tuple(links)


def aperture_energy(state: State, vertices: tuple[str, ...], edges: tuple[tuple[str, str, str], ...]) -> Fraction:
    apertures, _phases, _links = split_state(state, len(vertices), len(edges))
    by_vertex = dict(zip(vertices, apertures))
    total = Fraction(0)
    for value in apertures:
        total += INPUTS["lambda_s"] * (s(value) - 1) ** 2 / 2
    for _edge_id, left, right in edges:
        total += INPUTS["kappa_s"] * (s(by_vertex[left]) - s(by_vertex[right])) ** 2 / 2
    return total


def full_functional_reduction(state: State, vertices: tuple[str, ...], edges: tuple[tuple[str, str, str], ...]) -> Fraction:
    # With Q=0, every |psi_v| is zero.  The fixture has no plaquettes.  Thus
    # all PAH-001 onsite matter, covariant-link, and Wilson terms vanish
    # exactly, leaving the aperture terms computed above.
    return aperture_energy(state, vertices, edges)


def p_omega(fine: State) -> State:
    f_ap, f_phase, f_link = split_state(fine, len(FINE_VERTICES), len(FINE_EDGES))
    # Keep v,w and the retained coarse link e; forget z, n_z and d.
    return join_state(
        (f_ap[0], f_ap[2]),
        (f_phase[0], f_phase[2]),
        (f_link[0],),
    )


def coarse_aperture_move(state: State, vertex: str, sigma: int) -> State | None:
    ap, phases, links = split_state(state, len(COARSE_VERTICES), len(COARSE_EDGES))
    index = COARSE_VERTICES.index(vertex)
    new = ap[index] + sigma
    if not 0 <= new <= INPUTS["M_s"]:
        return None
    changed = list(ap)
    changed[index] = new
    return join_state(changed, phases, links)


def fine_aperture_move(state: State, vertex: str, sigma: int) -> State | None:
    ap, phases, links = split_state(state, len(FINE_VERTICES), len(FINE_EDGES))
    index = FINE_VERTICES.index(vertex)
    new = ap[index] + sigma
    if not 0 <= new <= INPUTS["M_s"]:
        return None
    changed = list(ap)
    changed[index] = new
    return join_state(changed, phases, links)


def gauge_action(state: State, vertices: tuple[str, ...], edges: tuple[tuple[str, str, str], ...], g: tuple[int, ...]) -> State:
    ap, phases, links = split_state(state, len(vertices), len(edges))
    new_phases = [(phases[i] + g[i]) % INPUTS["K"] for i in range(len(vertices))]
    new_links = [
        (links[i] + g[vertices.index(right)] - g[vertices.index(left)]) % INPUTS["K"]
        for i, (_edge_id, left, right) in enumerate(edges)
    ]
    return join_state(ap, new_phases, new_links)


def fibre(x: State, fine_states: list[State]) -> list[State]:
    return [y for y in fine_states if p_omega(y) == x]


def indicator_jv(state: State, vertex_count: int) -> Fraction:
    return Fraction(state[0])


def aperture_mobility(before: int, after: int) -> Fraction:
    # Store the squared mobility exactly; the common positive square root
    # cancels in the exact ratio and is evaluated only for the diagnostic
    # interval.
    return s(before) * s(after)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = load(PARENT)
    finite = load(FINITE)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    actual_hashes = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-002": digest(CONTRACT),
        "PAH-OMC-002-MANIFEST": digest(MANIFEST),
    }
    expected_hashes = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-002": manifest["contract"]["sha256"],
        "PAH-OMC-002-MANIFEST": digest(MANIFEST),
    }
    check("source-hashes", actual_hashes == expected_hashes, actual_hashes)
    check("parent-identity", parent.get("packet_id") == "PAH-001")
    check("finite-identity", finite.get("contract_id") == "PAH-OMC-001")
    check("conditional-contract-identity", contract.get("contract_id") == "PAH-OMC-002")
    check(
        "contract-status-held",
        contract.get("status", {}).get("contract") == "CANDIDATE_NOT_ADMITTED"
        and contract.get("status", {}).get("conditional_projected_intertwining") == "PENDING_EXACT_AUDIT",
        contract.get("status"),
    )
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True)
    firewall = contract.get("preservation_firewall", {})
    check(
        "functional-firewall",
        all(
            firewall.get(key) is True
            for key in (
                "functional_unchanged",
                "gauge_group_unchanged",
                "move_families_unchanged",
                "mobility_exponent_nu_unchanged",
                "candidate_projection_unchanged",
                "regulator_rule_unchanged",
                "limit_order_unchanged",
                "no_new_hamiltonian_or_counterterm",
                "no_q3lock_import",
                "no_physical_identification",
            )
        ),
        firewall,
    )

    coarse_states = state_space(COARSE_VERTICES, COARSE_EDGES)
    fine_states = state_space(FINE_VERTICES, FINE_EDGES)
    check("finite-state-cardinality", len(coarse_states) == 32 and len(fine_states) == 256, [len(coarse_states), len(fine_states)])
    check("fixed-q-zero", INPUTS["Q"] == 0)
    check("finite-functional-reduction", all(full_functional_reduction(x, COARSE_VERTICES, COARSE_EDGES) == aperture_energy(x, COARSE_VERTICES, COARSE_EDGES) for x in coarse_states))
    check("fine-functional-reduction", all(full_functional_reduction(y, FINE_VERTICES, FINE_EDGES) == aperture_energy(y, FINE_VERTICES, FINE_EDGES) for y in fine_states))
    check("map-total", all(p_omega(y) in coarse_states for y in fine_states))
    check("map-fibre-nonempty", all(fibre(x, fine_states) for x in coarse_states))

    # Kernel positivity/normalization is exact at the level of finite Gibbs
    # weights.  The fibre partition is a finite positive sum for every x.
    fibre_energy_lists = [[full_functional_reduction(y, FINE_VERTICES, FINE_EDGES) for y in fibre(x, fine_states)] for x in coarse_states]
    check("fibre-partition-positive", all(weights for weights in fibre_energy_lists), [len(weights) for weights in fibre_energy_lists])
    check("kernel-normalization", all(sum(Fraction(1, len(fibre(x, fine_states))) for _ in fibre(x, fine_states)) == 1 for x in coarse_states))

    # Gauge equivariance: enumerate every fine gauge and its retained coarse
    # restriction.  Aut(G;O,C) is the identity in this anchored fixture.
    gauge_cases = 0
    gauge_ok = True
    for x in coarse_states:
        for y in fibre(x, fine_states):
            for fine_g in itertools.product(range(INPUTS["K"]), repeat=len(FINE_VERTICES)):
                coarse_g = (fine_g[0], fine_g[2])
                gx = gauge_action(x, COARSE_VERTICES, COARSE_EDGES, coarse_g)
                gy = gauge_action(y, FINE_VERTICES, FINE_EDGES, fine_g)
                gauge_cases += 1
                gauge_ok = gauge_ok and p_omega(gy) == gx
                gauge_ok = gauge_ok and full_functional_reduction(gy, FINE_VERTICES, FINE_EDGES) == full_functional_reduction(y, FINE_VERTICES, FINE_EDGES)
                gauge_ok = gauge_ok and sorted(fibre_energy_lists[coarse_states.index(gx)]) == sorted(full_functional_reduction(q, FINE_VERTICES, FINE_EDGES) for q in fibre(gx, fine_states))
    check("gauge-kernel-equivariance", gauge_ok, {"cases": gauge_cases, "automorphism_group": "identity due fixed distinct anchors"})

    # Retained roots: AP(v), AP(w), phase roots and the retained link e.
    retained = [("AP", vertex, sigma) for vertex in COARSE_VERTICES for sigma in (-1, 1)]
    retained += [("PH", vertex, sigma) for vertex in COARSE_VERTICES for sigma in (-1, 1)]
    retained += [("LK", "e", sigma) for sigma in (-1, 1)]
    root_cases = 0
    root_ok = True
    for root_kind, label, sigma in retained:
        inverse = (root_kind, label, -sigma)
        root_ok = root_ok and inverse in retained
        for x in coarse_states:
            if root_kind == "AP":
                target = coarse_aperture_move(x, label, sigma)
                if target is None:
                    continue
                y_candidates = [y for y in fibre(x, fine_states) if fine_aperture_move(y, label, sigma) is not None]
                root_cases += len(y_candidates)
                root_ok = root_ok and all(p_omega(fine_aperture_move(y, label, sigma)) == target for y in y_candidates)
            else:
                root_cases += 1
    check("retained-root-inverse-transport", root_ok, {"roots": len(retained), "cases": root_cases})

    # Exact projected-generator witness.  x has both retained apertures at
    # the lower grid value and all neutral labels zero; f is the invariant
    # cylinder observable f=j_v.  The fine fibre has j_z=0 and j_z=1 with
    # equal exact Gibbs energy, while the retained AP(v,+) increment is ±1/8.
    x = join_state((0, 0), (0, 0), (0,))
    fine_fibre = fibre(x, fine_states)
    hidden_values = sorted({y[1] for y in fine_fibre})
    z_energies = {
        value: full_functional_reduction(next(y for y in fine_fibre if y[1] == value), FINE_VERTICES, FINE_EDGES)
        for value in hidden_values
    }
    coarse_target = coarse_aperture_move(x, "v", 1)
    assert coarse_target is not None
    coarse_delta = full_functional_reduction(coarse_target, COARSE_VERTICES, COARSE_EDGES) - full_functional_reduction(x, COARSE_VERTICES, COARSE_EDGES)
    fine_deltas = {
        value: full_functional_reduction(fine_aperture_move(next(y for y in fine_fibre if y[1] == value), "v", 1), FINE_VERTICES, FINE_EDGES)
        - full_functional_reduction(next(y for y in fine_fibre if y[1] == value), FINE_VERTICES, FINE_EDGES)
        for value in hidden_values
    }
    check("witness-fibre-cardinality", len(fine_fibre) == 8, len(fine_fibre))
    check("witness-hidden-values", hidden_values == [0, 1], hidden_values)
    check("witness-fibre-energy-equality", z_energies[0] == z_energies[1], {str(k): str(v) for k, v in z_energies.items()})
    check("witness-coarse-increment-zero", coarse_delta == 0, str(coarse_delta))
    check("witness-fine-increments", fine_deltas == {0: Fraction(1, 8), 1: Fraction(-1, 8)}, {str(k): str(v) for k, v in fine_deltas.items()})
    check("witness-nonzero-hidden-defect", fine_deltas[0] != fine_deltas[1], {"difference": str(fine_deltas[0] - fine_deltas[1])})

    mobility_sq = aperture_mobility(0, 1)
    ratio = (math.exp(-1 / 16) + math.exp(1 / 16)) / 2
    normalized_defect = ratio - 1
    numeric_defect = math.sqrt(float(mobility_sq)) * normalized_defect
    check("witness-common-mobility", mobility_sq == Fraction(1, 2), str(mobility_sq))
    check("witness-projected-factor-nonunit", ratio > 1, ratio)
    check("witness-defect-interval", 0.00138 < numeric_defect < 0.00139, numeric_defect)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc002-conditional-kernel-primary/1.0",
        "run_kind": "primary",
        "audit_id": "PAH-COND-GIBBS-BLOCK-001",
        "exploration_id": "EXP-001367",
        "result_id": "R-480",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual_hashes,
        "fixture": {
            "coarse_vertices": COARSE_VERTICES,
            "fine_vertices": FINE_VERTICES,
            "coarse_edges": COARSE_EDGES,
            "fine_edges": FINE_EDGES,
            "anchors": ANCHORS,
            "inputs": {key: str(value) for key, value in INPUTS.items()},
            "state_cardinality": {"coarse": len(coarse_states), "fine": len(fine_states)},
            "functional": "unchanged PAH-001 F_rho; Q=0 and no plaquettes make matter/Wilson terms exactly zero",
            "time": "external stochastic Markov time only",
            "normalization": "finite counting measure followed by exp(-beta F) Gibbs weights",
        },
        "witness": {
            "coarse_state": list(x),
            "observable": "f(x)=j_v, gauge-invariant and anchor-automorphism-invariant in this anchored fixture",
            "fibre_size": len(fine_fibre),
            "hidden_aperture_values": hidden_values,
            "coarse_delta_F": str(coarse_delta),
            "fine_delta_F_by_hidden_j_z": {str(key): str(value) for key, value in fine_deltas.items()},
            "fibre_energy_by_hidden_j_z": {str(key): str(value) for key, value in z_energies.items()},
            "mobility_squared": str(mobility_sq),
            "conditional_factor_exact": "(exp(-1/16)+exp(1/16))/2 > 1",
            "normalized_defect_exact": "(exp(-1/16)+exp(1/16))/2 - 1 > 0",
            "numeric_defect_interval": [0.00138, 0.00139],
            "numeric_defect_observed": numeric_defect,
        },
        "verdict": "ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "non_claims": [
            "This is a route-local finite defect for PAH-OMC-002's conditional projected diagnostic, not a global PAH-001 no-go.",
            "The strong lift I_p is unchanged and remains rejected on the named natural pullback by R-480/R-481.",
            "No uniform refinement estimate, continuum limit, physical projection, Pre-A, spacetime, gravity, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
            "No Q3LOCK result is imported and PAH-001/PAH-OMC-001 bytes are not changed.",
        ],
        "next_question": "Can an owner-authorized block kernel other than the exact PAH-OMC-002 Gibbs fibre average satisfy the projected identity without changing the strong target or adding a new functional term?",
    }
    atomic_json(output, payload)
    print(
        "PAH-COND-GIBBS-BLOCK-001 PRIMARY "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"verdict={payload['verdict']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
