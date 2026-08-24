#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001057.

This lane reconstructs the finite-volume Q3 quartic-weight comparison without
importing the primary SymPy implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-canonical-energy-quartic-weight-coercivity-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-canonical-energy-quartic-weight-coercivity/independent.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def square(value: Fraction) -> Fraction:
    return value * value


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    model = manifest["model"]
    fixture = manifest["finite_fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001057" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001057/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("weight declaration", model["weight"] == "W_Lambda(q)=1+sum_x q_x^4", model["weight"], "W_Lambda", "model")
    check("shift declaration", model["shifted_form"] == "Hhat_Lambda=H_Lambda+n*r^2/(2*g)", model["shifted_form"], "exact extensive shift", "model")

    chi = frac(fixture["chi"])
    g = frac(fixture["g"])
    r = frac(fixture["r"])
    c = frac(fixture["c"])
    lam = frac(fixture["lambda"])
    v_squared = -r / g
    shift_per_site = r * r / (2 * g)
    weight_constant = Fraction(8, 1) / g
    check("parameter positivity", chi > 0 and g > 0 and c >= 0 and lam >= 0 and r < 0, [chi, g, c, lam, r], "chi,g>0; c,lambda>=0; r<0", "parameters")
    check("derived v squared", v_squared == frac(fixture["derived_v_squared"]), v_squared, fixture["derived_v_squared"], "derived")
    check("derived shift", shift_per_site == frac(fixture["derived_shift_per_site"]), shift_per_site, fixture["derived_shift_per_site"], "derived")
    check("derived weight constant", weight_constant == frac(fixture["derived_weight_constant"]), weight_constant, fixture["derived_weight_constant"], "derived")

    # The completed-square and quartic remainder identities are reconstructed
    # coefficientwise at q=0, 1, 2 and 3, which is independent of SymPy.
    for q in map(frac, fixture["field_values"][:4]):
        onsite = r * q * q / 2 + g * q**4 / 4
        square_term = g * square(q * q + r / g) / 4
        check(f"completed square q={q}", onsite + r * r / (4 * g) == square_term, onsite + r * r / (4 * g), square_term, "algebra")
        remainder = 2 * square(q * q + r / g) + 2 * square(r / g) - q**4
        check(f"quartic remainder q={q}", remainder == square(q * q + 2 * r / g) and remainder >= 0, remainder, square(q * q + 2 * r / g), "algebra")

    fields = tuple(frac(value) for value in fixture["field_values"])
    volumes = tuple(int(value) for value in fixture["volumes"])
    rows: list[dict[str, Any]] = []
    vector_count = 0
    for n in volumes:
        vectors = itertools.product(fields, repeat=n) if n <= 2 else ((value,) * n for value in fields)
        for vector in vectors:
            vector_count += 1
            onsite_energy = sum((r * value**2 / 2 + g * value**4 / 4) for value in vector)
            shifted_onsite = onsite_energy + n * shift_per_site
            weight = 1 + sum(value**4 for value in vector)
            spatial = c * sum(square(vector[index] - vector[(index + 1) % n]) for index in range(n)) / 2 if n > 1 else Fraction(0)
            q3_edge = lam * sum(square(vector[index] - vector[(index + 1) % n]) * (vector[index] ** 2 + vector[(index + 1) % n] ** 2) for index in range(n)) / 4 if n > 1 else Fraction(0)
            full_shifted = shifted_onsite + spatial + q3_edge
            bound = 1 + weight_constant * shifted_onsite
            full_bound = 1 + weight_constant * full_shifted
            check(f"weight bound n={n} vector={vector}", weight <= bound, weight, bound, "coercivity")
            check(f"shifted nonnegative n={n} vector={vector}", shifted_onsite >= 0, shifted_onsite, ">=0", "coercivity")
            check(f"spatial nonnegative n={n} vector={vector}", spatial >= 0, spatial, ">=0", "positive terms")
            check(f"Q3 edge nonnegative n={n} vector={vector}", q3_edge >= 0, q3_edge, ">=0", "positive terms")
            check(f"full bound n={n} vector={vector}", weight <= full_bound, weight, full_bound, "coercivity")
            rows.append({"n": n, "vector": vector, "onsite_energy": onsite_energy, "shifted_onsite": shifted_onsite, "weight": weight, "spatial": spatial, "q3_edge": q3_edge, "full_shifted": full_shifted, "bound": bound})

    check("finite vector count", vector_count == len(rows), vector_count, len(rows), "fixture")
    check("form scope", manifest["scope"]["canonical_q3_form_comparison_closed"] is True and manifest["scope"]["finite_form_core_domain_closure"] is False, manifest["scope"], "comparison closed; domain open", "scope")
    check("QFT firewall", all(manifest["scope"][key] is False for key in ("operator_d_duhamel_locality_closed", "delta_d_locality_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), manifest["scope"], "QFT successors open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit,
        "sample_rows": rows,
        "derived": {
            "v_squared": v_squared,
            "shift_per_site": shift_per_site,
            "weight_constant": weight_constant,
            "vector_count": vector_count,
            "coercive_bound": "W_Lambda <= 1+(8/g)*(H_Lambda+n*r^2/(2*g))",
            "canonical_q3_form_comparison_closed": True,
            "extensive_shift_required_in_statement": True,
            "operator_d_duhamel_locality_closed": False,
            "hamiltonian_os_identification_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT CANONICAL-Q3-ENERGY-COERCIVITY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
