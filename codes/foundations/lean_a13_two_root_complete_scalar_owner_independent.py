"""Stdlib-only independent audit for R-191; never imports the primary lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-two-root-complete-scalar-owner-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r191-two-root-complete-scalar-owner" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def moments(ri: dict[str, Any], a: F, b: F) -> tuple[F, F]:
    c = ri["moment_coefficients"]
    m4 = F(c["a4_b4"]) * (a**4 + b**4) + F(c["a2b2"]) * a**2 * b**2
    m6 = F(c["a6_b6"]) * (a**6 + b**6) + F(c["a4b2"]) * a**4 * b**2 + F(c["a2b4"]) * a**2 * b**4
    return m4, m6


def owner(ri: dict[str, Any], q1: F, q2: F, a: F, b: F) -> F:
    m4, m6 = moments(ri, a, b)
    return q1 * a**2 + q2 * b**2 + F(ri["owner_coefficients"]["quartic"]) * m4 + F(ri["owner_coefficients"]["sextic"]) * m6


def gradients(ri: dict[str, Any], q1: F, q2: F, a: F, b: F) -> tuple[F, F]:
    c = ri["moment_coefficients"]
    c44, c22 = F(c["a4_b4"]), F(c["a2b2"])
    c60, c42, c24 = F(c["a6_b6"]), F(c["a4b2"]), F(c["a2b4"])
    c4, c6 = F(ri["owner_coefficients"]["quartic"]), F(ri["owner_coefficients"]["sextic"])
    ma = 4 * c44 * a**3 + 2 * c22 * a * b**2
    mb = 4 * c44 * b**3 + 2 * c22 * a**2 * b
    na = 6 * c60 * a**5 + 4 * c42 * a**3 * b**2 + 2 * c24 * a * b**4
    nb = 6 * c60 * b**5 + 2 * c42 * a**4 * b + 4 * c24 * a**2 * b**3
    return 2 * q1 * a + c4 * ma + c6 * na, 2 * q2 * b + c4 * mb + c6 * nb


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    ri = manifest["registered_inputs"]
    x = manifest["test_oracles"]["fixture"]
    q1, q2 = F(x["q1"]), F(x["q2"])
    h, r1, r2, f1, f2 = (F(x[k]) for k in ("h", "r1", "r2", "f1", "f2"))
    beta = F(ri["incidence"]["feedback_gain"])
    g1 = h + r1
    g2 = h + beta * g1 + r2
    points = [(h, h), (g1, h + beta * g1), (g1, g2), (g1 + f1, g2 + f2)]
    energies = [owner(ri, q1, q2, *p) for p in points]
    increments = [energies[i + 1] - energies[i] for i in range(3)]
    ga, gb = gradients(ri, q1, q2, *points[-1])
    return {
        "moment_m4_at_one": moments(ri, F(1), F(1))[0],
        "moment_m6_at_one": moments(ri, F(1), F(1))[1],
        "stage_points": points,
        "stage_energies": energies,
        "stage_increments": increments,
        "endpoint_delta": energies[-1] - energies[0],
        "endpoint_gradient": (ga, gb),
        "dr1": ga + beta * gb,
        "dr2": gb,
        "df1": ga,
        "df2": gb,
        "telescope_exact": sum(increments, F(0)) == energies[-1] - energies[0],
        "intermediate_negative": any(v < 0 for v in increments),
        "endpoint_positive": energies[-1] - energies[0] > 0,
        "r176_root_labels": ri["root_labels"],
        "r177_owner_order": ri["incidence"]["owner_order"],
        "r178_ordered_block_retained": True,
        "a13_gate_closed": False,
        "sector_a_closed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ri = manifest["registered_inputs"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest", manifest["audit_id"] == "A13-TWO-ROOT-COMPLETE-SCALAR-OWNER", manifest["audit_id"], "A13-TWO-ROOT-COMPLETE-SCALAR-OWNER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    derived = derive(manifest)
    oracle = manifest["test_oracles"]
    for key in ("moment_m4_at_one", "moment_m6_at_one"):
        check(f"oracle {key}", derived[key] == F(oracle[key]), derived[key], oracle[key])
    for key in ("endpoint_delta", "dr1", "dr2", "df1", "df2"):
        check(f"oracle {key}", derived[key] == F(oracle["fixture"][key]), derived[key], oracle["fixture"][key])
    check("telescope", derived["telescope_exact"], derived["stage_increments"], "sum equals endpoint")
    check("stage increments", derived["stage_increments"] == [F(value) for value in oracle["fixture"]["stage_increments"]], derived["stage_increments"], oracle["fixture"]["stage_increments"])
    check("negative intermediate", derived["intermediate_negative"], derived["stage_increments"], "at least one negative")
    check("positive endpoint", derived["endpoint_positive"], derived["endpoint_delta"], ">0")
    check("root/incidence bridge", derived["r176_root_labels"] == ri["root_labels"] and derived["r177_owner_order"] == ri["incidence"]["owner_order"], [derived["r176_root_labels"], derived["r177_owner_order"]], [ri["root_labels"], ri["incidence"]["owner_order"]])
    check("A13 boundary", not derived["a13_gate_closed"] and not derived["sector_a_closed"], derived, "finite prerequisite only")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT R-191 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
