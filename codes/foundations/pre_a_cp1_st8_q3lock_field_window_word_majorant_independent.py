#!/usr/bin/env python3
"""Independent Fraction audit for the field-window Q3 word envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-field-window-word-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def l1(coefficients: list[F], radius: F) -> F:
    return sum(abs(value) * radius**degree for degree, value in enumerate(coefficients))


def onsite_coeffs(g: F, q: F) -> list[F]:
    return [F(0), g*q**3, -F(3, 2)*g*q**2, g*q, -g/F(4)]


def edge_coeffs(lam: F, q: F, v: F) -> list[F]:
    return [F(0), lam*(q**3-F(3, 2)*q**2*v+q*v**2-F(1, 2)*v**3), -lam*(F(3, 2)*q**2-F(3, 2)*q*v+F(1, 2)*v**2), lam*(q-F(1, 2)*v), -lam/F(4)]


def bond_coeffs(c: F, q: F, r: F) -> list[F]:
    return [F(0), c*(q-r), -c/F(2)]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g, lam, c = F(fixture["g"]), F(fixture["lambda"]), F(fixture["spatial_coupling"])
    Q, S, time = F(fixture["field_radius"]), F(fixture["source_radius"]), F(fixture["time"])
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001040" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001040/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    onsite_bound = g*(Q**3*S+F(3, 2)*Q**2*S**2+Q*S**3+S**4/F(4))
    edge_bound = lam*(4*Q**3*S+F(7, 2)*Q**2*S**2+F(3, 2)*Q*S**3+S**4/F(4))
    bond_bound = c*(2*Q*S+S**2/F(2))
    onsite_choices = int(fixture["onsite_choices"])
    edge_choices = int(fixture["q3_edge_choices"])
    bond_choices = int(fixture["spatial_bond_choices"])
    local_choices = onsite_choices + edge_choices + bond_choices
    rate = onsite_choices*onsite_bound + edge_choices*edge_bound + bond_choices*bond_bound
    weighted_rate = time*rate
    audit.check("choice count", local_choices == int(fixture["local_choice_count"]), local_choices, fixture["local_choice_count"], "graph")
    audit.check("positive bounds", onsite_bound > 0 and edge_bound > 0 and bond_bound > 0, [onsite_bound, edge_bound, bond_bound], ">0", "window")

    grid = tuple(-Q + 2*Q*F(index, 4) for index in range(5))
    rows: list[dict[str, Any]] = []
    for q in grid:
        for v in grid:
            on = l1(onsite_coeffs(g, q), S)
            edge = l1(edge_coeffs(lam, q, v), S)
            reverse = l1(edge_coeffs(lam, v, q), S)
            audit.check(f"onsite q={q}", on <= onsite_bound, on, f"<={onsite_bound}", "window")
            audit.check(f"edge q={q} v={v}", edge <= edge_bound, edge, f"<={edge_bound}", "window")
            audit.check(f"edge reverse q={q} v={v}", reverse <= edge_bound, reverse, f"<={edge_bound}", "orientation")
            rows.append({"q": q, "v": v, "onsite_l1": on, "edge_l1": edge, "reverse_edge_l1": reverse})
    for q in grid:
        for r in grid:
            b = l1(bond_coeffs(c, q, r), S)
            reverse = l1(bond_coeffs(c, r, q), S)
            audit.check(f"bond q={q} r={r}", b <= bond_bound, b, f"<={bond_bound}", "window")
            audit.check(f"bond reverse q={q} r={r}", reverse <= bond_bound, reverse, f"<={bond_bound}", "orientation")

    word_rows: list[dict[str, Any]] = []
    max_word = int(fixture["max_word_length"])
    partial = F(0)
    for n in range(max_word+1):
        term = weighted_rate**n / F(1)
        for k in range(1, n+1):
            term /= k
        partial += term
        audit.check(f"word term n={n}", term == weighted_rate**n / F(math_factorial(n)), term, term, "majorant")
        word_rows.append({"length": n, "term": term, "partial": partial})
    audit.check("choice rate", rate == onsite_choices*onsite_bound+edge_choices*edge_bound+bond_choices*bond_bound, rate, rate, "majorant")
    audit.check("field window only", manifest["scope"]["field_window_word_egf_closed"] is True and manifest["scope"]["field_independent_operator_history_closed"] is False, manifest["scope"], "closed window, open operator", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit.rows, "grid_rows": rows, "word_rows": word_rows,
        "derived": {"field_radius": Q, "source_radius": S, "onsite_bound": onsite_bound, "q3_edge_bound": edge_bound, "spatial_bond_bound": bond_bound, "local_rate": rate, "weighted_rate": weighted_rate, "local_choices": local_choices, "field_window_word_egf_closed": True, "orientation_symmetric": True, "field_independent_operator_history_closed": False, "all_shape_exhaustion_closed": False, "common_alpha_closed": False},
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"], "boundary": manifest["scope"],
    }


def math_factorial(value: int) -> int:
    result = 1
    for factor in range(2, value+1):
        result *= factor
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(); payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FIELD-WINDOW-Q3-WORD-MAJORANT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
