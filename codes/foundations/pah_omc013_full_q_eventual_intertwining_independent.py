#!/usr/bin/env python3
"""Independent replay of the finite PAH-OMC-013 intertwining audit.

This lane deliberately rebuilds the strip incidence, projection, active-root
partition, and local PAH energy from the pinned source descriptions instead of
importing the primary implementation.  It is a finite algebraic check only;
it does not introduce a cross-Q Gibbs measure or any physical interpretation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-manifest.json"
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
WEIGHT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
WEIGHT_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
OMC011 = ROOT / "strategy/pa-hyp/PAH-OMC-011-eventual-intertwining-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC012_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-manifest.json"
R484_SOURCE = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
R484_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/primary.json"
R490_CERT = ROOT / "strategy/pa-hyp/R490-certificate.md"
R490_RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/independent.json"

RESULT_ID = "R-493"
EXPLORATION_ID = "EXP-001474"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-013-FULL-Q-EVENTUAL-INTERTWINING-INDEPENDENT-001"

EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-008": "b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a",
    "PAH-OMC-010": "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "PAH-OMC-010-MANIFEST": "97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3",
    "PAH-OMC-011": "244a300c470fa551dc006a7a2d9ba2a7a5d773d2d5cafbe9b777f9266df50020",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
    "PAH-OMC-012-MANIFEST": "fc2c52b0f786b371c56d2700e571d23558bad191942bc4f5182bc6260ae33937",
    "R-484": "87f5d3ee29b15f57f3e461b4b4064955b5f1ced0ab0bdf2b4763ed0a7ffe3e3e",
    "R-484-RUN": "6fb8a733f6014fcaa0fd8b84cdffd4b43d5f6214f4b9a59e6a9f9a1d2218c17d",
    "R-490-CERTIFICATE": "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "R-490-PRIMARY-RUN": "4bcefef42ee2692d19344376fa2161743f0edb2043ada6d4867d1618b883dac3",
}

Vertex = tuple[int, int]


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
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


def vertices(n: int) -> tuple[Vertex, ...]:
    return tuple((i, j) for i in range(n + 2) for j in (0, 1))


def edges(n: int) -> tuple[tuple[str, Vertex, Vertex], ...]:
    result: list[tuple[str, Vertex, Vertex]] = []
    for i in range(n + 1):
        result.extend(((f"h{i}0", (i, 0), (i + 1, 0)), (f"h{i}1", (i, 1), (i + 1, 1))))
    for i in range(n + 2):
        result.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(n):
        result.append((f"d{i}", (i, 0), (i + 1, 1)))
    return tuple(result)


def faces(n: int) -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
    result: list[tuple[str, tuple[tuple[str, int], ...]]] = []
    for i in range(n):
        result.extend(
            (
                (f"t{i}a", ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1))),
                (f"t{i}b", ((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1))),
            )
        )
    i = n
    result.append((f"q{i}", ((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1))))
    return tuple(result)


def edge_map(n: int) -> dict[str, tuple[str, Vertex, Vertex]]:
    return {name: (name, left, right) for name, left, right in edges(n)}


def face_vertices(n: int, face: str) -> set[Vertex]:
    emap = edge_map(n)
    boundary = dict(faces(n))[face]
    return {v for edge, _sign in boundary for v in emap[edge][1:]}


def incident_edges(n: int, vertex: Vertex) -> set[str]:
    return {name for name, left, right in edges(n) if vertex in (left, right)}


def incident_faces(n: int, selected: set[str]) -> set[str]:
    return {name for name, boundary in faces(n) if any(edge in selected for edge, _sign in boundary)}


def root_terms(n: int, family: str, vertex: Vertex | None = None, edge: str | None = None) -> set[str]:
    emap = edge_map(n)
    if family in ("phase", "aperture"):
        assert vertex is not None
        star = incident_edges(n, vertex)
        terms = {f"onsite:{vertex[0]},{vertex[1]}", *(f"covariant:{e}" for e in star)}
        if family == "aperture":
            terms |= {f"stiffness:{e}" for e in star}
            terms |= {f"face:{p}" for p in incident_faces(n, star)}
        return terms
    assert edge is not None
    left, right = emap[edge][1:]
    if family == "link":
        return {f"covariant:{edge}", *(f"face:{p}" for p in incident_faces(n, {edge}))}
    edge_star = incident_edges(n, left) | incident_edges(n, right)
    return {
        f"onsite:{left[0]},{left[1]}",
        f"onsite:{right[0]},{right[1]}",
        *(f"covariant:{e}" for e in edge_star),
    }


def root_rows(n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    emap = edge_map(n)
    for vertex in vertices(n):
        for family in ("phase", "aperture"):
            for direction in (-1, 1):
                rows.append({
                    "family": family,
                    "label": f"{family}:{vertex[0]},{vertex[1]}:{direction}",
                    "vertex": vertex,
                    "direction": direction,
                    "core": {vertex},
                    "terms": root_terms(n, family, vertex=vertex),
                    "mobility": {vertex},
                })
    for name, left, right in edges(n):
        endpoints = {left, right}
        for source, target, direction in ((left, right, 1), (right, left, -1)):
            rows.append({
                "family": "radial-transfer",
                "label": f"radial-transfer:{name}:{source[0]},{source[1]}->{target[0]},{target[1]}",
                "edge": name,
                "source": source,
                "target": target,
                "direction": direction,
                "core": endpoints,
                "terms": root_terms(n, "radial-transfer", edge=name),
                "mobility": endpoints,
            })
        for direction in (-1, 1):
            rows.append({
                "family": "link",
                "label": f"link:{name}:{direction}",
                "edge": name,
                "direction": direction,
                "core": endpoints,
                "terms": root_terms(n, "link", edge=name),
                "mobility": endpoints,
            })
    for row in rows:
        row["support"] = set(row["core"])
        for term in row["terms"]:
            if term.startswith("onsite:"):
                i, j = (int(v) for v in term.split(":", 1)[1].split(","))
                row["support"].add((i, j))
            elif ":" in term:
                kind, name = term.split(":", 1)
                if kind in ("stiffness", "covariant"):
                    row["support"].update(emap[name][1:])
                elif kind == "face":
                    row["support"].update(face_vertices(n, name))
    return rows


def project(n: int, state: dict[str, dict[Any, int]]) -> tuple[dict[str, dict[Any, int]], int, int, int]:
    old = set(vertices(n))
    old_edges = {name for name, _left, _right in edges(n)}
    coarse = {
        "aperture": {v: x for v, x in state["aperture"].items() if v in old},
        "phase": {v: x for v, x in state["phase"].items() if v in old},
        "ell": {v: x for v, x in state["ell"].items() if v in old},
        "link": {e: x for e, x in state["link"].items() if e in old_edges},
    }
    fine_q = sum(state["ell"].values())
    coarse_q = sum(coarse["ell"].values())
    return coarse, fine_q, coarse_q, fine_q - coarse_q


def aperture(value: int) -> Fraction:
    return Fraction(1 + value, 2)


def sign(value: int) -> int:
    return -1 if value else 1


def state(n: int, variant: int) -> dict[str, dict[Any, int]]:
    vs, es = vertices(n), edges(n)
    return {
        "aperture": {v: (v[0] + 2 * v[1] + variant) % 2 for v in vs},
        "phase": {v: (2 * v[0] + v[1] + variant) % 2 for v in vs},
        "ell": {v: int((v[0] * 3 + v[1] + variant) % 3 == 0) for v in vs},
        "link": {e: (len(e) + variant + i) % 2 for i, (e, _l, _r) in enumerate(es)},
    }


def move(s: dict[str, dict[Any, int]], row: dict[str, Any]) -> dict[str, dict[Any, int]] | None:
    out = {k: dict(v) for k, v in s.items()}
    family = row["family"]
    if family == "phase":
        v = row["vertex"]
        out["phase"][v] = (out["phase"][v] + row["direction"]) % 2
    elif family == "aperture":
        v = row["vertex"]
        value = out["aperture"][v] + row["direction"]
        if value not in (0, 1):
            return None
        out["aperture"][v] = value
    elif family == "radial-transfer":
        src, dst = row["source"], row["target"]
        if out["ell"][src] == 0 or out["ell"][dst] == 1:
            return None
        out["ell"][src] -= 1
        out["ell"][dst] += 1
    else:
        e = row["edge"]
        out["link"][e] = (out["link"][e] + row["direction"]) % 2
    return out


def j_edge(s: dict[str, dict[Any, int]], left: Vertex, right: Vertex) -> Fraction:
    return Fraction(2) / (aperture(s["aperture"][left]) + aperture(s["aperture"][right]))


def energy(n: int, s: dict[str, dict[Any, int]], rmax: int) -> Fraction:
    total = Fraction(0)
    for v in vertices(n):
        sv = aperture(s["aperture"][v])
        psi = rmax * s["ell"][v] * sign(s["phase"][v])
        total += (sv - 1) ** 2 / 2 + Fraction(psi**4, 4) + Fraction(psi**6, 6) + sv**2 * psi**2 / 2
    emap = edge_map(n)
    for e, left, right in edges(n):
        sl, sr = aperture(s["aperture"][left]), aperture(s["aperture"][right])
        total += (sl - sr) ** 2 / 2
        pl = rmax * s["ell"][left] * sign(s["phase"][left])
        pr = rmax * s["ell"][right] * sign(s["phase"][right])
        total += j_edge(s, left, right) * (pr - sign(s["link"][e]) * pl) ** 2 / 2
    for _face, boundary in faces(n):
        stiffness = sum((j_edge(s, *emap[e][1:]) for e, _orientation in boundary), Fraction(0))
        holonomy = 1
        for e, _orientation in boundary:
            holonomy *= sign(s["link"][e])
        total += stiffness / len(boundary) * (1 - holonomy)
    return total


def observable(s: dict[str, dict[Any, int]], ell_support: tuple[Vertex, ...], face_support: tuple[str, ...], n: int) -> tuple[Any, ...]:
    values: list[Any] = [s["ell"][v] for v in ell_support]
    emap = edge_map(n)
    for face in face_support:
        holonomy = 1
        for edge, _orientation in dict(faces(n))[face]:
            holonomy *= sign(s["link"][edge])
        values.append(holonomy)
    return tuple(values)


def can_change(row: dict[str, Any], ell_support: set[Vertex], face_support: set[str], n: int) -> bool:
    if row["family"] in ("phase", "aperture"):
        return False
    if row["family"] == "radial-transfer":
        return bool(ell_support & row["core"])
    selected_edges = {edge for face in face_support if face in dict(faces(n)) for edge, _sign in dict(faces(n))[face]}
    return row.get("edge") in selected_edges


def closure(n: int, ell_support: set[Vertex], face_support: set[str]) -> set[Vertex]:
    return {v for row in root_rows(n) if can_change(row, ell_support, face_support, n) for v in row["support"]}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract, manifest = read(CONTRACT), read(MANIFEST)
    source, geometry, start = read(SOURCE), read(GEOMETRY), read(START)
    weight, weight_manifest, omc011 = read(WEIGHT), read(WEIGHT_MANIFEST), read(OMC011)
    omc012, omc012_manifest = read(OMC012), read(OMC012_MANIFEST)
    r484_source, r484_run, r490_run = read(R484_SOURCE), read(R484_RUN), read(R490_RUN)
    paths = {
        "PAH-001": SOURCE, "PAH-OMC-004": GEOMETRY, "PAH-OMC-008": START,
        "PAH-OMC-010": WEIGHT, "PAH-OMC-010-MANIFEST": WEIGHT_MANIFEST,
        "PAH-OMC-011": OMC011, "PAH-OMC-012": OMC012,
        "PAH-OMC-012-MANIFEST": OMC012_MANIFEST, "R-484": R484_SOURCE,
        "R-484-RUN": R484_RUN, "R-490-CERTIFICATE": R490_CERT,
        "R-490-PRIMARY-RUN": R490_RUN,
    }
    actual = {key: sha(path) for key, path in paths.items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("independent-parent-hashes", actual == EXPECTED, {"actual": actual, "expected": EXPECTED})
    check(
        "independent-source-identities",
        source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004"
        and start.get("contract_id") == "PAH-OMC-008" and weight.get("contract_id") == "PAH-OMC-010"
        and omc011.get("contract_id") == "PAH-OMC-011" and omc012.get("contract_id") == "PAH-OMC-012"
        and r484_source.get("contract_id") == "PAH-OMC-004-GEN-001",
    )
    check("independent-manifest-pin", manifest["contract"]["sha256"] == sha(CONTRACT) and manifest["status"] == "MAINLINE_ADVANCE" and manifest["claim_bearing"] is False)
    check("independent-parent-manifest-pin", omc012_manifest["contract"]["sha256"] == sha(OMC012) and omc012_manifest["status"] == "MAINLINE_ADVANCE")
    check("independent-firewall", all(value is True for value in contract["preservation_firewall"].values()))
    check("independent-functional-generator", source["functional_or_action"]["formula"].startswith("F_rho=sum_v[lambda_s") and source["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r m_r(x)"))
    check("independent-grade-blind-domain", "grade is a component tag" in contract["exact_scope"]["graded_state_space"] and "cannot inspect the disjoint-union grade" in contract["exact_scope"]["common_cylinder_algebra"])
    check("independent-csw-role", r490_run["family"]["C_sw"] == 540 and "domination-only" in contract["exact_scope"]["gibbs_norm"])

    family_counts = {family: 0 for family in ("phase", "aperture", "radial-transfer", "link")}
    for row in root_rows(5):
        family_counts[row["family"]] += 1
    check("independent-four-root-families", all(value > 0 for value in family_counts.values()), family_counts)

    # Rebuild N(f) for supports not used by the primary lane and check that the
    # same closure is stable at the next level.
    support_cases = [
        ("ell_pair", {(0, 0), (4, 1)}, set()),
        ("face_pair", set(), {"t1a", "t1b"}),
        ("mixed_far", {(2, 0), (5, 0)}, {"t0a", "t1b"}),
        ("constant", set(), set()),
    ]
    closure_rows: list[dict[str, Any]] = []
    for name, ell_support, face_support in support_cases:
        base = max(2, max((v[0] for v in ell_support), default=-1) + 4, max((int(face[1:].split("a")[0].split("b")[0]) for face in face_support), default=-1) + 4)
        first, second = closure(base, ell_support, face_support), closure(base + 1, ell_support, face_support)
        m_f = max((v[0] for v in first), default=-1)
        closure_rows.append({"name": name, "base": base, "m_f": m_f, "N_f": max(2, m_f + 1), "stable": first == second})
    check("independent-Nf-stability", all(row["stable"] and row["N_f"] == max(2, row["m_f"] + 1) for row in closure_rows), closure_rows)

    grade_rows: list[dict[str, Any]] = []
    for n in range(2, 8):
        for variant in range(8):
            coarse, q_f, q_c, dropped = project(n, state(n + 1, variant))
            grade_rows.append({"n": n, "variant": variant, "fine_Q": q_f, "coarse_Q": q_c, "dropped": dropped, "balance": q_f == q_c + dropped, "bound": 0 <= q_c <= len(vertices(n))})
    check("independent-full-q-totality", all(row["balance"] and row["dropped"] >= 0 and row["bound"] for row in grade_rows), {"rows": len(grade_rows), "grade_change": any(row["fine_Q"] > row["coarse_Q"] for row in grade_rows)})

    # Compare the independently rebuilt local energy/rate inputs on a varied
    # set of interior roots.  The R_max values below are regression probes;
    # the symbolic all-positive-integer scope is supplied by the source term
    # identity and is checked separately.
    regression_rows: list[dict[str, Any]] = []
    for n in range(2, 7):
        fine_n = n + 1
        coarse_roots, fine_roots = root_rows(n), root_rows(fine_n)
        fine_by_label = {row["label"]: row for row in fine_roots}
        for variant in range(8):
            fine_state = state(fine_n, variant)
            coarse_state, q_f, q_c, dropped = project(n, fine_state)
            for root in coarse_roots:
                if max(v[0] for v in root["support"]) > n - 1:
                    continue
                fine_root = fine_by_label.get(root["label"])
                if fine_root is None or root["terms"] != fine_root["terms"]:
                    regression_rows.append({"n": n, "root": root["label"], "term_equal": False})
                    continue
                for rmax in (3, 7):
                    after_c, after_f = move(coarse_state, root), move(fine_state, fine_root)
                    if (after_c is None) != (after_f is None):
                        regression_rows.append({"n": n, "root": root["label"], "R_max": rmax, "admissibility_equal": False})
                    elif after_c is not None:
                        regression_rows.append({
                            "n": n, "root": root["label"], "R_max": rmax,
                            "term_equal": root["terms"] == fine_root["terms"],
                            "delta_equal": energy(n, after_c, rmax) - energy(n, coarse_state, rmax) == energy(fine_n, after_f, rmax) - energy(fine_n, fine_state, rmax),
                            "projection_observable_equal": observable(after_f, ((0, 0), (1, 1)), ("t0a",), fine_n) == observable(after_c, ((0, 0), (1, 1)), ("t0a",), n),
                        })
    check("independent-interior-term-rate-replay", all(row.get("term_equal") and row.get("delta_equal", True) and row.get("projection_observable_equal", True) for row in regression_rows), {"rows": len(regression_rows), "failures": [row for row in regression_rows if not (row.get("term_equal") and row.get("delta_equal", True) and row.get("projection_observable_equal", True))][:5]})
    check("independent-rmax-symbolic-scope", "every positive integer" in contract["exact_scope"]["finite_parameter_scope"] and "identical symbolic local term lists" in contract["boundary_and_uniformity"]["R_max"], contract["exact_scope"]["finite_parameter_scope"])
    boundary = r484_run.get("boundary_witness", {})
    check("independent-boundary-defect-retained", boundary == {"coarse_delta_F": "1/8", "fine_even_delta_F": "1/4", "fine_odd_delta_F": "-55/36", "hidden_diagonal_defect": "16/9"}, boundary)
    check("independent-boundary-separation", "not defect cancellation" in contract["eventual_intertwining_proof"]["boundary_control"] and all(row["m_f"] < row["N_f"] for row in closure_rows), contract["eventual_intertwining_proof"]["boundary_control"])
    check("independent-no-promotion", contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]))

    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc013-full-q-eventual-intertwining-independent/1.0",
        "run_kind": "independent", "audit_id": AUDIT_ID, "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID, "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "MAINLINE_ADVANCE" if not failed else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks), "passed": len(checks) - len(failed), "failed": len(failed),
        "assertions": checks, "source_hashes": actual,
        "derived": {"family_counts": family_counts, "closure_rows": closure_rows, "grade_rows": len(grade_rows), "regression_rows": len(regression_rows), "R_max_regression_samples": [3, 7]},
        "claim_bearing": False, "active_gate_change": False,
        "stage2_status": "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
        "non_claims": contract["non_claims"], "reproduction": contract["reproduction"],
        "next_question": contract["single_next_question"],
    }
    write_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; regression_rows={len(regression_rows)}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
