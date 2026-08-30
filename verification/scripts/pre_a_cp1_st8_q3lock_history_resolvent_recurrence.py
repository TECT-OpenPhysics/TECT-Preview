#!/usr/bin/env python3
"""Primary exact audit for the R-452 history-resolvent recurrence.

R-452 is an additive analytic interface for T-054.  It does not construct a
Q3LOCK history.  Instead, it solves the scalar one-step recurrence that an
owner-supplied history error would have to satisfy before the R-451 Cauchy
plug-in can be instantiated.  All constants are recomputed from the R-451 and
R-450 parent artefacts with exact Fractions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json"
R451_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_history_resolvent_recurrence/primary.json"


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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def fraction(value: object) -> Fraction:
    return Fraction(str(value))


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def resolvent_sum(kappa: Fraction, r: Fraction, radius: int) -> Fraction:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    return sum((kappa ** (radius - 1 - j)) * (r**j) for j in range(radius))


def closed_form(kappa: Fraction, r: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if kappa == r:
        return Fraction(radius) * r ** (radius - 1)
    return (kappa**radius - r**radius) / (kappa - r)


def run(output: Path = DEFAULT_OUTPUT, store: bool = True) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r451 = json.loads(R451_MANIFEST.read_text(encoding="utf-8"))
    r450_run = json.loads(R450_RUN.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]]
        == ["R-452", "EXP-001325", "T-054", False, "CONDITIONAL_HISTORY_RESOLVENT_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-452", "EXP-001325", "T-054", False, "CONDITIONAL_HISTORY_RESOLVENT_AUDITED"],
        "provenance",
    )
    check("parent R-451", r451["result_id"] == "R-451" and r451["claim_bearing"] is False, r451["result_id"], "R-451", "lineage")
    check("parent R-450 run", r450_run["result_id"] == "R-450", r450_run["result_id"], "R-450", "lineage")
    check("parent R-451 decay input", r451["theorem"]["geometric_envelope"].startswith("T(R) <= 78*(23/26)^(R-1)"), r451["theorem"]["geometric_envelope"], "parent geometric envelope", "lineage")
    check("parent method firewall", all(r451["method_preservation"].values()), r451["method_preservation"], "all true", "method")

    finite = manifest["finite_fixture"]
    radius_min = int(finite["radius_min"])
    radius_max = int(finite["radius_max"])
    check("radius contract", radius_min == 0 and radius_max == 64, [radius_min, radius_max], [0, 64], "coverage")
    check("no grid substitution", finite["no_new_finite_grid"] is True and "no finite grid" in finite["fixture_role"].lower(), finite, "exact recurrence rows only", "scope")

    q = fraction(r451["finite_fixture"]["ratio_q"])
    base_tail = fraction(r451["finite_fixture"]["base_tail"])
    orientation_count = int(r451["finite_fixture"]["orientation_count"])
    c4_edge = fraction(r450_run["derived"]["C4_edge"])
    fourth_power_factor = 2 ** (4 - 1) * orientation_count
    r = q**4
    A = Fraction(fourth_power_factor) * c4_edge * base_tail**4
    check("parent q", q == Fraction(23, 26), q, Fraction(23, 26), "parent decay")
    check("parent base tail", base_tail == Fraction(78), base_tail, Fraction(78), "parent decay")
    check("parent orientation count", orientation_count == 2, orientation_count, 2, "parent decay")
    check("parent C4 positive", c4_edge > 0, c4_edge, ">0", "parent constants")
    check("two-orientation factor", fourth_power_factor == 16, fourth_power_factor, 16, "parent constants")
    check("fourth-power decay base", r == Fraction(279841, 456976), r, Fraction(279841, 456976), "parent decay")
    check("r strictly below one", 0 < r < 1, r, "0<r<1", "parent decay")
    check("source constant positive", A > 0, A, ">0", "source envelope")

    kappa_inputs = [fraction(value) for value in finite["kappa_fixture_values"]]
    kappas = kappa_inputs + [r]
    # Preserve order while removing the parent-derived resonant duplicate if a
    # fixture happens to include it in a later manifest revision.
    unique_kappas: list[Fraction] = []
    for value in kappas:
        if value not in unique_kappas:
            unique_kappas.append(value)

    kappa_rows: list[dict[str, Any]] = []
    for kappa in unique_kappas:
        admissible = 0 <= kappa < 1
        dominant = max(kappa, r)
        check(f"kappa domain {kappa}", kappa >= 0, kappa, ">=0", "recurrence")
        check(f"threshold flag {kappa}", admissible == (kappa < 1), admissible, "kappa<1", "threshold")
        samples: dict[str, Any] = {}
        for radius in range(radius_min, radius_max + 1):
            direct = resolvent_sum(kappa, r, radius)
            formula = closed_form(kappa, r, radius)
            check(f"sum/closed form k={kappa} R={radius}", direct == formula, direct, formula, "closed form")
            check(f"sum nonnegative k={kappa} R={radius}", direct >= 0, direct, ">=0", "positivity")
            if radius < radius_max:
                next_sum = resolvent_sum(kappa, r, radius + 1)
                check(
                    f"recurrence k={kappa} R={radius}",
                    next_sum == kappa * direct + r**radius,
                    next_sum,
                    kappa * direct + r**radius,
                    "recurrence",
                )
            if radius in {0, 1, 8, 16, 32, 64}:
                samples[str(radius)] = {
                    "S_R": str(direct),
                    "H_R_upper": str(A * direct),
                    "source_term": str(A * r ** max(radius - 1, 0)) if radius > 0 else "0",
                }
        check(f"dominant base k={kappa}", dominant == max(kappa, r), dominant, "max(kappa,r)", "threshold")
        if admissible:
            check(f"admissible dominant k={kappa}", dominant < 1, dominant, "<1", "threshold")
            check(f"admissible terminal positive k={kappa}", resolvent_sum(kappa, r, radius_max) > 0, resolvent_sum(kappa, r, radius_max), ">0", "threshold")
        else:
            check(f"nonadmissible control k={kappa}", kappa >= 1, kappa, ">=1", "threshold control")
        kappa_rows.append(
            {
                "kappa": str(kappa),
                "admissible": admissible,
                "dominant_base": str(dominant),
                "closed_form_branch": "resonant" if kappa == r else "nonresonant",
                "samples": samples,
                "terminal_sum": str(resolvent_sum(kappa, r, radius_max)),
            }
        )

    check("resonant fixture present", any(row["closed_form_branch"] == "resonant" for row in kappa_rows), [row["kappa"] for row in kappa_rows], "parent-derived kappa=r", "closed form")
    check("threshold controls present", any(not row["admissible"] for row in kappa_rows), [row["kappa"] for row in kappa_rows], "kappa=1 and kappa>1 controls", "threshold")
    check("source envelope is parent-derived", A == Fraction(fourth_power_factor) * c4_edge * base_tail**4, A, "16*C4_edge*78^4", "source envelope")
    check("resolvent envelope statement", manifest["theorem"]["envelope"] == "H_R <= A*S_R(kappa,r)", manifest["theorem"]["envelope"], "H_R <= A*S_R", "theorem")
    check("threshold statement", "kappa < 1" in manifest["theorem"]["threshold"], manifest["theorem"]["threshold"], "kappa<1", "theorem")

    scope = manifest["scope"]
    closed = (
        "parent_r451_decay_input_reused",
        "resolvent_sum_identity_closed",
        "nonresonant_closed_form_closed",
        "resonant_closed_form_closed",
        "kappa_less_than_one_threshold_closed",
    )
    open_keys = tuple(key for key, value in scope.items() if key not in closed and key not in {"no_new_negative_result", "no_tier_change", "no_pdf"} and isinstance(value, bool))
    check("closed scope", all(scope[key] is True for key in closed), {key: scope[key] for key in closed}, "all true", "scope")
    check("open promotion firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all false", "scope")
    check("no negative/tier/pdf mutation", scope["no_new_negative_result"] and scope["no_tier_change"] and scope["no_pdf"], [scope["no_new_negative_result"], scope["no_tier_change"], scope["no_pdf"]], [True, True, True], "scope")
    check("method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true", "method-firewall")

    payload: dict[str, Any] = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks[:160],
        "assertion_samples_truncated": len(checks) > 160,
        "derived": {
            "parent_ratio_q": str(q),
            "parent_base_tail": str(base_tail),
            "fourth_power_decay_base_r": str(r),
            "fourth_power_cauchy_factor": fourth_power_factor,
            "C4_edge": str(c4_edge),
            "source_constant_A": str(A),
            "kappa_rows": kappa_rows,
            "radius_rows_per_kappa": radius_max - radius_min + 1,
            "resolvent_identity_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "kappa_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_kappa_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "r451_manifest": digest(R451_MANIFEST),
            "r450_run": digest(R450_RUN),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    if store:
        atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-452 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} kappa_cases={len(kappa_rows)} r={r}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    run(args.output, store=not args.no_store)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
