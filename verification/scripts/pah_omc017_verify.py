"""Replay exact PAH-OMC-017 audit lanes and the pinned Lean ratio bridge.

The analytic spectral and measure proof is in the pinned certificates, not
replaced by these runs. --check writes only to a temporary directory and
requires exact agreement with stored evidence. No remote theorem is run.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

__version__='1.0.1'
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'strategy/pa-hyp/PAH-OMC-017-result-v1.json'
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc017-cauchy-v2'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def compute(folder):
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    checks=[]
    def check(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True,'actual':bool(ok),'expected':True})
    for file,pin in m['source_files'].items(): check('pin:'+file,sha(ROOT/file)==pin)
    c=json.loads((ROOT/m['preregistration']).read_text())
    for file,pin in c['sources'].items(): check('parent:'+file,sha(ROOT/file)==pin)
    def lane(name):
        suffix='' if name=='primary' else '_'+name
        script=ROOT/f'codes/foundations/pah_omc017_transfer{suffix}.py'
        dest=folder/f'{name}.json'
        p=subprocess.run([sys.executable,'-X','utf8',str(script),'--output',str(dest)],
            cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120)
        if p.returncode: raise RuntimeError(p.stdout+p.stderr)
        return name,json.loads(dest.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        lanes=dict(pool.map(lane,('primary','independent','hostile')))
    for name,data in lanes.items(): check(name+' executed',data['status']=='PASS' and bool(data['checks']) and all(x['pass'] for x in data['checks']))
    check('nonimporting exact energy match',lanes['primary']['fixtures']==lanes['independent']['fixtures'])
    check('independent constants match',lanes['primary']['constants']==lanes['independent']['constants']==m['proof_constants'])
    # TEST ORACLES: Lean statements encode these separately. Proof constants
    # above are derived twice from the source, never read from these oracles.
    oracles={'column_box':'149/24','split_box':'163/8','kernel_box_cost':'319/12','radius_lower_prefactor':'256'}
    check('derived inputs to Lean bridge',all(m['proof_constants'][k]==v for k,v in oracles.items()))
    check('scope firewall',not m['active_gate_change'] and not m['physical_promotion'] and m['classification']=='auxiliary_support')
    reg=json.loads((ROOT/'verification/lean/registry.json').read_text())
    path=m['lean']['path']; entry=next(e for e in reg['entrypoints'] if e['path']==path)
    source=(ROOT/path).read_text()
    check('Lean pin',entry['sha256']==sha(ROOT/path))
    names=re.findall(r'(?m)^theorem\s+([A-Za-z0-9_]+)',source)
    check('Lean declaration coverage',names==entry['declarations']==m['lean']['declarations'])
    check('Lean policy',not any(t in source for t in ('sorry','admit','axiom','unsafe')) and b'\r' not in (ROOT/path).read_bytes())
    tc=reg['toolchain']
    for key in ('toolchain_file','lakefile','lockfile'):
        hk='toolchain_sha256' if key=='toolchain_file' else key+'_sha256'
        check('toolchain:'+key,sha(ROOT/tc[key])==tc[hk])
    encoded=tc['toolchain'].replace('/','--').replace(':','---')
    lake=Path.home()/'.elan/toolchains'/encoded/'bin/lake.exe'
    p=subprocess.run([str(lake),'env','lean','Tect/PahOmc017.lean'],cwd=ROOT/'verification/lean',
        text=True,encoding='utf-8',capture_output=True,timeout=600)
    diagnostics=(p.stdout+p.stderr).strip()
    check('Lean fresh diagnostics-free',p.returncode==0 and not diagnostics)
    return {'schema':'tect/pah-omc017-integrated/1.0','result_id':m['result_id'],'status':'PASS',
        'checks':checks,'code_sha256':sha(Path(__file__)),'code_version':__version__,
        'manifest_sha256':sha(MANIFEST),'base_commit':m['base_commit'],
        'environment':{'python':platform.python_version(),'sympy':__import__('sympy').__version__},
        'proof_constants':m['proof_constants'],'coverage':m['proof_coverage'],
        'lane_counts':{k:len(v['checks']) for k,v in lanes.items()},
        'run_hashes':{k:sha(folder/f'{k}.json') for k in lanes},
        'lean':{'status':'PASS','output':diagnostics,'command':'lake env lean Tect/PahOmc017.lean',
            'source_sha256':sha(ROOT/path),'toolchain':tc},
        'conclusion':m['conclusion'],'non_claims':m['non_claims']}


def main(check_only):
    if check_only:
        with tempfile.TemporaryDirectory(prefix='pah017-replay-') as tmp:
            folder=Path(tmp); result=compute(folder)
            assert json.loads((RUN/'integrated.json').read_text())==result,'integrated replay mismatch'
            for name in ('primary','independent','hostile'):
                assert (folder/f'{name}.json').read_bytes()==(RUN/f'{name}.json').read_bytes(),name+' replay mismatch'
    else:
        result=compute(RUN)
        RUN.mkdir(parents=True,exist_ok=True)
        (RUN/'integrated.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f"PAH-OMC-017 INTEGRATED: PASS ({len(result['checks'])} checks; Lean PASS; replay={check_only})")


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true')
    main(parser.parse_args().check)
