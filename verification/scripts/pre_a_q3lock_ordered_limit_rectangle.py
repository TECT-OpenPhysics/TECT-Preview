#!/usr/bin/env python3
"""Primary exact self-test for the R-474 ordered-limit rectangle contract.

The synthetic geometric fixture checks only epsilon bookkeeping.  It is not a
source-owned TECT dynamics or a finite-to-infinite extrapolation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-q3lock-ordered-limit-rectangle-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / "2026-08-31-primary-r474-ordered-limit-rectangle" / "primary.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def frac(value: str | int) -> Fraction:
    return Fraction(str(value))


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def threshold(base: int, tolerance: Fraction, maximum: int) -> int:
    for index in range(maximum + 1):
        if Fraction(1, base ** (index + 1)) < tolerance:
            return index
    raise AssertionError("fixture maximum does not contain a strict threshold")


def core(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fixture = manifest["fixture"]
    limit = frac(fixture["limit"])
    cutoff_base = int(fixture["cutoff_base"])
    volume_base = int(fixture["volume_base"])
    split = int(fixture["epsilon_split_denominator"])
    indices = [int(item) for item in fixture["sample_indices"]]
    maximum = int(fixture["max_index"])
    epsilons = [frac(item) for item in fixture["epsilon_values"]]

    def observable(n: int, m: int) -> Fraction:
        return limit + Fraction(1, cutoff_base ** (n + 1)) + Fraction(1, volume_base ** (m + 1))

    def forward_midpoint(m: int) -> Fraction:
        return limit + Fraction(1, volume_base ** (m + 1))

    def reverse_midpoint(n: int) -> Fraction:
        return limit + Fraction(1, cutoff_base ** (n + 1))

    rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for epsilon in epsilons:
        half = epsilon / split
        n0 = threshold(cutoff_base, half, maximum)
        m0 = threshold(volume_base, half, maximum)
        forward_cutoff_max = max(
            (abs(observable(n, m) - forward_midpoint(m)) for n in range(n0, maximum + 1) for m in indices),
            default=Fraction(0),
        )
        forward_volume_max = max(
            (abs(forward_midpoint(m) - limit) for m in range(m0, maximum + 1)),
            default=Fraction(0),
        )
        reverse_volume_max = max(
            (abs(observable(n, m) - reverse_midpoint(n)) for n in indices for m in range(m0, maximum + 1)),
            default=Fraction(0),
        )
        reverse_cutoff_max = max(
            (abs(reverse_midpoint(n) - limit) for n in range(n0, maximum + 1)),
            default=Fraction(0),
        )
        rectangle_max = max(
            (abs(observable(n, m) - limit) for n in range(n0, maximum + 1) for m in range(m0, maximum + 1)),
            default=Fraction(0),
        )
        check(rows, f"epsilon {epsilon} positive", epsilon > 0, str(epsilon), ">0")
        check(rows, f"forward cutoff tail {epsilon}", forward_cutoff_max < half, str(forward_cutoff_max), f"<{half}")
        check(rows, f"forward volume tail {epsilon}", forward_volume_max < half, str(forward_volume_max), f"<{half}")
        check(rows, f"reverse volume tail {epsilon}", reverse_volume_max < half, str(reverse_volume_max), f"<{half}")
        check(rows, f"reverse cutoff tail {epsilon}", reverse_cutoff_max < half, str(reverse_cutoff_max), f"<{half}")
        check(rows, f"forward rectangle {epsilon}", rectangle_max < epsilon, str(rectangle_max), f"<{epsilon}")
        check(rows, f"reverse rectangle {epsilon}", rectangle_max < epsilon, str(rectangle_max), f"<{epsilon}")
        records.append(
            {
                "epsilon": str(epsilon),
                "half": str(half),
                "cutoff_threshold": n0,
                "volume_threshold": m0,
                "forward_cutoff_max": str(forward_cutoff_max),
                "forward_volume_max": str(forward_volume_max),
                "reverse_volume_max": str(reverse_volume_max),
                "reverse_cutoff_max": str(reverse_cutoff_max),
                "rectangle_max": str(rectangle_max),
            }
        )
    check(rows, "manifest identity", manifest["result_id"] == "R-474" and manifest["exploration_id"] == "EXP-001353", [manifest["result_id"], manifest["exploration_id"]], ["R-474", "EXP-001353"])
    check(rows, "claim and tier firewall", manifest["claim_bearing"] is False and manifest["tier"] == "T0", [manifest["claim_bearing"], manifest["tier"]], [False, "T0"])
    for name, authority in manifest.get("authorities", {}).items():
        path = REPO / authority["path"]
        actual_hash = digest(path) if path.is_file() else None
        check(rows, f"authority hash {name}", actual_hash == authority["sha256"], actual_hash, authority["sha256"])
    check(rows, "strict geometric bases", cutoff_base > 1 and volume_base > 1, [cutoff_base, volume_base], ">1")
    check(rows, "method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")
    check(rows, "downstream firewalls", all(not value for key, value in manifest["scope"].items() if key.endswith("_closed") and key in {"source_owned_functional_closed", "source_owned_dynamics_closed", "common_core_closed", "common_norm_closed", "uniform_cutoff_bound_closed", "uniform_volume_bound_closed", "ordered_limit_closed", "physical_sector_closed", "continuum_closed", "pre_a_closed", "sector_a_closed", "qft_yang_mills_closed"}), "all false", "all false")
    derived = {
        "limit": str(limit),
        "cutoff_base": cutoff_base,
        "volume_base": volume_base,
        "epsilon_split_denominator": split,
        "rows": records,
        "forward_rectangle_closed": True,
        "reverse_rectangle_closed": True,
        "actual_owner_uniformity": False,
        "ordered_limit_closed": False,
    }
    return derived, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = load(MANIFEST)
    rows: list[dict[str, Any]] = []
    try:
        derived, rows = core(manifest)
        payload = {
            "schema": "tect/r474-ordered-limit-rectangle-primary/1.0",
            "run_kind": "primary",
            "audit_id": "R474-ORDERED-LIMIT-RECTANGLE-PRIMARY-v1",
            "result_id": "R-474",
            "exploration_id": "EXP-001353",
            "claim_id": "C6-SPACETIME-SIGNATURE",
            "task_id": "T-054",
            "tier": "T0",
            "claim_bearing": False,
            "verdict": "PASS",
            "assertions": rows,
            "assertion_summary": {"passed": len(rows), "total": len(rows)},
            "derived": derived,
            "source_hashes": {"manifest": digest(MANIFEST), "primary": digest(Path(__file__))},
            "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "evidence_level": manifest["evidence_level"],
            "assumptions": manifest["assumptions"],
            "missing_assumptions": manifest["missing_assumptions"],
            "non_claims": manifest["non_claims"],
            "boundary": manifest["boundary"],
        }
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"R-474 PRIMARY: FAIL ({error})")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, args.output)
    print(f"R-474 PRIMARY: PASS ({len(rows)}/{len(rows)} assertions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
