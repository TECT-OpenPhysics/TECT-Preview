#!/usr/bin/env python3
"""Non-importing independent arithmetic lane for R-474."""

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
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / "2026-08-31-independent-r474-ordered-limit-rectangle" / "independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def f(value: str | int) -> Fraction:
    return Fraction(str(value))


def first_strict(base: int, tolerance: Fraction, maximum: int) -> int:
    candidates = [index for index in range(maximum + 1) if Fraction(1, base ** (index + 1)) < tolerance]
    if not candidates:
        raise AssertionError("no threshold")
    return min(candidates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = read(MANIFEST)
    fixture = manifest["fixture"]
    limit = f(fixture["limit"])
    cb = int(fixture["cutoff_base"])
    vb = int(fixture["volume_base"])
    split = int(fixture["epsilon_split_denominator"])
    max_index = int(fixture["max_index"])
    epsilons = [f(x) for x in fixture["epsilon_values"]]
    rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for epsilon in epsilons:
        half = epsilon / split
        n0 = first_strict(cb, half, max_index)
        m0 = first_strict(vb, half, max_index)
        cutoff_tail = Fraction(1, cb ** (n0 + 1))
        volume_tail = Fraction(1, vb ** (m0 + 1))
        rectangle = cutoff_tail + volume_tail
        rows.extend(
            [
                {"name": f"epsilon {epsilon} positive", "pass": epsilon > 0, "actual": str(epsilon), "expected": ">0"},
                {"name": f"cutoff tail {epsilon}", "pass": cutoff_tail < half, "actual": str(cutoff_tail), "expected": f"<{half}"},
                {"name": f"volume tail {epsilon}", "pass": volume_tail < half, "actual": str(volume_tail), "expected": f"<{half}"},
                {"name": f"rectangle {epsilon}", "pass": rectangle < epsilon, "actual": str(rectangle), "expected": f"<{epsilon}"},
            ]
        )
        records.append({"epsilon": str(epsilon), "half": str(half), "cutoff_threshold": n0, "volume_threshold": m0, "rectangle": str(rectangle)})
    if any(not row["pass"] for row in rows):
        raise AssertionError("independent arithmetic failure")
    canonical = {"limit": str(limit), "cutoff_base": cb, "volume_base": vb, "split": split, "records": records}
    fingerprint = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    payload = {
        "schema": "tect/r474-ordered-limit-rectangle-independent/1.0",
        "run_kind": "independent",
        "audit_id": "R474-ORDERED-LIMIT-RECTANGLE-INDEPENDENT-v1",
        "result_id": "R-474",
        "exploration_id": "EXP-001353",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": "T-054",
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "PASS",
        "assertions": rows,
        "assertion_summary": {"passed": sum(row["pass"] for row in rows), "total": len(rows)},
        "core": {"canonical": canonical, "core_fingerprint": fingerprint},
        "source_hashes": {"manifest": digest(MANIFEST), "independent": digest(Path(__file__))},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
        "non_claims": manifest["non_claims"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, args.output)
    print(f"R-474 INDEPENDENT: PASS ({payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} assertions; fingerprint={fingerprint})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
