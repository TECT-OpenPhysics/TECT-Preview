"""Independent matrix and hostile exact checks of the R-530 closure repair.

This code does not prove Hilbert weak compactness. It independently checks
the stated algebra and rejection controls with rational arithmetic. Inputs
come from the immutable OMC-028 preregistration; no PAH model is constructed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'strategy/pa-hyp/PAH-OMC-028-prereg-v1.json'


def compute(mode):
    c = json.loads(CONTRACT.read_text(encoding='utf-8'))
    a = c['test_inputs']
    f, g = [[Q(x) for x in a[key]] for key in ('f', 'g')]
    pi = [Q(x) for x in a['state_weights']]
    rate = [Q(x) for x in a['directed_rates']]
    # Independent generator construction: no import of the root-sum checker.
    L = [[-rate[0], rate[0]], [rate[1], -rate[1]]]
    def dot(x, y): return sum(pi[i]*x[i]*y[i] for i in range(len(pi)))
    def energy(x):
        y = [sum(L[i][j]*x[j] for j in range(len(x))) for i in range(len(x))]
        return -dot(x, y)
    def sub(x, y): return [a-b for a, b in zip(x, y)]
    # Piecewise clipping, independent of min/max in the primary code.
    def eta(x): return Q(0) if x < 0 else (Q(1) if x > 1 else x)
    d = sub(f, g); e = sub(list(map(eta, f)), list(map(eta, g)))
    common = {'raw_difference_energy': str(energy(d)),
              'clipped_difference_energy': str(energy(e)),
              'raw_difference_form_norm_sq': str(dot(d,d)+energy(d)),
              'clipped_difference_form_norm_sq': str(dot(e,e)+energy(e))}
    assert pi[0]*rate[0] == pi[1]*rate[1]
    assert sum(pi) == 1
    assert energy(e) > energy(d)
    assert dot(e,e)+energy(e) > dot(d,d)+energy(d)
    # Reproduction oracles, never substitutes for the matrix computation.
    assert energy(d) == 0 and energy(e) == 1
    assert dot(e,e)+energy(e) == Q(3,2)
    checks = ['detailed_balance', 'probability_normalization',
              'paired_energy_counterexample', 'paired_form_norm_counterexample']
    controls = {}
    if mode == 'independent':
        for x in (f, g, [Q(1),Q(1)]):
            assert energy(list(map(eta,x))) <= energy(x)
        # Resolvent conservation by solving a 2x2 system with rational entries.
        lam = Q(1)  # Diagnostic input; not a PAH time or parameter selection.
        A = [[Q(i==j)-lam*L[i][j] for j in range(2)] for i in range(2)]
        determinant = A[0][0]*A[1][1]-A[0][1]*A[1][0]
        one_resolvent = [(A[1][1]-A[0][1])/determinant,
                        (A[0][0]-A[1][0])/determinant]
        assert one_resolvent == [Q(1), Q(1)]
        checks += ['single_vector_energy_contraction', 'constant_resolvent_identity']
    else:
        # Each control shows exactly why a tempting missing premise matters.
        assert not (energy(e) <= energy(d))
        controls['paired_energy_contraction_rejected'] = common
        x = [Q(0),Q(2)]; y = list(map(eta,x))
        assert -energy(y) > -energy(x)
        controls['negative_conductance_rejected'] = [str(-energy(y)),str(-energy(x))]
        assert energy([2*t for t in x]) > energy(x)
        controls['non_normal_map_rejected'] = [str(energy([2*t for t in x])),str(energy(x))]
        # Exact spike integrals from R-512's nonclosable evaluation control.
        controls['without_closedness'] = {
            'spike':'s_n(x)=max(1-n*x,0) on [0,1]',
            'L2_sq_formula':'1/(3*n)',
            'closability':'s_n -> 0, q(s_n-s_m)=0, q(s_n)=1',
            'lsc_witness':'u_n=1-s_n -> 1, q(u_n)=0<q(1)=1',
            'spike_alone_violates_lsc_at_zero':False}
        for n in (1,2,4):  # Tooling controls, not an asymptotic numerical proof.
            endpoint=Q(1,n)
            spike_L2=endpoint-n*endpoint**2+Q(n*n,3)*endpoint**3
            assert spike_L2==Q(1,3*n) and 0 < spike_L2 <= Q(1,3)
            spike_at_zero=Q(1)-n*Q(0)
            assert (Q(1)-spike_at_zero)**2 < Q(1)**2
        # Scalar killed form q(v)=v^2: J_1 1=1/2, despite sub-Markov property.
        killed_resolvent = Q(1)/(1+Q(1))
        assert 0 < killed_resolvent < 1
        controls['without_zero_constant_energy'] = str(killed_resolvent)
        checks += list(controls)
    return {'mode':mode,'status':'PASS','values':common,'checks':checks,
            'controls':controls,'contract_sha256':hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            'coverage':'Exact algebra and controls only; universal closure proof is analytic and Lean epigraph transfer.',
            'physical_promotion':False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['independent','hostile'],default='independent')
    p.add_argument('--stdout',action='store_true',help='Orchestrator returns JSON without writing a run')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    blob=(json.dumps(compute(a.mode),sort_keys=True,indent=2)+'\n').encode('utf-8')
    path=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc028-closure'/(a.mode+'.json')
    if a.check:
        assert path.read_bytes()==blob
    elif not a.stdout:
        path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
        with os.fdopen(fd,'wb') as stream: stream.write(blob)
        os.replace(tmp,path)
    print(blob.decode('utf-8'),end='')
