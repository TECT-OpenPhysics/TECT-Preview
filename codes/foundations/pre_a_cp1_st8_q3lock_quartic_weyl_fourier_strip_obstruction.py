#!/usr/bin/env python3
"""Primary exact audit for the quartic Weyl--Fourier strip obstruction.

The package tests only the positive-strip L1 Weyl--Fourier carrier for the
quartic onsite subflow.  It does not identify this carrier with the full Q3
dynamics or reject other analytic/Frechet, Gevrey, modular, or state-weighted
topologies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-quartic-weyl-fourier-strip-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    audit = Audit()
    fixture = manifest["fixture"]
    G = sp.Rational(fixture["G"])
    amplitude = sp.Rational(fixture["translation_amplitude"])
    time = sp.Rational(fixture["time"])
    hbar = sp.Rational(fixture["hbar"])
    strip_y = sp.Rational(fixture["strip_test_imaginary_height"])
    q = sp.symbols("q", real=True)
    x, y = sp.symbols("x y", real=True)

    audit.check("identity", manifest["exploration_id"] == "EXP-001056" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001056/T-054", "provenance")
    audit.check("upstream identity", upstream["exploration_id"] == "EXP-000800", upstream["exploration_id"], "EXP-000800", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("quartic coupling positive", G > 0, G, ">0", "input")
    audit.check("nonzero translation", amplitude != 0, amplitude, "!=0", "input")
    audit.check("nonzero time", time != 0, time, "!=0", "input")

    potential = G * q**4 / 4
    difference = sp.expand(potential.subs(q, q + amplitude) - potential)
    degree = sp.Poly(difference, q).degree()
    cubic_coefficient = sp.Poly(difference, q).coeff_monomial(q**3)
    phase = sp.expand(time * difference / hbar)
    kappa = sp.simplify(sp.Poly(phase, q).coeff_monomial(q**3))
    complex_phase = sp.expand(phase.subs(q, x + sp.I * y))
    imaginary_phase = sp.simplify(sp.im(complex_phase))
    x2_coefficient = sp.simplify(sp.Poly(sp.expand(imaginary_phase), x).coeff_monomial(x**2))
    chosen_growth_coefficient = sp.simplify(-x2_coefficient.subs(y, strip_y))

    audit.check("quartic difference degree", degree == 3, degree, 3, "polynomial")
    audit.check("cubic difference coefficient", cubic_coefficient == G * amplitude, cubic_coefficient, G * amplitude, "polynomial")
    audit.check("phase kappa", kappa == time * G * amplitude / hbar, kappa, time * G * amplitude / hbar, "phase")
    audit.check("imaginary x2 coefficient", x2_coefficient == 3 * kappa * y, x2_coefficient, 3 * kappa * y, "strip")
    audit.check("chosen strip sign", strip_y * kappa < 0, [strip_y, kappa], "opposite signs", "strip")
    audit.check("positive strip growth coefficient", chosen_growth_coefficient > 0, chosen_growth_coefficient, ">0", "strip")

    sample_values: dict[str, str] = {}
    previous: sp.Rational | None = None
    for raw_x in fixture["real_sample_points"]:
        point = sp.Rational(raw_x)
        growth = sp.simplify(-imaginary_phase.subs({x: point, y: strip_y}))
        sample_values[str(point)] = str(growth)
        if previous is not None:
            audit.check(f"growth sample monotone x={point}", growth > previous, growth, f">{previous}", "strip")
        previous = growth
    upstream_text = json.dumps(upstream, ensure_ascii=True); audit.check("upstream analytic precursor", "Weyl-Fourier" in upstream_text, "Weyl-Fourier" in upstream_text, True, "provenance")
    audit.check("strip contradiction premise", manifest["analytic_lemma"]["weighted_fourier_implies_bounded_strip"] is True, manifest["analytic_lemma"], True, "scope")
    audit.check("full dynamics firewall", manifest["scope"]["full_q3_dynamics_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "open", "scope")
    audit.check("alternative topology firewall", manifest["scope"]["gevery_or_subexponential_alternative_tested"] is False and manifest["scope"]["state_weighted_route_closed"] is False, manifest["scope"], "open", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "G": str(G),
            "translation_amplitude": str(amplitude),
            "time": str(time),
            "hbar": str(hbar),
            "quartic_difference_degree": degree,
            "cubic_difference_coefficient": str(cubic_coefficient),
            "phase_kappa": str(kappa),
            "strip_test_imaginary_height": str(strip_y),
            "imaginary_x2_coefficient": str(sp.simplify(x2_coefficient.subs(y, strip_y))),
            "positive_strip_growth_coefficient": str(chosen_growth_coefficient),
            "real_sample_points": [str(sp.Rational(v)) for v in fixture["real_sample_points"]],
            "growth_samples": sample_values,
            "positive_strip_weyl_fourier_carrier_refuted": True,
            "full_q3_dynamics_closed": False,
            "common_alpha_closed": False,
            "gevery_or_subexponential_alternative_tested": False,
            "state_weighted_route_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": normalized_sha256(MANIFEST),
            "upstream_manifest": str(UPSTREAM.relative_to(REPO)).replace("\\", "/"),
            "upstream_manifest_sha256": normalized_sha256(UPSTREAM),
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
    print(f"PRIMARY QUARTIC-WEYL-FOURIER-STRIP PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
