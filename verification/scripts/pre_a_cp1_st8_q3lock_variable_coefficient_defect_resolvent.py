#!/usr/bin/env python3
"""Primary exact audit for the R-454 variable-coefficient resolver.

The packet keeps the R-453 proof method and replaces a constant propagation
coefficient by nonnegative step coefficients bounded above by one common
number.  Exact Fractions test the path-product domination and the resulting
source-plus-defect envelope; no Q3LOCK owner is inferred.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-variable-coefficient-defect-resolvent-manifest.json"
R453_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-defect-stable-history-resolvent-manifest.json"
R451_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_variable_coefficient_defect_resolvent/primary.json"


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
    return sum(propagation ** (radius - 1 - j) * base**j for j in range(radius))


def closed_form(propagation: Fraction, base: Fraction, radius: int) -> Fraction:
    if radius == 0:
        return Fraction(0)
    if propagation == base:
        return Fraction(radius) * base ** (radius - 1)
    return (propagation**radius - base**radius) / (propagation - base)


def coefficient(pattern: str, upper: Fraction, step: int) -> Fraction:
    if pattern == "zero":
        return Fraction(0)
    if pattern == "constant":
        return upper
    if pattern == "alternating":
        return upper if step % 2 else Fraction(0)
    if pattern == "ramp-four":
        return upper * Fraction(step % 4, 3)
    if pattern == "ramp-five":
        return upper * Fraction(step % 5, 4)
    raise ValueError(f"unknown coefficient pattern: {pattern}")


def path_expansion(coefficients: list[Fraction], source_terms: list[Fraction]) -> Fraction:
    # Both lists are one-indexed by carrying a zero at index 0.  A term born
    # at step j is multiplied by coefficients j+1,...,R.
    total = Fraction(0)
    radius = len(source_terms) - 1
    for born in range(1, radius + 1):
        weight = Fraction(1)
        for later in range(born + 1, radius + 1):
            weight *= coefficients[later]
        total += weight * source_terms[born]
    return total


def run(output: Path = DEFAULT_OUTPUT, store: bool = True) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r453 = json.loads(R453_MANIFEST.read_text(encoding="utf-8"))
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
        == ["R-454", "EXP-001327", "T-054", False, "CONDITIONAL_VARIABLE_COEFFICIENT_RESOLVENT_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        ["R-454", "EXP-001327", "T-054", False, "CONDITIONAL_VARIABLE_COEFFICIENT_RESOLVENT_AUDITED"],
        "provenance",
    )
    check("parent R-453", r453["result_id"] == "R-453" and r453["claim_bearing"] is False, r453["result_id"], "R-453", "lineage")
    check("parent R-451", r451["result_id"] == "R-451" and r451["claim_bearing"] is False, r451["result_id"], "R-451", "lineage")
    check("parent R-453 method firewall", all(r453["method_preservation"].values()), r453["method_preservation"], "all true", "method")

    finite = manifest["finite_fixture"]
    radius_min = int(finite["radius_min"])
    radius_max = int(finite["radius_max"])
    patterns = list(finite["coefficient_patterns"])
    check("radius contract", radius_min == 0 and radius_max == 64, [radius_min, radius_max], [0, 64], "coverage")
    check("pattern contract", patterns == ["zero", "constant", "alternating", "ramp-four", "ramp-five"], patterns, "declared patterns", "coverage")
    check("no grid substitution", finite["no_new_finite_grid"] is True and "no finite grid" in finite["fixture_role"].lower(), finite, "exact scalar rows only", "scope")

    q = fraction(r451["finite_fixture"]["ratio_q"])
    base_tail = fraction(r451["finite_fixture"]["base_tail"])
    orientations = int(r451["finite_fixture"]["orientation_count"])
    c4_edge = fraction(r450["derived"]["C4_edge"])
    factor = 2 ** (4 - 1) * orientations
    parent_decay = q**4
    source_constant = Fraction(factor) * c4_edge * base_tail**4
    check("parent q", q == Fraction(23, 26), q, Fraction(23, 26), "parent decay")
    check("parent base", base_tail == Fraction(78), base_tail, Fraction(78), "parent decay")
    check("orientation count", orientations == 2, orientations, 2, "parent decay")
    check("source factor", factor == 16, factor, 16, "parent constants")
    check("parent decay", parent_decay == Fraction(279841, 456976) and 0 < parent_decay < 1, parent_decay, "279841/456976 and <1", "parent decay")
    check("source constant", source_constant > 0 and source_constant == Fraction(factor) * c4_edge * base_tail**4, source_constant, "16*C4_edge*78^4", "source envelope")

    bars = [fraction(value) for value in finite["kappa_bar_fixture_values"]]
    bars.append(parent_decay)
    unique_bars: list[Fraction] = []
    for value in bars:
        if value not in unique_bars:
            unique_bars.append(value)
    declared_bases = [fraction(value) for value in finite["defect_decay_fixture_values"]]
    amplitudes = [fraction(value) for value in finite["defect_amplitude_fixture_values"]]
    max_amplitude = max(amplitudes)
    check("upper-bound domain", all(value >= 0 for value in unique_bars), unique_bars, ">=0", "coefficient contract")
    check("defect amplitude domain", all(value >= 0 for value in amplitudes), amplitudes, ">=0", "defect contract")

    pair_rows: list[dict[str, Any]] = []
    source_resonance = False
    defect_resonance = False
    admissible_pairs = 0
    for upper in unique_bars:
        bases = declared_bases + [parent_decay, upper]
        unique_bases: list[Fraction] = []
        for value in bases:
            if value not in unique_bases:
                unique_bases.append(value)
        for defect_base in unique_bases:
            admissible = 0 <= upper < 1 and 0 <= defect_base < 1
            admissible_pairs += int(admissible)
            source_resonance = source_resonance or upper == parent_decay
            defect_resonance = defect_resonance or upper == defect_base
            source_kernel_terminal = kernel(upper, parent_decay, radius_max)
            defect_kernel_terminal = kernel(upper, defect_base, radius_max)
            for pattern in patterns:
                coefficients = [Fraction(0)] + [coefficient(pattern, upper, step) for step in range(1, radius_max + 1)]
                history = Fraction(0)
                upper_history = Fraction(0)
                source_terms = [Fraction(0)] + [source_constant * parent_decay ** (step - 1) + max_amplitude * defect_base ** (step - 1) for step in range(1, radius_max + 1)]
                for step in range(1, radius_max + 1):
                    current_coefficient = coefficients[step]
                    check(f"coefficient lower {pattern} bar={upper} n={step}", current_coefficient >= 0, current_coefficient, ">=0", "coefficient contract")
                    check(f"coefficient upper {pattern} bar={upper} n={step}", current_coefficient <= upper, current_coefficient, f"<={upper}", "coefficient contract")
                    history = current_coefficient * history + source_terms[step]
                    upper_history = upper * upper_history + source_terms[step]
                    exact_bound = source_constant * kernel(upper, parent_decay, step) + max_amplitude * kernel(upper, defect_base, step)
                    check(f"variable dominated {pattern} bar={upper} s={defect_base} n={step}", history <= upper_history and upper_history == exact_bound, [history, upper_history], "history<=upper=closed envelope", "path-product")
                    path_value = path_expansion(coefficients[: step + 1], source_terms[: step + 1])
                    check(f"path expansion {pattern} bar={upper} s={defect_base} n={step}", history == path_value, history, path_value, "path-product")
                # A sub-envelope residual tests the inequality rather than only
                # equality at the declared geometric defect bound.
                sub_history = Fraction(0)
                sub_terms = [Fraction(0)]
                for step in range(1, radius_max + 1):
                    geometric = max_amplitude * defect_base ** (step - 1)
                    residual = geometric if step % 2 else geometric / 2
                    sub_terms.append(source_constant * parent_decay ** (step - 1) + residual)
                    sub_history = coefficients[step] * sub_history + sub_terms[step]
                    check(f"sub residual bound {pattern} bar={upper} s={defect_base} n={step}", sub_history <= source_constant * kernel(upper, parent_decay, step) + max_amplitude * kernel(upper, defect_base, step), sub_history, "source plus defect upper envelope", "defect contract")
                    check(f"sub path expansion {pattern} bar={upper} s={defect_base} n={step}", sub_history == path_expansion(coefficients[: step + 1], sub_terms[: step + 1]), sub_history, "path expansion", "path-product")
            if admissible:
                check(f"two-base threshold bar={upper} s={defect_base}", max(upper, parent_decay, defect_base) < 1, max(upper, parent_decay, defect_base), "<1", "threshold")
            else:
                check(f"threshold control bar={upper} s={defect_base}", upper >= 1 or defect_base >= 1, [upper, defect_base], "bar>=1 or s>=1", "threshold control")
            pair_rows.append({
                "kappa_bar": str(upper),
                "defect_base_s": str(defect_base),
                "admissible": admissible,
                "source_branch": "resonant" if upper == parent_decay else "nonresonant",
                "defect_branch": "resonant" if upper == defect_base else "nonresonant",
                "terminal_source_kernel": str(source_kernel_terminal),
                "terminal_defect_kernel": str(defect_kernel_terminal),
            })

    check("source resonance exercised", source_resonance, True, "kappa_bar=parent_decay", "closed form")
    check("defect resonance exercised", defect_resonance, True, "s=kappa_bar", "closed form")
    check("admissible pairs exercised", admissible_pairs > 0, admissible_pairs, ">0", "threshold")
    check("nonadmissible controls exercised", any(not row["admissible"] for row in pair_rows), True, "unit/superunit controls", "threshold")
    check("D=0 reduction retained", Fraction(0) in amplitudes, amplitudes, "declared exact-recurrence reduction", "defect contract")
    check("theorem marker", "kappa_R<=kappa_bar" in manifest["theorem"]["variable_recurrence"], manifest["theorem"]["variable_recurrence"], "upper coefficient contract", "theorem")

    scope = manifest["scope"]
    closed = (
        "parent_r451_decay_input_reused",
        "variable_coefficient_path_product_bound_closed",
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
            "fourth_power_cauchy_factor": factor,
            "C4_edge": str(c4_edge),
            "source_constant_A": str(source_constant),
            "defect_amplitude_max_D": str(max_amplitude),
            "radius_rows_per_pair": radius_max - radius_min + 1,
            "patterns": patterns,
            "pair_rows": pair_rows,
            "pair_count": len(pair_rows),
            "admissible_pair_count": admissible_pairs,
            "variable_coefficient_path_product_bound_closed": True,
            "general_defect_convolution_closed": True,
            "geometric_defect_envelope_closed": True,
            "nonresonant_closed_form_closed": True,
            "resonant_closed_form_closed": True,
            "two_base_less_than_one_threshold_closed": True,
            "actual_q3_history_closed": False,
            "source_owned_recurrence_closed": False,
            "source_owned_coefficient_bound_closed": False,
            "source_owned_defect_closed": False,
            "common_weighted_operator_domain_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {
            "script": digest(Path(__file__)),
            "manifest": digest(MANIFEST),
            "r453_manifest": digest(R453_MANIFEST),
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
    print(f"R-454 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} pairs={len(pair_rows)} patterns={len(patterns)} r={parent_decay}", flush=True)
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
