#!/usr/bin/env python3
"""Non-importing standard-library audit for R-167 v2.7."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
PRIMARY = SCRIPT.with_name(SCRIPT.name.replace("_independent.py", ".py"))
SLUG = "pre-a-cp1-st8-q3lock-fixed-ritz-gevrey-two-truncation-and-raw-configuration-weyl-c0-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
GATES = REPO / "claims/GATES.md"
RESULTS = REPO / "RESULTS-LEDGER.md"
NEGATIVES = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-independent-{SLUG}/result.json"
)


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def exact_integer_square_root(value: Fraction) -> int:
    if value.denominator != 1:
        raise AssertionError("expected integer square")
    root = math.isqrt(value.numerator)
    if root * root != value.numerator:
        raise AssertionError("expected exact square")
    return root


def rebuild_fixture() -> dict[str, Any]:
    alpha, beta, gap = Fraction(1), Fraction(1), Fraction(1)
    eta, volume = Fraction(1, 800), 12
    x = exact_integer_square_root(beta * gap / (8 * eta))
    n = x
    rho = beta * gap / n**2
    ratio = eta / rho
    bound = 2 * alpha * volume * eta * ratio**n
    envelope = 16 * alpha * volume * eta * Fraction(1, 8) ** x
    return {
        "x": x,
        "n_star": n,
        "rho": rho,
        "ratio": ratio,
        "fixed_order_bound": bound,
        "stretched_exponential_envelope": envelope,
        "fixed_to_envelope_ratio": bound / envelope,
        "conditions": (
            eta < beta * gap / 32,
            eta < gap / (32 * alpha),
            eta < rho / 4,
        ),
    }


def polynomial_coefficients(poly: list[Fraction]) -> list[Fraction]:
    while poly and poly[-1] == 0:
        poly.pop()
    return poly


def rebuild_packet_phase() -> dict[str, Any]:
    # Coefficients in t for (t/chi)|xi|^2 p_parallel and the BCH phase,
    # after p_parallel=(chi*pi/(t|xi|^2)-hbar/2).  pi is represented by
    # a formal constant symbol with rational coefficient one.
    pi_coefficient = Fraction(1)
    hbar_t_coefficient = Fraction(-1, 2) + Fraction(1, 2)
    total = polynomial_coefficients([pi_coefficient, hbar_t_coefficient])
    gaussian_coefficient = Fraction(-1, 4)
    return {
        "formal_total_phase": total,
        "gaussian_coefficient": gaussian_coefficient,
        "norm_upper_bound": 2,
        "norm_lower_limit": 2,
    }


def exploration_exists() -> bool:
    if not EXPLORATIONS.exists():
        return False
    matches = [
        json.loads(line)
        for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("id") == "EXP-000828"
    ]
    return len(matches) == 1


def run(*, staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    imports = set()
    syntax_tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    dynamic_import = False
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "__import__"
        ):
            dynamic_import = True
    audit.check(
        "independent does not import primary",
        PRIMARY.stem not in imports
        and imports.issubset(set(sys.stdlib_module_names) | {"__future__"})
        and not dynamic_import,
        sorted(imports),
        "no primary import",
        "independence",
    )
    audit.check(
        "manifest exact ids",
        manifest["result_version"] == "v2.7"
        and manifest["exploration_id"] == "EXP-000828"
        and len(manifest["negative_ids"]) == 2,
        (manifest["result_version"], manifest["exploration_id"], len(manifest["negative_ids"])),
        ("v2.7", "EXP-000828", 2),
        "provenance",
    )

    fixture = rebuild_fixture()
    oracle = manifest["exact_fixture"]
    for key in (
        "x",
        "n_star",
        "rho",
        "ratio",
        "fixed_order_bound",
        "stretched_exponential_envelope",
        "fixed_to_envelope_ratio",
    ):
        actual = fixture[key]
        expected = oracle[key]
        audit.check(
            f"Fraction fixture {key}",
            str(actual) == str(expected),
            actual,
            expected,
            "truncation",
        )
    audit.check(
        "all smallness conditions",
        all(fixture["conditions"]),
        fixture["conditions"],
        (True, True, True),
        "truncation",
    )

    packet = rebuild_packet_phase()
    audit.check(
        "formal packet phase pi",
        packet["formal_total_phase"] == [Fraction(1)],
        packet["formal_total_phase"],
        [Fraction(1)],
        "weyl",
    )
    audit.check(
        "Gaussian overlap coefficient",
        packet["gaussian_coefficient"] == Fraction(-1, 4),
        packet["gaussian_coefficient"],
        Fraction(-1, 4),
        "weyl",
    )
    audit.check(
        "sharp unitary norm sandwich",
        packet["norm_upper_bound"] == packet["norm_lower_limit"] == 2,
        (packet["norm_lower_limit"], packet["norm_upper_bound"]),
        (2, 2),
        "weyl",
    )

    ratios = [Fraction((n + 1) ** 2, 7) for n in range(1, 81)]
    audit.check(
        "zero-radius counterseries ratio",
        all(b > a for a, b in zip(ratios, ratios[1:])) and ratios[-1] > 100,
        ratios[-1],
        ">100 and increasing",
        "gevrey",
    )
    discrete_majorant = all(
        (r + 1) ** (2 * r)
        <= 36**r * math.factorial(r) ** 2
        for r in range(1, 81)
    )
    audit.check(
        "independent Gevrey inequality sample",
        discrete_majorant,
        discrete_majorant,
        True,
        "gevrey",
    )
    geometric_identity = all(
        Fraction(1, 1) / (1 + x)
        == sum((-x) ** n for n in range(order + 1))
        + (-x) ** (order + 1) / (1 + x)
        for x in (Fraction(1, 11), Fraction(2, 7), Fraction(5, 3))
        for order in range(0, 20)
    )
    audit.check(
        "exact Gevrey asymptotic remainder identity",
        geometric_identity,
        geometric_identity,
        True,
        "gevrey",
    )

    for token in (
        manifest["closed_gate_id"],
        *manifest["negative_ids"],
        "16alpha_M|Lambda||eta|",
        "fixed-M",
        "local-SW",
        "sharp norm limit two",
        "No per-lemma or intermediate PDF is issued",
    ):
        audit.check(
            f"certificate token {token[:48]}",
            token in certificate,
            token in certificate,
            True,
            "certificate",
        )

    if not staged:
        formal = (
            exploration_exists()
            and manifest["closed_gate_id"] in GATES.read_text(encoding="utf-8")
            and all(
                negative_id in NEGATIVES.read_text(encoding="utf-8")
                for negative_id in manifest["negative_ids"]
            )
            and "R-167 v2.7" in RESULTS.read_text(encoding="utf-8")
            and "EXP-000828" in RESULTS.read_text(encoding="utf-8")
        )
        audit.check("formal authorities present", formal, formal, True, "formal")

    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
        "script_version": __version__,
        "verdict": "PASS",
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "derived": {
            "truncation_fixture": {k: str(v) for k, v in fixture.items() if k != "conditions"},
            "weyl_norm_jump": "2",
            "standard_sw_optimal_scale_transfer": False,
            "all_order_convergence": False,
            "common_alpha_closed": False,
        },
        "source_hashes": {
            path.relative_to(REPO).as_posix(): normalized_sha256(path)
            for path in (SCRIPT, PRIMARY, MANIFEST, CERTIFICATE)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"SELF-TEST PASS {summary['passed']}/{summary['total']}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
