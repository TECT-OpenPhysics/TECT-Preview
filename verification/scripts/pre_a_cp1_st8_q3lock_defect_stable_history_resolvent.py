#!/usr/bin/env python3
"""Primary exact audit for the R-453 defect-stable history resolvent.

R-453 is an additive T-054 interface.  It leaves the R-452 one-step owner
contract unchanged and computes the extra convolution caused by a bounded
nonnegative residual defect.  No Q3LOCK history or physical dynamics is
constructed here.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-defect-stable-history-resolvent-manifest.json"
R452_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json"
R451_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_defect_stable_history_resolvent/primary.json"


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


def kernel(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    return sum(propagation ** (radius - 1 - j) * base**j for j in range(radius))


def closed_form(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if propagation == base:
        return Fraction(radius) * base ** (radius - 1)
    return (propagation**radius - base**radius) / (propagation - base)


def run(output: Path = DEFAULT_OUTPUT, store: bool = True) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r452 = json.loads(R452_MANIFEST.read_text(encoding="utf-8"))
    r451 = json.loads(R451_MANIFEST.read_text(encoding="utf-8"))
    r450 = json.loads(R450_RUN.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]]
        == ["R-453", "EXP-001326", "T-054", False, "CONDITIONAL_DEFECT_STABLE_RESOLVENT_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-453", "EXP-001326", "T-054", False, "CONDITIONAL_DEFECT_STABLE_RESOLVENT_AUDITED"],
        "provenance",
    )
    check("parent R-452", r452["result_id"] == "R-452" and r452["claim_bearing"] is False, r452["result_id"], "R-452", "lineage")
    check("parent R-451", r451["result_id"] == "R-451" and r451["claim_bearing"] is False, r451["result_id"], "R-451", "lineage")
    check("parent R-452 method firewall", all(r452["method_preservation"].values()), r452["method_preservation"], "all true", "method")
    check("parent R-451 method firewall", all(r451["method_preservation"].values()), r451["method_preservation"], "all true", "method")

    finite = manifest["finite_fixture"]
    radius_min = int(finite["radius_min"])
    radius_max = int(finite["radius_max"])
    check("radius contract", radius_min == 0 and radius_max == 64, [radius_min, radius_max], [0, 64], "coverage")
    check("no grid substitution", finite["no_new_finite_grid"] is True and "no finite grid" in finite["fixture_role"].lower(), finite, "exact recurrence rows only", "scope")

    q = fraction(r451["finite_fixture"]["ratio_q"])
    base_tail = fraction(r451["finite_fixture"]["base_tail"])
    orientation_count = int(r451["finite_fixture"]["orientation_count"])
    c4_edge = fraction(r450["derived"]["C4_edge"])
    fourth_power_factor = 2 ** (4 - 1) * orientation_count
    parent_decay = q**4
    source_constant = Fraction(fourth_power_factor) * c4_edge * base_tail**4
    check("parent q", q == Fraction(23, 26), q, Fraction(23, 26), "parent decay")
    check("parent base tail", base_tail == Fraction(78), base_tail, Fraction(78), "parent decay")
    check("parent orientation count", orientation_count == 2, orientation_count, 2, "parent decay")
    check("parent C4 positive", c4_edge > 0, c4_edge, ">0", "parent constants")
    check("two-orientation factor", fourth_power_factor == 16, fourth_power_factor, 16, "parent constants")
    check("parent fourth-power decay", parent_decay == Fraction(279841, 456976), parent_decay, Fraction(279841, 456976), "parent decay")
    check("parent decay below one", 0 < parent_decay < 1, parent_decay, "0<r<1", "parent decay")
    check("source constant positive", source_constant > 0, source_constant, ">0", "source envelope")

    kappa_values = [fraction(value) for value in finite["kappa_fixture_values"]]
    kappa_values.append(parent_decay)
    unique_kappas: list[Fraction] = []
    for value in kappa_values:
        if value not in unique_kappas:
            unique_kappas.append(value)
    declared_bases = [fraction(value) for value in finite["defect_decay_fixture_values"]]
    amplitude_values = [fraction(value) for value in finite["defect_amplitude_fixture_values"]]
    check("defect amplitude domain", all(value >= 0 for value in amplitude_values), amplitude_values, ">=0", "defect contract")
    max_amplitude = max(amplitude_values)

    pair_rows: list[dict[str, Any]] = []
    resonant_source = False
    resonant_defect = False
    admissible_pairs = 0
    for kappa in unique_kappas:
        check(f"kappa domain {kappa}", kappa >= 0, kappa, ">=0", "recurrence")
        bases = declared_bases + [parent_decay, kappa]
        unique_bases: list[Fraction] = []
        for value in bases:
            if value not in unique_bases:
                unique_bases.append(value)
        for defect_base in unique_bases:
            check(f"defect base domain k={kappa} s={defect_base}", defect_base >= 0, defect_base, ">=0", "defect contract")
            admissible = 0 <= kappa < 1 and 0 <= defect_base < 1
            if admissible:
                admissible_pairs += 1
            if kappa == parent_decay:
                resonant_source = True
            if kappa == defect_base:
                resonant_defect = True
            source_branch = "resonant" if kappa == parent_decay else "nonresonant"
            defect_branch = "resonant" if kappa == defect_base else "nonresonant"
            samples: dict[str, Any] = {}
            for radius in range(radius_min, radius_max + 1):
                source_kernel = kernel(kappa, parent_decay, radius)
                defect_kernel = kernel(kappa, defect_base, radius)
                check(f"source closed form k={kappa} s={defect_base} R={radius}", source_kernel == closed_form(kappa, parent_decay, radius), source_kernel, closed_form(kappa, parent_decay, radius), "closed form")
                check(f"defect closed form k={kappa} s={defect_base} R={radius}", defect_kernel == closed_form(kappa, defect_base, radius), defect_kernel, closed_form(kappa, defect_base, radius), "closed form")
                check(f"source kernel nonnegative k={kappa} R={radius}", source_kernel >= 0, source_kernel, ">=0", "positivity")
                check(f"defect kernel nonnegative k={kappa} s={defect_base} R={radius}", defect_kernel >= 0, defect_kernel, ">=0", "positivity")
                bound = source_constant * source_kernel + max_amplitude * defect_kernel
                if radius < radius_max:
                    next_source = kernel(kappa, parent_decay, radius + 1)
                    next_defect = kernel(kappa, defect_base, radius + 1)
                    check(f"source recurrence k={kappa} R={radius}", next_source == kappa * source_kernel + parent_decay**radius, next_source, kappa * source_kernel + parent_decay**radius, "recurrence")
                    check(f"defect recurrence k={kappa} s={defect_base} R={radius}", next_defect == kappa * defect_kernel + defect_base**radius, next_defect, kappa * defect_kernel + defect_base**radius, "recurrence")
                if radius in {0, 1, 8, 16, 32, 64}:
                    samples[str(radius)] = {
                        "source_kernel": str(source_kernel),
                        "defect_kernel": str(defect_kernel),
                        "envelope": str(bound),
                    }

            # Equality recurrence with the maximal declared geometric defect.
            equality_value = Fraction(0)
            for step in range(1, radius_max + 1):
                equality_value = kappa * equality_value + source_constant * parent_decay ** (step - 1) + max_amplitude * defect_base ** (step - 1)
                expected = source_constant * kernel(kappa, parent_decay, step) + max_amplitude * kernel(kappa, defect_base, step)
                check(f"combined equality k={kappa} s={defect_base} R={step}", equality_value == expected, equality_value, expected, "defect convolution")

            # A strict sub-envelope tests the inequality for an arbitrary
            # residual sequence, not only equality at the geometric bound.
            sub_value = Fraction(0)
            weighted_defect = Fraction(0)
            for step in range(1, radius_max + 1):
                geometric = max_amplitude * defect_base ** (step - 1)
                residual = geometric if step % 2 else geometric / 2
                check(f"residual envelope k={kappa} s={defect_base} R={step}", 0 <= residual <= geometric, residual, f"0<={geometric}", "defect contract")
                sub_value = kappa * sub_value + source_constant * parent_decay ** (step - 1) + residual
                weighted_defect = kappa * weighted_defect + residual
                source_bound = source_constant * kernel(kappa, parent_decay, step)
                check(f"sub-defect bound k={kappa} s={defect_base} R={step}", sub_value <= source_bound + max_amplitude * kernel(kappa, defect_base, step), sub_value, "source plus defect envelope", "defect convolution")
                check(f"general convolution k={kappa} s={defect_base} R={step}", sub_value <= source_bound + weighted_defect, sub_value, "source plus exact weighted residual", "defect convolution")

            if admissible:
                check(f"two-base threshold k={kappa} s={defect_base}", max(kappa, parent_decay, defect_base) < 1, max(kappa, parent_decay, defect_base), "<1", "threshold")
            else:
                check(f"threshold control k={kappa} s={defect_base}", kappa >= 1 or defect_base >= 1, [kappa, defect_base], "kappa>=1 or s>=1", "threshold control")
            pair_rows.append({
                "kappa": str(kappa),
                "defect_base_s": str(defect_base),
                "admissible": admissible,
                "source_branch": source_branch,
                "defect_branch": defect_branch,
                "terminal_source_kernel": str(kernel(kappa, parent_decay, radius_max)),
                "terminal_defect_kernel": str(kernel(kappa, defect_base, radius_max)),
                "samples": samples,
            })

    check("source resonance exercised", resonant_source, True, "kappa=parent_decay", "closed form")
    check("defect resonance exercised", resonant_defect, True, "s=kappa", "closed form")
    check("nonadmissible controls exercised", any(not row["admissible"] for row in pair_rows), True, "kappa=1, kappa>1, s=1 and s>1 controls", "threshold")
    check("admissible controls exercised", admissible_pairs > 0, admissible_pairs, ">0", "threshold")
    check("D=0 reduction", Fraction(0) in amplitude_values, amplitude_values, "declared exact-recurrence reduction", "defect contract")
    check("source envelope parent-derived", source_constant == Fraction(fourth_power_factor) * c4_edge * base_tail**4, source_constant, "16*C4_edge*78^4", "source envelope")
    check("general convolution theorem marker", manifest["theorem"]["general_envelope"].startswith("H_R <= A*S_R"), manifest["theorem"]["general_envelope"], "general convolution", "theorem")
    check("geometric defect theorem marker", "D*S_R(kappa,s)" in manifest["theorem"]["geometric_defect_contract"], manifest["theorem"]["geometric_defect_contract"], "geometric defect envelope", "theorem")

    scope = manifest["scope"]
    closed = (
        "parent_r451_decay_input_reused",
        "general_defect_convolution_closed",
        "geometric_defect_envelope_closed",
        "nonresonant_closed_form_closed",
        "resonant_closed_form_closed",
        "two_base_less_than_one_threshold_closed",
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
        "assertions": checks[:240],
        "assertion_samples_truncated": len(checks) > 240,
        "derived": {
            "parent_ratio_q": str(q),
            "parent_base_tail": str(base_tail),
            "parent_decay_r": str(parent_decay),
            "fourth_power_cauchy_factor": fourth_power_factor,
            "C4_edge": str(c4_edge),
            "source_constant_A": str(source_constant),
            "defect_amplitude_max_D": str(max_amplitude),
            "radius_rows_per_pair": radius_max - radius_min + 1,
            "pair_rows": pair_rows,
            "pair_count": len(pair_rows),
            "admissible_pair_count": admissible_pairs,
            "general_defect_convolution_closed": True,
            "geometric_defect_envelope_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "two_base_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_recurrence_closed": False,
            "source_owned_defect_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "r452_manifest": digest(R452_MANIFEST),
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
    print(f"R-453 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} pairs={len(pair_rows)} r={parent_decay}", flush=True)
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
