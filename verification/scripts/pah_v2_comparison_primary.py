#!/usr/bin/env python3
"""Post-adoption full-contract implementation checks, version 1.0.0.

Finite implementation evidence plus a separate all-index admission proof;
sample checks are never a claim of full fine-state enumeration or dynamics.
"""
import argparse
import hashlib
from itertools import permutations
import json
from pathlib import Path
import platform
import subprocess
import sys

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'codes/foundations'))
import pah_v2_morton_crt as m
en = m.en
SPEC = ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-admission-prereg.json'
PIN = 'f3c724535900c56a71a0b66000b34916b12c2981ce1a2b1dd95a63b3e11c34f3'  # INPUT.
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-comparison/primary.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def packed(x):
    return [list(c) for c in (x.aperture,x.occupation,x.phase,x.link)]


def fixture(idx,seed):
    reg = m.regulator(idx)
    occ = [0]*reg.vertices
    for t in range(reg.Q):
        occ[(seed+t*(seed+1))%reg.vertices] += 1
    return en.State(tuple((seed+v)%(reg.M_s+1) for v in range(reg.vertices)),tuple(occ),
                    tuple((seed+v*v+2*v)%reg.K for v in range(reg.vertices)),
                    tuple((seed+3*e+e*e)%reg.K for e in range(len(reg.edges))))


def validate_authority():
    assert sha(SPEC) == PIN
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    operative = spec['operative']
    assert sha(ROOT/operative['path']) == operative['sha256']
    contract = json.loads((ROOT/operative['path']).read_text(encoding='utf-8'))
    for key in ('approval','adopted_bundle','definition'):
        ref = contract[key]
        assert sha(ROOT/ref['path']) == ref['sha256']
    approval = json.loads((ROOT/contract['approval']['path']).read_text(encoding='utf-8'))
    assert approval['approval_received'] is True
    assert approval['mathematical_proof_approved'] is False
    assert approval['addresses']['sha256'] == contract['adopted_bundle']['sha256']
    bundle = json.loads((ROOT/contract['adopted_bundle']['path']).read_text(encoding='utf-8'))
    for path,h in {**bundle['source_pins'],**bundle['evidence_hashes']}.items():
        assert sha(ROOT/path) == h,path
    return spec,contract


def run():
    spec,contract = validate_authority()
    cases = []
    all_orders = list(permutations(range(3)))
    for cfg in spec['fixtures']:
        co = m.Index(*cfg['co'],cfg['q0'],cfg['m0'])
        fi = m.Index(*cfg['fi'],cfg['q0'],cfg['m0'])
        for seed in spec['seeds']:
            x = fixture(fi,seed)
            images = [m.project_to(x,fi,co,order) for order in all_orders]
            assert len(set(images)) == 1
            y = fixture(co,seed)
            jy,at = y,co
            for axis in range(3):
                while (at.r,at.h,at.N)[axis] < cfg['fi'][axis]:
                    jy = m.inject(jy,at,axis)
                    at = at.step(axis)
            assert m.project_to(jy,fi,co) == y
            g = tuple((seed+5*v+1)%m.regulator(fi).K for v in range(m.regulator(fi).vertices))
            gg,at = g,fi
            for axis in (2,1,0):
                while (at.r,at.h,at.N)[axis] > cfg['co'][axis]:
                    gg = m.gauge_project(gg,at,axis)
                    at = at.step(axis,-1)
            pgx = m.project_to(m.gauge(x,fi,g),fi,co)
            assert pgx == m.gauge(images[0],co,gg)
            cases.append({'config':cfg,'seed':seed,'x':packed(x),'px':packed(images[0]),
                          'y':packed(y),'Jy':packed(jy),'g':g,'pgx':packed(pgx)})
    # All adjacent interleavings on the prescribed mixed corner, not just
    # three-axis block orders. This remains one bounded implementation check.
    cfg = spec['fixtures'][1]
    fi = m.Index(*cfg['fi'],cfg['q0'],cfg['m0'])
    co = m.Index(*cfg['co'],cfg['q0'],cfg['m0'])
    word = tuple(axis for axis in range(3) for _ in range(cfg['fi'][axis]-cfg['co'][axis]))
    words = sorted(set(permutations(word)))
    for seed in spec['seeds']:
        x = fixture(fi,seed)
        expected = m.project_to(x,fi,co)
        for order in words:
            z,at = x,fi
            for axis in order:
                z = m.project(z,at,axis)
                at = at.step(axis,-1)
            assert at == co and z == expected
    cfg = spec['root_base']
    co = m.Index(*cfg['co'],cfg['q0'],cfg['m0'])
    root_cases = []
    for axis in cfg['axes']:
        fi = co.step(axis)
        x = fixture(fi,cfg['seed'])
        px = m.project(x,fi,axis)
        paired = set()
        labels = []
        for s,y in en.incidences(m.regulator(fi),x):
            a = m.assign_root(x,fi,axis,s)
            back = m.assign_root(y,fi,axis,s.inverse())
            assert back == (a.inverse() if a is not None else None)
            if a is not None:
                assert en.apply_move(m.regulator(co),px,a) == m.project(y,fi,axis)
                paired.add(a)
            labels.append({'label':[s.family,s.cell,s.sign],
                           'assigned':[a.family,a.cell,a.sign] if a else None})
        unmatched = {s for s,_ in en.incidences(m.regulator(co),px)}-paired
        root_cases.append({'config':{'co':[co.r,co.h,co.N],'fi':[fi.r,fi.h,fi.N],
                                      'q0':co.q0,'m0':co.m0},'axis':axis,'x':packed(x),
                           'labels':labels,'unmatched_coarse':sorted([s.family,s.cell,s.sign] for s in unmatched)})
    replay = []
    for name in ('pah_v2_morton_crt_primary.py','pah_v2_morton_crt_independent.py'):
        cmd = [sys.executable,'-X','utf8',str(ROOT/'verification/scripts'/name),'--check']
        proc = subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=120)
        assert proc.returncode == 0,proc.stdout+proc.stderr
        replay.append({'script':name,'exit_code':proc.returncode,'stdout':proc.stdout.strip()})
    return {'schema':'tect/pah-v2-comparison-primary/1.0','status':'PASS_FINITE_DEFINITION_CHECKS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'spec_sha256':PIN,'operative':spec['operative'],'approval':contract['approval'],
            'cases':cases,'axis_orders':all_orders,'interleavings':words,
            'root_cases':root_cases,'development_replay':replay,
            'counts':{'state_cases':len(cases),'axis_order_comparisons':len(cases)*len(all_orders),
                      'interleaving_checks':len(words)*len(spec['seeds']),
                      'root_incidences':sum(len(c['labels']) for c in root_cases)},
            'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'scope':'Finite exact implementation checks of the approved definitions, not an all-index proof by enumeration.',
            'non_claims':spec['non_claims']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    if args.check:
        old = json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'} == {k:v for k,v in result.items() if k!='environment'}
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PAH-V2-COMPARISON PRIMARY: PASS',result['counts'])


if __name__ == '__main__':
    main()
