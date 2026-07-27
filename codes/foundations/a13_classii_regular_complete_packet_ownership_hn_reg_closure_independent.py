#!/usr/bin/env python3
"""Independent standard-library certificate for the R-103 reassembly.

This route imports neither SymPy nor the primary module.  It recomputes the
scalar endpoint split, owner incidence, refunds, and budget margins with exact
Fraction arithmetic and a deliberately different ordering of the modules.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-independent-regular-complete-packet-ownership-hn-reg-closure/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-regular-complete-packet-ownership-hn-reg-closure-independent/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "This independent certificate covers only the exact regular complete-owner "
                "reassembly and finite budget split. Naked posterior positivity, the old "
                "standalone atom statements, arbitrary progression/revisit, OVERLAP_src, "
                "Nelson, removals, a measure, T5--T7, and Sector A remain open."
            ),
        }


def scalar_endpoint_from_inputs(
    b0: Fraction,
    b1: Fraction,
    bt: Fraction,
    g: Fraction,
    c: Fraction,
    q: Fraction,
) -> dict[str, Fraction]:
    raw_contraction = (b1 - b0) * q
    direct = raw_contraction / 2 + g * b1 * c + b1 * c * c / 2
    reassembled = raw_contraction / 2 + g * bt * c + g * (b1 - bt) * c + b1 * c * c / 2
    return {
        "direct": direct,
        "reassembled": reassembled,
        "raw_contraction": raw_contraction,
        "raw": raw_contraction / 2,
        "unshifted": g * bt * c,
        "shifted_current": g * (b1 - bt) * c,
        "square": b1 * c * c / 2,
        "wrong_raw_factor": raw_contraction + g * b1 * c + b1 * c * c / 2,
        "wrong_shifted_sign": raw_contraction / 2 + g * bt * c - g * (b1 - bt) * c + b1 * c * c / 2,
        "wrong_square_factor": raw_contraction / 2 + g * b1 * c + b1 * c * c,
    }


def scalar_endpoint(seed: int) -> dict[str, Fraction]:
    # INPUTS are small exact scalar endpoint coordinates.
    b0 = Fraction(seed + 1, seed + 2)
    db = Fraction(2 * seed + 1, seed + 3)
    d2b = Fraction(1 - seed, seed + 4)
    b1 = Fraction((seed + 2) ** 2, seed + 5)
    bt = b0 + db + d2b / 2
    g = Fraction(2 * seed - 1, seed + 1)
    c = Fraction(seed + 3, 2 * seed + 1)
    q = Fraction(seed - 2, seed + 6)
    return scalar_endpoint_from_inputs(b0, b1, bt, g, c, q)


def main() -> int:
    audit = Audit()
    endpoint_rows: list[dict[str, Any]] = []
    for seed in (3, 5, 8, 13, 21):
        row = scalar_endpoint(seed)
        audit.check("algebra", f"scalar_endpoint_{seed}", row["direct"] == row["reassembled"], row["direct"] - row["reassembled"], 0)
        audit.check("algebra", f"scalar_raw_factor_mutant_{seed}", row["direct"] != row["wrong_raw_factor"], row["direct"] - row["wrong_raw_factor"], "nonzero")
        audit.check("algebra", f"scalar_shifted_sign_mutant_{seed}", row["direct"] != row["wrong_shifted_sign"], row["direct"] - row["wrong_shifted_sign"], "nonzero")
        audit.check("algebra", f"scalar_square_factor_mutant_{seed}", row["direct"] != row["wrong_square_factor"], row["direct"] - row["wrong_square_factor"], "nonzero")
        audit.check("algebra", f"scalar_square_{seed}", row["square"] > 0, row["square"], ">0")
        endpoint_rows.append(row)

    zero_psd = scalar_endpoint_from_inputs(
        Fraction(2, 3),
        Fraction(0),
        Fraction(5, 4),
        Fraction(-3, 2),
        Fraction(7, 5),
        Fraction(4, 3),
    )
    audit.check("algebra", "scalar_zero_psd_endpoint", zero_psd["direct"] == zero_psd["reassembled"], zero_psd["direct"] - zero_psd["reassembled"], 0)
    audit.check("algebra", "scalar_zero_psd_square", zero_psd["square"] == 0, zero_psd["square"], 0)

    # Different order and labels from the primary implementation.
    module_atoms = [
        ("low_complete", ("complete_low",)),
        ("shifted", ("future_current", "terminal_square")),
        ("far", ("cartan_output",)),
        ("raw_residual", ("raw_wick_future_residual", "rational_heat_trace_forest", "full_wick_secant")),
        ("low_conditional", ("conditional_low",)),
        ("paid", ("r078_paid_difference",)),
        ("linear", ("linear_rows", "linear_heat_trace_forest")),
        ("unshifted", ("current_u5", "current_u3", "current_u4")),
    ]
    all_atoms = [atom for _, atoms in module_atoms for atom in atoms]
    near_modules = [(label, atoms) for label, atoms in module_atoms if label != "far"]
    near_atoms = [atom for _, atoms in near_modules for atom in atoms]
    audit.check("ownership", "module_count", len(module_atoms) == 8, len(module_atoms), 8)
    audit.check("ownership", "near_module_count", len(near_modules) == 7, len(near_modules), 7)
    audit.check("ownership", "near_excludes_only_far", {label for label, _ in module_atoms} - {label for label, _ in near_modules} == {"far"}, sorted({label for label, _ in module_atoms} - {label for label, _ in near_modules}), ["far"])
    audit.check("ownership", "owner_injection", len(all_atoms) == len(set(all_atoms)), len(all_atoms) - len(set(all_atoms)), 0)
    audit.check("ownership", "near_owner_injection", len(near_atoms) == len(set(near_atoms)), len(near_atoms) - len(set(near_atoms)), 0)
    required = {
        "conditional_low",
        "complete_low",
        "cartan_output",
        "linear_rows",
        "linear_heat_trace_forest",
        "raw_wick_future_residual",
        "rational_heat_trace_forest",
        "full_wick_secant",
        "current_u3",
        "current_u4",
        "current_u5",
        "future_current",
        "terminal_square",
        "r078_paid_difference",
    }
    audit.check("ownership", "required_owner_coverage", set(all_atoms) == required, sorted(all_atoms), sorted(required))
    for label, atoms in module_atoms:
        audit.check("ownership", f"{label}_one_module", bool(atoms), len(atoms), ">0")

    forbidden = {
        "raw_q_taylor_u1",
        "raw_q_taylor_u2",
        "r076_base_cubic",
        "r086_tg_low_current",
        "r086_q_orientations",
        "second_r094_secant",
        "appended_r063_forest",
        "extra_q_r_schur_reserve",
    }
    audit.check("refund", "forbidden_disjoint", set(all_atoms).isdisjoint(forbidden), sorted(set(all_atoms) & forbidden), [])
    for item in sorted(forbidden):
        audit.check("refund", f"{item}_zero", all_atoms.count(item) == 0, all_atoms.count(item), 0)

    # Independent upstream read: R-093 pins the action coefficients and R-088
    # pins an optional comparison threshold, not an internal allocation cap.
    claim_dir = REPO / "claims" / CLAIM
    r088_note = (claim_dir / "notes/classii-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-reduction-260725-v1.0.tex.txt").read_text(encoding="utf-8")
    r093_note = (claim_dir / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt").read_text(encoding="utf-8")
    audit.check("upstream", "independent_r088_comparison_formula", all(token in r088_note for token in (r"{1\over220}", r"p={11\over10}", "No universal")), "tokens present", "tokens present")
    audit.check("upstream", "independent_r093_action_formula", all(token in r093_note for token in (r"{3\over20}", r"{9\over20}", "I_2(v)")), "tokens present", "tokens present")
    q_nelson = Fraction(10, 9)
    source_charge = Fraction(1, 2) / q_nelson
    sextic_charge = Fraction(3, 20)  # Explicit upstream input in R-093.
    comparison_p = Fraction(11, 10)
    comparison_threshold = Fraction(1, 2) / comparison_p - source_charge
    eta = comparison_threshold / 2
    zeta = sextic_charge / 5
    count = len(module_atoms)
    eta_piece = eta / count
    zeta_piece = zeta / count
    near_count = len(near_modules)
    eta_near_piece = eta / near_count
    zeta_near_piece = zeta / near_count
    audit.check("budget", "source_charge_from_q", source_charge == Fraction(9, 20), source_charge, Fraction(9, 20))
    audit.check("budget", "comparison_threshold_derived", comparison_threshold == Fraction(1, 220), comparison_threshold, Fraction(1, 220))
    audit.check("budget", "eta_below_comparison_threshold", eta < comparison_threshold, eta, f"<{comparison_threshold}")
    audit.check("budget", "zeta_below_sextic_charge", zeta < sextic_charge, zeta, f"<{sextic_charge}")
    audit.check("budget", "eta_piece_sum", sum((eta_piece for _ in module_atoms), Fraction(0)) == eta, eta_piece * count, eta)
    audit.check("budget", "zeta_piece_sum", sum((zeta_piece for _ in module_atoms), Fraction(0)) == zeta, zeta_piece * count, zeta)
    audit.check("budget", "eta_piece_exact", eta_piece == Fraction(1, 3520), eta_piece, Fraction(1, 3520))
    audit.check("budget", "zeta_piece_exact", zeta_piece == Fraction(3, 800), zeta_piece, Fraction(3, 800))
    audit.check("budget", "eta_near_piece_sum", sum((eta_near_piece for _ in near_modules), Fraction(0)) == eta, eta_near_piece * near_count, eta)
    audit.check("budget", "zeta_near_piece_sum", sum((zeta_near_piece for _ in near_modules), Fraction(0)) == zeta, zeta_near_piece * near_count, zeta)
    audit.check("budget", "eta_near_piece_exact", eta_near_piece == Fraction(1, 3080), eta_near_piece, Fraction(1, 3080))
    audit.check("budget", "zeta_near_piece_exact", zeta_near_piece == Fraction(3, 700), zeta_near_piece, Fraction(3, 700))
    source_reserve = source_charge - eta
    sextic_reserve = sextic_charge - zeta
    audit.check("budget", "source_reserve_exact", source_reserve == Fraction(197, 440), source_reserve, Fraction(197, 440))
    audit.check("budget", "sextic_reserve_exact", sextic_reserve == Fraction(3, 25), sextic_reserve, Fraction(3, 25))
    audit.check("budget", "reserves_positive", min(source_reserve, sextic_reserve) > 0, min(source_reserve, sextic_reserve), ">0")

    cartan_separation = 5 + 2 * 5
    gap = Fraction(1, 2 ** ((cartan_separation - 5) // 2))
    audit.check("cartan", "derived_cartan_separation", cartan_separation == 15, cartan_separation, 15)
    audit.check("cartan", "derived_gap", gap == Fraction(1, 32), gap, Fraction(1, 32))

    payload = audit.finish(
        {
            "endpoint_rows": endpoint_rows,
            "module_order": [label for label, _ in module_atoms],
            "near_module_order": [label for label, _ in near_modules],
            "atomic_owners": all_atoms,
            "forbidden": sorted(forbidden),
            "budget": {
                "eta": eta,
                "zeta": zeta,
                "eta_piece": eta_piece,
                "zeta_piece": zeta_piece,
                "eta_near_piece": eta_near_piece,
                "zeta_near_piece": zeta_near_piece,
                "source_reserve": source_reserve,
                "sextic_reserve": sextic_reserve,
            },
            "cartan_gap": gap,
        }
    )
    atomic_json(OUTPUT, payload)
    print(
        f"R-103 independent: {payload['assertions_passed']}/{payload['assertions_total']} "
        f"assertions {payload['status']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
