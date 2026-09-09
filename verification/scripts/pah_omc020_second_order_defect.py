#!/usr/bin/env python3
"""Primary exact finite second-order semigroup-defect replay for PAH-OMC-020.

The witness is preregistered in the companion contract.  The script imports
only the frozen finite strip/root implementation used by R-493, reconstructs
the unchanged midpoint rates in the exact quadratic field Q(sqrt(2)), and
computes the two generator applications as exponential polynomials.  The
nonzero residual is a route-local finite obstruction; it is not a change to
PAH-001 and it is not an infinite-volume or physical statement.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-second-order-defect-contract-v1.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
OMC013_CODE = ROOT / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
R493_LEAN = ROOT / "verification/lean/Tect/R493.lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-second-order-defect/primary.json"

RESULT_ID = "R-551"
TASK_ID = "T-083"
AUDIT_ID = "PAH-OMC-020-SECOND-ORDER-DEFECT-PRIMARY-001"

PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "OMC013-code": "bda0c7bd7ed5f8b3871fd7590b600458589c4b5feBA0a147219e94cdae0526a0".lower(),
    "R493-Lean": "c350035719b939c429a9e09d163015d34a471c3e6ea7c4678d4a88049060bc88",
}

# These are preregistered INPUTS, not fitted output values.
WITNESS = {"coarse_level": 3, "R_max": 1, "sample_variant": 3, "observable": "ell_a"}
# Expected exact term locations are test oracles for the independently derived
# exponential polynomial.  The primary calculation does not use them to form
# the residual.
EXPECTED_RESIDUAL = {
    Fraction(-25, 8): (Fraction(-1, 2), Fraction(0)),
    Fraction(-67, 24): (Fraction(1, 2), Fraction(0)),
    Fraction(-59, 24): (Fraction(1, 2), Fraction(0)),
    Fraction(-17, 8): (Fraction(-1, 2), Fraction(0)),
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Quad):
        return {"rational": str(value.a), "sqrt2": str(value.b)}
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(serial(value), ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_source_module() -> Any:
    spec = importlib.util.spec_from_file_location("pah_omc013_source", OMC013_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen OMC-013 implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Quad:
    """a + b*sqrt(2), with exact rational coefficients."""

    __slots__ = ("a", "b")

    def __init__(self, a: Fraction | int = 0, b: Fraction | int = 0) -> None:
        self.a = Fraction(a)
        self.b = Fraction(b)

    def __add__(self, other: "Quad") -> "Quad":
        return Quad(self.a + other.a, self.b + other.b)

    def __neg__(self) -> "Quad":
        return Quad(-self.a, -self.b)

    def __sub__(self, other: "Quad") -> "Quad":
        return self + (-other)

    def __mul__(self, other: "Quad") -> "Quad":
        return Quad(self.a * other.a + 2 * self.b * other.b, self.a * other.b + self.b * other.a)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Quad) and self.a == other.a and self.b == other.b

    def zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def text(self) -> str:
        return f"{self.a}+({self.b})sqrt2"


def state_key(state: dict[str, dict[Any, int]]) -> tuple[tuple[str, tuple[tuple[Any, int], ...]], ...]:
    return tuple((name, tuple(sorted(values.items()))) for name, values in sorted(state.items()))


def state_from_key(key: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...]) -> dict[str, dict[Any, int]]:
    return {name: dict(values) for name, values in key}


def psi(module: Any, state: dict[str, dict[Any, int]], vertex: tuple[int, int], r_max: int) -> Fraction:
    return Fraction(r_max) * state["ell"][vertex] * module.z2(state["phase"][vertex])


def term_value(module: Any, level: int, state: dict[str, dict[Any, int]], term: str, r_max: int) -> Fraction:
    kind, name = term.split(":", 1)
    edges = module.edge_lookup(level)
    if kind == "onsite":
        i, j = (int(value) for value in name.split(","))
        vertex = (i, j)
        s = module.aperture(state["aperture"][vertex])
        p = psi(module, state, vertex, r_max)
        return (s - 1) ** 2 / Fraction(2) + p**4 / Fraction(4) + p**6 / Fraction(6) + s**2 * p**2 / Fraction(2)
    if kind == "stiffness":
        _edge, left, right = edges[name]
        sl = module.aperture(state["aperture"][left])
        sr = module.aperture(state["aperture"][right])
        return (sl - sr) ** 2 / Fraction(2)
    if kind == "covariant":
        _edge, left, right = edges[name]
        sl = module.aperture(state["aperture"][left])
        sr = module.aperture(state["aperture"][right])
        stiffness = Fraction(2) / (sl + sr)
        return stiffness * (psi(module, state, right, r_max) - module.z2(state["link"][name]) * psi(module, state, left, r_max)) ** 2 / Fraction(2)
    if kind == "face":
        _face, boundary = module.face_lookup(level)[name]
        stiffness = sum(
            Fraction(2) / (module.aperture(state["aperture"][edges[edge][1]]) + module.aperture(state["aperture"][edges[edge][2]]))
            for edge, _orientation in boundary
        )
        holonomy = 1
        for edge, _orientation in boundary:
            holonomy *= module.z2(state["link"][edge])
        return stiffness / Fraction(len(boundary)) * (1 - holonomy)
    raise ValueError(kind)


def local_delta(module: Any, level: int, before: dict[str, dict[Any, int]], after: dict[str, dict[Any, int]], root: dict[str, Any], r_max: int) -> Fraction:
    return sum(term_value(module, level, after, term, r_max) - term_value(module, level, before, term, r_max) for term in root["affected_terms"])


def mobility(module: Any, before: dict[str, dict[Any, int]], after: dict[str, dict[Any, int]], root: dict[str, Any]) -> Quad:
    family = root["family"]
    if family == "phase":
        return Quad(module.aperture(before["aperture"][root["vertex"]]))
    if family == "aperture":
        # nu=1 and an admissible aperture step gives sqrt((1/2)*1)=sqrt(2)/2.
        return Quad(0, Fraction(1, 2))
    left, right = module.edge_lookup(root["level"])[root["edge"]][1:]
    product = module.aperture(before["aperture"][left]) * module.aperture(before["aperture"][right])
    if product == Fraction(1, 4):
        return Quad(Fraction(1, 2))
    if product == Fraction(1, 2):
        return Quad(0, Fraction(1, 2))
    if product == Fraction(1):
        return Quad(1)
    raise AssertionError(f"unexpected mobility product {product}")


def poly_add(left: dict[Fraction, Quad], right: dict[Fraction, Quad]) -> dict[Fraction, Quad]:
    out = dict(left)
    for exponent, coefficient in right.items():
        value = out.get(exponent, Quad()) + coefficient
        if value.zero():
            out.pop(exponent, None)
        else:
            out[exponent] = value
    return out


def poly_scale(poly: dict[Fraction, Quad], scalar: Quad) -> dict[Fraction, Quad]:
    out: dict[Fraction, Quad] = {}
    for exponent, coefficient in poly.items():
        value = coefficient * scalar
        if not value.zero():
            out[exponent] = value
    return out


def poly_shift_scale(poly: dict[Fraction, Quad], shift: Fraction, scalar: Quad) -> dict[Fraction, Quad]:
    return {exponent + shift: coefficient * scalar for exponent, coefficient in poly.items() if not (coefficient * scalar).zero()}


def poly_sub(left: dict[Fraction, Quad], right: dict[Fraction, Quad]) -> dict[Fraction, Quad]:
    return poly_add(left, poly_scale(right, Quad(-1)))


def exact_transitions(module: Any, level: int, key: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...], r_max: int) -> tuple[tuple[Any, Quad, Fraction, str], ...]:
    before = state_from_key(key)
    transitions = []
    for root0 in module.root_catalog(level):
        root = dict(root0)
        root["level"] = level
        after = module.apply_root(before, root)
        if after is None:
            continue
        target = state_key(after)
        delta = local_delta(module, level, before, after, root, r_max)
        transitions.append((target, mobility(module, before, after, root), -delta / Fraction(2), root["label"]))
    return tuple(transitions)


def observable(module: Any, state: dict[str, dict[Any, int]], _level: int) -> int:
    return state["ell"][(0, 0)]


def lifted_value(module: Any, coarse_level: int, key: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...]) -> int:
    return observable(module, module.project_state(coarse_level, state_from_key(key))[0], coarse_level)


def generator_poly(module: Any, level: int, key: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...], r_max: int, lift_to: int | None = None) -> dict[Fraction, Quad]:
    state = state_from_key(key)
    value = lifted_value(module, lift_to, key) if lift_to is not None else observable(module, state, level)
    result: dict[Fraction, Quad] = {}
    for target, coefficient, exponent, _label in exact_transitions(module, level, key, r_max):
        target_value = lifted_value(module, lift_to, target) if lift_to is not None else observable(module, state_from_key(target), level)
        increment = target_value - value
        if increment:
            result = poly_add(result, {exponent: coefficient * Quad(increment)})
    return result


def second_poly(module: Any, level: int, key: tuple[tuple[str, tuple[tuple[Any, int], ...]], ...], r_max: int, lift_to: int | None = None) -> dict[Fraction, Quad]:
    first = generator_poly(module, level, key, r_max, lift_to)
    result: dict[Fraction, Quad] = {}
    for target, coefficient, exponent, _label in exact_transitions(module, level, key, r_max):
        next_first = generator_poly(module, level, target, r_max, lift_to)
        result = poly_add(result, poly_shift_scale(poly_sub(next_first, first), exponent, coefficient))
    return result


def poly_text(poly: dict[Fraction, Quad]) -> dict[str, str]:
    return {str(exponent): coefficient.text() for exponent, coefficient in sorted(poly.items())}


def numeric(poly: dict[Fraction, Quad]) -> float:
    return sum(float(coefficient.a + coefficient.b * Fraction(2) ** Fraction(1, 2)) * math.exp(float(exponent)) for exponent, coefficient in poly.items())


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    module = load_source_module()
    paths = {"PAH-001": PAH001, "PAH-OMC-013": OMC013, "OMC013-code": OMC013_CODE, "R493-Lean": R493_LEAN}
    actual = {name: sha(path) for name, path in paths.items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": serial(detail)})

    check("parent hashes", actual == PINS, {"actual": actual, "expected": PINS})
    check("contract identity", contract.get("contract_id") == "PAH-OMC-020-SECOND-ORDER-DEFECT" and contract.get("result_id") == RESULT_ID and contract.get("task_id") == TASK_ID, {"contract_id": contract.get("contract_id"), "result_id": contract.get("result_id"), "task_id": contract.get("task_id")})
    check("unchanged model firewall", all(contract["preservation_firewall"].values()), contract["preservation_firewall"])
    check("finite external-time scope", "external stochastic" in contract["exact_scope"]["time"].lower() and "not quantum" in " ".join(contract["non_claims"]).lower(), contract["exact_scope"])

    n = int(WITNESS["coarse_level"])
    r_max = int(WITNESS["R_max"])
    fine = state_key(module.sample_state(n + 1, int(WITNESS["sample_variant"])))
    coarse = state_key(module.project_state(n, state_from_key(fine))[0])
    first = poly_sub(generator_poly(module, n + 1, fine, r_max, lift_to=n), generator_poly(module, n, coarse, r_max))
    fine_second = second_poly(module, n + 1, fine, r_max, lift_to=n)
    coarse_second = second_poly(module, n, coarse, r_max)
    residual = poly_sub(fine_second, coarse_second)
    expected = {exponent: Quad(a, b) for exponent, (a, b) in EXPECTED_RESIDUAL.items()}
    check("R-493 first-order witness is zero", not first, poly_text(first))
    check("exact second-order residual matches oracle", residual == expected, {"actual": poly_text(residual), "expected": poly_text(expected)})
    check("residual is nonzero", bool(residual), poly_text(residual))
    check("factorized sign certificate", set(residual) == set(expected) and all(value.b == 0 for value in residual.values()), poly_text(residual))

    # The local affected-term calculation is checked against the frozen full
    # source energy for every admissible witness transition.
    delta_checks = []
    witness_state = state_from_key(fine)
    for target, _coefficient, _exponent, label in exact_transitions(module, n + 1, fine, r_max):
        after = state_from_key(target)
        root = next(item for item in module.root_catalog(n + 1) if item["label"] == label)
        root["level"] = n + 1
        local = local_delta(module, n + 1, witness_state, after, root, r_max)
        full = module.energy(n + 1, after, Fraction(r_max)) - module.energy(n + 1, witness_state, Fraction(r_max))
        delta_checks.append(local == full)
    check("affected-term delta equals full frozen energy", all(delta_checks), {"transitions": len(delta_checks), "failures": len(delta_checks) - sum(delta_checks)})
    check("threshold is the R-493 threshold", contract["witness"]["N_f"] == n and "N(f)=max(2,m_f+1)" in contract["source_boundary"]["R-493_threshold"], contract["witness"])
    check("no physical promotion", not contract["status"]["claim_bearing"] and not contract["status"]["active_gate_change"] and not contract["status"]["physical_promotion"], contract["status"])

    failed = [row for row in checks if row["status"] != "PASS"]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-second-order-defect-primary/1.0",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "NEGATIVE_RESULT" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "negative_result",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual,
        "witness": {**WITNESS, "N_f": contract["witness"]["N_f"], "fine_state": serial(fine)},
        "first_order_residual": poly_text(first),
        "fine_second_order": poly_text(fine_second),
        "coarse_second_order": poly_text(coarse_second),
        "second_order_residual": poly_text(residual),
        "second_order_numeric": numeric(residual),
        "factorization": "D = -1/2 exp(-25/8) (exp(1/3)-1)^2 (exp(1/3)+1) < 0",
        "checks": checks,
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "finding": contract["finding"],
        "scope_boundary": contract["exact_scope"]["scope_boundary"],
        "missing_assumptions": contract["missing_assumptions"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": sha(Path(__file__)),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID}: {payload['verification']} {payload['checks_passed']}/{len(checks)}; verdict={payload['verdict']}; residual={payload['second_order_numeric']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    return 0 if run(destination)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
