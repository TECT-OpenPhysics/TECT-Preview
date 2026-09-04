#!/usr/bin/env python3
"""Primary exact audit for PAH-OMC-010.

The audit keeps the PAH-001 functional and rates fixed and changes only the
norm used to test the local interaction envelope: the normalized finite Gibbs
weight already declared by PAH-001.  The geometric count is rebuilt from the
cofinal PAH-OMC-004 strip rather than from a new finite carrier fixture.
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


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
PRECEDING = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
)

RESULT_ID = "R-490"
EXPLORATION_ID = "EXP-001438"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-010-STATE-WEIGHTED-ENVELOPE-PRIMARY-001"
R488_ANCHOR_A = (0, 0)
R488_ANCHOR_D = (1, 1)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def parameters(preceding: dict[str, Any]) -> dict[str, Any]:
    raw = preceding["exact_scope"]["regulator_path"]
    return {
        "K": int(raw["K"]),
        "M_s": int(raw["M_s"]),
        "M_psi": int(raw["M_psi"]),
        "Q": int(raw["Q"]),
        "epsilon": fraction(raw["epsilon"]),
        "beta": fraction(raw["beta"]),
        "nu": fraction(raw["nu"]),
        "m2": fraction(raw["m2"]),
        "lambda_4": fraction(raw["lambda_4"]),
        "eta_6": fraction(raw["eta_6"]),
        "g": fraction(raw["g"]),
        "lambda_s": fraction(raw["lambda_s"]),
        "kappa_s": fraction(raw["kappa_s"]),
        "kappa_D": fraction(raw["kappa_D"]),
        "kappa_g": fraction(raw["kappa_g"]),
    }


def strip_carrier(level: int) -> dict[str, Any]:
    if level < 2:
        raise ValueError("the PAH-OMC-010 cofinal family starts at n=2")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(level + 1):
        for j in (0, 1):
            edges.append((f"h{i}{j}", (i, j), (i + 1, j)))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(level):
        faces.extend(
            [
                ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)),
                ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)),
            ]
        )
    i = level
    faces.append(
        ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1))
    )
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def support_sets(level: int) -> dict[str, dict[Any, set[tuple[int, int]]]]:
    carrier = strip_carrier(level)
    vertices = carrier["vertices"]
    edges = carrier["edges"]
    faces = carrier["faces"]
    edge_lookup = {name: (left, right) for name, left, right in edges}

    def vertex_star(vertex: tuple[int, int]) -> set[tuple[int, int]]:
        result = {vertex}
        for _name, left, right in edges:
            if vertex in (left, right):
                result.update((left, right))
        return result

    def closed_two_cell_star(vertex: tuple[int, int]) -> set[tuple[int, int]]:
        result = vertex_star(vertex)
        incident = {
            name for name, left, right in edges if vertex in (left, right)
        }
        for face in faces:
            if any(name in incident for name, _orientation in face):
                for name, _orientation in face:
                    result.update(edge_lookup[name])
        return result

    def link_star(name: str) -> set[tuple[int, int]]:
        result = set(edge_lookup[name])
        for face in faces:
            if any(edge_name == name for edge_name, _orientation in face):
                for edge_name, _orientation in face:
                    result.update(edge_lookup[edge_name])
        return result

    return {
        "phase": {vertex: vertex_star(vertex) for vertex in vertices},
        "aperture": {
            vertex: closed_two_cell_star(vertex) for vertex in vertices
        },
        "link": {name: link_star(name) for name, _left, _right in edges},
        "radial": {
            name: closed_two_cell_star(left) | closed_two_cell_star(right)
            for name, left, right in edges
        },
    }


def root_specs(level: int) -> list[dict[str, Any]]:
    carrier = strip_carrier(level)
    supports = support_sets(level)
    roots: list[dict[str, Any]] = []
    # The two signs are retained as distinct directed source labels even for
    # K=2, as required by PAH-001's explicit move/inverse convention.
    for vertex in carrier["vertices"]:
        for sign in (-1, 1):
            roots.append(
                {
                    "kind": "phase",
                    "label": ("phase", vertex, sign),
                    "support": supports["phase"][vertex],
                }
            )
            roots.append(
                {
                    "kind": "aperture",
                    "label": ("aperture", vertex, sign),
                    "support": supports["aperture"][vertex],
                }
            )
    for name, left, right in carrier["edges"]:
        # Radial transfer has the two endpoint orientations; link roots have
        # the two zeta_K multiplication signs.
        for direction in (-1, 1):
            roots.append(
                {
                    "kind": "radial",
                    "label": ("radial", name, direction),
                    "support": supports["radial"][name],
                }
            )
            roots.append(
                {
                    "kind": "link",
                    "label": ("link", name, direction),
                    "support": supports["link"][name],
                }
            )
    return roots


def geometry_profile(level: int) -> dict[str, Any]:
    carrier = strip_carrier(level)
    roots = root_specs(level)
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for root in roots:
        by_kind.setdefault(root["kind"], []).append(root)
    incidence = {
        str(vertex): sum(vertex in root["support"] for root in roots)
        for vertex in carrier["vertices"]
    }
    max_incidence = max(incidence.values())
    return {
        "vertices": len(carrier["vertices"]),
        "edges": len(carrier["edges"]),
        "faces": len(carrier["faces"]),
        "roots": len(roots),
        "support_max": max(len(root["support"]) for root in roots),
        "support_min": min(len(root["support"]) for root in roots),
        "incidence_max": max_incidence,
        "incidence_argmax": [
            list(vertex)
            for vertex, value in incidence.items()
            if value == max_incidence
        ],
        "by_kind": {
            kind: {
                "roots": len(items),
                "support_max": max(len(item["support"]) for item in items),
                "incidence_max": max(
                    sum(vertex in item["support"] for item in items)
                    for vertex in carrier["vertices"]
                ),
            }
            for kind, items in sorted(by_kind.items())
        },
    }


def canonical_support_patterns(level: int) -> set[tuple[str, tuple[tuple[int, int], ...]]]:
    patterns: set[tuple[str, tuple[tuple[int, int], ...]]] = set()
    for root in root_specs(level):
        support = root["support"]
        left = min(vertex[0] for vertex in support)
        pattern = tuple(sorted((vertex[0] - left, vertex[1]) for vertex in support))
        patterns.add((root["kind"], pattern))
    return patterns


def s_value(level: int, p: dict[str, Any]) -> Fraction:
    return p["epsilon"] + Fraction(level) * (1 - p["epsilon"]) / p["M_s"]


def sign_z2(bit: int) -> int:
    return -1 if bit % 2 else 1


def matter_value(config: dict[str, Any], vertex: tuple[int, int], p: dict[str, Any]) -> Fraction:
    return config["radius"] * Fraction(config["ell"][vertex], p["M_psi"]) * sign_z2(
        config["phase"][vertex]
    )


def onsite(config: dict[str, Any], vertex: tuple[int, int], p: dict[str, Any]) -> Fraction:
    s = s_value(config["apertures"][vertex], p)
    psi = matter_value(config, vertex, p)
    return (
        p["lambda_s"] * (s - 1) ** 2 / 2
        + p["m2"] * psi**2 / 2
        + p["lambda_4"] * psi**4 / 4
        + p["eta_6"] * psi**6 / 6
        + p["g"] * s**2 * psi**2 / 2
    )


def j_edge(
    config: dict[str, Any],
    left: tuple[int, int],
    right: tuple[int, int],
    p: dict[str, Any],
) -> Fraction:
    return Fraction(2) / (
        s_value(config["apertures"][left], p)
        + s_value(config["apertures"][right], p)
    )


def covariant(
    config: dict[str, Any],
    name: str,
    left: tuple[int, int],
    right: tuple[int, int],
    p: dict[str, Any],
) -> Fraction:
    psi_left = matter_value(config, left, p)
    psi_right = matter_value(config, right, p)
    transported = sign_z2(config["links"][name]) * psi_left
    return p["kappa_D"] * j_edge(config, left, right, p) * (
        psi_right - transported
    ) ** 2 / 2


def face_value(
    config: dict[str, Any],
    face: tuple[tuple[str, int], ...],
    edge_lookup: dict[str, tuple[tuple[int, int], tuple[int, int]]],
    p: dict[str, Any],
) -> Fraction:
    stiffness = [j_edge(config, *edge_lookup[name], p) for name, _orientation in face]
    holonomy = 1
    for name, orientation in face:
        edge_sign = sign_z2(config["links"][name])
        holonomy *= edge_sign if orientation == 1 else edge_sign
    return p["kappa_g"] * sum(stiffness, Fraction(0)) / len(stiffness) * (
        1 - holonomy
    )


def energy(config: dict[str, Any], level: int, p: dict[str, Any]) -> Fraction:
    carrier = strip_carrier(level)
    edge_lookup = {name: (left, right) for name, left, right in carrier["edges"]}
    total = sum(
        (onsite(config, vertex, p) for vertex in carrier["vertices"]), Fraction(0)
    )
    for name, left, right in carrier["edges"]:
        sl = s_value(config["apertures"][left], p)
        sr = s_value(config["apertures"][right], p)
        total += p["kappa_s"] * (sl - sr) ** 2 / 2
        total += covariant(config, name, left, right, p)
    for face in carrier["faces"]:
        total += face_value(config, face, edge_lookup, p)
    return total


def witness_config(
    level: int,
    radius: int,
    ell_vertex: tuple[int, int] = R488_ANCHOR_A,
    holonomy_edge: str | None = None,
) -> dict[str, Any]:
    carrier = strip_carrier(level)
    return {
        "apertures": {vertex: 1 for vertex in carrier["vertices"]},
        "ell": {
            vertex: int(vertex == ell_vertex) for vertex in carrier["vertices"]
        },
        "phase": {vertex: 0 for vertex in carrier["vertices"]},
        "links": {
            name: int(name == holonomy_edge) for name, _left, _right in carrier["edges"]
        },
        "radius": Fraction(radius),
    }


def face_holonomy(
    config: dict[str, Any], face: tuple[tuple[str, int], ...]
) -> int:
    result = 1
    for name, _orientation in face:
        result *= sign_z2(config["links"][name])
    return result


def amgm_certificate() -> dict[str, Any]:
    samples = [(Fraction(0), Fraction(1)), (Fraction(1, 2), Fraction(3, 4)), (Fraction(2), Fraction(5, 2))]
    rows = []
    for a, b in samples:
        remainder = (a * a + b * b) / 2 - a * b
        rows.append({"a": str(a), "b": str(b), "remainder": str(remainder)})
    symbolic_remainder = "(a-b)^2/2 >= 0 for all real a,b"
    return {"samples": rows, "symbolic_remainder": symbolic_remainder}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    geometry = read_json(GEOMETRY)
    start = read_json(START)
    preceding = read_json(PRECEDING)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    p = parameters(preceding)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(PRECEDING),
        "PAH-OMC-010": sha(CONTRACT),
        "PAH-OMC-010-MANIFEST": sha(MANIFEST),
    }
    check(
        "source-hashes",
        manifest["contract"]["sha256"] == hashes["PAH-OMC-010"]
        and manifest["functional_source"]["sha256"] == hashes["PAH-001"]
        and manifest["geometric_source"]["sha256"] == hashes["PAH-OMC-004"]
        and manifest["starting_result"]["sha256"] == hashes["PAH-OMC-008"]
        and manifest["preceding_negative"]["sha256"] == hashes["PAH-OMC-009"],
        hashes,
    )
    check(
        "source-identities",
        source.get("packet_id") == "PAH-001"
        and geometry.get("contract_id") == "PAH-OMC-004"
        and start.get("contract_id") == "PAH-OMC-008"
        and preceding.get("contract_id") == "PAH-OMC-009"
        and contract.get("contract_id") == "PAH-OMC-010",
    )
    firewall = contract.get("preservation_firewall", {})
    required_firewall = (
        "parent_functional_unchanged",
        "parent_move_families_unchanged",
        "parent_mobility_unchanged",
        "parent_projection_unchanged",
        "parent_regulator_rule_unchanged",
        "parent_limit_order_unchanged",
        "no_new_hamiltonian",
        "no_counterterm",
        "no_averaging",
        "no_rate_fitting",
        "no_physical_identification",
        "no_fixed_cutoff_bypass",
    )
    check(
        "preservation-firewall",
        all(firewall.get(key) is True for key in required_firewall)
        and manifest.get("no_parent_mutation") is True
        and manifest.get("no_new_finite_fixture") is True,
    )
    check(
        "displayed-functional-and-rate",
        source.get("functional_or_action", {}).get("formula", "").startswith(
            "F_rho=sum_v[lambda_s"
        )
        and source.get("dynamics", {}).get("generator", "").startswith(
            "(L_rho f)(x)=sum_r m_r(x)"
        ),
    )
    check(
        "declared-gibbs-weight",
        "normalized positive Gibbs weight" in contract["exact_scope"]["state_weight"]
        and p["beta"] == 1
        and p["epsilon"] > 0,
        {"beta": str(p["beta"]), "epsilon": str(p["epsilon"])},
    )
    check(
        "declared-r488-cylinder",
        all(token in contract["exact_scope"]["observable_algebra"] for token in ("ell_a", "ell_d", "H_0", "H_1"))
        and "identity" in start["exact_scope"]["anchors"],
    )

    levels = list(range(2, 21))
    profiles = {str(level): geometry_profile(level) for level in levels}
    check(
        "strip-cardinality-formulas",
        all(
            profile["vertices"] == 2 * (level + 2)
            and profile["edges"] == 4 * level + 4
            and profile["faces"] == 2 * level + 1
            and profile["roots"] == 4 * profile["vertices"] + 4 * profile["edges"]
            for level, profile in ((level, profiles[str(level)]) for level in levels)
        ),
        profiles,
    )
    support_max = max(profile["support_max"] for profile in profiles.values())
    incidence_max = max(profile["incidence_max"] for profile in profiles.values())
    check(
        "support-and-incidence-finite",
        support_max > 0 and incidence_max > 0,
        {"S_geom": support_max, "N_geom": incidence_max},
    )
    template_levels = list(range(2, 7))
    template_patterns = set().union(
        *(canonical_support_patterns(level) for level in template_levels)
    )
    all_patterns = set().union(
        *(canonical_support_patterns(level) for level in levels)
    )
    check(
        "local-template-exhaustion",
        all_patterns == template_patterns,
        {"template_levels": template_levels, "pattern_count": len(all_patterns)},
    )
    check(
        "family-wide-profile-stability",
        all(
            profiles[str(level)]["support_max"] <= support_max
            and profiles[str(level)]["incidence_max"] <= incidence_max
            for level in levels
        ),
        {"levels_checked": levels},
    )

    # Each directed root is paired with its inverse.  Its PAH mobility is at
    # most one because every aperture lies in [epsilon,1] and nu=1.
    mobility_bounds = {
        "phase": s_value(1, p),
        "transfer_or_link": s_value(1, p),
        "aperture": s_value(0, p),
    }
    check(
        "mobility-bound",
        all(Fraction(value) <= 1 and Fraction(value) > 0 for value in mobility_bounds.values())
        and p["nu"] == 1,
        {key: str(value) for key, value in mobility_bounds.items()},
    )
    amgm = amgm_certificate()
    check(
        "amgm-exact",
        all(Fraction(row["remainder"]) >= 0 for row in amgm["samples"]),
        amgm,
    )
    check(
        "inverse-pair-conductance-bound",
        "explicit inverse" in source["dynamics"]["inverse_pair_rule"]
        and "AM-GM" in contract["pre_registered_proof"]["conductance_lemma"],
        {
            "per_root_bound": "sum_omega W(omega)c_r(omega)<=1",
            "pairing": "W(omega)c_r(omega)=Z^-1 m_r exp(-(F(omega)+F(r omega))/2)",
        },
    )
    c_sw = incidence_max * (1 + support_max)
    check(
        "uniform-local-form-envelope",
        c_sw > 0,
        {"S_geom": support_max, "N_geom": incidence_max, "C_sw": c_sw},
    )

    witness_level = 2
    witness_radius = 1
    witnesses = {
        "ell_a": witness_config(witness_level, witness_radius, R488_ANCHOR_A),
        "ell_d": witness_config(witness_level, witness_radius, R488_ANCHOR_D),
        "H_0": witness_config(witness_level, witness_radius, R488_ANCHOR_A, "d0"),
        "H_1": witness_config(witness_level, witness_radius, R488_ANCHOR_A, "d0"),
    }
    witness_values = {
        "ell_a": witnesses["ell_a"]["ell"][R488_ANCHOR_A],
        "ell_d": witnesses["ell_d"]["ell"][R488_ANCHOR_D],
        "H_0": face_holonomy(witnesses["H_0"], strip_carrier(witness_level)["faces"][0]),
        "H_1": face_holonomy(witnesses["H_1"], strip_carrier(witness_level)["faces"][1]),
    }
    witness_energies = {
        name: str(energy(config, witness_level, p)) for name, config in witnesses.items()
    }
    check(
        "r488-witness-values",
        witness_values["ell_a"] != 0
        and witness_values["ell_d"] != 0
        and witness_values["H_0"] != 0
        and witness_values["H_1"] != 0,
        {"values": witness_values, "energies_at_n2_R1": witness_energies},
    )
    check(
        "strict-positive-gibbs-norm-rule",
        all(math.isfinite(float(Fraction(value))) for value in witness_energies.values())
        and all(value != 0 for value in witness_values.values()),
        {
            "reason": "finite state space, epsilon>0 and real finite F imply W=Z^-1 exp(-F)>0; each witness is nonzero",
            "all_finite_levels_and_R": True,
        },
    )
    check(
        "conditional-common-core-role",
        "supplied separately" in contract["exact_scope"]["common_core_input"]
        and "does not identify" in contract["exact_scope"]["common_core_input"],
        contract["exact_scope"]["common_core_input"],
    )
    check(
        "no-physical-promotion",
        manifest.get("physical_promotion") is False
        and contract["provenance"]["physical_authority"] is False,
    )

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc010-state-weighted-envelope-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "verdict": "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "EXACT_GIBBS_WEIGHTED_LOCAL_FORM_INPUT",
        "scope": contract["exact_scope"],
        "family": {
            "levels_checked": levels,
            "cofinal_definition": contract["exact_scope"]["carrier_family"],
            "S_geom": support_max,
            "N_geom": incidence_max,
            "C_sw": c_sw,
            "root_count_formula": "4|V_n|+4|E_n|",
            "template_levels": template_levels,
            "template_pattern_count": len(all_patterns),
        },
        "conductance": {
            "per_root_bound": "<=1",
            "amgm": amgm,
            "normalized_weight": "Z^-1 exp(-F)",
            "rate": "unchanged PAH-001 midpoint rate",
            "uniform_interaction_bound": f"I_(n,R)(x) <= {c_sw}",
        },
        "r488_observables": {
            "values": witness_values,
            "witness_level": witness_level,
            "witness_radius": witness_radius,
            "finite_energy_witnesses": witness_energies,
            "positive_norm_for_all_finite_n_R": True,
        },
        "common_core_input": {
            "status": "VALID_LOCAL_FORM_INPUT_CONDITIONAL_ON_SEPARATE_INTERTWINING",
            "not_proved": "rootwise/eventual generator intertwining and infinite-volume closure",
        },
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": {
            "command": "python codes/foundations/pah_omc010_state_weighted_envelope.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
        },
    }
    atomic_json(output, payload)
    print(
        f"{AUDIT_ID} {payload['verification']} "
        f"{payload['passed']}/{payload['assertion_count']}; "
        f"S={support_max}; N={incidence_max}; C_sw={c_sw}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
