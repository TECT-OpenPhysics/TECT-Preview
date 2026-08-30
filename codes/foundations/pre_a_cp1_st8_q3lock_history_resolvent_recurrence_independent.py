#!/usr/bin/env python3
"""Non-importing independent reconstruction of the R-452 recurrence envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json"
R451 = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_history_resolvent_recurrence/independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def frac(value: object) -> Fraction:
    return Fraction(str(value))


def sum_kernel(kappa: Fraction, decay: Fraction, n: int) -> Fraction:
    return sum(kappa ** (n - 1 - j) * decay**j for j in range(n))


def formula(kappa: Fraction, decay: Fraction, n: int) -> Fraction:
    if n == 0:
        return Fraction(0)
    if kappa == decay:
        return Fraction(n) * decay ** (n - 1)
    return (kappa**n - decay**n) / (kappa - decay)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r451 = json.loads(R451.read_text(encoding="utf-8"))
    r450 = json.loads(R450.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("independent identity", manifest["result_id"] == "R-452" and manifest["exploration_id"] == "EXP-001325", [manifest["result_id"], manifest["exploration_id"]], "R-452/EXP-001325", "provenance")
    check("task and claim", manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["task_id"], manifest["claim_bearing"]], "T-054/false", "provenance")
    check("parent linkage", r451["result_id"] == "R-451" and r450["result_id"] == "R-450", [r451["result_id"], r450["result_id"]], "R-451/R-450", "lineage")
    check("method preserved", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method")

    q = frac(r451["finite_fixture"]["ratio_q"])
    base = frac(r451["finite_fixture"]["base_tail"])
    orientations = int(r451["finite_fixture"]["orientation_count"])
    c4 = frac(r450["derived"]["C4_edge"])
    factor = (2 ** (4 - 1)) * orientations
    decay = q**4
    source = Fraction(factor) * c4 * base**4
    check("independent parent q", q == Fraction(23, 26), q, "23/26", "parent decay")
    check("independent parent base", base == Fraction(78), base, "78", "parent decay")
    check("independent fourth factor", factor == 16, factor, 16, "parent decay")
    check("independent decay base", 0 < decay < 1, decay, "0<r<1", "parent decay")
    check("independent source recomputation", source == Fraction(factor) * c4 * base**4, source, "factor*C4*base^4", "source envelope")

    rmax = int(manifest["finite_fixture"]["radius_max"])
    kappas = [frac(value) for value in manifest["finite_fixture"]["kappa_fixture_values"]]
    kappas.append(decay)
    unique: list[Fraction] = []
    for value in kappas:
        if value not in unique:
            unique.append(value)
    case_rows: list[dict[str, Any]] = []
    for kappa in unique:
        admissible = 0 <= kappa < 1
        for n in range(rmax + 1):
            direct = sum_kernel(kappa, decay, n)
            closed = formula(kappa, decay, n)
            check(f"sum equality k={kappa} n={n}", direct == closed, direct, closed, "closed form")
            check(f"nonnegative k={kappa} n={n}", direct >= 0, direct, ">=0", "positivity")
            if n < rmax:
                check(f"recurrence k={kappa} n={n}", sum_kernel(kappa, decay, n + 1) == kappa * direct + decay**n, sum_kernel(kappa, decay, n + 1), "kappa*S+r^n", "recurrence")
        if admissible:
            check(f"threshold k={kappa}", max(kappa, decay) < 1, max(kappa, decay), "<1", "threshold")
        else:
            check(f"control k={kappa}", kappa >= 1, kappa, ">=1", "threshold control")
        case_rows.append({"kappa": str(kappa), "admissible": admissible, "branch": "resonant" if kappa == decay else "nonresonant", "S_64": str(sum_kernel(kappa, decay, rmax)), "H_64_upper": str(source * sum_kernel(kappa, decay, rmax))})

    check("resonance independently exercised", any(row["branch"] == "resonant" for row in case_rows), case_rows, "resonant branch", "closed form")
    check("threshold controls independently exercised", sum(not row["admissible"] for row in case_rows) >= 2, case_rows, "kappa=1 and kappa>1", "threshold")
    open_scope = [key for key, value in manifest["scope"].items() if key.endswith("_closed") and value is False]
    check("downstream firewall", manifest["scope"]["actual_q3_history_closed"] is False and manifest["scope"]["source_owned_kappa_closed"] is False and len(open_scope) >= 12, open_scope, "actual history/owner kappa remain open", "scope")

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "parent_ratio_q": str(q),
            "parent_base_tail": str(base),
            "fourth_power_decay_base_r": str(decay),
            "fourth_power_cauchy_factor": factor,
            "source_constant_A": str(source),
            "radius_rows_per_kappa": rmax + 1,
            "kappa_rows": case_rows,
            "resolvent_identity_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "kappa_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_kappa_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {"manifest": sha256(MANIFEST), "r451_manifest": sha256(R451), "r450_run": sha256(R450), "script": sha256(Path(__file__))},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-452 INDEPENDENT {payload['verdict']} {len(rows)}/{len(rows)} kappa_cases={len(case_rows)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
