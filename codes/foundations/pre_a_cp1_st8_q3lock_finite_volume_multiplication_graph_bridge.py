#!/usr/bin/env python3
"""Primary exact audit for EXP-001055.

The multivariate pointwise Q3 source bound is lifted to a declared commuting
multiplication representation with the explicit potential weight W_Lambda.
The full Q3 Hamiltonian comparison remains outside this package.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-finite-volume-multiplication-graph-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound-manifest.json"
FIXTURE = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["fixture"]
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001055" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001055/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-001054", upstream["exploration_id"], "EXP-001054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("operator model", manifest["operator_model"]["configuration_space"] == "R^Lambda with commuting multiplication coordinates" and manifest["operator_model"]["weight"] == "W_Lambda(q)=1+sum_x q_x^4", manifest["operator_model"], "declared model", "model")

    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    q, v, a = sp.symbols("q v a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    edge_v = sp.expand(edge - lam * (q - (v - a)) ** 2 * (q**2 + (v - a) ** 2) / 4)
    bond = coupling * (q - v) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - v) ** 2 / 2)
    bond_v = sp.expand(bond - coupling * (q - (v - a)) ** 2 / 2)
    onsite_q = sp.Rational(3, 5) * (q**4 - (q - a) ** 4) / 4
    onsite_v = sp.Rational(3, 5) * (v**4 - (v - a) ** 4) / 4
    P = sp.expand(onsite_q + 3 * edge_u + 6 * bond_u)
    P_reverse = sp.expand(onsite_v + 3 * edge_v + 6 * bond_v)
    C = sp.Rational(manifest["operator_model"]["constant"].split("=")[-1])
    fields = tuple(sp.Rational(value) for value in manifest["finite_fixture"]["field_values"])
    sources = tuple(sp.Rational(value) for value in manifest["finite_fixture"]["source_values"])
    local_rows: list[dict[str, Any]] = []
    for volume in manifest["finite_fixture"]["volumes"]:
        check(f"volume declared {volume}", volume >= 2, volume, ">=2", "volume")
        for q_value, v_value, a_value in itertools.product(fields, fields, sources):
            config = (q_value, v_value) + tuple(sp.Integer(0) for _ in range(volume - 2))
            W = 1 + sum(entry**4 for entry in config)
            center_value = sp.factor(P.subs({q: q_value, v: v_value, a: a_value}))
            reverse_value = sp.factor(P_reverse.subs({q: q_value, v: v_value, a: a_value}))
            bound_power = C**4 * W**3
            check(f"local center volume={volume} {q_value},{v_value},{a_value}", abs(center_value) ** 4 <= bound_power, center_value, "graph bound", "local")
            check(f"local reverse volume={volume} {q_value},{v_value},{a_value}", abs(reverse_value) ** 4 <= bound_power, reverse_value, "graph bound", "local")
            local_rows.append({"volume": volume, "config": config, "a": a_value, "center": center_value, "reverse": reverse_value, "W": W, "bound_power": bound_power})

    product_rows: list[dict[str, Any]] = []
    volume = 4
    for q_values, a_value in itertools.product(itertools.product(fields, repeat=volume), sources):
        W = 1 + sum(entry**4 for entry in q_values)
        for length in manifest["finite_fixture"]["word_lengths"]:
            factors: list[sp.Expr] = []
            for index in range(length):
                left = q_values[index % volume]
                right = q_values[(index + 1) % volume]
                expression = P if index % 2 == 0 else P_reverse
                factors.append(sp.factor(expression.subs({q: left, v: right, a: a_value})))
            product = sp.factor(sp.prod(factors))
            bound_power = C ** (4 * length) * W ** (3 * length)
            check(f"commuting word length={length} {q_values},{a_value}", abs(product) ** 4 <= bound_power, product, "C^n graph product", "product")
            product_rows.append({"length": length, "config": q_values, "a": a_value, "product": product, "W": W, "bound_power": bound_power})
    check("local fixture cardinality", len(local_rows) == len(manifest["finite_fixture"]["volumes"]) * len(fields) ** 2 * len(sources), len(local_rows), "expected", "fixture")
    check("product fixture cardinality", len(product_rows) == len(fields) ** volume * len(sources) * len(manifest["finite_fixture"]["word_lengths"]), len(product_rows), "expected", "fixture")
    check("conditional scope", manifest["scope"]["potential_multiplication_graph_bound_closed"] is True and manifest["scope"]["commuting_product_bound_closed_conditionally"] is True and manifest["scope"]["full_q3_energy_comparison_proved"] is False, manifest["scope"], "potential-only/open", "scope")
    check("QFT scope", manifest["scope"]["factorial_incidence_supplied"] is False and manifest["scope"]["kms_os_closed"] is False and manifest["scope"]["continuum_closed"] is False, manifest["scope"], "conditional/open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit, "local_rows": local_rows, "product_rows": product_rows,
        "derived": {
            "C": C, "volumes_checked": list(manifest["finite_fixture"]["volumes"]), "local_rows": len(local_rows), "product_rows": len(product_rows), "word_lengths_checked": len(manifest["finite_fixture"]["word_lengths"]),
            "potential_multiplication_graph_bound_closed": True, "commuting_product_bound_closed_conditionally": True, "full_q3_energy_comparison_proved": False,
            "actual_q3_common_core_map_proved": False, "operator_domain_closure_proved": False, "factorial_incidence_supplied": False, "actual_q3_history_closed": False, "common_alpha_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "upstream_manifest_sha256": sha256(UPSTREAM), "fixture_manifest_sha256": sha256(FIXTURE)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY Q3-FINITE-MULTIPLICATION-GRAPH PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
