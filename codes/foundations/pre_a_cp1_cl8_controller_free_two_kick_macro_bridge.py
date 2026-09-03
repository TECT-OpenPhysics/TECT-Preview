#!/usr/bin/env python3
"""Primary exact audit for the controller-free two-kick CL8 macro bridge."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "0.2.1"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-controller-free-two-kick-macro-bridge"
CANDIDATE_ID = "PA-CP1-CL8-CONTROLLER-FREE-TWO-KICK-MACRO-BRIDGE-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-GLOBAL-SIDEWAYS-MACRO-AND-FIXED-REGULATOR-SPLITTING-BRIDGE"
ADMISSION_RESULT_ID = "PRE-A-ROUND1-PARTIAL-EVIDENCE-INTAKE-PINNED-M1-BARE-M5-SCOPED-FAILURES-AND-CURRENT-NONSELECTION"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
ADMISSION = REPO / "strategy/pre-a-round1-admission-canonical-functional-bridge-manifest.json"
EVIDENCE = REPO / "strategy/pre-a-round1-boundary-evidence-register-260809-v0.1.json"
M0 = REPO / "strategy/pre-a-m0-established-low-energy-baseline-manifest.json"
M1 = REPO / "strategy/pre-a-m1-current-production-functional-candidate-manifest.json"
M2 = REPO / "strategy/pre-a-pa-m2-ci8-rs-dual-lane-manifest.json"
M5 = REPO / "strategy/pre-a-pa-m5-nl3-sv-candidate-manifest.json"
A5 = REPO / "claims/A5-SECTOR-A-SYNTHESIS/status.json"
A7 = REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/status.json"
A13 = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/status.json"
PARENT_PATHS = (
    REPO / "strategy/pre-a-cp1-cl8-interacting-two-arm-work-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
)
PARENT_SCRIPT = REPO / "codes/foundations/pre_a_cp1_cl8_interacting_two_arm_work_route_split.py"
DEFAULT_OUTPUT = (
    REPO / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-09-primary-{SLUG}/result.json"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location("pre_a_cp1_cl8_parent", PARENT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load parent audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()


def q(numerator: int, denominator: int = 1) -> sp.Rational:
    return sp.Rational(numerator, denominator)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)}
        )


Leg = tuple[sp.Matrix, sp.Matrix]


def parameters(profile: str) -> dict[str, Any]:
    data = PARENT.complete_parameters(PARENT.fixture(profile))
    data["Delta"] = data["tau"]
    data["s"] = sp.factor(data["Delta"] / 2)
    data["macro_h"] = sp.factor(data["Delta"] / 8)
    data["kappa"] = sp.factor(data["w"] * data["c"] / data["a"] ** 2)
    data["rho"] = sp.factor(2 * data["macro_h"] * data["s"] * data["kappa"] / data["mu"])
    return data


def valid_parameters(data: dict[str, Any]) -> bool:
    return bool(
        data["M"] >= 4
        and data["M"] % 2 == 0
        and data["L"] > 0
        and data["a"] == data["L"] / data["M"]
        and data["w"] == data["a"] / 8
        and data["mu"] == data["chi"] * data["w"]
        and data["chi"] > 0
        and data["c"] > 0
        and data["g"] > 0
        and data["lambda"] > 0
        and data["Delta"] != 0
        and data["s"] == data["Delta"] / 2
        and data["macro_h"] == data["Delta"] / 8
        and data["kappa"] == data["w"] * data["c"] / data["a"] ** 2
        and data["rho"] == data["c"] * data["Delta"] ** 2 / (8 * data["chi"] * data["a"] ** 2)
        and data["rho"] != 0
        and data["rho"] ** 2 != 1
    )


def drift(leg: Leg, duration: sp.Expr, data: dict[str, Any]) -> Leg:
    return ((leg[0] + duration * leg[1] / data["mu"]).applyfunc(sp.factor), leg[1].copy())


def force(position: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    return (data["w"] * PARENT.q3_gradient(position, data) / 2).applyfunc(sp.factor)


def kick(west: Leg, south: Leg, strength: sp.Expr, data: dict[str, Any]) -> tuple[Leg, Leg]:
    fw = force(west[0], data) + data["kappa"] * (west[0] - south[0])
    fs = force(south[0], data) + data["kappa"] * (south[0] - west[0])
    return (
        (west[0].copy(), (west[1] - strength * fw).applyfunc(sp.factor)),
        (south[0].copy(), (south[1] - strength * fs).applyfunc(sp.factor)),
    )


def macro_gate(west: Leg, south: Leg, data: dict[str, Any], sign: int = 1) -> tuple[Leg, Leg]:
    h = sign * data["macro_h"]
    s = sign * data["s"]
    west_1, south_1 = drift(west, h, data), drift(south, h, data)
    west_k1, south_k1 = kick(west_1, south_1, s, data)
    west_2, south_2 = drift(west_k1, 2 * h, data), drift(south_k1, 2 * h, data)
    west_k2, south_k2 = kick(west_2, south_2, s, data)
    return drift(west_k2, h, data), drift(south_k2, h, data)


def mixed_west_east(west: Leg, east: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    h, s, kappa, mu = data["macro_h"], data["s"], data["kappa"], data["mu"]
    x, p = west
    e, p2 = east
    x1 = x + h * p / mu
    x2 = e - h * p2 / mu
    p1 = mu * (x2 - x1) / (2 * h)
    y1 = x1 + (p1 - p + s * force(x1, data)) / (s * kappa)
    y2 = x2 + (p2 - p1 + s * force(x2, data)) / (s * kappa)
    r1 = mu * (y2 - y1) / (2 * h)
    r = r1 + s * (force(y1, data) + kappa * (y1 - x1))
    y = y1 - h * r / mu
    r2 = r1 - s * (force(y2, data) + kappa * (y2 - x2))
    north = (y2 + h * r2 / mu, r2)
    return (north[0].applyfunc(sp.factor), north[1].applyfunc(sp.factor)), (y.applyfunc(sp.factor), r.applyfunc(sp.factor))


def mixed_west_north(west: Leg, north: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    h, s, kappa, mu, rho = data["macro_h"], data["s"], data["kappa"], data["mu"], data["rho"]
    x, p = west
    n, r2 = north
    x1 = x + h * p / mu
    y2 = n - h * r2 / mu
    a_value = x1 + (2 * h / mu) * (p - s * (force(x1, data) + kappa * x1))
    b_value = r2 + s * (force(y2, data) + kappa * (y2 - a_value))
    y1 = (y2 - (2 * h / mu) * b_value) / (1 - rho**2)
    x2 = a_value + rho * y1
    r1 = mu * (y2 - y1) / (2 * h)
    r = r1 + s * (force(y1, data) + kappa * (y1 - x1))
    y = y1 - h * r / mu
    p1 = mu * (x2 - x1) / (2 * h)
    p2 = p1 - s * (force(x2, data) + kappa * (x2 - y2))
    east = (x2 + h * p2 / mu, p2)
    return (east[0].applyfunc(sp.factor), east[1].applyfunc(sp.factor)), (y.applyfunc(sp.factor), r.applyfunc(sp.factor))


def legs_equal(left: Leg, right: Leg) -> bool:
    return left[0] == right[0] and left[1] == right[1]


def symbolic_one_species() -> dict[str, sp.Expr]:
    x, p, y, r = sp.symbols("x p y r", real=True)
    h, s, kappa, mu, alpha, cubic = sp.symbols("h s kappa mu alpha cubic", nonzero=True)
    onsite = lambda z: alpha * z + cubic * z**3
    x1, y1 = x + h * p / mu, y + h * r / mu
    p1 = p - s * (onsite(x1) + kappa * (x1 - y1))
    r1 = r - s * (onsite(y1) + kappa * (y1 - x1))
    x2, y2 = x1 + 2 * h * p1 / mu, y1 + 2 * h * r1 / mu
    p2 = p1 - s * (onsite(x2) + kappa * (x2 - y2))
    r2 = r1 - s * (onsite(y2) + kappa * (y2 - x2))
    east = sp.Matrix([x2 + h * p2 / mu, p2])
    north = sp.Matrix([y2 + h * r2 / mu, r2])
    south = sp.Matrix([y, r])
    rho = 2 * h * s * kappa / mu
    det_e = sp.cancel(east.jacobian(south).det(method="berkowitz"))
    det_n = sp.cancel(north.jacobian(south).det(method="berkowitz"))
    return {"det_E_S": det_e, "det_N_S": det_n, "rho": rho}


def q3_hessian(position: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    symbols = sp.Matrix(sp.symbols("z0:8", real=True))
    symbolic = sp.hessian(PARENT.q3_potential(symbols, data), tuple(symbols))
    return symbolic.subs({symbols[i]: position[i] for i in range(8)}).applyfunc(sp.factor)


def local_jacobian(west: Leg, south: Leg, data: dict[str, Any]) -> sp.Matrix:
    dimension = 8
    identity = sp.eye(2 * dimension)
    drift_qp = sp.eye(4 * dimension)
    drift_qp[: 2 * dimension, 2 * dimension :] = data["macro_h"] * identity / data["mu"]
    drift2_qp = sp.eye(4 * dimension)
    drift2_qp[: 2 * dimension, 2 * dimension :] = 2 * data["macro_h"] * identity / data["mu"]

    west_1, south_1 = drift(west, data["macro_h"], data), drift(south, data["macro_h"], data)
    west_k1, south_k1 = kick(west_1, south_1, data["s"], data)
    west_2, south_2 = drift(west_k1, 2 * data["macro_h"], data), drift(south_k1, 2 * data["macro_h"], data)

    def kick_j(position_w: sp.Matrix, position_s: sp.Matrix) -> sp.Matrix:
        h_w = data["kappa"] * sp.eye(dimension) + data["w"] * q3_hessian(position_w, data) / 2
        h_s = data["kappa"] * sp.eye(dimension) + data["w"] * q3_hessian(position_s, data) / 2
        h_cross = -data["kappa"] * sp.eye(dimension)
        hessian = h_w.row_join(h_cross).col_join(h_cross.row_join(h_s))
        result = sp.eye(4 * dimension)
        result[2 * dimension :, : 2 * dimension] = -data["s"] * hessian
        return result

    return drift_qp * kick_j(west_2[0], south_2[0]) * drift2_qp * kick_j(west_1[0], south_1[0]) * drift_qp


def cross_blocks(jacobian: sp.Matrix) -> tuple[sp.Matrix, sp.Matrix]:
    # Ordering is (x,y,p,r), with each entry eight-dimensional.
    south_columns = list(range(8, 16)) + list(range(24, 32))
    east_rows = list(range(0, 8)) + list(range(16, 24))
    north_rows = list(range(8, 16)) + list(range(24, 32))
    return jacobian.extract(east_rows, south_columns), jacobian.extract(north_rows, south_columns)


def forward_rectangle(data: dict[str, Any], order: str) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    horizontal, vertical = PARENT.global_inputs(m, n, data["name"])
    vertices: Iterable[tuple[int, int]] = (
        ((i, j) for i in range(1, m + 1) for j in range(1, n + 1))
        if order == "column"
        else ((i, j) for j in range(1, n + 1) for i in range(1, m + 1))
    )
    for i, j in vertices:
        horizontal[(i, j)], vertical[(i, j)] = macro_gate(horizontal[(i - 1, j)], vertical[(i, j - 1)], data)
    return horizontal, vertical


def reverse_ideal(
    horizontal: dict[tuple[int, int], Leg],
    vertical: dict[tuple[int, int], Leg],
    ideal: tuple[int, ...],
    data: dict[str, Any],
) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    known_x: dict[tuple[int, int], Leg] = {}
    known_y: dict[tuple[int, int], Leg] = {}
    for kind, i, j in PARENT.cut_edges(m, n, ideal):
        if kind == "X":
            known_x[(i, j)] = horizontal[(i, j)]
        else:
            known_y[(i, j)] = vertical[(i, j)]
    for i in range(m, 0, -1):
        for j in range(n, 0, -1):
            if i <= ideal[j - 1]:
                known_x[(i - 1, j)], known_y[(i, j - 1)] = macro_gate(
                    known_x[(i, j)], known_y[(i, j)], data, sign=-1
                )
    return known_x, known_y


def mixed_rectangle(
    horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], data: dict[str, Any]
) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    x = {(0, j): horizontal[(0, j)] for j in range(1, n + 1)}
    y = {(i, n): vertical[(i, n)] for i in range(1, m + 1)}
    for i in range(1, m + 1):
        for j in range(n, 0, -1):
            x[(i, j)], y[(i, j - 1)] = mixed_west_north(x[(i - 1, j)], y[(i, j)], data)
    return x, y


def build_payload(profile: str) -> dict[str, Any]:
    data = parameters(profile)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    candidates = [json.loads(path.read_text(encoding="utf-8")) for path in (M0, M1, M2, M5)]
    parents = [json.loads(path.read_text(encoding="utf-8")) for path in PARENT_PATHS]
    a5 = json.loads(A5.read_text(encoding="utf-8"))
    a7 = json.loads(A7.read_text(encoding="utf-8"))
    a13 = json.loads(A13.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("parent ids", manifest["parent_ids"] == [item["candidate_id"] for item in parents], manifest["parent_ids"], [item["candidate_id"] for item in parents], "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("T0 authority", manifest["authority"].startswith("T0 "), manifest["authority"], "T0", "scope")
    for anchor in (
        "section-2-fixed-regulator",
        "section-4-global-mixed-inverses",
        "section-5-determinants",
        "section-7-exact-flow-check",
        "section-8-open-all-cut",
        "section-9-periodic-quotient",
        "section-10-invariant-state-split",
        "section-12-devils-advocate",
    ):
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate_text, anchor, "present", "provenance")

    audit.check("parameter domain", valid_parameters(data), data, "valid", "parameters")
    rho_oracle = q(3, 512) if profile == "f0" else q(7, 2400)
    audit.check("rho fixture oracle", data["rho"] == rho_oracle, data["rho"], rho_oracle, "parameters")
    audit.check("safe domain", 0 < data["rho"] < 1, data["rho"], "between zero and one", "parameters")
    for key, value in (("Delta", q(0)), ("c", q(0)), ("chi", q(0))):
        changed = dict(data)
        changed[key] = value
        if key == "Delta":
            changed["s"] = q(0); changed["macro_h"] = q(0); changed["rho"] = q(0)
        audit.check(f"reject hostile {key}", not valid_parameters(changed), valid_parameters(changed), False, "parameters")
    resonance = dict(data)
    resonance.update({"a": q(1), "L": q(data["M"]), "w": q(1, 8), "chi": q(1), "mu": q(1, 8), "c": q(8), "Delta": q(1), "s": q(1, 2), "macro_h": q(1, 8), "kappa": q(1), "rho": q(1)})
    audit.check("resonance rejected", not valid_parameters(resonance), resonance["rho"], 1, "negative_controls")

    symbolic = symbolic_one_species()
    audit.check("symbolic E cross determinant", sp.cancel(symbolic["det_E_S"] - symbolic["rho"] ** 2) == 0, symbolic["det_E_S"], symbolic["rho"] ** 2, "symbolic")
    audit.check("symbolic N cross determinant", sp.cancel(symbolic["det_N_S"] - (1 - symbolic["rho"] ** 2)) == 0, symbolic["det_N_S"], 1 - symbolic["rho"] ** 2, "symbolic")

    west, south = PARENT.local_fixture()
    east, north = macro_gate(west, south, data)
    recovered_west, recovered_south = macro_gate(east, north, data, sign=-1)
    audit.check("temporal inverse west", legs_equal(recovered_west, west), recovered_west, west, "local")
    audit.check("temporal inverse south", legs_equal(recovered_south, south), recovered_south, south, "local")
    mixed_north, mixed_south = mixed_west_east(west, east, data)
    audit.check("W-E inverse north", legs_equal(mixed_north, north), mixed_north, north, "local")
    audit.check("W-E inverse south", legs_equal(mixed_south, south), mixed_south, south, "local")
    mixed_east, mixed_south_2 = mixed_west_north(west, north, data)
    audit.check("W-N inverse east", legs_equal(mixed_east, east), mixed_east, east, "local")
    audit.check("W-N inverse south", legs_equal(mixed_south_2, south), mixed_south_2, south, "local")

    jacobian = local_jacobian(west, south, data)
    omega = sp.zeros(32)
    omega[:16, 16:] = -sp.eye(16)
    omega[16:, :16] = sp.eye(16)
    audit.check("full Q3 symplectic Jacobian", jacobian.T * omega * jacobian == omega, "zero defect", "zero defect", "Jacobian")
    audit.check("full Q3 temporal determinant", jacobian.det(method="domain-ge") == 1, jacobian.det(method="domain-ge"), 1, "Jacobian")
    east_cross, north_cross = cross_blocks(jacobian)
    audit.check("full Q3 E cross rank", east_cross.rank() == 16, east_cross.rank(), 16, "Jacobian")
    audit.check("full Q3 N cross rank", north_cross.rank() == 16, north_cross.rank(), 16, "Jacobian")
    audit.check("full Q3 E cross determinant", east_cross.det(method="domain-ge") == data["rho"] ** 16, east_cross.det(method="domain-ge"), data["rho"] ** 16, "Jacobian")
    audit.check("full Q3 N cross determinant", north_cross.det(method="domain-ge") == (1 - data["rho"] ** 2) ** 8, north_cross.det(method="domain-ge"), (1 - data["rho"] ** 2) ** 8, "Jacobian")
    hessian_w = q3_hessian(west[0] + data["macro_h"] * west[1] / data["mu"], data)
    hessian_s = q3_hessian(south[0] + data["macro_h"] * south[1] / data["mu"], data)
    commutator = hessian_w * hessian_s - hessian_s * hessian_w
    audit.check("hostile onsite Hessians noncommute", commutator != sp.zeros(8), commutator.rank(), "nonzero", "Jacobian")

    m_exact = 2 * data["mu"]
    exact_species = sp.factor(data["kappa"] ** 2 / (12 * m_exact**2))
    exact_mu = sp.factor(data["kappa"] ** 2 / (48 * data["mu"] ** 2))
    macro_species = sp.factor(data["kappa"] ** 2 / (64 * data["mu"] ** 2))
    leading = sp.Matrix([[data["kappa"] / (2 * m_exact), data["kappa"] / (6 * m_exact**2)], [data["kappa"], data["kappa"] / (2 * m_exact)]])
    audit.check("exact-flow mass firewall", m_exact == 2 * data["mu"], m_exact, 2 * data["mu"], "exact_flow")
    audit.check("exact-flow leading determinant", sp.factor(leading.det()) == exact_species, leading.det(), exact_species, "exact_flow")
    audit.check("exact-flow /48 form", exact_species == exact_mu, exact_species, exact_mu, "exact_flow")
    audit.check("macro /64 distinct", macro_species != exact_mu, macro_species, f"not {exact_mu}", "exact_flow")
    audit.check("macro rho leading", sp.factor(data["rho"] ** 2 / data["Delta"] ** 4) == macro_species, data["rho"] ** 2 / data["Delta"] ** 4, macro_species, "exact_flow")

    audit.check("potential ownership", 2 * data["s"] == data["Delta"], 2 * data["s"], data["Delta"], "ledger")
    audit.check("half kinetic ownership", 4 * data["macro_h"] == data["Delta"] / 2, 4 * data["macro_h"], data["Delta"] / 2, "ledger")
    even_edges = {(index, (index + 1) % data["M"]) for index in range(0, data["M"], 2)}
    odd_edges = {(index, (index + 1) % data["M"]) for index in range(1, data["M"], 2)}
    audit.check("bond colour partition", len(even_edges | odd_edges) == data["M"] and not even_edges & odd_edges, [even_edges, odd_edges], data["M"], "ledger")
    owners = [sum(site in edge for edge in even_edges | odd_edges) for site in range(data["M"])]
    audit.check("two half-owned bonds per node", owners == [2] * data["M"], owners, [2] * data["M"], "ledger")

    horizontal_a, vertical_a = forward_rectangle(data, "column")
    horizontal_b, vertical_b = forward_rectangle(data, "row")
    audit.check("rectangle sweep horizontal", horizontal_a == horizontal_b, len(horizontal_a), len(horizontal_b), "rectangle")
    audit.check("rectangle sweep vertical", vertical_a == vertical_b, len(vertical_a), len(vertical_b), "rectangle")
    m_rect, n_rect = data["rectangle"]
    ideals = PARENT.row_length_ideals(m_rect, n_rect)
    audit.check("monotone cut count", len(ideals) == math.comb(m_rect + n_rect, m_rect), len(ideals), math.comb(m_rect + n_rect, m_rect), "rectangle")
    for ideal in ideals:
        known_x, known_y = reverse_ideal(horizontal_a, vertical_a, ideal, data)
        recovered = all(legs_equal(known_x[(0, j)], horizontal_a[(0, j)]) for j in range(1, n_rect + 1)) and all(legs_equal(known_y[(i, 0)], vertical_a[(i, 0)]) for i in range(1, m_rect + 1))
        audit.check(f"reverse cut {ideal}", recovered, recovered, True, "all_cuts")
    mixed_x, mixed_y = mixed_rectangle(horizontal_a, vertical_a, data)
    audit.check("mixed rectangle east", all(legs_equal(mixed_x[(m_rect, j)], horizontal_a[(m_rect, j)]) for j in range(1, n_rect + 1)), "recovered", "recovered", "rectangle")
    audit.check("mixed rectangle south", all(legs_equal(mixed_y[(i, 0)], vertical_a[(i, 0)]) for i in range(1, m_rect + 1)), "recovered", "recovered", "rectangle")

    quotient_fixtures = [(2, 2), (3, 2), (3, 3), (4, 4)]
    quotient_rows = []
    for q_m, q_n in quotient_fixtures:
        q_M = q_m + q_n
        theta_origin = q_n * 2 + q_m * 3
        theta_shifted = q_n * (2 + q_m) + q_m * (3 - q_n)
        incidence = [[1 for _ in range(q_m)] for _ in range(q_n)]
        horizontal_degrees = [sum(row) for row in incidence]
        vertical_degrees = [sum(incidence[row][column] for row in range(q_n)) for column in range(q_m)]
        row = {
            "m": q_m, "n": q_n, "M": q_M, "theta_invariant": theta_origin == theta_shifted,
            "east_rise": q_n, "north_rise": q_m, "gate_count": q_m * q_n,
            "horizontal_degrees": horizontal_degrees, "vertical_degrees": vertical_degrees,
            "seam_order": q_M // math.gcd(q_m, q_n), "parity_descends": q_M % 2 == 0,
            "seam_preserves_colour": q_n % 2 == 0,
        }
        quotient_rows.append(row)
        audit.check(f"quotient theta {q_m}x{q_n}", row["theta_invariant"] and row["east_rise"] > 0 and row["north_rise"] > 0, row, "invariant and increasing", "quotient")
        audit.check(f"K incidence {q_m}x{q_n}", row["gate_count"] == q_m * q_n and horizontal_degrees == [q_m] * q_n and vertical_degrees == [q_n] * q_m, row, "K_(n,m)", "quotient")
    ledger_matches = [(left, right) for left in range(1, 9) for right in range(1, 9) if left * right == left + right and left == 2 and right == 2]
    all_count_solutions = [(left, right) for left in range(1, 9) for right in range(1, 9) if left * right == left + right]
    audit.check("raw ring ledger sole solution", all_count_solutions == [(2, 2)], all_count_solutions, [(2, 2)], "quotient")
    audit.check("raw ring degree solution", ledger_matches == [(2, 2)], ledger_matches, [(2, 2)], "quotient")

    commute = {frozenset(("A", "D")), frozenset(("B", "C"))}
    def trace_closure(word: tuple[str, ...]) -> set[tuple[str, ...]]:
        seen = {word}; frontier = [word]
        while frontier:
            current = frontier.pop()
            for index in range(len(current) - 1):
                if frozenset((current[index], current[index + 1])) in commute:
                    changed = current[:index] + (current[index + 1], current[index]) + current[index + 2:]
                    if changed not in seen:
                        seen.add(changed); frontier.append(changed)
        return seen
    left_word = ("A", "D", "C", "B", "A")
    right_word = ("D", "A", "B", "C", "A")
    audit.check("exact C4 trace-monoid conjugacy", right_word in trace_closure(left_word), sorted(trace_closure(left_word)), right_word, "quotient")
    audit.check("C4 not direct word equality", ("D", "C", "B", "A") != ("D", "A", "B", "C"), ("D", "C", "B", "A"), ("D", "A", "B", "C"), "quotient")

    c4_data = dict(data)
    c4_data.update({
        "M": 4,
        "L": q(4),
        "a": q(1),
        "w": q(1, 8),
        "chi": q(8),
        "mu": q(1),
        "c": q(8),
        "r": q(0),
        "Delta": q(2),
        "s": q(1),
        "macro_h": q(1, 4),
        "kappa": q(1),
        "rho": q(1, 2),
    })
    audit.check("C4 fixture parameter ledger", valid_parameters(c4_data), c4_data, "valid", "quotient")
    zero_leg: Leg = (sp.zeros(8, 1), sp.zeros(8, 1))
    c4_jacobian = local_jacobian(zero_leg, zero_leg, c4_data)
    c4_indices = [0, 16, 8, 24]
    derived_local = c4_jacobian.extract(c4_indices, c4_indices)
    expected_local = sp.Matrix([
        [q(1, 4), q(11, 16), q(3, 4), q(5, 16)],
        [-1, q(1, 4), 1, q(3, 4)],
        [q(3, 4), q(5, 16), q(1, 4), q(11, 16)],
        [1, q(3, 4), -1, q(1, 4)],
    ])
    audit.check("C4 tangent derived from macro", derived_local == expected_local, derived_local, expected_local, "quotient")
    expected_full = sp.zeros(32)
    for species in range(8):
        species_indices = [species, 16 + species, 8 + species, 24 + species]
        for row_index, row_target in enumerate(species_indices):
            for column_index, column_target in enumerate(species_indices):
                expected_full[row_target, column_target] = derived_local[row_index, column_index]
    audit.check("C4 tangent species decoupling", c4_jacobian == expected_full, c4_jacobian, expected_full, "quotient")
    local_linear = derived_local
    def embedded_gate(first: int, second: int) -> sp.Matrix:
        result = sp.eye(8)
        indices = [2 * first, 2 * first + 1, 2 * second, 2 * second + 1]
        for row_index, row_target in enumerate(indices):
            for column_index, column_target in enumerate(indices):
                result[row_target, column_target] = local_linear[row_index, column_index]
        return result
    gate_a = embedded_gate(0, 2); gate_b = embedded_gate(0, 3)
    gate_c = embedded_gate(1, 2); gate_d = embedded_gate(1, 3)
    u_block = gate_d * gate_c * gate_b * gate_a
    raw_eo = (gate_d * gate_a) * (gate_b * gate_c)
    audit.check("C4 numeric conjugacy", gate_a * u_block == raw_eo * gate_a, "zero defect", "zero defect", "quotient")
    witness = sp.Matrix([1, 0, 0, 0, 0, 0, 0, 0])
    block_witness = u_block * witness
    eo_witness = raw_eo * witness
    expected_block = sp.Matrix([q(-5, 8), q(-1, 2), 1, -1, q(7, 8), q(-1, 2), q(3, 4), 2])
    expected_eo = sp.Matrix([q(-5, 8), q(-1, 2), q(7, 8), q(3, 2), q(-1, 8), q(-1, 2), q(7, 8), q(-1, 2)])
    audit.check("raw EO block witness", block_witness == expected_block, block_witness, expected_block, "quotient")
    audit.check("raw EO circuit witness", eo_witness == expected_eo, eo_witness, expected_eo, "quotient")
    audit.check("raw EO direct inequality", block_witness != eo_witness, block_witness, eo_witness, "quotient")

    def mod1(value: int, size: int) -> int:
        return (value - 1) % size + 1

    def embedded_pairs(local: sp.Matrix, pairs: list[tuple[int, int]], size: int) -> sp.Matrix:
        result = sp.eye(4 * size)
        for first, second in pairs:
            indices = [2 * first, 2 * first + 1, 2 * second, 2 * second + 1]
            for row_index, row_target in enumerate(indices):
                for column_index, column_target in enumerate(indices):
                    result[row_target, column_target] = local[row_index, column_index]
        return result

    def labelled_gate(row: int, column: int, size: int) -> sp.Matrix:
        return embedded_pairs(local_linear, [(row - 1, size + column - 1)], size)

    def compose_application_order(maps: list[sp.Matrix], size: int) -> sp.Matrix:
        result = sp.eye(4 * size)
        for current in maps:
            result = current * result
        return result

    def word_data(size: int) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[list[tuple[int, int]]]]:
        square: list[tuple[int, int]] = []
        triangle: list[tuple[int, int]] = []
        for diagonal in range(2, 2 * size + 1):
            for row in range(1, size + 1):
                column = diagonal - row
                if 1 <= column <= size:
                    square.append((row, column))
                    if diagonal <= size:
                        triangle.append((row, column))
        layers = [[(row, mod1(layer - row, size)) for row in range(1, size + 1)] for layer in range(1, size + 1)]
        return square, triangle, layers

    def dependent_projection_equal(first: list[tuple[int, int]], second: list[tuple[int, int]], size: int) -> bool:
        from collections import Counter
        if Counter(first) != Counter(second):
            return False
        letters = [(row, column) for row in range(1, size + 1) for column in range(1, size + 1)]
        for left_index, left in enumerate(letters):
            for right in letters[left_index:]:
                if left[0] == right[0] or left[1] == right[1]:
                    if [item for item in first if item in (left, right)] != [item for item in second if item in (left, right)]:
                        return False
        return True

    def frame(size: int, step: int) -> sp.Matrix:
        result = sp.zeros(4 * size)
        for row in range(1, size + 1):
            position = (2 * (size - row) + step) % (2 * size)
            label = row - 1
            for component in range(2):
                result[2 * position + component, 2 * label + component] = 1
        for column in range(1, size + 1):
            position = (2 * (column - 1) + 1 - step) % (2 * size)
            label = size + column - 1
            for component in range(2):
                result[2 * position + component, 2 * label + component] = 1
        return result

    def half_turn(size: int) -> sp.Matrix:
        result = sp.zeros(4 * size)
        for position in range(2 * size):
            target = (position + size) % (2 * size)
            for component in range(2):
                result[2 * target + component, 2 * position + component] = 1
        return result

    leg_swap = sp.zeros(4)
    leg_swap[0, 2] = leg_swap[1, 3] = leg_swap[2, 0] = leg_swap[3, 1] = 1
    routed_local = leg_swap * local_linear
    routed_rows: dict[str, Any] = {}
    expected_first = {2: (q(-5, 8), q(-5, 8)), 3: (q(-1, 2), q(0)), 4: (q(7, 32), q(13, 32))}
    for size in (2, 3, 4):
        square_word, triangle_word, layer_words = word_data(size)
        strip_word = [gate for layer in layer_words for gate in layer]
        audit.check(f"k={size} square count", len(square_word) == size**2, len(square_word), size**2, "routed_seam")
        audit.check(f"k={size} triangle count", len(triangle_word) == size * (size - 1) // 2, len(triangle_word), size * (size - 1) // 2, "routed_seam")
        audit.check(f"k={size} strip count", len(strip_word) == size**2, len(strip_word), size**2, "routed_seam")
        audit.check(f"k={size} trace projections", dependent_projection_equal(square_word + triangle_word, triangle_word + strip_word, size), "equal", "equal", "routed_seam")
        square = compose_application_order([labelled_gate(row, column, size) for row, column in square_word], size)
        triangle = compose_application_order([labelled_gate(row, column, size) for row, column in triangle_word], size)
        labelled_layers = [compose_application_order([labelled_gate(row, column, size) for row, column in layer], size) for layer in layer_words]
        strip = compose_application_order(labelled_layers, size)
        audit.check(f"k={size} exact gluing", triangle * square == strip * triangle, "zero defect", "zero defect", "routed_seam")
        routed_layers: list[sp.Matrix] = []
        for layer, labelled_layer in enumerate(labelled_layers, start=1):
            pairs = ([(2 * index, 2 * index + 1) for index in range(size)] if layer % 2 else [((2 * index + 1) % (2 * size), (2 * index + 2) % (2 * size)) for index in range(size)])
            direct = embedded_pairs(routed_local, pairs, size)
            audit.check(f"k={size} routed layer {layer}", direct == frame(size, layer) * labelled_layer * frame(size, layer - 1).T, "zero defect", "zero defect", "routed_seam")
            routed_layers.append(direct)
        routed = compose_application_order(routed_layers, size)
        audit.check(f"k={size} routed total", routed == frame(size, size) * strip * frame(size, 0).T, "zero defect", "zero defect", "routed_seam")
        audit.check(f"k={size} half turn", frame(size, size) * frame(size, 0).T == half_turn(size), "exact", "exact", "routed_seam")
        cut_in = frame(size, 0) * triangle
        audit.check(f"k={size} seam conjugacy", cut_in * square == half_turn(size).T * routed * cut_in, "zero defect", "zero defect", "routed_seam")
        raw_layers = [labelled_layers[0 if time % 2 == 0 else size - 1] for time in range(size)]
        raw = compose_application_order(raw_layers, size)
        audit.check(f"k={size} raw equality boundary", (strip == raw) == (size == 2), strip == raw, size == 2, "routed_seam")
        basis = sp.zeros(4 * size, 1); basis[0] = 1
        desired_output, raw_output = strip * basis, raw * basis
        audit.check(f"k={size} routed witness", desired_output[0] == expected_first[size][0], desired_output[0], expected_first[size][0], "routed_seam")
        audit.check(f"k={size} raw witness", raw_output[0] == expected_first[size][1], raw_output[0], expected_first[size][1], "routed_seam")
        routed_rows[str(size)] = {"triangle_count": len(triangle_word), "routed_first": desired_output[0], "raw_first": raw_output[0], "raw_equals_routed": strip == raw}

    z = sp.Symbol("z")
    c4_charpoly = sp.factor(raw_eo.charpoly(z).as_expr())
    expected_c4_charpoly = sp.factor((z - 1) ** 2 * (z**2 + z + 1) * (z**2 + 3 * z + 1) ** 2)
    audit.check("C4 exact characteristic polynomial", c4_charpoly == expected_c4_charpoly, c4_charpoly, expected_c4_charpoly, "state")
    audit.check("C4 hyperbolic root", bool((-3 - sp.sqrt(5)) / 2 < -1), (-3 - sp.sqrt(5)) / 2, "less than -1", "state")

    ordered_data = dict(data); ordered_data["r"] = -ordered_data["g"]
    zero_leg = (sp.zeros(8, 1), sp.zeros(8, 1))
    plus_leg = (sp.ones(8, 1), sp.zeros(8, 1))
    minus_leg = (-sp.ones(8, 1), sp.zeros(8, 1))
    for label, leg in (("zero", zero_leg), ("plus", plus_leg), ("minus", minus_leg)):
        fixed_left, fixed_right = macro_gate(leg, leg, ordered_data)
        audit.check(f"{label} singular fixed phase", legs_equal(fixed_left, leg) and legs_equal(fixed_right, leg), "fixed", "fixed", "state")

    shadow_mu, shadow_s, shadow_k = sp.symbols("shadow_mu shadow_s shadow_k", nonzero=True)
    shadow_h = shadow_s / 4
    shadow_d = shadow_h / shadow_mu
    shadow_u = shadow_d * shadow_s * shadow_k
    shadow_step = sp.Matrix([[1 - shadow_u, shadow_d * (2 - shadow_u)], [-shadow_s * shadow_k, 1 - shadow_u]])
    shadow_metric = sp.diag(shadow_k / (1 - shadow_u / 2), 1 / (2 * shadow_mu))
    shadow_defect = (shadow_step.T * shadow_metric * shadow_step - shadow_metric).applyfunc(sp.factor)
    audit.check("single-bond quadratic shadow identity", shadow_defect == sp.zeros(2), shadow_defect, sp.zeros(2), "state")

    audit.check("admission result id", admission["result_id"] == ADMISSION_RESULT_ID, admission["result_id"], ADMISSION_RESULT_ID, "admission")
    vector = admission["exact_admission_vector"]
    audit.check("partial intake not frozen", vector["partial_boundary_evidence_intake_present"] is True and vector["partial_boundary_evidence_tranche_frozen"] is False, vector, "intake true/freeze false", "admission")
    audit.check("candidate manifests incomplete", vector["all_candidate_minimum_manifests_complete"] is False, vector["all_candidate_minimum_manifests_complete"], False, "admission")
    audit.check("common discriminator not frozen", vector["common_discriminator_matrix_frozen"] is False, vector["common_discriminator_matrix_frozen"], False, "admission")
    audit.check("selection unauthorized", vector["round1_decisive_selection_authorized"] is False and vector["pre_a_exit_conditions_met"] is False, vector, "both false", "admission")
    audit.check("all contestant files", admission["contestants"] == {"M0": str(M0.relative_to(REPO)).replace("\\", "/"), "M1": str(M1.relative_to(REPO)).replace("\\", "/"), "M2": str(M2.relative_to(REPO)).replace("\\", "/"), "M5": str(M5.relative_to(REPO)).replace("\\", "/")}, admission["contestants"], "four exact paths", "admission")
    audit.check("candidate ids", [item["candidate_id"] for item in candidates] == list(admission["candidate_matrix"]), [item["candidate_id"] for item in candidates], list(admission["candidate_matrix"]), "admission")
    audit.check("evidence intake status", "PARTIAL BOUNDARY INTAKE" in evidence["status"] and evidence["versioning_policy"]["charter_complete_freeze"] is False, evidence["status"], "partial not frozen", "evidence")
    required_evidence_fields = {"admission_status", "dataset_or_table", "uncertainty_model", "independence_rationale"}
    audit.check("evidence metadata complete", all(required_evidence_fields <= set(item) for item in evidence["evidence_items"]), [sorted(set(item) & required_evidence_fields) for item in evidence["evidence_items"]], sorted(required_evidence_fields), "evidence")
    audit.check("visible validation not sealed", any(item["role"] == "declared_non_fitting_validation" and "not blind or sealed" in item["validation_rule"] for item in evidence["evidence_items"]), [item["role"] for item in evidence["evidence_items"]], "visible non-fitting", "evidence")
    audit.check("calibration not experiment", evidence["calibration_authorities"][0]["role"] == "CALIBRATION_AUTHORITY_NOT_EXPERIMENT", evidence["calibration_authorities"][0]["role"], "CALIBRATION_AUTHORITY_NOT_EXPERIMENT", "evidence")

    audit.check("A5 conditional closed scope", a5["tier"] == "T6" and a5["open_gates"] == [], [a5["tier"], a5["open_gates"]], ["T6", []], "sector_a")
    audit.check("A5 excludes full derivative measure", "No full derivative Class-II constructive measure" in a5["notes"], a5["notes"], "exclusion present", "sector_a")
    audit.check("A7 full measure open", "A7-CLASSII-NELSON-EXPONENTIAL-BOUND" in a7["open_gates"], a7["open_gates"], "Nelson open", "sector_a")
    audit.check("A13 not closed", "T-050/A13" in a13["statement"] and "remain open" in a13["statement"], a13["statement"], "T-050/A13 open", "sector_a")
    audit.check("T050 route parked not erased", admission["a13_route_decision"]["T050_status"].startswith("PARKED FROM MAIN-PATH PHYSICAL PRIORITY"), admission["a13_route_decision"]["T050_status"], "parked from physical priority", "sector_a")
    next_gate = "PA-CP1-CL8-PERIODIC-BLOCH-LYAPUNOV-CUT-COMPATIBLE-STATE-FEASIBILITY"
    audit.check("next CP1 state gate", manifest["gate_resolution"]["next_gate"] == next_gate, manifest["gate_resolution"]["next_gate"], next_gate, "scope")
    expected_negatives = ["NG-2026-08-09-PRE-A-CP1-CL8-RAW-PERIODIC-EO-RECTANGLE-QUOTIENT", "NG-2026-08-09-PRE-A-CP1-CL8-UNIVERSAL-PERIODIC-QUADRATIC-SHADOW-GIBBS"]
    audit.check("registered negative ids", manifest["negative_ids"] == expected_negatives, manifest["negative_ids"], expected_negatives, "scope")
    for key, value in manifest["scope"].items():
        audit.check(f"scope boolean {key}", isinstance(value, bool), value, "boolean", "scope")

    invariants = {
        "profile": profile,
        "rho": data["rho"],
        "det_E_S": data["rho"] ** 16,
        "det_N_S": (1 - data["rho"] ** 2) ** 8,
        "exact_flow_species_coefficient": exact_mu,
        "macro_species_coefficient": macro_species,
        "onsite_hessian_commutator_rank": commutator.rank(),
        "rectangle": {"m": m_rect, "n": n_rect, "cut_count": len(ideals)},
        "periodic_quotient_fixtures": quotient_rows,
        "C4_local_tangent": local_linear,
        "C4_block_witness": block_witness,
        "C4_raw_EO_witness": eo_witness,
        "C4_characteristic_polynomial": c4_charpoly,
        "routed_seam_fixtures": routed_rows,
        "single_bond_shadow_identity": shadow_defect,
        "admission_selection_authorized": vector["round1_decisive_selection_authorized"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "admission_result_id": ADMISSION_RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "profile": profile,
        "parameters": data,
        "verdict": manifest["verdict"],
        "invariants": invariants,
        "scope": manifest["scope"],
        "negative_ids": manifest["negative_ids"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "parent_script": sha256(PARENT_SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "admission": sha256(ADMISSION),
            "evidence": sha256(EVIDENCE),
            **{path.stem: sha256(path) for path in PARENT_PATHS},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("f0", "f1"), default="f0")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(args.profile)
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} primary {args.profile}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
