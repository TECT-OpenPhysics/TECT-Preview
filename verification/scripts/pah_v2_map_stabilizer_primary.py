#!/usr/bin/env python3
"""Exact definition diagnostic: strict anchor equivariance and B odd states.

Uses the pinned source enumerator on the issued triangle only. No F, rates,
generator, semigroup or limit calculation; no new counting-state quotient.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "strategy/pa-hyp/PAH-v2-map-stabilizer-prereg.json"
SPEC_HASH = "bcaf96f3d03c5c8cbaa32aa57ac160ff4e98b09432ff71fe98f4a2f6dc7f4512"  # INPUT.
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-map-stabilizer/primary.json"
sys.path.insert(0, str(ROOT / "codes/foundations"))
import pah_v2_root_enumerator as en


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cyclic(word):
    word = tuple(word)
    return {word[i:]+word[:i] for i in range(len(word))}


def run():
    assert sha(SPEC) == SPEC_HASH
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    for path, digest in spec["source_pins"].items():
        assert sha(ROOT/path) == digest, path
    inp = json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    nv = inp["vertices"]; edges = tuple(map(tuple, inp["edges"]))
    face = tuple(map(tuple, inp["faces"][0]))
    assert nv == 3 and len(inp["faces"]) == 1, "Scope: issued triangle, not arbitrary carriers"
    outer, core = set(inp["outer_anchor"]), set(inp["core_anchor"])
    admissible_words = cyclic(face) | cyclic(tuple((e, -s) for e, s in reversed(face)))
    autos = []
    for perm in it.permutations(range(nv)):
        if {perm[v] for v in outer} != outer or {perm[v] for v in core} != core: continue
        emap = []
        for v, w in edges:
            target = (perm[v], perm[w])
            if target in edges: emap.append((edges.index(target), 1))
            elif target[::-1] in edges: emap.append((edges.index(target[::-1]), -1))
            else: break
        if len(emap) != len(edges): continue
        transported = tuple((emap[e][0], sign*emap[e][1]) for e, sign in face)
        if transported in admissible_words: autos.append((perm, tuple(emap)))
    identity = tuple(range(nv))
    nonidentity = [a for a in autos if a[0] != identity]
    assert len(nonidentity) == 1
    tau, edge_tau = nonidentity[0]

    def act(x, k):
        blocks = []
        for vals in (x.aperture, x.occupation, x.phase):
            y = [0]*nv
            for v in range(nv): y[tau[v]] = vals[v]
            blocks.append(tuple(y))
        link = [0]*len(edges)
        for e, (dest, sign) in enumerate(edge_tau): link[dest] = sign*x.link[e] % k
        return en.State(*blocks, tuple(link))

    q = inp["Q"]
    coarse = en.Regulator(nv, edges, inp["K"], inp["M_s"], inp["M_psi"], q)
    fine = en.Regulator(nv, edges, 2*coarse.K, 2*coarse.M_s, 4*coarse.M_psi, 2*q)
    witness = en.State((0,)*nv, (2*q-2, 1, 1), (0,)*nv, (0,)*len(edges))
    assert en.valid_state(fine, witness) and act(witness, fine.K) == witness
    states = tuple(en.states(coarse))
    fixed = tuple(x for x in states if act(x, coarse.K) == x)
    assert all(act(act(x, coarse.K), coarse.K) == x for x in states)
    occupations = sorted({x.occupation for x in fixed})
    assert fixed and all(x.occupation[1] == x.occupation[2] for x in fixed)
    assert all(x.occupation[0] == q-2*x.occupation[1] for x in fixed)
    d = F(inp["R_max"])/coarse.M_psi
    ideal = tuple(F(l, 2) for l in witness.occupation)
    errors = [{"occupation": occ, "outer_amplitude_error": str(d*abs(occ[0]-ideal[0])),
               "radial_l1_error": str(d*sum(abs(F(x)-y) for x, y in zip(occ, ideal)))}
              for occ in occupations]
    assert all(F(row["outer_amplitude_error"]) >= d for row in errors)
    assert all(F(row["radial_l1_error"]) >= 2*d for row in errors)
    assert not any(x.occupation[0] == 0 for x in fixed), "q=1 fixture: strict equivariance forces occupation at O"
    # Scope control: distinct coarse states can agree on every invariant f.
    a = en.State((0,)*nv, (0, q, 0), (0,)*nv, (0,)*len(edges))
    b = act(a, coarse.K)
    assert en.valid_state(coarse, a) and en.valid_state(coarse, b) and a != b
    return {"schema": "tect/pah-v2-map-stabilizer-primary/1.0", "status": "PASS_SCOPED_DEFINITION_DIAGNOSTIC",
            "prereg_sha256": sha(SPEC), "script_sha256": sha(Path(__file__)), "source_pins": spec["source_pins"],
            "automorphisms": [{"vertices": p, "edges_with_sign": e} for p, e in autos],
            "full_coarse_states": len(states), "tau_fixed_coarse_states": len(fixed),
            "fine_witness": {"aperture": witness.aperture, "occupation": witness.occupation, "phase": witness.phase, "link": witness.link, "fixed_by_tau": True},
            "fixed_output_occupations": occupations, "radial_errors": errors,
            "strict_plus_zero_outer_possible_on_witness": False,
            "invariant_observable_scope_control": {"distinct_a": a.occupation, "distinct_b": b.occupation,
                "reason": "b=tau a: every full gauge/anchor-invariant f agrees, though these counting states differ. No full p is constructed."},
            "non_claims": "No all-map no-go, full contract, altered source, generator defect, limit or physical claim. Additional outer-fidelity condition is unapproved."}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); result = json.loads(json.dumps(run()))
    if args.check: assert json.loads(OUT.read_text(encoding="utf-8")) == result
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
    print("PAH-V2-MAP-STABILIZER PRIMARY: PASS (strict-state necessary condition only)")


if __name__ == "__main__": main()
