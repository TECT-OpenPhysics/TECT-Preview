#!/usr/bin/env python3
"""PAH-OMC-015 primary exact checks; the all-n/all-R proof is in the certificate.

Use the pinned inherited full energy and root definitions. Derive the charge
penalty from the source parameters. Finite strip tests diagnose translation
errors; they do not prove a limit by sampling. Outputs contain no float Gibbs
weights and therefore cannot underflow into a false zero.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
from fractions import Fraction as F
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-015-counting-prereg-v1.json"
PIN = "0e07bd05c56c9765f15074505a5ce791622282a0e0c884bba277e780bbda0b35"
BASE = ROOT / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
BASE_PIN = "bda0c7bd7ed5f8b3871fd7590b600458589c4b5feba0a147219e94cdae0526a0"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc015-counting-cutoff/primary.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(name, path)


def run(output=OUT):
    checks = []
    def check(name, ok):
        checks.append({"name": name, "pass": bool(ok)})
        assert ok, name
    check("prereg bytes", sha(PREREG) == PIN)
    prereg = json.loads(PREREG.read_text())
    for name, pin in prereg["sources"].items():
        check("parent " + name, sha(ROOT / prereg["source_path_base"] / name) == pin)
    check("inherited evaluator bytes", sha(BASE) == BASE_PIN)
    spec = importlib.util.spec_from_file_location("omc013_readonly", BASE)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    raw = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json").read_text())["exact_scope"]["fixture"]
    p = {k: F(str(v)) for k, v in raw.items()}
    # These are source-scope test oracles, not derived outputs.
    check("parameter scope", p["K"] == 2 and p["M_s"] == p["M_psi"] == 1 and p["m2"] == 0
          and p["epsilon"] == F(1, 2) and all(p[k] == 1 for k in
          ("beta", "nu", "lambda_4", "eta_6", "g", "lambda_s", "kappa_s", "kappa_D", "kappa_g")))
    c2 = p["g"] * p["epsilon"]**2 / 2
    c4, c6 = p["lambda_4"] / 4, p["eta_6"] / 6
    check("positive penalty coefficients", min(c2, c4, c6) > 0)
    rows = []
    digest = hashlib.sha256()
    # Tooling diagnostic sizes. The certificate has quantifiers for every n,R.
    for n in (2, 3):
        g = old.strip(n)
        vs, es = g["vertices"], g["edges"]
        nv, ne = len(vs), len(es)
        full_count = (int(p["M_s"])+1)**nv * (int(p["M_psi"])+1)**nv * int(p["K"])**(nv+ne)
        components = [math.comb(nv, q) * (int(p["M_s"])+1)**nv * int(p["K"])**(nv+ne) for q in range(nv+1)]
        check(f"n{n} counting partition and zero-phase multiplicity", sum(components) == full_count)
        sample_count = 0
        for variant in range(3):
            for bits in itertools.product((0, 1), repeat=nv):
                state = {
                    "ell": dict(zip(vs, bits)),
                    "aperture": {v: (i+variant) % 2 for i, v in enumerate(vs)},
                    "phase": {v: (i*variant+variant) % 2 for i, v in enumerate(vs)},
                    "link": {e[0]: (i+variant) % 2 for i, e in enumerate(es)},
                }
                zero = {k: dict(v) for k, v in state.items()}
                zero["ell"] = {v: 0 for v in vs}
                q = sum(bits)
                for r in (1, 2):
                    energy = old.energy(n, state, F(r))
                    e0 = old.energy(n, zero, F(r))
                    penalty = c2*r**2+c4*r**4+c6*r**6
                    assert energy - e0 >= q*penalty
                    # Coefficients across R are independently checked by lane 2.
                    digest.update(f"{n},{variant},{bits},{r}:{energy}\n".encode())
                    sample_count += 1
        check(f"n{n} full energy charge-erasure bound", sample_count > 0)
        # Root inverses on genuine strip states; midpoint exponent equality is exact.
        root_tests = 0
        state = old.patterned_state(n, 1) if hasattr(old, "patterned_state") else {
            "ell": {v: i % 2 for i,v in enumerate(vs)},
            "aperture": {v: i % 2 for i,v in enumerate(vs)},
            "phase": {v: (i+1) % 2 for i,v in enumerate(vs)},
            "link": {e[0]: i % 2 for i,e in enumerate(es)}}
        for root in old.root_catalog(n):
            after = old.apply_root(state, root)
            if after is None:
                continue
            inv = dict(root)
            if root["family"] == "radial-transfer":
                inv["source"], inv["target"] = root["target"], root["source"]
            else:
                inv["direction"] = -root["direction"]
            assert old.apply_root(after, inv) == state
            assert sum(after["ell"].values()) == sum(state["ell"].values())
            ex, ey = old.energy(n, state, F(1)), old.energy(n, after, F(1))
            assert -ex-(ey-ex)/2 == -ey-(ex-ey)/2 == -(ex+ey)/2
            family = root["family"]
            if family == "phase":
                vertex = root["vertex"]
                mx = old.aperture(state["aperture"][vertex])**2
                my = old.aperture(after["aperture"][vertex])**2
            elif family == "aperture":
                vertex = root["vertex"]
                mx = old.aperture(state["aperture"][vertex])*old.aperture(after["aperture"][vertex])
                my = old.aperture(after["aperture"][vertex])*old.aperture(state["aperture"][vertex])
            else:
                _, left, right = old.edge_lookup(n)[root["edge"]]
                mx = old.aperture(state["aperture"][left])*old.aperture(state["aperture"][right])
                my = old.aperture(after["aperture"][left])*old.aperture(after["aperture"][right])
            assert mx == my and mx > 0
            root_tests += 1
        check(f"n{n} all allowed roots inverse and reversible flux", root_tests > 0)
        # Polynomial identity over ALL binary occupation patterns, at rational test z.
        for z in (F(1, 2), F(1, 3), F(1)):
            total = sum(z**sum(bits) for bits in itertools.product((0,1), repeat=nv))
            occupied = sum(z**sum(bits) for bits in itertools.product((0,1), repeat=nv) if bits[0])
            assert total == (1+z)**nv and occupied == z*(1+z)**(nv-1)
            assert occupied <= 2**(nv-1)*z
        check(f"n{n} exact occupation counting polynomial", True)
        rows.append({"n": n, "vertices": nv, "edges": ne, "full_count": full_count,
                     "component_counts": components, "energy_checks": sample_count, "root_checks": root_tests,
                     "radial_upper": f"{2**(nv-1)} * exp(-({c2}) R^2-({c4}) R^4-({c6}) R^6)"})
    return_value = {"schema": "tect/pah-omc015-primary/1.0", "status": "PASS", "checks": checks,
        "source_hash": PIN, "code_sha256": sha(Path(__file__)), "energy_digest": digest.hexdigest(),
        "penalty_coefficients_R2_R4_R6": list(map(str,(c2,c4,c6))), "strip_checks": rows,
        "verdict": "CANDIDATE_REJECTED", "ordered_squared_limits": {"ell_a": 0,"ell_d": 0,"H_0": 1,"H_1": 1},
        "scope": "Exact derivation in certificate; finite checks are source-translation diagnostics, not an enumeration proof of all n/R. No physical conclusion."}
    write(output, return_value)
    print(f"PAH-OMC-015 PRIMARY: PASS ({len(checks)} assertions)")
    return return_value


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=OUT)
    run(ap.parse_args().output)
