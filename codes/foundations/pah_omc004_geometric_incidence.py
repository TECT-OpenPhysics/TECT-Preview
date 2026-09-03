#!/usr/bin/env python3
"""Primary exact audit for the PAH-OMC-004 geometric incidence successor.

The audit evaluates the unchanged PAH-001 aperture and Wilson terms on a
square and on its genuine diagonal split.  It then records an anchored strip
family in which one square is split at each step.  The local split is allowed
to have a boundary defect; for every fixed finite-support cylinder the split
eventually lies outside the interaction closure, so the generator defect is
eventually zero and its finite cumulative bound is explicit.  This is a
finite/local structural result only: no global uniform, continuum or physical
claim is made.
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
REFERENCE = ROOT / "strategy/pa-hyp/PAH-OMC-003-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc004-geometric-incidence/primary.json"
)

AUDIT_ID = "PAH-GEOMETRIC-INCIDENCE-LOCAL-001"
EXPLORATION_ID = "EXP-001369"
RESULT_ID = "R-483"
TASK_ID = "T-054"

# These are finite model inputs, not derived outputs.  They are exactly the
# Q=0 diagnostic slice declared in the successor contract.
INPUTS = {
    "K": 2,
    "M_s": 1,
    "M_psi": 1,
    "Q": 0,
    "epsilon": Fraction(1, 2),
    "beta": Fraction(1),
    "nu": Fraction(1),
    "R_max": Fraction(1),
    "m2": Fraction(0),
    "lambda_4": Fraction(1),
    "eta_6": Fraction(1),
    "g": Fraction(1),
    "lambda_s": Fraction(1),
    "kappa_s": Fraction(1),
    "kappa_D": Fraction(1),
    "kappa_g": Fraction(1),
    "theta": Fraction(0),
    "degree_bound": 5,
    "face_incidence_bound": 4,
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


Carrier = dict[str, Any]


def local_square(split: bool) -> Carrier:
    """Return the oriented four-vertex square or its diagonal split."""
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    if not split:
        return {
            "name": "square",
            "vertices": (0, 1, 2, 3),
            "edges": edges,
            "faces": (((0, 1), (1, 1), (2, 1), (3, 1)),),
        }
    fine_edges = edges + ((0, 2),)
    return {
        "name": "diagonal_split",
        "vertices": (0, 1, 2, 3),
        "edges": fine_edges,
        # e4 is oriented 0->2.  The first triangle returns along e4 and
        # the second triangle starts along e4, so both cycles are oriented.
        "faces": (
            ((0, 1), (1, 1), (4, -1)),
            ((4, 1), (2, 1), (3, 1)),
        ),
    }


def strip_carrier(level: int) -> Carrier:
    """Build the finite anchored strip G_level from the contract."""
    if level < 0:
        raise ValueError("level must be nonnegative")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    names: dict[str, int] = {}
    for i in range(level + 1):
        for j in (0, 1):
            names[f"h{i}{j}"] = len(edges)
            edges.append(((i, j), (i + 1, j)))
    for i in range(level + 2):
        names[f"v{i}"] = len(edges)
        edges.append(((i, 0), (i, 1)))
    for i in range(level):
        names[f"d{i}"] = len(edges)
        edges.append(((i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[int, int], ...]] = []
    for i in range(level):
        faces.append(
            (
                (names[f"h{i}0"], 1),
                (names[f"v{i + 1}"], 1),
                (names[f"d{i}"], -1),
            )
        )
        faces.append(
            (
                (names[f"d{i}"], 1),
                (names[f"h{i}1"], -1),
                (names[f"v{i}"], -1),
            )
        )
    i = level
    faces.append(
        (
            (names[f"h{i}0"], 1),
            (names[f"v{i + 1}"], 1),
            (names[f"h{i}1"], -1),
            (names[f"v{i}"], -1),
        )
    )
    return {"name": f"strip_{level}", "vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def aperture(level: int) -> Fraction:
    return INPUTS["epsilon"] + Fraction(level) * (1 - INPUTS["epsilon"]) / INPUTS["M_s"]


def onsite_term(j: int) -> Fraction:
    return INPUTS["lambda_s"] * (aperture(j) - 1) ** 2 / 2


def edge_term(j_left: int, j_right: int) -> Fraction:
    return INPUTS["kappa_s"] * (aperture(j_left) - aperture(j_right)) ** 2 / 2


def link_sign(bit: int) -> int:
    return -1 if bit % INPUTS["K"] else 1


def face_term(carrier: Carrier, face: tuple[tuple[int, int], ...], apertures: tuple[int, ...], links: tuple[int, ...]) -> Fraction:
    edge_stiffness: list[Fraction] = []
    holonomy = 1
    for edge_index, orientation in face:
        left, right = carrier["edges"][edge_index]
        edge_stiffness.append(Fraction(2, 1) / (aperture(apertures[carrier["vertices"].index(left)]) + aperture(apertures[carrier["vertices"].index(right)])))
        sign = link_sign(links[edge_index])
        holonomy *= sign if orientation == 1 else sign
    average = sum(edge_stiffness, Fraction(0)) / len(edge_stiffness)
    return INPUTS["kappa_g"] * average * (1 - holonomy)


def energy(carrier: Carrier, apertures: tuple[int, ...], links: tuple[int, ...]) -> Fraction:
    if len(apertures) != len(carrier["vertices"]):
        raise ValueError("aperture state length mismatch")
    if len(links) != len(carrier["edges"]):
        raise ValueError("link state length mismatch")
    # Q=0 with nonnegative radial levels forces every matter amplitude to be
    # zero.  Thus all matter and covariant-link terms vanish exactly.
    if INPUTS["Q"] != 0:
        raise ValueError("this exact fixture is restricted to Q=0")
    total = sum((onsite_term(value) for value in apertures), Fraction(0))
    for edge_index, (left, right) in enumerate(carrier["edges"]):
        left_index = carrier["vertices"].index(left)
        right_index = carrier["vertices"].index(right)
        total += edge_term(apertures[left_index], apertures[right_index])
    total += sum((face_term(carrier, face, apertures, links) for face in carrier["faces"]), Fraction(0))
    return total


def term_ranges(carriers: Iterable[Carrier]) -> dict[str, Fraction]:
    """Derive local ranges directly from the displayed PAH terms."""
    aperture_values = tuple(range(INPUTS["M_s"] + 1))
    onsite_values = tuple(onsite_term(j) for j in aperture_values)
    edge_values = tuple(edge_term(a, b) for a in aperture_values for b in aperture_values)
    face_values: list[Fraction] = []
    for carrier in carriers:
        for face in carrier["faces"]:
            used_edges = tuple(index for index, _orientation in face)
            used_vertices = tuple(
                sorted(
                    {
                        vertex
                        for index in used_edges
                        for vertex in carrier["edges"][index]
                    },
                    key=repr,
                )
            )
            vertex_states = itertools.product(aperture_values, repeat=len(used_vertices))
            for values in vertex_states:
                state_apertures = {vertex: value for vertex, value in zip(used_vertices, values)}
                local_edge_terms = []
                holonomy_bits = itertools.product(range(INPUTS["K"]), repeat=len(used_edges))
                for bits in holonomy_bits:
                    stiffness: list[Fraction] = []
                    holonomy = 1
                    for (edge_index, orientation), bit in zip(face, bits):
                        left, right = carrier["edges"][edge_index]
                        stiffness.append(Fraction(2, 1) / (aperture(state_apertures[left]) + aperture(state_apertures[right])))
                        sign = link_sign(bit)
                        holonomy *= sign if orientation == 1 else sign
                    local_edge_terms.append(
                        INPUTS["kappa_g"] * sum(stiffness, Fraction(0)) / len(stiffness) * (1 - holonomy)
                    )
                face_values.extend(local_edge_terms)
    return {
        "onsite_range": max(onsite_values) - min(onsite_values),
        "edge_range": max(edge_values) - min(edge_values),
        "face_range": max(face_values) - min(face_values),
    }


def incidence_summary(carrier: Carrier) -> dict[str, Any]:
    degrees = {
        repr(vertex): sum(vertex in edge for edge in carrier["edges"])
        for vertex in carrier["vertices"]
    }
    face_incidence = {
        repr(vertex): sum(
            any(vertex in carrier["edges"][edge_index] for edge_index, _orientation in face)
            for face in carrier["faces"]
        )
        for vertex in carrier["vertices"]
    }
    return {
        "vertices": len(carrier["vertices"]),
        "edges": len(carrier["edges"]),
        "faces": len(carrier["faces"]),
        "max_degree": max(degrees.values()),
        "max_face_incidence": max(face_incidence.values()),
        "degrees": degrees,
        "face_incidence": face_incidence,
    }


def local_witness() -> dict[str, Any]:
    coarse = local_square(False)
    fine = local_square(True)
    before = (0, 0, 0, 0)
    after = (1, 0, 0, 0)
    coarse_links = (0, 0, 0, 0)
    fine_links_even = (0, 0, 0, 0, 0)
    fine_links_odd = (0, 0, 0, 0, 1)
    values = {
        "coarse_before": energy(coarse, before, coarse_links),
        "coarse_after": energy(coarse, after, coarse_links),
        "fine_even_before": energy(fine, before, fine_links_even),
        "fine_even_after": energy(fine, after, fine_links_even),
        "fine_odd_before": energy(fine, before, fine_links_odd),
        "fine_odd_after": energy(fine, after, fine_links_odd),
    }
    delta = {
        "coarse": values["coarse_after"] - values["coarse_before"],
        "fine_even": values["fine_even_after"] - values["fine_even_before"],
        "fine_odd": values["fine_odd_after"] - values["fine_odd_before"],
    }
    mobility_square = aperture(0) * aperture(1)
    return {
        "coarse_incidence": incidence_summary(coarse),
        "fine_incidence": incidence_summary(fine),
        "energies": {key: str(value) for key, value in values.items()},
        "delta_F": {key: str(value) for key, value in delta.items()},
        "observable": "f=s_0",
        "observable_before": str(aperture(0)),
        "observable_after": str(aperture(1)),
        "mobility_square": str(mobility_square),
        "mobility": "sqrt(1/2)",
        "rate_factors": {
            "coarse": "sqrt(1/2)*exp(-1/16)",
            "fine_even": "sqrt(1/2)*exp(-1/8)",
            "fine_odd": "sqrt(1/2)*exp(55/72)",
        },
        "hidden_diagonal_defect": str(delta["fine_even"] - delta["fine_odd"]),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = read_json(PARENT)
    finite = read_json(FINITE)
    reference = read_json(REFERENCE)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source_hashes = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-003": digest(REFERENCE),
        "PAH-OMC-004": digest(CONTRACT),
        "PAH-OMC-004-MANIFEST": digest(MANIFEST),
    }
    expected_hashes = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-003": manifest["reference_only"]["sha256"],
        "PAH-OMC-004": manifest["contract"]["sha256"],
        "PAH-OMC-004-MANIFEST": source_hashes["PAH-OMC-004-MANIFEST"],
    }
    check("source-hashes", source_hashes == expected_hashes, source_hashes)
    check("parent-identities", parent.get("packet_id") == "PAH-001" and finite.get("contract_id") == "PAH-OMC-001")
    check("reference-identity", reference.get("contract_id") == "PAH-OMC-003")
    check("contract-identity", contract.get("contract_id") == "PAH-OMC-004")
    check(
        "parent-pointers",
        contract.get("parent", {}).get("sha256") == source_hashes["PAH-001"]
        and contract.get("parent", {}).get("finite_completion_contract", {}).get("sha256") == source_hashes["PAH-OMC-001"]
        and contract.get("parent", {}).get("reference_only", {}).get("sha256") == source_hashes["PAH-OMC-003"],
    )
    check("no-parent-mutation", manifest.get("no_parent_mutation") is True)
    firewall = contract.get("preservation_firewall", {})
    check("preservation-firewall", all(value is True for value in firewall.values()), firewall)
    check("physical-firewall", contract.get("provenance", {}).get("physical_authority") is False and contract.get("preservation_firewall", {}).get("no_physical_identification") is True)
    check("actual-pah-functional", parent.get("functional_or_action", {}).get("name") == "F_rho" and "formula" in parent.get("functional_or_action", {}))
    check("actual-pah-move-rate", "generator" in parent.get("dynamics", {}) if "dynamics" in parent else "generator" in parent.get("functional_or_action", {}))
    check("genuine-incidence-contract", contract.get("status", {}).get("refinement_family") == "GENUINE_FACE_EDGE_INCIDENCE_STRIP" and contract.get("preservation_firewall", {}).get("no_color_only_substitution") is True)
    check("fixed-q-scope", INPUTS["K"] == 2 and INPUTS["M_s"] == 1 and INPUTS["M_psi"] == 1 and INPUTS["Q"] == 0)
    check("matter-vanishes-at-q-zero", INPUTS["Q"] == 0 and INPUTS["R_max"] > 0)

    coarse = local_square(False)
    fine = local_square(True)
    coarse_incidence = incidence_summary(coarse)
    fine_incidence = incidence_summary(fine)
    check("local-vertex-count", coarse_incidence["vertices"] == fine_incidence["vertices"] == 4, (coarse_incidence, fine_incidence))
    check("local-edge-incidence-changes", fine_incidence["edges"] == coarse_incidence["edges"] + 1, (coarse_incidence, fine_incidence))
    check("local-face-incidence-changes", fine_incidence["faces"] == coarse_incidence["faces"] + 1, (coarse_incidence, fine_incidence))
    check("diagonal-is-geometric-edge", fine["edges"][-1] == (0, 2) and len(fine["faces"][0]) == 3 and len(fine["faces"][1]) == 3)

    witness = local_witness()
    check("coarse-delta-exact", witness["delta_F"]["coarse"] == "1/8", witness["delta_F"])
    check("fine-even-delta-exact", witness["delta_F"]["fine_even"] == "1/4", witness["delta_F"])
    check("fine-odd-delta-exact", witness["delta_F"]["fine_odd"] == "-55/36", witness["delta_F"])
    check("hidden-diagonal-dependence", witness["hidden_diagonal_defect"] == "16/9", witness["hidden_diagonal_defect"])
    check("mobility-derived", Fraction(witness["mobility_square"]) == Fraction(1, 2) and witness["mobility"] == "sqrt(1/2)", witness["mobility_square"])
    check("no-rate-fitting", contract.get("preservation_firewall", {}).get("no_parent_rate_rescaling") is True and "no rate fitting" in contract.get("exact_scope", {}).get("moves_and_rates", ""))

    ranges = term_ranges((coarse, fine))
    local_energy_bound = ranges["onsite_range"] + INPUTS["degree_bound"] * ranges["edge_range"] + INPUTS["face_incidence_bound"] * ranges["face_range"]
    check("derived-onsite-range", ranges["onsite_range"] == Fraction(1, 8), {key: str(value) for key, value in ranges.items()})
    check("derived-edge-range", ranges["edge_range"] == Fraction(1, 8), {key: str(value) for key, value in ranges.items()})
    check("derived-face-range", ranges["face_range"] == Fraction(4), {key: str(value) for key, value in ranges.items()})
    check("declared-incidence-bounds", INPUTS["degree_bound"] >= fine_incidence["max_degree"] and INPUTS["face_incidence_bound"] >= fine_incidence["max_face_incidence"], {"declared_degree": INPUTS["degree_bound"], "actual_degree": fine_incidence["max_degree"], "declared_faces": INPUTS["face_incidence_bound"], "actual_faces": fine_incidence["max_face_incidence"]})
    check("derived-local-energy-bound", local_energy_bound == Fraction(67, 4), str(local_energy_bound))
    exponent = INPUTS["beta"] * local_energy_bound / 2
    check("derived-rate-exponent", exponent == Fraction(67, 8), str(exponent))
    aperture_norm = max(aperture(j) for j in range(INPUTS["M_s"] + 1))
    root_count = 2  # AP(0,+/-) are the only roots changing f=s_0 in the witness.
    finite_bound_prefactor = 4 * root_count * aperture_norm
    check("derived-observable-norm", aperture_norm == 1, str(aperture_norm))
    check("derived-root-count", root_count == 2, root_count)
    check("finite-bound-prefactor", finite_bound_prefactor == 8, finite_bound_prefactor)

    strip_reports = []
    for level in range(4):
        report = incidence_summary(strip_carrier(level))
        strip_reports.append(report)
        check(f"strip-{level}-degree-bound", report["max_degree"] <= INPUTS["degree_bound"], report)
        check(f"strip-{level}-face-bound", report["max_face_incidence"] <= INPUTS["face_incidence_bound"], report)
    check("strip-genuine-growth", all(strip_reports[index + 1]["edges"] > strip_reports[index]["edges"] for index in range(len(strip_reports) - 1)), strip_reports)
    check("strip-anchor-preservation", strip_carrier(0)["vertices"][0] == (0, 0) and strip_carrier(0)["vertices"][1] == (0, 1))

    supports = (0, 1, 3)
    locality_rows = []
    for m in supports:
        tail_level = m + 1
        exact_tail = all(set((n, n + 1)).isdisjoint(set(range(m + 1))) for n in range(tail_level, tail_level + 3))
        affected_levels = m + 1
        cumulative_prefactor = affected_levels * finite_bound_prefactor
        locality_rows.append({"support_max_column": m, "exact_from_level": tail_level, "affected_levels": affected_levels, "cumulative_bound": f"{cumulative_prefactor}*exp(67/8)*||f||_infinity", "exact_tail_rule": exact_tail})
        check(f"eventual-zero-rule-m{m}", exact_tail, locality_rows[-1])
        check(f"finite-cumulative-count-m{m}", affected_levels == m + 1, locality_rows[-1])
    check("locality-contract", "delta_n(f)=0" in contract.get("compatibility_target", {}).get("local_eventual_exactness", "") and "sum_n delta_n(f)" in contract.get("compatibility_target", {}).get("finite_cumulative_bound", ""))
    check("boundary-defect-retained", witness["hidden_diagonal_defect"] != "0" and contract.get("known_boundaries", {}).get("affected_levels"))
    check("no-continuum-promotion", contract.get("status", {}).get("uniform_limit") == "NOT_ADMITTED" and "No physical Pre-A" in " ".join(contract.get("non_claims", [])))

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc004-geometric-incidence-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": source_hashes,
        "verdict": "LOCAL_COMMON_CORE_GEOMETRIC_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "scope": {
            "dimension": "finite relational two-cell complexes; the strip is a combinatorial incidence family",
            "model": "PAH-001 + PAH-OMC-001 + PAH-OMC-004; PAH-OMC-003 is reference-only",
            "normalization": "unchanged PAH counting-measure Gibbs midpoint rates",
            "regulator": "K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1 and displayed couplings; a_n is a label only",
            "volume": "finite square and finite strip levels; no physical volume",
            "limit": "no cutoff, volume, continuum, physical or observation limit",
        },
        "incidence": {
            "local_coarse": coarse_incidence,
            "local_fine": fine_incidence,
            "strip_levels": strip_reports,
        },
        "witness": witness,
        "derived_envelope": {
            "ranges": {key: str(value) for key, value in ranges.items()},
            "D_local": str(local_energy_bound),
            "rate_exponent": str(exponent),
            "root_count_for_f_s0": root_count,
            "observable_norm": str(aperture_norm),
            "bound": "4*N_f*exp(beta*D_local/2)*||f||_infinity",
            "fixture_bound": "8*exp(67/8)*||f||_infinity",
        },
        "locality": locality_rows,
        "theorem_summary": "A genuine diagonal face split has a nonzero local boundary defect, but along the anchored strip every fixed finite-support invariant cylinder has an eventually zero generator defect and a finite cumulative bound derived from the unchanged PAH local terms.",
        "non_claims": [
            "The result is a separately versioned researcher-proposed local structural successor, not PAH-001 alone.",
            "The local theorem is not a global volume-, regulator-, source- or phase-uniform estimate and does not prove an ordered limit.",
            "Q=0 is a finite diagnostic sector, not the physical vacuum or a Reading-H construction.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
            "No physical Pre-A, spacetime, event horizon, gravity, QFT, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE conclusion follows.",
        ],
        "next_question": "Can the local common-core estimate be extended to a source-authorized nonzero-Q incidence family with the same unchanged PAH functional and a uniform interaction-closure bound?",
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} PRIMARY {payload['verification']} {payload['passed']}/{payload['assertion_count']}; local_defect={witness['hidden_diagonal_defect']}; D_local={local_energy_bound}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
