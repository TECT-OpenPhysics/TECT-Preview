#!/usr/bin/env python3
"""PAH-v2 exact finite fixture cross-check; not an all-regulator proof.

Version 0.1.0, first/version issued 2026-09-11. Inputs come from the frozen
audit specification. K=2 and nu=2 make the displayed energy/mobility rational.
Each rate is coefficient * exp(rational exponent); no float comparison or
time change is used. Weighted generator and directed root Gram matrices are
assembled separately, then compared coefficient-by-coefficient. Arbitrary
complex observables follow on this fixture from matrix equality, not samples.
The all-finite proof and future independent audit remain separate obligations.
"""

import argparse
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys

__version__ = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-v2-finite-audit-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-finite/primary.json"
MANIFEST_HASH = "531697fa28c5f2e7f4177b42bc12ebd8fc1ffb7e9790d07063082e0ec3d6a331"  # INPUT provenance pin


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_inputs():
    assert sha(MANIFEST) == MANIFEST_HASH
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for name, expected in spec["source_pins"].items():
        assert sha(ROOT / name) == expected, name
    module_spec = importlib.util.spec_from_file_location("pah_v2_frozen_coordinates", ROOT / "codes/foundations/pah_v2_root_enumerator.py")
    enum = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = enum
    module_spec.loader.exec_module(enum)
    return spec, enum


