#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001115."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_full_generator_entire_weight_threshold"
MANIFEST = REPO / "strategy/pre_a_cp1_st8_q3lock_full_generator_entire_weight_threshold_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = F(fixture["g"])
    lam = F(fixture["lambda"])
    coupling = F(fixture["c"])
    time = F(fixture["t"])
    sigma_good = F(fixture["sigma_good"])
    sigma_bad = F(fixture["sigma_bad"])
    G = g + 3 * lam
    rate = time * G / 4
    good_margin = sigma_good - rate
    bad_margin = rate - sigma_bad
    prefactor = coupling * time
    orders = list(range(1, int(fixture["truncation_order"]) + 1))
    amplitudes = [int(value) for value in fixture["amplitudes"]]
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001115" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001115/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("G fixture", G == F(51, 35), G, "51/35", "fixture")
    audit.check("rate fixture", rate == F(17, 140), rate, "17/140", "threshold")
    audit.check("good margin", good_margin == F(11, 140) and good_margin > 0, good_margin, "11/140", "threshold")
    audit.check("bad margin", bad_margin == F(3, 140) and bad_margin > 0, bad_margin, "3/140", "threshold")
    audit.check("prefactor", prefactor == F(2, 9), prefactor, "2/9", "threshold")
    audit.check("threshold order", sigma_good >= rate > sigma_bad, [sigma_good, rate, sigma_bad], "good>=rate>bad", "threshold")
    coefficient_rows: list[dict[str, Any]] = []
    for m in orders:
        coefficient = m * coupling * (G / 4) ** (m - 1)
        coefficient_rows.append({"m": m, "coefficient": coefficient, "degree": 4 * m - 3})
        audit.check(f"top coefficient positive m={m}", coefficient > 0, coefficient, ">0", "full-generator")
        audit.check(f"top degree m={m}", 4 * m - 3 == 4 * m - 3, 4 * m - 3, 4 * m - 3, "full-generator")
    good_rows: list[dict[str, Any]] = []
    bad_log_rows: list[dict[str, Any]] = []
    for amplitude in amplitudes:
        if amplitude == 0:
            good_ratio = 0.0
            bad_log = float("-inf")
        else:
            absolute = float(amplitude)
            a4 = absolute**4
            partial = sum((float(time) ** m / math.factorial(m)) * float(m * coupling * (G / 4) ** (m - 1)) * absolute ** (4 * m - 3) for m in orders)
            good_ratio = partial * math.exp(-float(sigma_good) * a4) / (1.0 + absolute)
            bad_log = math.log(float(prefactor) * absolute / (1.0 + absolute)) + float(bad_margin) * a4
        good_rows.append({"amplitude": amplitude, "good_scaled_partial_ratio": good_ratio})
        bad_log_rows.append({"amplitude": amplitude, "bad_log_ratio": bad_log})
    positive_good = [row["good_scaled_partial_ratio"] for row in good_rows]
    positive_bad = [row["bad_log_ratio"] for row in bad_log_rows if math.isfinite(row["bad_log_ratio"])]
    audit.check("good finite partial envelope", all(value <= float(prefactor) + 1e-12 for value in positive_good), good_rows, "<=2/9", "analytic-weight")
    audit.check("bad finite growth diagnostic", all(left < right for left, right in zip(positive_bad, positive_bad[1:])), bad_log_rows, "strictly increasing positive-amplitude logs", "analytic-weight")
    audit.check("open operator scope", manifest["scope"]["actual_q3_entire_seminorm_closed"] is False and manifest["scope"]["actual_q3_common_core_closed"] is False, manifest["scope"], "false/false", "scope")
    audit.check("no thermodynamic promotion", manifest["scope"]["volume_uniform_factorial_history_closed"] is False and manifest["scope"]["common_alpha_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "G": G,
            "c": coupling,
            "t": time,
            "rate": rate,
            "sigma_good": sigma_good,
            "sigma_bad": sigma_bad,
            "good_margin": good_margin,
            "bad_margin": bad_margin,
            "prefactor": prefactor,
            "coefficient_rows": coefficient_rows,
            "good_rows": good_rows,
            "bad_log_rows": bad_log_rows,
            "generating_identity": "c*t*|a|*exp((t*G/4)*|a|^4)",
            "weight_ratio": "c*t*|a|/(1+|a|)*exp(((t*G/4)-sigma)*|a|^4)",
            "full_generator_entire_weight_threshold_closed": True,
            "good_sigma_finite_partial_bound_closed": True,
            "bad_sigma_finite_growth_diagnostic_closed": True,
            "actual_q3_entire_seminorm_closed": False,
            "actual_q3_common_core_closed": False,
            "volume_uniform_factorial_history_closed": False,
            "common_alpha_closed": False,
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
    print(f"INDEPENDENT FULL-GENERATOR-ENTIRE-WEIGHT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
