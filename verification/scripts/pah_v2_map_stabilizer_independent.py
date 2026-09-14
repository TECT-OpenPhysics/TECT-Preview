#!/usr/bin/env python3
"""Independent integer equations and hostile scope audit, no primary imports.

Checks the source triangle using coordinate constraints rather than enumerating
full states. Same author; not an external independent-person review. No dynamics.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools as it
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT/"strategy/pa-hyp/PAH-v2-map-stabilizer-prereg.json"
SPEC_HASH = "bcaf96f3d03c5c8cbaa32aa57ac160ff4e98b09432ff71fe98f4a2f6dc7f4512"  # INPUT.
RUN = ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-map-stabilizer"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    assert sha(SPEC) == SPEC_HASH
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    for p, h in spec["source_pins"].items(): assert sha(ROOT/p) == h
    inp = json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    nv, q, ms, mp, k = (inp[s] for s in ("vertices", "Q", "M_s", "M_psi", "K"))
    assert nv == 3 and inp["outer_anchor"] == [0] and inp["core_anchor"] == [1, 2]
    # Explicit reflection is INPUT from the anchored triangle geometry. Verify
    # the edge/face incidence equations independently, including orientation.
    perm = (0, 2, 1)
    edges = inp["edges"]
    emap = []
    for a, b in edges:
        matches = [(i, 1) for i, (v, w) in enumerate(edges) if (v, w) == (perm[a], perm[b])]
        matches += [(i, -1) for i, (v, w) in enumerate(edges) if (w, v) == (perm[a], perm[b])]
        assert len(matches) == 1; emap.append(matches[0])
    assert all(sign == -1 for _, sign in emap)
    face = [tuple(p) for p in inp["faces"][0]]
    transported = [(emap[e][0], sign*emap[e][1]) for e, sign in face]
    reverse = [(e, -sign) for e, sign in reversed(face)]
    assert any(transported == reverse[i:]+reverse[:i] for i in range(len(reverse)))
    # Solve all fixed occupation constraints ell_1=ell_2; no imported states.
    outputs = [(q-2*c, c, c) for c in range(mp+1) if 0 <= q-2*c <= mp]
    aperture_fixed = (ms+1)**2
    phase_fixed = k**2
    link_fixed = sum(all(u[dest] == sign*u[src] % k for src, (dest, sign) in enumerate(emap))
                     for u in it.product(range(k), repeat=len(edges)))
    fixed_count = len(outputs)*aperture_fixed*phase_fixed*link_fixed
    fine_occ = (2*q-2, 1, 1)
    assert sum(fine_occ) == 2*q and max(fine_occ) <= 4*mp and min(fine_occ) >= 0
    d = F(inp["R_max"])/mp
    errors = []
    for out in outputs:
        ideal = [F(v, 2) for v in fine_occ]
        outer = d*abs(out[0]-ideal[0]); l1 = d*sum(abs(F(v)-z) for v, z in zip(out, ideal))
        assert outer >= d and l1 >= 2*d
        errors.append({"occupation": out, "outer_amplitude_error": str(outer), "radial_l1_error": str(l1)})
    # These are bounded software controls for the general written odd-integer
    # identity, not evidence obtained by a family of new model calculations.
    parity_cases = []
    for charge in range(1, 9):  # INPUT tooling range; no cutoff convergence claim.
        for c in range(charge//2+1):
            out = (charge-2*c, c, c); ideal = (F(charge-1), F(1, 2), F(1, 2))
            assert abs(out[0]-ideal[0]) == abs(1-2*c) >= 1
            assert sum(abs(F(v)-w) for v, w in zip(out, ideal)) == 2*abs(1-2*c)
            parity_cases.append((charge, c))
    primary = json.loads((RUN/"primary.json").read_text(encoding="utf-8"))
    assert primary["tau_fixed_coarse_states"] == fixed_count
    assert primary["fixed_output_occupations"] == [list(x) for x in outputs]
    assert primary["radial_errors"] == json.loads(json.dumps(errors))
    hostile = {
        "half_integer_output_admitted": any(F(v, 2).denominator != 1 for v in fine_occ),
        "empty_outer_preserved_by_strict_map_at_q1": q == 1 and all(out[0] > 0 for out in outputs),
        "gauge_can_repair_occupation_parity": "Source gauge action changes n,u only; ell is fixed. Rejected by source formula.",
        "erase_zero_radius_labels": "Counting states remain distinct even where displayed psi is zero; no such quotient is taken.",
        "state_equivariance_follows_from_invariant_pullback": "Countercontrol: two different core-unit states are exchanged by tau and thus agree on every invariant f.",
        "nonzero_coordinate_error_refutes_norm_convergence": "Rejected: lower bound d_r shrinks on the B schedule; it is not a generator-defect estimate."
    }
    assert hostile["half_integer_output_admitted"] and hostile["empty_outer_preserved_by_strict_map_at_q1"]
    return {"schema": "tect/pah-v2-map-stabilizer-independent/1.0", "status": "PASS_SCOPED_DEFINITION_AUDIT",
            "prereg_sha256": sha(SPEC), "script_sha256": sha(Path(__file__)), "primary_sha256": sha(RUN/"primary.json"),
            "source_pins": spec["source_pins"], "fixed_output_occupations": outputs, "tau_fixed_count_from_constraints": fixed_count,
            "factors": {"occupation": len(outputs), "aperture": aperture_fixed, "phase": phase_fixed, "link": link_fixed},
            "radial_errors": errors, "parity_identity_software_cases": len(parity_cases),
            "hostile_controls": hostile, "independence": "No primary or enumerator import. Same-task authorship, not external review.",
            "Lean": "NOT_RUN; no kernel claim", "unresolved": "Total full-domain invariant-observable pullback, support, root assignment and entire approved tower remain absent."}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); value = json.loads(json.dumps(run())); out = RUN/"independent-hostile.json"
    if args.check: assert json.loads(out.read_text(encoding="utf-8")) == value
    else:
        with out.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True); stream.write("\n")
    print("PAH-V2-MAP-STABILIZER INDEPENDENT/HOSTILE: PASS (constraint derivation; scope retained)")


if __name__ == "__main__": main()
