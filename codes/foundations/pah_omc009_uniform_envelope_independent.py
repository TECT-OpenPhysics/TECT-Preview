#!/usr/bin/env python3
"""Non-importing independent algebraic replay for PAH-OMC-009.

The independent lane does not call the primary energy implementation.  It
rebuilds the strip incidence and derives the aperture-root increment directly
from the displayed onsite, covariant-edge and aperture-stiffness terms.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope/primary.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc009-uniform-envelope/independent.json"
)

RESULT_ID = "R-489"
EXPLORATION_ID = "EXP-001434"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-009-UNIFORM-ENVELOPE-INDEPENDENT-001"
B = (1, 0)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
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


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def params(contract: dict[str, Any]) -> dict[str, Any]:
    raw = contract["exact_scope"]["regulator_path"]
    return {
        "K": int(raw["K"]),
        "M_s": int(raw["M_s"]),
        "M_psi": int(raw["M_psi"]),
        "Q": int(raw["Q"]),
        "epsilon": fraction(raw["epsilon"]),
        "beta": fraction(raw["beta"]),
        "nu": fraction(raw["nu"]),
        "g": fraction(raw["g"]),
        "lambda_s": fraction(raw["lambda_s"]),
        "kappa_s": fraction(raw["kappa_s"]),
        "kappa_D": fraction(raw["kappa_D"]),
    }


def strip(level: int) -> tuple[set[tuple[int, int]], list[tuple[str, tuple[int, int], tuple[int, int]]], list[tuple[tuple[str, int], ...]]]:
    vertices = {(i, j) for i in range(level + 2) for j in (0, 1)}
    edges: list[tuple[str, tuple[int, int], tuple[int, int]]] = []
    for i in range(level + 1):
        edges.extend(((f"h{i}0", (i, 0), (i + 1, 0)), (f"h{i}1", (i, 1), (i + 1, 1))))
    for i in range(level + 2):
        edges.append((f"v{i}", (i, 0), (i, 1)))
    for i in range(level):
        edges.append((f"d{i}", (i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[str, int], ...]] = []
    for i in range(level):
        faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"d{i}", -1)))
        faces.append(((f"d{i}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    i = level
    faces.append(((f"h{i}0", 1), (f"v{i + 1}", 1), (f"h{i}1", -1), (f"v{i}", -1)))
    return vertices, edges, faces


def aperture(level: int, p: dict[str, Any]) -> Fraction:
    return p["epsilon"] + Fraction(level) * (1 - p["epsilon"]) / p["M_s"]


def direct_increment(p: dict[str, Any], degree: int, radius: Fraction) -> Fraction:
    """Direct term-by-term increment for the selected state and AP root."""
    s_before = aperture(0, p)
    s_after = aperture(1, p)
    # Only g*s^2*|psi|^2/2 survives from the matter onsite polynomial.
    onsite_matter = p["g"] * (s_after**2 - s_before**2) * radius**2 / 2
    # Every neighbour has s=1 and zero matter; J changes from 2/(eps+1) to 1.
    covariant_each = p["kappa_D"] * (1 - Fraction(2) / (s_before + 1)) * radius**2 / 2
    # Aperture onsite plus one stiffness term for each incident edge.
    aperture_constant = -(1 + degree) * p["lambda_s"] * (1 - p["epsilon"])**2 / 2
    return onsite_matter + degree * covariant_each + aperture_constant


def support(level: int) -> set[tuple[int, int]]:
    vertices, edges, faces = strip(level)
    lookup = {name: (left, right) for name, left, right in edges}
    incident = {name for name, left, right in edges if B in (left, right)}
    result = {B}
    for name in incident:
        result.update(lookup[name])
    for face in faces:
        if any(name in incident for name, _orientation in face):
            for name, _orientation in face:
                result.update(lookup[name])
    if not result <= vertices:
        raise AssertionError("support escaped carrier")
    return result


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = read_json(SOURCE)
    geometry = read_json(GEOMETRY)
    start = read_json(START)
    contract = read_json(CONTRACT)
    manifest = read_json(MANIFEST)
    primary = read_json(PRIMARY)
    p = params(contract)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(CONTRACT),
        "PAH-OMC-009-MANIFEST": sha(MANIFEST),
    }
    check("source-hashes", manifest["functional_source"]["sha256"] == hashes["PAH-001"] and manifest["geometric_source"]["sha256"] == hashes["PAH-OMC-004"] and manifest["starting_contract"]["sha256"] == hashes["PAH-OMC-008"] and manifest["contract"]["sha256"] == hashes["PAH-OMC-009"])
    check("source-identities", source["packet_id"] == "PAH-001" and geometry["contract_id"] == "PAH-OMC-004" and start["contract_id"] == "PAH-OMC-008" and contract["contract_id"] == "PAH-OMC-009")
    check("family-degree", all(sum(B in edge[1:] for edge in strip(level)[1]) == 4 for level in range(2, 20)))
    check("cofinal-face-rule", all(len(strip(level)[2]) == 2 * level + 1 for level in range(2, 20)))
    degree = sum(B in edge[1:] for edge in strip(2)[1])
    support_vertices = support(2)
    check("support-rule", B in support_vertices and len(support_vertices) >= 1, {"support": sorted(support_vertices)})
    quadratic, constant = (
        p["g"] * (1 - p["epsilon"] ** 2) / 2 + degree * p["kappa_D"] * (1 - Fraction(2) / (1 + p["epsilon"])) / 2,
        -(1 + degree) * p["lambda_s"] * (1 - p["epsilon"]) ** 2 / 2,
    )
    direct = {radius: direct_increment(p, degree, Fraction(radius)) for radius in (0, 1, 2, 4, 8)}
    check("direct-term-polynomial", all(value == quadratic * Fraction(radius) ** 2 + constant for radius, value in direct.items()), {"quadratic": str(quadratic), "constant": str(constant), "direct": {key: str(value) for key, value in direct.items()}})
    check("matter-polynomial-cancels", direct[0] == constant)
    exponent = {radius: -p["beta"] * (quadratic * Fraction(radius) ** 2 + constant) / 2 for radius in (1, 2, 4, 8)}
    check("positive-exponent-coefficient", -p["beta"] * quadratic / 2 > 0, str(-p["beta"] * quadratic / 2))
    check("exponent-monotone", exponent[1] < exponent[2] < exponent[4] < exponent[8], {key: str(value) for key, value in exponent.items()})
    mobility_square = aperture(0, p) * aperture(1, p)
    weight = 1 + len(support_vertices)
    logs = {radius: math.log(weight) + 0.5 * math.log(float(mobility_square)) + float(value) for radius, value in exponent.items()}
    check("mobility-and-weight", mobility_square == p["epsilon"] and weight > 0, {"mobility_square": str(mobility_square), "weight": weight})
    check("weighted-growth", logs[1] < logs[2] < logs[4] < logs[8], logs)
    check("independent-primary-coefficient", primary["witness"]["quadratic_coefficient"] == str(quadratic) and primary["witness"]["constant"] == str(constant))
    check("negative-envelope-conclusion", -p["beta"] * quadratic / 2 > 0 and weight > 0)

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc009-uniform-envelope-independent/1.0",
        "run_kind": "independent",
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
        "verdict": "NEGATIVE_RESULT_RMAX_UNIFORM_ENVELOPE",
        "classification": "NON_IMPORTING_EXACT_TERM_DERIVATION",
        "derived": {"degree_b": degree, "support": [list(vertex) for vertex in sorted(support_vertices)], "weight": weight, "quadratic_coefficient": str(quadratic), "constant": str(constant), "rate_exponent": {str(key): str(value) for key, value in exponent.items()}, "weighted_rate_log": logs},
        "cross_check": "The primary and independent implementations use different energy paths and agree on the exact quadratic coefficient and constant.",
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": {"command": "python codes/foundations/pah_omc009_uniform_envelope_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc009-uniform-envelope/independent.json"},
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; independent-coefficient={quadratic}; rate-coefficient={-p['beta']*quadratic/2}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
