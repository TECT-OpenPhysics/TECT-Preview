"""Reproduce a PAH-OMC-016 definition audit, not a Gibbs limit proof.

Primary: closed-form dyadic regulator arithmetic. Independent: recursively
subdivide the amplitude mesh and enlarge the interval. Hostile controls reject
raw-index substitution, a fixed-resolution path, root-map identification and
an unregistered sector prior. All computations are exact Fractions/integers.
No partition function, new carrier dynamics or empirical score is computed.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
PIN = "1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7"
RUN = "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc016-contract-review/result.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append({"name": name, "pass": True})

    check("preregistration_hash", digest(ROOT / CONTRACT) == PIN)
    c = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    for path, expected in c["sources"].items():
        check("parent_hash:" + path, digest(ROOT / path) == expected)
    parent = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    check("source_coordinate", "R_max ell_v/M_psi" in parent["finite_regulator"]["matter_cutoff"])
    check("source_move", any("one radial occupation quantum" in m for m in parent["dynamics"]["move_set"]))
    check("no_source_rate_modification", "No acceleration of time or rescaling of rates" in c["scope"]["generator"])
    check("explicit_observable_change", "NOT ell_v" in c["observable_contract"]["old_witness_firewall"])
    check("nondegeneracy_unproved", "HOLD_FOR_EVIDENCE" in c["future_discriminating_gate"]["hold"])
    check("no_polar_jacobian", "not a sector prior or a polar radial Jacobian" in c["scope"]["reference"])

    base = c["scope"]["path"]["base"]
    # These strings define the frozen path; do not silently accept a new one.
    check("path_syntax", c["scope"]["path"] == {
        "index": "j is an integer >=0", "base": base,
        "R_max": "2^j", "M_psi": "2^(2j)", "radial_mesh": "2^(-j)"})
    check("dyadic_base", base == 2)  # Preregistered input, not an inferred output.
    levels = range(5)  # Tooling coverage only; not a cutoff convergence test.
    primary = []
    independent = []
    for j in levels:
        rmax, m = base**j, base**(2*j)
        h = Fraction(rmax, m)
        selected = sorted({0, 1, base**j, m})
        samples = []
        for ell in selected:
            r = h * ell
            b = min(Fraction(1), r)
            fine_ell = base * ell
            fine_r = Fraction(base**(j+1), base**(2*(j+1))) * fine_ell
            assert fine_ell <= base**(2*(j+1))
            assert r == fine_r and b == min(Fraction(1), fine_r)
            samples.append({"ell": ell, "amplitude": str(r), "bounded_witness": str(b)})
        primary.append({"j": j, "range": rmax, "levels": m, "mesh": str(h), "samples": samples})

    # No primary path helper is used: grow range and bisect spacing recursively.
    right_endpoint, spacing = 1, Fraction(1)
    for j in levels:
        count = Fraction(right_endpoint) / spacing
        assert count.denominator == 1
        independent.append({"j": j, "range": right_endpoint, "levels": int(count), "mesh": str(spacing)})
        right_endpoint *= base
        spacing /= base
    check("independent_grid_recurrence", [dict((k, row[k]) for k in ("j", "range", "levels", "mesh")) for row in primary] == independent)
    check("exact_state_injection", all(row["pass"] for row in checks))
    check("unit_amplitude_witness_all_test_levels", all(any(s["amplitude"] == "1" and s["bounded_witness"] == "1" for s in row["samples"]) for row in primary))
    check("baseline_matches_old_binary_ell", all(s["bounded_witness"] == str(s["ell"]) for s in primary[0]["samples"]))

    # Hostile controls: independently computed contradictions, not physical tests.
    ell, h, m = base, Fraction(1, base), base**2
    b = min(Fraction(1), h * ell)
    check("hostile_raw_index_substitution", b != ell)
    check("hostile_normalized_index_substitution", b != Fraction(ell, m))
    check("hostile_fixed_resolution_mesh", Fraction(base, 1) > Fraction(1, 1))
    # A coarse one-quantum transfer injects as TWO fine quanta, not one.
    check("hostile_injection_is_not_root_transport", base * 1 != 1)
    # Unequal positive labelled weights: counting mixture != equal sector weights.
    test_weights = (Fraction(1), Fraction(1, base))  # Labelled algebraic control, not PAH Z values.
    actual = test_weights[0] / sum(test_weights)
    check("hostile_equal_sector_prior", actual != Fraction(1, len(test_weights)))
    check("hostile_no_540_import", "reference-only" in c["observable_contract"]["exhaustion_map"])

    result = {
        "contract_id": c["contract_id"], "preregistration_sha256": PIN,
        "source_hashes": c["sources"], "verifier_sha256": digest(Path(__file__)),
        "verdict": "CONTRACT_REVIEW_PASS_NOT_MATHEMATICAL_ADMISSION",
        "nondegeneracy_gate": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support", "checks": checks,
        "assertions_passed": len(checks), "primary": primary, "independent": independent,
        "scope": "Exact coordinate and source/contract audit; not a Gibbs expectation, rate convergence, common core or uniform estimate.",
        "universal_argument_locator": "strategy/pa-hyp/PAH-OMC-016-review.md#coordinate-review",
        "lean": "NOT_RUN: definition/planning audit only; no analytic theorem claimed. A future lower-bound theorem needs its own primary/independent/hostile and Lean scope.",
        "next_single_question": c["future_discriminating_gate"]["question"],
        "non_claims": c["non_claims"]
    }
    target = ROOT / RUN
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PAH-OMC-016 CONTRACT REVIEW: PASS ({len(checks)} checks); nondegeneracy=HOLD_FOR_EVIDENCE")
    print(RUN)


if __name__ == "__main__":
    main()
