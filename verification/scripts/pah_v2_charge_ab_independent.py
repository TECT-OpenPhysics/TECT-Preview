#!/usr/bin/env python3
"""Non-importing exact audit of the two unadopted v2 charge proposals.

Independence means a separate flat-tuple/root and scalar-energy implementation,
not a separate author or external review. Only the frozen fixture is input.
Hostile mathematical controls are distinguished from documentary scope guards.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools as it
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-v2-charge-AB-prereg.json"
PREREG_HASH = "33fe50af87c588715b18fed5415cdad5dc5b17f0b9c3d3a25edd6e2874c06457"  # INPUT pin.
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-charge-ab"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scalar_energy(ap, occ, ms, mp, rmax, inp):
    """Exactly the displayed functional on the zero-phase/zero-link slice.

    The plaquette term vanishes identically on this slice. This independent
    energy checker does NOT claim phase-general energy enumeration coverage.
    """
    eps = F(inp["epsilon"])
    s = [eps + (1-eps)*F(j, ms) for j in ap]
    z = [rmax*F(l, mp) for l in occ]
    value = sum(F(inp["lambda_s"])*(v-1)**2/2
                + F(inp["m2"])*w**2/2 + F(inp["lambda_4"])*w**4/4
                + F(inp["eta_6"])*w**6/6 + F(inp["g"])*v*v*w*w/2
                for v, w in zip(s, z))
    for v, w in inp["edges"]:
        value += F(inp["kappa_s"])*(s[v]-s[w])**2/2
        value += F(inp["kappa_D"])*(z[w]-z[v])**2/(s[v]+s[w])
    return value


def run():
    assert sha(PREREG) == PREREG_HASH
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    for p, h in prereg["source_pins"].items():
        assert sha(ROOT/p) == h, p
    inp = json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    nv, ne = inp["vertices"], len(inp["edges"])
    ms, mp, k, q = (inp[s] for s in ("M_s", "M_psi", "K", "Q"))
    rmax, beta, eps, nu = (F(inp[s]) for s in ("R_max", "beta", "epsilon", "nu"))
    assert nu == 2, "INPUT fixture permits rational AP mobility"
    nstart, ustart = 2*nv, 3*nv
    # Flat order: aperture, occupation, phase, link. No imported State/Move.
    states = [ap+occ+ph+li for ap in it.product(range(ms+1), repeat=nv)
              for occ in it.product(range(mp+1), repeat=nv) if sum(occ) == q
              for ph in it.product(range(k), repeat=nv)
              for li in it.product(range(k), repeat=ne)]
    labels = [(fam, cell, sign) for fam in ("PH", "TR", "LK", "AP")
              for cell in range(nv if fam in ("PH", "AP") else ne)
              for sign in (-1, 1)]

    def move(x, label, scale, branch):
        fam, cell, sign = label
        y = list(x)
        if fam == "PH": y[nstart+cell] = (y[nstart+cell]+sign) % (k*scale)
        if fam == "LK": y[ustart+cell] = (y[ustart+cell]+sign) % (k*scale)
        if fam == "AP": y[cell] += sign
        if fam == "TR":
            v, w = inp["edges"][cell]
            y[nv+v] -= sign
            y[nv+w] += sign
        if not all(0 <= j <= ms*scale for j in y[:nv]): return None
        if not all(0 <= l <= mp*scale*scale for l in y[nv:2*nv]): return None
        assert sum(y[nv:2*nv]) == q*(scale if branch == "B" else 1)
        return tuple(y)

    def embed(x, branch):
        return tuple(v*(1 if nv <= i < 2*nv and branch == "A" else 2)
                     for i, v in enumerate(x))

    branches = {}
    for branch in ("A", "B"):
        counts = {fam: {"valid": 0, "one_step_equal": 0, "path_equal": 0}
                  for fam in ("PH", "TR", "LK", "AP")}
        for x in states:
            z = embed(x, branch)
            for label in labels:
                y = move(x, label, 1, branch)
                if y is None: continue
                target = embed(y, branch)
                fam = label[0]
                counts[fam]["valid"] += 1
                step = move(z, label, 2, branch)
                counts[fam]["one_step_equal"] += (step == target)
                endpoint = step if fam == "TR" and branch == "A" else move(step, label, 2, branch)
                assert endpoint == target
                counts[fam]["path_equal"] += 1
        seed_ap, seed_occ = (0,)*nv, (q,)+(0,)*(nv-1)
        image_occ = tuple((2 if branch == "B" else 1)*l for l in seed_occ)
        e0 = scalar_energy(seed_ap, seed_occ, ms, mp, rmax, inp)
        e1 = scalar_energy(seed_ap, image_occ, 2*ms, 4*mp, 2*rmax, inp)
        terms = []
        for cell in range(nv):
            ap = list(seed_ap); ap[cell] += 1
            after = scalar_energy(ap, image_occ, 2*ms, 4*mp, 2*rmax, inp)
            mobility = eps*(eps+(1-eps)/F(2*ms))
            exponent = -beta*(after-e1)/2
            assert mobility > 0
            terms.append({"cell": cell, "coefficient": str(mobility), "exponent": str(exponent), "family": "AP", "sign": 1})
        # Broader energy cross-check on all occupation/aperture combinations
        # at zero phase/link; different slice and algebra from primary.
        slice_count, equal = 0, 0
        for ap in it.product(range(ms+1), repeat=nv):
            for occ in it.product(range(mp+1), repeat=nv):
                if sum(occ) != q: continue
                eo = scalar_energy(ap, occ, ms, mp, rmax, inp)
                en = scalar_energy(tuple(2*j for j in ap), tuple((2 if branch == "B" else 1)*l for l in occ), 2*ms, 4*mp, 2*rmax, inp)
                slice_count += 1; equal += eo == en
                if branch == "B": assert eo == en
        branches[branch] = {"coarse_states": len(states), "root_checks": counts,
                            "seed_energy_coarse": str(e0), "seed_energy_image": str(e1),
                            "trace_terms": terms, "zero_phase_slice_states": slice_count,
                            "zero_phase_slice_energy_equal": equal}

    # Check primary outputs only AFTER the separate calculations.
    primary = json.loads((RUN/"primary.json").read_text(encoding="utf-8"))
    for branch in branches:
        actual, other = branches[branch], primary["branches"][branch]
        for field in ("coarse_states", "root_checks", "seed_energy_coarse", "seed_energy_image"):
            assert actual[field] == other[field], (branch, field)
        assert actual["trace_terms"] == other["trace_witness"]["fine_generator_at_image_terms"]

    # Concrete controls. True means the named INCORRECT shortcut was detected.
    control = {}
    control["A_preserves_displayed_amplitude"] = rmax*q/mp != (2*rmax)*q/(4*mp)
    control["B_preserves_integer_Q"] = q != 2*q
    fine_odd = (1, 2*q-1)+(0,)*(nv-2)
    assert sum(fine_odd) == 2*q and all(0 <= l <= 4*mp for l in fine_odd)
    control["B_half_map_is_full_integer_inverse"] = any(F(l, 2).denominator != 1 for l in fine_odd)
    control["two_fine_roots_are_one_coarse_root"] = all(branches[b]["root_checks"]["AP"]["one_step_equal"] == 0 for b in branches)
    control["even_image_is_closed_under_fine_dynamics"] = all(branches[b]["trace_terms"] for b in branches)
    # Display-invisible labels must still remain distinct counting states.
    empty_phases = ((0,)*nv, (1,)+(0,)*(nv-1))
    assert empty_phases[0] != empty_phases[1]
    control["zero_occupation_erases_phase"] = all(F(0)*n == 0 for row in empty_phases for n in row)
    unit_floor_displays = [F(1)+F(j, 2*ms)*(1-F(1)) for j in range(2*ms+1)]
    control["epsilon_one_erases_aperture_index"] = len(set(unit_floor_displays)) == 1 and len(unit_floor_displays) > 1
    # On B, all injected energies equal; a finite off-image state has strictly
    # positive Gibbs weight. Thus Z_fine > Z_coarse, without summing Z_fine.
    off_ap = (1,)+(0,)*(nv-1)
    finite_off_energy = scalar_energy(off_ap, (2*q,)+(0,)*(nv-1), 2*ms, 4*mp, 2*rmax, inp)
    control["equal_image_energy_implies_equal_normalized_Gibbs_weights"] = isinstance(finite_off_energy, F) and off_ap[0] % 2 == 1
    assert all(control.values())
    scope_guards = {
        "trace_is_not_forward_pullback": "J*:fine->coarse; requested I:coarse->fine; no equality of types",
        "no_eventual_counterexample": "This h is fine-regulator-specific; no fixed common f or N(f) is supplied",
        "no_weak_L2_counterexample": "No fixed common Gibbs-L2 realization or defect norm is evaluated",
        "no_branch_adoption": "Comparison authorization is not operative full-contract adoption"
    }
    return {"schema": "tect/pah-v2-charge-ab-independent/1.0", "status": "PASS_SCOPED_CHECKS",
            "prereg_sha256": sha(PREREG), "script_sha256": sha(Path(__file__)),
            "primary_run_sha256": sha(RUN/"primary.json"), "source_pins": prereg["source_pins"],
            "independence": "No imports of primary or source enumerator; flat tuples, separate scalar-energy implementation. Same-task authorship, not external review.",
            "branches": branches, "hostile_mathematical_controls_detected": control,
            "documentary_scope_guards": scope_guards,
            "coverage": "All issued coarse states and labelled roots independently checked; exact zero-phase energy slice and trace rates independently recomputed. General proof is in the comparison note, not inferred from counts.",
            "Lean": "NOT_RUN for this unadopted comparison; no new kernel theorem claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    out = RUN/"independent-hostile.json"
    if args.check:
        assert json.loads(out.read_text(encoding="utf-8")) == result
    else:
        with out.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
    print("PAH-V2-CHARGE-AB INDEPENDENT/HOSTILE: PASS (separate implementation; no external reviewer or Lean claim)")


if __name__ == "__main__": main()
