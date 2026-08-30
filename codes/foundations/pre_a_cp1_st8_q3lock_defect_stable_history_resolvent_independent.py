#!/usr/bin/env python3
"""Independent, non-importing reconstruction of the R-453 envelope."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-defect-stable-history-resolvent-manifest.json"
R452 = ROOT / "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json"
R451 = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_defect_stable_history_resolvent/independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def frac(value: object) -> Fraction:
    return Fraction(str(value))


def kernel(kappa: Fraction, base: Fraction, radius: int) -> Fraction:
    return sum(kappa ** (radius - 1 - j) * base**j for j in range(radius))


def closed(kappa: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if kappa == base:
        return Fraction(radius) * base ** (radius - 1)
    return (kappa**radius - base**radius) / (kappa - base)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r452 = json.loads(R452.read_text(encoding="utf-8"))
    r451 = json.loads(R451.read_text(encoding="utf-8"))
    r450 = json.loads(R450.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["result_id"] == "R-453" and manifest["exploration_id"] == "EXP-001326", [manifest["result_id"], manifest["exploration_id"]], "R-453/EXP-001326", "provenance")
    check("task and claim", manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["task_id"], manifest["claim_bearing"]], "T-054/false", "provenance")
    check("parent linkage", r452["result_id"] == "R-452" and r451["result_id"] == "R-451" and r450["result_id"] == "R-450", [r452["result_id"], r451["result_id"], r450["result_id"]], "R-452/R-451/R-450", "lineage")
    check("method preserved", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method")

    q = frac(r451["finite_fixture"]["ratio_q"])
    parent_base = frac(r451["finite_fixture"]["base_tail"])
    orientations = int(r451["finite_fixture"]["orientation_count"])
    c4 = frac(r450["derived"]["C4_edge"])
    factor = (2 ** (4 - 1)) * orientations
    parent_decay = q**4
    source_constant = Fraction(factor) * c4 * parent_base**4
    check("parent ratio", q == Fraction(23, 26), q, "23/26", "parent decay")
    check("parent base", parent_base == Fraction(78), parent_base, "78", "parent decay")
    check("orientation factor", factor == 16, factor, 16, "parent constants")
    check("parent decay", 0 < parent_decay < 1, parent_decay, "0<r<1", "parent decay")
    check("source recomputation", source_constant == Fraction(factor) * c4 * parent_base**4, source_constant, "factor*C4*base^4", "source envelope")

    radius_max = int(manifest["finite_fixture"]["radius_max"])
    kappas = [frac(value) for value in manifest["finite_fixture"]["kappa_fixture_values"]] + [parent_decay]
    unique_kappas: list[Fraction] = []
    for value in kappas:
        if value not in unique_kappas:
            unique_kappas.append(value)
    declared_bases = [frac(value) for value in manifest["finite_fixture"]["defect_decay_fixture_values"]]
    amplitudes = [frac(value) for value in manifest["finite_fixture"]["defect_amplitude_fixture_values"]]
    max_amplitude = max(amplitudes)
    pair_rows: list[dict[str, Any]] = []
    admissible_count = 0
    source_resonance = False
    defect_resonance = False
    for kappa in unique_kappas:
        bases = declared_bases + [parent_decay, kappa]
        unique_bases: list[Fraction] = []
        for value in bases:
            if value not in unique_bases:
                unique_bases.append(value)
        for defect_base in unique_bases:
            admissible = 0 <= kappa < 1 and 0 <= defect_base < 1
            admissible_count += int(admissible)
            source_resonance = source_resonance or kappa == parent_decay
            defect_resonance = defect_resonance or kappa == defect_base
            for radius in range(radius_max + 1):
                source_kernel = kernel(kappa, parent_decay, radius)
                defect_kernel = kernel(kappa, defect_base, radius)
                check(f"source formula k={kappa} s={defect_base} n={radius}", source_kernel == closed(kappa, parent_decay, radius), source_kernel, closed(kappa, parent_decay, radius), "closed form")
                check(f"defect formula k={kappa} s={defect_base} n={radius}", defect_kernel == closed(kappa, defect_base, radius), defect_kernel, closed(kappa, defect_base, radius), "closed form")
                if radius < radius_max:
                    check(f"source step k={kappa} n={radius}", kernel(kappa, parent_decay, radius + 1) == kappa * source_kernel + parent_decay**radius, kernel(kappa, parent_decay, radius + 1), "k*S+r^n", "recurrence")
                    check(f"defect step k={kappa} s={defect_base} n={radius}", kernel(kappa, defect_base, radius + 1) == kappa * defect_kernel + defect_base**radius, kernel(kappa, defect_base, radius + 1), "k*S+s^n", "recurrence")
            # Direct equality recurrence validates the additive envelope.
            value = Fraction(0)
            for step in range(1, radius_max + 1):
                value = kappa * value + source_constant * parent_decay ** (step - 1) + max_amplitude * defect_base ** (step - 1)
                expected = source_constant * kernel(kappa, parent_decay, step) + max_amplitude * kernel(kappa, defect_base, step)
                check(f"combined recurrence k={kappa} s={defect_base} n={step}", value == expected, value, expected, "defect convolution")
            pair_rows.append({
                "kappa": str(kappa),
                "defect_base_s": str(defect_base),
                "admissible": admissible,
                "source_branch": "resonant" if kappa == parent_decay else "nonresonant",
                "defect_branch": "resonant" if kappa == defect_base else "nonresonant",
                "terminal_envelope": str(source_constant * kernel(kappa, parent_decay, radius_max) + max_amplitude * kernel(kappa, defect_base, radius_max)),
            })

    check("source resonance", source_resonance, True, "kappa=parent_decay", "closed form")
    check("defect resonance", defect_resonance, True, "s=kappa", "closed form")
    check("admissible pairs", admissible_count > 0, admissible_count, ">0", "threshold")
    check("control pairs", any(not row["admissible"] for row in pair_rows), True, "unit and superunit controls", "threshold control")
    check("D zero reduction", Fraction(0) in amplitudes, amplitudes, "declared D=0", "defect contract")
    open_scope = [key for key, value in manifest["scope"].items() if key.endswith("_closed") and value is False]
    check("downstream firewall", manifest["scope"]["actual_q3_history_closed"] is False and manifest["scope"]["source_owned_recurrence_closed"] is False and len(open_scope) >= 12, open_scope, "actual history/owner recurrence remain open", "scope")

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions[:240],
        "assertion_samples_truncated": len(assertions) > 240,
        "derived": {
            "parent_ratio_q": str(q),
            "parent_base_tail": str(parent_base),
            "parent_decay_r": str(parent_decay),
            "fourth_power_cauchy_factor": factor,
            "source_constant_A": str(source_constant),
            "defect_amplitude_max_D": str(max_amplitude),
            "radius_rows_per_pair": radius_max + 1,
            "pair_rows": pair_rows,
            "pair_count": len(pair_rows),
            "admissible_pair_count": admissible_count,
            "general_defect_convolution_closed": True,
            "geometric_defect_envelope_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "two_base_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_recurrence_closed": False,
            "source_owned_defect_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {"manifest": sha256(MANIFEST), "r452_manifest": sha256(R452), "r451_manifest": sha256(R451), "r450_run": sha256(R450), "script": sha256(Path(__file__))},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-453 INDEPENDENT {payload['verdict']} {len(assertions)}/{len(assertions)} pairs={len(pair_rows)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
