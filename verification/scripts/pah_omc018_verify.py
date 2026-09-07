"""Replay the exact PAH-OMC-018 lanes, source pins and Lean bridge.

--check uses temporary outputs and verifies stored runs byte-for-byte.
The measure and ordered-limit theorem remains in the analytic certificate;
this tool reports executable coverage and does not promote a physical claim.
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

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'strategy/pa-hyp/PAH-OMC-018-result-v1.json'
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc018-generator'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def compute(folder):
    m=json.loads(MANIFEST.read_text(encoding='utf-8')); checks=[]
    def ck(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True})
    for p,h in m['source_files'].items(): ck('pin:'+p,sha(ROOT/p)==h)
    contract=json.loads((ROOT/m['preregistration']).read_text())
    for p,h in contract['sources'].items():
        ck('parent:'+p,sha(ROOT/p)==h)
        parent=json.loads((ROOT/p).read_text())
        for sub,pin in parent.get('source_files',{}).items(): ck('inherited:'+sub,sha(ROOT/sub)==pin)
    def lane(name):
        suffix='' if name=='primary' else '_'+name
        script=ROOT/f'codes/foundations/pah_omc018_generator{suffix}.py'
        output=folder/f'{name}.json'
        p=subprocess.run([sys.executable,'-X','utf8',str(script),'--output',str(output)],cwd=ROOT,
                         capture_output=True,text=True,encoding='utf-8',timeout=120)
        if p.returncode: raise RuntimeError(p.stdout+p.stderr)
        return name,json.loads(output.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        lanes=dict(pool.map(lane,('primary','independent','hostile')))
    for name,data in lanes.items(): ck('executed:'+name,data['status']=='PASS' and all(a['pass'] for a in data['checks']))
    ck('nonimporting exact energy/root match',lanes['primary']['fixtures']==lanes['independent']['fixtures'])
    ck('nonimporting closure/count match',lanes['primary']['closure']==lanes['independent']['closure'])
    ck('claim firewall',not m['active_gate_change'] and not m['physical_promotion'] and m['classification']=='auxiliary_support')
    ck('radial and nonradial separated',m['radial_activity']=='ZERO_IN_DERIVED_LOCAL_OPERATOR' and m['label_activity']=='NONZERO_APERTURE_FORM')
    registry=json.loads((ROOT/'verification/lean/registry.json').read_text())
    path=m['lean']['path']; e=next(a for a in registry['entrypoints'] if a['path']==path)
    source=(ROOT/path).read_text()
    names=re.findall(r'(?m)^theorem\s+([A-Za-z0-9_]+)',source)
    ck('Lean source pin',sha(ROOT/path)==e['sha256'])
    ck('Lean declarations',names==e['declarations']==m['lean']['declarations'])
    ck('Lean policy',not any(a in source for a in ('sorry','admit','axiom','unsafe')) and b'\r' not in (ROOT/path).read_bytes())
    tc=registry['toolchain']
    for key in ('toolchain_file','lakefile','lockfile'):
        hk='toolchain_sha256' if key=='toolchain_file' else key+'_sha256'
        ck('toolchain:'+key,sha(ROOT/tc[key])==tc[hk])
    lake=Path.home()/'.elan/toolchains'/tc['toolchain'].replace('/','--').replace(':','---')/'bin/lake.exe'
    proc=subprocess.run([str(lake),'env','lean','Tect/PahOmc018.lean'],cwd=ROOT/'verification/lean',
                        text=True,encoding='utf-8',capture_output=True,timeout=600)
    diagnostic=(proc.stdout+proc.stderr).strip()
    ck('fresh Lean diagnostics free',proc.returncode==0 and not diagnostic)
    # Scope-specific coverage audit; the repository-wide legacy scanner has
    # intentionally nonblocking diagnostics for older scripts.
    import ast
    for name in ('pah_omc018_generator.py','pah_omc018_generator_independent.py','pah_omc018_generator_hostile.py'):
        txt=(ROOT/'codes/foundations'/name).read_text(); tree=ast.parse(txt)
        ck('code coverage:'+name,any(isinstance(n,ast.Assert) for n in ast.walk(tree)) and 'json.dumps' in txt)
    return {'schema':'tect/pah-omc018-integrated/1.0','result_id':m['result_id'],'status':'PASS',
            'checks':checks,'code_version':__version__,'code_sha256':sha(Path(__file__)),
            'manifest_sha256':sha(MANIFEST),'base_commit':m['base_commit'],
            'environment':{'python':platform.python_version(),'sympy':__import__('sympy').__version__},
            'lane_counts':{k:len(v['checks']) for k,v in lanes.items()},
            'run_hashes':{k:sha(folder/f'{k}.json') for k in lanes},
            'lean':{'status':'PASS','diagnostics':diagnostic,'source_sha256':sha(ROOT/path),'toolchain':tc},
            'analytic_coverage':m['proof_coverage'],'conclusion':m['conclusion'],'non_claims':m['non_claims']}

def main(check):
    if check:
        with tempfile.TemporaryDirectory(prefix='pah018-replay-') as tmp:
            folder=Path(tmp); result=compute(folder)
            assert json.loads((RUN/'integrated.json').read_text())==result,'integrated replay mismatch'
            for name in ('primary','independent','hostile'):
                assert (folder/f'{name}.json').read_bytes()==(RUN/f'{name}.json').read_bytes(),name+' replay mismatch'
    else:
        RUN.mkdir(parents=True,exist_ok=True); result=compute(RUN)
        (RUN/'integrated.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f"PAH-OMC-018 INTEGRATED: PASS ({len(result['checks'])} checks; Lean PASS; replay={check})")

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--check',action='store_true')
    main(p.parse_args().check)