def verify():
    spec, e = load_inputs()
    p = spec["primary_fixture_inputs"]
    reg = e.Regulator(p["vertices"], tuple(map(tuple, p["edges"])), p["K"], p["M_s"], p["M_psi"], p["Q"])
    assert reg.K == 2 and F(p["nu"]) == 2  # Explicit fixture scope; not universal.
    params = {k: F(p[k]) for k in ("epsilon", "R_max", "beta", "nu", "lambda_s", "m2", "lambda_4", "eta_6", "g", "kappa_s", "kappa_D", "kappa_g")}
    faces = tuple(tuple(map(tuple, face)) for face in p["faces"])
    assert faces and all(faces)
    for face in faces:
        walk = [reg.edges[edge] if sign == 1 else tuple(reversed(reg.edges[edge])) for edge, sign in face]
        assert all(walk[i][1] == walk[(i+1) % len(walk)][0] for i in range(len(walk)))
    assert set(p["outer_anchor"]) and set(p["core_anchor"])
    assert set(p["outer_anchor"]).isdisjoint(p["core_anchor"])

    def aperture(x):
        return tuple(params["epsilon"] + F(j, reg.M_s)*(1-params["epsilon"]) for j in x.aperture)

    def energy(x):
        s = aperture(x)
        psi = tuple(params["R_max"]*F(l, reg.M_psi)*(-1)**n for l,n in zip(x.occupation, x.phase))
        links = tuple((-1)**u for u in x.link)
        J = tuple(F(2)/(s[v]+s[w]) for v,w in reg.edges)
        onsite = sum(params["lambda_s"]*(s[v]-1)**2/2 + params["m2"]*psi[v]**2/2
                     + params["lambda_4"]*psi[v]**4/4 + params["eta_6"]*psi[v]**6/6
                     + params["g"]*s[v]**2*psi[v]**2/2 for v in range(reg.vertices))
        edges = sum(params["kappa_s"]*(s[v]-s[w])**2/2
                    + params["kappa_D"]*J[i]*(psi[w]-links[i]*psi[v])**2/2
                    for i,(v,w) in enumerate(reg.edges))
        plaquettes = F(0)
        for face in faces:
            hol = 1
            for edge, sign in face:
                # At K=2 the link is its own inverse; retain the signed word.
                hol *= links[edge] if sign == 1 else 1/ F(links[edge])
            plaquettes += params["kappa_g"]*sum(J[i] for i,_ in face)/len(face)*(1-hol)
        return F(onsite+edges+plaquettes)

    def mobility(x,r,y):
        a,b = aperture(x), aperture(y)
        if r.family == "PH":
            return a[r.cell]**2
        if r.family == "AP":
            return a[r.cell]*b[r.cell]
        v,w = reg.edges[r.cell]
        return a[v]*a[w]

    def gauge(x,g):
        return e.State(x.aperture, x.occupation,
                       tuple((n+gv)%reg.K for n,gv in zip(x.phase,g)),
                       tuple((x.link[i]+g[w]-g[v])%reg.K for i,(v,w) in enumerate(reg.edges)))

    # INPUT automorphism of the fixed triangle, preserving O and C setwise.
    perm = (0,2,1)
    assert {perm[v] for v in p["outer_anchor"]} == set(p["outer_anchor"])
    assert {perm[v] for v in p["core_anchor"]} == set(p["core_anchor"])
    edge_image = []
    for v,w in reg.edges:
        mapped = (perm[v],perm[w])
        if mapped in reg.edges:
            edge_image.append((reg.edges.index(mapped),1))
        else:
            edge_image.append((reg.edges.index(tuple(reversed(mapped))),-1))

    def auto(x):
        coords = []
        for original in (x.aperture,x.occupation,x.phase):
            dest = [0]*reg.vertices
            for v in range(reg.vertices):
                dest[perm[v]] = original[v]
            coords.append(tuple(dest))
        links = [0]*len(reg.edges)
        for i,(j,sign) in enumerate(edge_image):
            links[j] = sign*x.link[i] % reg.K
        return e.State(*coords,tuple(links))

    def root_auto(r):
        if r.family in ("PH","AP"):
            return e.Move(r.family,perm[r.cell],r.sign)
        j,sign = edge_image[r.cell]
        return e.Move(r.family,j,r.sign*sign)

    full = tuple(e.states(reg))
    ix = {x:i for i,x in enumerate(full)}
    assert len(ix) == len(full)
    energies = {x:energy(x) for x in full}
    gauges = tuple(product(range(reg.K),repeat=reg.vertices))
    graph, gram, rowsums = defaultdict(F), defaultdict(F), defaultdict(F)
    totals = defaultdict(int)
    digest = hashlib.sha256()
    for x in full:
        i = ix[x]
        assert auto(auto(x)) == x and energies[auto(x)] == energies[x]
        for g in gauges:
            gx = gauge(x,g)
            assert energies[gx] == energies[x]
            # P_G conjugates under Aut by a permutation of the gauge coordinates.
            ag = tuple(g[perm[v]] for v in range(reg.vertices))
            assert auto(gx) == gauge(auto(x),ag)
            totals["gauge_state_checks"] += 1
        for r,y in e.incidences(reg,x):
            j = ix[y]
            back = r.inverse()
            assert e.apply_move(reg,y,back) == x
            m = mobility(x,r,y)
            assert m > 0 and m == mobility(y,back,x)
            rate_exp = -params["beta"]*(energies[y]-energies[x])/2
            flux_exp = -params["beta"]*energies[x] + rate_exp
            reverse_exp = -params["beta"]*energies[y] - rate_exp
            assert flux_exp == reverse_exp
            # Weighted generator w L is assembled directly from outgoing jumps.
            graph[i,j,flux_exp] += m
            graph[i,i,flux_exp] -= m
            rowsums[i,rate_exp] += m
            rowsums[i,rate_exp] -= m
            # Gram B^* W_R B assembled independently from each directed row.
            # Its unnormalized coefficient is w(x)c_r(x)/2.
            for a,b,sign in ((j,j,1),(i,i,1),(j,i,-1),(i,j,-1)):
                gram[a,b,flux_exp] += sign*m/2
            ar = root_auto(r)
            ax,ay = auto(x),auto(y)
            assert e.apply_move(reg,ax,ar) == ay
            assert mobility(ax,ar,ay) == m
            for g in gauges:
                gx,gy = gauge(x,g),gauge(y,g)
                assert e.apply_move(reg,gx,r) == gy
                assert mobility(gx,r,gy) == m
                totals["gauge_incidence_checks"] += 1
            if r.family == "TR":
                assert (y.aperture,y.phase,y.link) == (x.aperture,x.phase,x.link)
            totals["valid_incidences"] += 1
            totals[r.family] += 1
            digest.update(repr((i,r.family,r.cell,r.sign,j,str(m),str(rate_exp))).encode())
    assert all(v == 0 for v in rowsums.values())
    keys = set(graph)|set(gram)
    assert all(graph[k]+gram[k] == 0 for k in keys)
    assert all(value == graph[j,i,q] for (i,j,q),value in tuple(graph.items()))
    totals["states"] = len(full)
    totals["weighted_matrix_coefficient_slots"] = len(keys)
    # Exact coefficient equality is sufficient for equality of exponential
    # polynomials; no independence of different exponential values is assumed.
    return {
        "schema":"tect/pah-v2-finite-primary/1.0", "status":"PASS",
        "evidence_scope":"EXACT_SINGLE_FINITE_FIXTURE_NOT_UNIVERSAL_PROOF",
        "script_version":__version__, "script_sha256":sha(Path(__file__)),
        "manifest_sha256":sha(MANIFEST), "source_pins":spec["source_pins"],
        "config":p, "counts":dict(totals), "transition_digest":digest.hexdigest(),
        "checks":{name:True for name in ("source_pins", "nonempty_closed_face", "exact_inverse_maps",
                   "mobility_inverse_symmetry", "L1_zero", "exact_gibbs_flux", "functional_gauge_invariance",
                   "orientation_reversing_automorphism", "root_rate_equivariance", "gauge_normalization_by_auto",
                   "weighted_generator_equals_negative_root_gram", "weighted_generator_symmetric")},
        "environment":{"python":platform.python_version(),"platform":platform.platform()},
        "producing_base_commit":"f15c01d1201ff5bdc153bfa2a027cbef563c8f6e",
        "randomness":"NONE", "arithmetic":"fractions.Fraction and formal exponential monomials; exact zero comparison",
        "all_finite_proof_verified":False,
        "non_claims":"No independent author audit, all-regulator machine proof, refinement, limit or physical conclusion."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        # Environment is reported, not mistaken for a mathematical invariant.
        assert {k:v for k,v in prior.items() if k != "environment"} == {k:v for k,v in result.items() if k != "environment"}
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        with OUTPUT.open("w",encoding="utf-8",newline="\n") as stream:
            json.dump(result,stream,indent=2,sort_keys=True)
            stream.write("\n")
    print("PAH-V2-PRIMARY: PASS (exact finite fixture only)")
    print(json.dumps(result["counts"],sort_keys=True))


if __name__ == "__main__":
    main()
