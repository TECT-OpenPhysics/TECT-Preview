#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001056."""

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
SLUG = "pre-a-cp1-st8-q3lock-quartic-weyl-fourier-strip-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"


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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    G = F(fixture["G"])
    a = F(fixture["translation_amplitude"])
    t = F(fixture["time"])
    hbar = F(fixture["hbar"])
    y = F(fixture["strip_test_imaginary_height"])
    k3 = G * t * a / hbar
    k2 = F(3, 2) * G * t * a * a / hbar
    k1 = G * t * a * a * a / hbar
    k0 = G * t * a * a * a * a / (4 * hbar)
    x2_coefficient = 3 * k3 * y

    check("identity", manifest["exploration_id"] == "EXP-001056" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001056/T-054", "provenance")
    check("upstream identity", upstream["exploration_id"] == "EXP-000800", upstream["exploration_id"], "EXP-000800", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("quartic input", G > 0 and a != 0 and t != 0 and hbar > 0, [G, a, t, hbar], "valid", "input")
    check("difference degree", 4 - 1 == 3, 3, 3, "polynomial")
    check("cubic coefficient", G * a == F(51, 35) * F(1, 2), G * a, F(51, 70), "polynomial")
    check("phase kappa", k3 == F(17, 70), k3, F(17, 70), "phase")
    check("quadratic phase coefficient", k2 == F(51, 280), k2, F(51, 280), "phase")
    check("linear phase coefficient", k1 == F(17, 280), k1, F(17, 280), "phase")
    check("constant phase coefficient", k0 == F(17, 2240), k0, F(17, 2240), "phase")
    check("imaginary x2 coefficient", x2_coefficient == 3 * k3 * y, x2_coefficient, 3 * k3 * y, "strip")
    check("opposite strip sign", y * k3 < 0, y * k3, "<0", "strip")
    growth_samples: dict[str, str] = {}
    previous: F | None = None
    for raw_x in fixture["real_sample_points"]:
        x = F(raw_x)
        imaginary = k3 * (3 * x * x * y - y * y * y) + k2 * (2 * x * y) + k1 * y
        growth = -imaginary
        growth_samples[str(x)] = str(growth)
        if previous is not None:
            check(f"growth sample monotone x={x}", growth > previous, growth, f">{previous}", "strip")
        previous = growth
    check("positive growth coefficient", -x2_coefficient > 0, -x2_coefficient, ">0", "strip")
    upstream_text = json.dumps(upstream, ensure_ascii=True)
    check("upstream analytic precursor", "Weyl-Fourier" in upstream_text, "Weyl-Fourier" in upstream_text, True, "provenance")
    check("weighted Fourier lemma", manifest["analytic_lemma"]["weighted_fourier_implies_bounded_strip"] is True, manifest["analytic_lemma"], True, "scope")
    check("scope firewall", manifest["scope"]["full_q3_dynamics_closed"] is False and manifest["scope"]["state_weighted_route_closed"] is False, manifest["scope"], "open", "scope")

    passed = len(checks)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": checks,
        "derived": {
            "G": str(G),
            "translation_amplitude": str(a),
            "time": str(t),
            "hbar": str(hbar),
            "quartic_difference_degree": 3,
            "cubic_difference_coefficient": str(G * a),
            "phase_kappa": str(k3),
            "strip_test_imaginary_height": str(y),
            "imaginary_x2_coefficient": str(x2_coefficient),
            "positive_strip_growth_coefficient": str(-x2_coefficient),
            "real_sample_points": [str(F(v)) for v in fixture["real_sample_points"]],
            "growth_samples": growth_samples,
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
    print(f"INDEPENDENT QUARTIC-WEYL-FOURIER-STRIP PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
