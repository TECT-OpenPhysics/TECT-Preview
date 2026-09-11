#!/usr/bin/env python3
"""Non-importing PAH-v2 matrix cross-check, version 0.1.0 (2026-09-11).

Uses a flattened tuple encoding, vectorized field evaluation, explicit group
orbits and independently assembled weighted adjoint matrices. Imports neither
the primary script nor the frozen enumerator. Same author: implementation
independence is not an external-person mathematical audit. Floating matrix
checks are corroboration; the all-finite exact proof is a separate document.
"""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import numpy as np

__version__ = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-v2-finite-audit-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-finite/independent.json"
PIN = "531697fa28c5f2e7f4177b42bc12ebd8fc1ffb7e9790d07063082e0ec3d6a331"  # INPUT provenance
RTOL, ATOL = 1e-11, 1e-14  # Tooling floating-point check thresholds, not proof bounds.


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def audit():
    assert sha(MANIFEST) == PIN
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for p,h in manifest["source_pins"].items():
        assert sha(ROOT/p) == h
    p = manifest["primary_fixture_inputs"]
    from fractions import Fraction
    val = lambda k: float(Fraction(p[k]))
    V, K = p["vertices"],p["K"]
    edges = p["edges"]
    E = len(edges)
    assert K == 2 and val("nu") == 2
    ranges = [range(p["M_s"]+1)]*V + [range(p["M_psi"]+1)]*V + [range(K)]*(V+E)
    tuples = [x for x in product(*ranges) if sum(x[V:2*V]) == p["Q"]]
    X = np.array(tuples,dtype=np.int64)
    N = len(X)
    index = {x:i for i,x in enumerate(tuples)}
    s = val("epsilon") + X[:,:V]*(1-val("epsilon"))/p["M_s"]
    psi = val("R_max")*X[:,V:2*V]/p["M_psi"]*(-1.0)**X[:,2*V:3*V]
    U = (-1.0)**X[:,3*V:]
    onsite = (val("lambda_s")*(s-1)**2/2 + val("m2")*psi**2/2 + val("lambda_4")*psi**4/4
              + val("eta_6")*psi**6/6 + val("g")*s*s*psi*psi/2).sum(axis=1)
    energy = onsite.copy()
    stiffness = []
    for e,(a,b) in enumerate(edges):
        J = 2/(s[:,a]+s[:,b])
        stiffness.append(J)
        energy += val("kappa_s")*(s[:,a]-s[:,b])**2/2
        energy += val("kappa_D")*J*(psi[:,b]-U[:,e]*psi[:,a])**2/2
    for face in p["faces"]:
        assert face
        hol = np.ones(N)
        for e,sign in face:
            hol *= U[:,e]**sign
        energy += val("kappa_g")*sum(stiffness[e] for e,_ in face)/len(face)*(1-hol)
    weights = np.exp(-val("beta")*energy)
    assert np.all(weights > 0) and np.isfinite(weights.sum())
    pi = weights/weights.sum()
    L,gram = np.zeros((N,N)),np.zeros((N,N))
    roots = [(family,cell,sign) for family in range(4)
             for cell in range(V if family in (0,3) else E) for sign in (-1,1)]
    transitions = 0
    inverse_checks = 0
    for family,cell,sign in roots:
        Y = X.copy()
        if family == 0:
            Y[:,2*V+cell] = (Y[:,2*V+cell]+sign)%K
        elif family == 1:
            a,b = edges[cell]
            Y[:,V+a] -= sign
            Y[:,V+b] += sign
        elif family == 2:
            Y[:,3*V+cell] = (Y[:,3*V+cell]+sign)%K
        else:
            Y[:,cell] += sign
        mask = np.all((Y[:,:V]>=0)&(Y[:,:V]<=p["M_s"]),axis=1)
        mask &= np.all((Y[:,V:2*V]>=0)&(Y[:,V:2*V]<=p["M_psi"]),axis=1)
        ii = np.flatnonzero(mask)
        jj = np.array([index[tuple(y)] for y in Y[mask]])
        if family == 0:
            mobility = s[ii,cell]**val("nu")
        elif family == 3:
            mobility = (s[ii,cell]*s[jj,cell])**(val("nu")/2)
        else:
            a,b = edges[cell]
            mobility = (s[ii,a]*s[ii,b])**(val("nu")/2)
        rate = mobility*np.exp(-val("beta")*(energy[jj]-energy[ii])/2)
        assert np.all(rate > 0)
        np.add.at(L,(ii,jj),rate)
        np.add.at(L,(ii,ii),-rate)
        # Direct root-row sqrt and weighted Gram, not an assumed Laplacian.
        bcoef = np.sqrt(rate/2)
        root_w = pi[ii]*bcoef*bcoef
        for aa,bb,sgn in ((ii,ii,1),(jj,jj,1),(ii,jj,-1),(jj,ii,-1)):
            np.add.at(gram,(aa,bb),sgn*root_w)
        transitions += len(ii)
        Z = Y[mask].copy()
        if family == 0:
            Z[:,2*V+cell] = (Z[:,2*V+cell]-sign)%K
        elif family == 1:
            a,b = edges[cell]
            Z[:,V+a] += sign
            Z[:,V+b] -= sign
        elif family == 2:
            Z[:,3*V+cell] = (Z[:,3*V+cell]-sign)%K
        else:
            Z[:,cell] -= sign
        assert np.array_equal(Z,X[mask])
        inverse_checks += len(ii)
    errors = {}

    def close(name,A,B):
        errors[name] = float(np.max(np.abs(A-B)))
        assert np.allclose(A,B,rtol=RTOL,atol=ATOL), (name,errors[name])

    close("L1",L.sum(axis=1),np.zeros(N))
    close("detailed_balance",pi[:,None]*L,(pi[:,None]*L).T)
    close("BstarB_weighted",gram,-pi[:,None]*L)
    # Full finite group action and its uniform orbit projection.
    group_maps = []
    for flip in (False,True):
        perm = list(range(V)) if not flip else [0,2,1]  # INPUT source fixture automorphism
        for gauge in product(range(K),repeat=V):
            Y = X.copy()
            Y[:,2*V:3*V] = (Y[:,2*V:3*V]+np.array(gauge))%K
            for e,(a,b) in enumerate(edges):
                Y[:,3*V+e] = (Y[:,3*V+e]+gauge[b]-gauge[a])%K
            Z = np.empty_like(Y)
            for block in range(3):
                for v in range(V):
                    Z[:,block*V+perm[v]] = Y[:,block*V+v]
            for e,(a,b) in enumerate(edges):
                mapped = [perm[a],perm[b]]
                if mapped in edges:
                    dest,sign = edges.index(mapped),1
                else:
                    dest,sign = edges.index(list(reversed(mapped))),-1
                Z[:,3*V+dest] = sign*Y[:,3*V+e]%K
            h = np.array([index[tuple(z)] for z in Z])
            assert len(set(map(int,h))) == N
            close("group_energy",energy[h],energy)
            close("group_generator",L[np.ix_(h,h)],L)
            group_maps.append(h)
    P = np.zeros((N,N))
    for h in group_maps:
        P[np.arange(N),h] += 1/len(group_maps)
    orbits, seen = [],set()
    for i in range(N):
        if i in seen:
            continue
        orbit = sorted({int(h[i]) for h in group_maps})
        assert not (set(orbit)&seen)
        seen.update(orbit)
        orbits.append(orbit)
        close("orbit_uniformity",P[np.ix_(orbit,orbit)],np.full((len(orbit),len(orbit)),1/len(orbit)))
        assert np.all(np.count_nonzero(P[orbit],axis=1) == len(orbit))
    assert len(seen) == N
    close("projection_self_adjoint",pi[:,None]*P,(pi[:,None]*P).T)
    # Orbit blocks prove P^2=P exactly as a finite counting identity. For PL
    # and LP, use independent row and column orbit sums, not a precondition.
    PL,LP = np.empty_like(L),np.empty_like(L)
    for orbit in orbits:
        PL[orbit,:] = L[orbit,:].mean(axis=0)
        LP[:,orbit] = L[:,orbit].mean(axis=1)[:,None]
    close("projection_commutation",PL,LP)
    assert len(roots) == len(set(roots))
    return {"schema":"tect/pah-v2-finite-independent/1.0","status":"PASS",
            "script_version":__version__,"script_sha256":sha(Path(__file__)),"manifest_sha256":sha(MANIFEST),
            "scope":"SINGLE_FIXED_FINITE_FIXTURE_FLOATING_MATRIX_CORROBORATION",
            "implementation_independence":"No primary or enumerator import; flattened states and explicit group orbit projection; same author, not an external audit",
            "states":N,"valid_incidences":transitions,"inverse_checks":inverse_checks,"orbits":len(orbits),
            "checks":{"inverse_validity":True,"L1":True,"detailed_balance":True,"projection_idempotent_orbit_blocks":True,
                      "projection_self_adjoint":True,"projection_commutation":True,"BstarB":True},
            "max_absolute_residuals":errors,"tolerance":{"rtol":RTOL,"atol":ATOL},
            "min_pi":float(pi.min()),"max_pi":float(pi.max()),
            "environment":{"python":platform.python_version(),"numpy":np.__version__,"platform":platform.platform()},
            "all_finite_proof_verified":False,"randomness":"NONE",
            "non_claims":"Floating cross-checks are not exact universal proofs; no refinement, limit or physical promotion."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=audit()
    if args.check:
        prior=json.loads(OUTPUT.read_text())
        for k in ("script_sha256","manifest_sha256","states","valid_incidences","orbits","checks"):
            assert prior[k] == result[k],k
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        with OUTPUT.open("w",encoding="utf-8",newline="\n") as f:
            json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
    print("PAH-V2-INDEPENDENT: PASS (finite floating matrix cross-check only)")
    print(json.dumps(result["max_absolute_residuals"],sort_keys=True))


if __name__ == "__main__":
    main()
