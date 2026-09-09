"""Reproduce PAH-OMC-028 exact controls and compile its universal Lean lemma.

The analytic certificate proves the form-closure result under the inherited
R-511/R-512 hypotheses. PASS here is evidence integrity, rational diagnostics,
and formal verification of the explicitly stated Lean coverage, not a new
measure construction or a PAH-OMC-020 temporal convergence theorem.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/'strategy/pa-hyp/PAH-OMC-028-prereg-v1.json'
CERT=ROOT/'strategy/pa-hyp/PAH-OMC-028-certificate.md'
OTHER=ROOT/'codes/foundations/pah_omc028_independent.py'
LEAN=ROOT/'verification/lean/Tect/PahOmc028Closure.lean'
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc028-closure'
PREREG_SHA='3bb509a383d7b4eba0bb04af1d7d9c37614c3f79f540fd96c09074c34aac81b0'  # Immutable input pin.


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def command(args, env=None):
    p=subprocess.run([str(x) for x in args],cwd=ROOT,env=env,capture_output=True,
                     text=True,encoding='utf-8',timeout=180)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()


def primary(c):
    a=c['test_inputs']
    f,g=[[Q(x) for x in a[k]] for k in ('f','g')]
    pi=[Q(x) for x in a['state_weights']]
    rates=[Q(x) for x in a['directed_rates']]
    def clip(x): return max(Q(0),min(Q(1),x))
    def sub(x,y): return [x[i]-y[i] for i in range(len(x))]
    def energy(h):
        return sum(pi[i]*rates[i]*(h[1-i]-h[i])**2 for i in range(2))/2
    def form_norm_sq(h): return sum(p*x*x for p,x in zip(pi,h))+energy(h)
    d=sub(f,g); e=sub(list(map(clip,f)),list(map(clip,g)))
    assert energy(e)>energy(d)
    assert form_norm_sq(e)>form_norm_sq(d)
    assert energy(list(map(clip,f)))<=energy(f)
    assert energy(list(map(clip,g)))<=energy(g)
    # Exact independently derived expected values are test oracles only.
    assert energy(d)==Q(0) and energy(e)==Q(1)
    assert form_norm_sq(d)==Q(1) and form_norm_sq(e)==Q(3,2)
    return {'mode':'primary','status':'PASS','values':{
        'raw_difference_energy':str(energy(d)),
        'clipped_difference_energy':str(energy(e)),
        'raw_difference_form_norm_sq':str(form_norm_sq(d)),
        'clipped_difference_form_norm_sq':str(form_norm_sq(e))},
        'coverage':'Directed-half root sum, exact rational example; not an infinite-dimensional proof.'}


def compute(cache):
    assert sha(CONTRACT)==PREREG_SHA, 'preregistration drift'
    c=json.loads(CONTRACT.read_text(encoding='utf-8'))
    for rel,digest in c['source_files'].items():
        assert sha(ROOT/rel)==digest, 'source drift: '+rel
    independent=json.loads(command([sys.executable,'-X','utf8',OTHER,'--stdout']))
    hostile=json.loads(command([sys.executable,'-X','utf8',OTHER,'--mode','hostile','--stdout']))
    p=primary(c)
    assert p['values']==independent['values']==hostile['values']
    imports=[]
    for n in ast.walk(ast.parse(OTHER.read_text(encoding='utf-8'))):
        if isinstance(n,ast.Import): imports += [v.name for v in n.names]
        if isinstance(n,ast.ImportFrom): imports.append(n.module or '')
    assert not any('pah_' in s or 'verification' in s for s in imports)
    registry=json.loads((ROOT/'verification/lean/registry.json').read_text(encoding='utf-8'))
    tc=registry['toolchain']
    for key,hkey in [('toolchain_file','toolchain_sha256'),('lakefile','lakefile_sha256'),('lockfile','lockfile_sha256')]:
        assert sha(ROOT/tc[key])==tc[hkey], key
    libraries=[]; revisions={}
    for package in json.loads((ROOT/tc['lockfile']).read_text())['packages']:
        folder=(cache/package['name']).resolve()
        rev=command(['git','-c','safe.directory='+folder.as_posix(),'-C',folder,'rev-parse','HEAD'])
        assert rev==package['rev'], package['name']
        lib=folder/'.lake/build/lib/lean'
        if lib.is_dir(): libraries.append(str(lib))
        revisions[package['name']]=rev
    compiler=Path.home()/'.elan/toolchains'/tc['toolchain'].replace('/','--').replace(':','---')/'bin/lean.exe'
    version=command([compiler,'--version'])
    assert 'version 4.32.1' in version
    lean_text=LEAN.read_text(encoding='utf-8')
    assert not re.search(r'\b(sorry|admit|axiom|unsafe)\b',lean_text)
    env=dict(os.environ);env['LEAN_PATH']=os.pathsep.join(libraries)
    diagnostics=command([compiler,LEAN],env)
    assert not diagnostics, diagnostics
    names=re.findall(r'^theorem\s+(\w+)',lean_text,re.M)
    entry=next(x for x in registry['entrypoints'] if x['path']==LEAN.relative_to(ROOT).as_posix())
    assert entry['sha256']==sha(LEAN) and entry['declarations']==names
    lean={'status':'PASS','compiler_version':version,'compiler_sha256':sha(compiler),
          'source_sha256':sha(LEAN),'declarations':names,'dependencies':revisions,
          'coverage':'Exact counterexamples, arbitrary single root, universal sequence closed-epigraph transfer; closedness and model crosswalk analytic.'}
    integrated={'schema':'tect/pah-omc028-integrated/1.0','status':'PASS',
       'classification':'auxiliary_support','active_gate_change':False,'physical_promotion':False,
       'verdict':'PASS_CONDITIONAL_PROOF_REPAIR','original_omc020_verdict':'HOLD_FOR_EVIDENCE',
       'source_hashes':{**c['source_files'],**{p.relative_to(ROOT).as_posix():sha(p) for p in [CONTRACT,CERT,Path(__file__),OTHER,LEAN]}},
       'primary':p,'independent':independent,'hostile':hostile,'lean':lean,
       'coverage':{'analytic':'Certificate sections 3-6: all normal contractions, full minimal domain, resolvent and semigroup conservation.',
                   'not_formalized':'Weak compactness, Mazur lemma, probability construction and spectral representation.',
                   'negative_scope':'Paired energy/form-distance inequality only, not the Cauchy-image theorem or PAH convergence.'},
       'non_claims':c['non_claims']}
    return {'primary':p,'independent':independent,'hostile':hostile,'integrated':integrated}


def atomic_save(path,blob):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    with os.fdopen(fd,'wb') as f: f.write(blob)
    os.replace(tmp,path)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--lean-cache',type=Path,default=Path('E:/Dev/TECT/verification/lean/.lake/packages'))
    args=parser.parse_args()
    runs=compute(args.lean_cache)
    for name,payload in runs.items():
        blob=(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8')
        path=RUN/(name+'.json')
        if args.check:
            assert path.read_bytes()==blob, 'replay differs: '+str(path)
        else: atomic_save(path,blob)
    print('PAH-OMC-028: PASS conditional closure proof repair; exact primary/independent/hostile controls; '+str(len(runs['integrated']['lean']['declarations']))+' Lean theorems; OMC-020 remains HOLD_FOR_EVIDENCE')
