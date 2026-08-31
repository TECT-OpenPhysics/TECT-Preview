#!/usr/bin/env python3
"""Hostile mutation audit for R-463.

Each mutation targets a sign, factor, shell-convention, flat-direction, or
promotion firewall.  The script must reject all eight and never changes the
canonical manifest or any research authority.
"""

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
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-tube-metric-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-hostile-a6-active-branch-tube-metric"
    / "hostile.json"
)


def normalized_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def qform(a: F, b: F, c: F, x: F, y: F) -> F:
    return a * x * x + 2 * b * x * y + c * y * y


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_production_functional_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    p = a1["parameters"]
    alpha = F(str(p["alpha_X"]))
    beta = F(str(p["beta_X"]))
    denominator = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    a = F(str(p["cJJ"])) * alpha * alpha / denominator
    b = F(str(p["cJK"])) * alpha * beta / denominator
    c = F(str(p["cKK"])) * beta * beta / denominator
    determinant = a * c - b * b
    trace = a + c
    lambda_r = determinant / trace
    kappa = a + 2 * b + c
    values = [F(value) for value in manifest["audit"]["active_grid_values"]]
    threshold = F(str(manifest["audit"]["tube_thresholds"][-1]))
    convention_threshold = lambda_r
    points = [(x, y, u1, u2, u3) for x in values for y in values for u1 in values for u2 in values for u3 in values]
    zero = (F(0), F(0), F(0), F(0), F(0))
    sample = (F(1), F(1), F(0), F(0), F(0))
    sample_q = qform(a, b, c, sample[0], sample[1])
    sample_gap = sample_q - lambda_r * (sample[0] ** 2 + sample[1] ** 2)
    sample_squares = (a * sample[0] + b * sample[1]) ** 2 + (b * sample[0] + c * sample[1]) ** 2
    active_metrics = [lambda_r * (point[0] ** 2 + point[1] ** 2) + kappa * sum(value * value for value in point[2:]) for point in points]
    canonical_count = sum(metric >= threshold for metric in active_metrics)
    rows: list[dict[str, Any]] = []

    def reject(name: str, detected: bool, mutation: str, witness: Any) -> None:
        rows.append({"name": name, "pass": bool(detected), "mutation": mutation, "witness": str(witness)})
        if not detected:
            raise AssertionError(f"hostile mutation accepted: {name}")

    reject("wrong radial sign", determinant / (-trace) <= 0, "lambda_r=Delta/(-(a+c))", determinant / (-trace))
    reject("wrong angular coefficient", a + 2 * b - c != kappa, "kappa=a+2*b-c", (a + 2 * b - c, kappa))
    reject("omit mixed term", qform(a, F(0), c, sample[0], sample[1]) != sample_q, "b=0 in q_Q", (qform(a, F(0), c, sample[0], sample[1]), sample_q))
    reject("radial identity mutation", trace * sample_gap != sample_squares + b * b, "add b^2 to the exact gap", (trace * sample_gap, sample_squares + b * b))
    convention_canonical = sum(metric >= convention_threshold for metric in active_metrics)
    strict_count = sum(metric > convention_threshold for metric in active_metrics)
    reject("strict shell convention", strict_count != convention_canonical, "> instead of >=", (strict_count, convention_canonical))
    beta_sample = F(str(manifest["audit"]["beta_values"][0]))
    shell_energies = [
        qform(a, b, c, point[0], point[1]) + kappa * sum(value * value for value in point[2:])
        for point, metric in zip(points, active_metrics)
        if metric >= threshold
    ]
    canonical_exponent = beta_sample * min(shell_energies) / 2
    mutated_exponent = beta_sample * min(shell_energies)
    reject("Boltzmann factor of two", mutated_exponent != canonical_exponent, "use beta*E2_min instead of beta*E2_min/2", (canonical_exponent, mutated_exponent))
    flat_points = [(F(-1), F(0)), (F(0), F(-1)), (F(1), F(0)), (F(0), F(1))]
    fake_flat_energy = [kappa * (f1 * f1 + f2 * f2) for f1, f2 in flat_points]
    reject("flat energy promotion", any(value != 0 for value in fake_flat_energy), "assign active kappa energy to flat proxy", fake_flat_energy[0])
    reject("proxy-to-tightness promotion", manifest["scope_firewall"]["tightness_closed"] is False, "set tightness_closed=true", manifest["scope_firewall"]["tightness_closed"])

    payload = {
        "schema": "tect/a6-classii-active-branch-tube-metric-hostile-result/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": "1.0.0",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "source_hash": normalized_sha(MANIFEST),
        "canonical_shell_count": canonical_count,
        "canonical_zero": [str(value) for value in zero],
        "evidence_level": "hostile firewall audit only",
        "non_claims": manifest["non_claims"],
    }
    output = args.output if args.output.is_absolute() else REPO / args.output
    save(output, payload)
    print(f"HOSTILE MUTATIONS REJECTED {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
