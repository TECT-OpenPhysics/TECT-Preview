"""Replay PAH-OMC-019 source, analytic-identity and universal Lean checks.

Use --lean-cache for an existing read-only .lake/packages cache when running
in an isolated worktree. No dependency update, download or shared build is run.
--check regenerates runs in temporary storage and compares exact JSON bytes.
"""
from __future__ import annotations
import argparse
import ast
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'strategy/pa-hyp/PAH-OMC-019-result-v1.json'
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc019-closure'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command, cwd=ROOT, env=None, timeout=180):
    p=subprocess.run([str(x) for x in command],cwd=cwd,env=env,capture_output=True,
                     text=True,encoding='utf-8',timeout=timeout)
    if p.returncode:
        raise RuntimeError(f'{command[0]} exited {p.returncode}\n{p.stdout}{p.stderr}')
    return (p.stdout+p.stderr).strip()


def compute(folder, cache):
    m=json.loads(MANIFEST.read_text(encoding='utf-8')); checks=[]
    def ck(name, ok):
        assert bool(ok), name
        checks.append({'name':name,'pass':True})
    for p,h in m['source_files'].items():
        ck('source:'+p,sha(ROOT/p)==h)
        if p.endswith(('.py','.json','.md','.txt','.lean')):
            ck('exact LF:'+p,b'\r' not in (ROOT/p).read_bytes())
    prereg=json.loads((ROOT/m['preregistration']).read_text(encoding='utf-8'))
    for p,h in prereg['sources'].items():
        ck('parent:'+p,sha(ROOT/p)==h)
    # Revalidate R-511's direct source pins; inherited analytic statements are
    # explicitly hypotheses, not proved merely by their source hashes.
    parent=json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-018-result-v1.json').read_text(encoding='utf-8'))
    for p,h in parent['source_files'].items(): ck('R511 source:'+p,sha(ROOT/p)==h)
    def lane(job):
        stage,name=job
        suffix='' if name=='primary' else '_'+name
        stem='pah_omc019_closure' if stage=='current' else 'pah_omc018_generator'
        script=ROOT/f'codes/foundations/{stem}{suffix}.py'
        out=folder/f'{stage}-{name}.json'
        execute([sys.executable,'-X','utf8',script,'--output',out])
        data=json.loads(out.read_text(encoding='utf-8'))
        return stage,name,out,data
    jobs=[(stage,name) for stage in ('current','parent') for name in ('primary','independent','hostile')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lane,jobs))
    run_hashes={}; counts={}
    for stage,name,out,data in results:
        key=f'{stage}-{name}'
        ck('execute:'+key,data['status']=='PASS' and all(c['pass'] for c in data['checks']))
        run_hashes[key]=sha(out); counts[key]=len(data['checks'])
        if stage=='parent':
            ck('R511 exact replay:'+name,out.read_bytes()==(ROOT/parent['verification']['runs']/f'{name}.json').read_bytes())
    for name in ('pah_omc019_closure','pah_omc019_closure_independent','pah_omc019_closure_hostile'):
        tree=ast.parse((ROOT/f'codes/foundations/{name}.py').read_text(encoding='utf-8'))
        ck('code assert:'+name,any(isinstance(n,ast.Assert) for n in ast.walk(tree)))
        if name.endswith('_independent'):
            imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
            imports += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
            ck('independent nonimporting',not any('pah_' in x for x in imports))
    registry=json.loads((ROOT/'verification/lean/registry.json').read_text(encoding='utf-8'))
    tc=registry['toolchain']; lock=json.loads((ROOT/tc['lockfile']).read_text(encoding='utf-8'))
    for key in ('toolchain_file','lakefile','lockfile'):
        hk='toolchain_sha256' if key=='toolchain_file' else key+'_sha256'
        ck('toolchain:'+key,sha(ROOT/tc[key])==tc[hk])
    libraries=[]; revisions={}
    for package in lock['packages']:
        path=cache/package['name']; lib=path/'.lake/build/lib/lean'
        ck('dependency source:'+package['name'],path.is_dir())
        # Read only the explicitly selected cache; no global trust configuration.
        rev=execute(['git','-c','safe.directory='+path.resolve().as_posix(),'-C',path,'rev-parse','HEAD'])
        ck('locked dependency:'+package['name'],rev==package['rev'])
        # Lake-only dependencies need not have an imported object library.
        # The compiler itself rejects any missing library actually imported.
        if lib.is_dir(): libraries.append(str(lib))
        revisions[package['name']]={'revision':rev,'compiled_library_present':lib.is_dir()}
    tool=Path.home()/'.elan/toolchains'/tc['toolchain'].replace('/','--').replace(':','---')/'bin'/('lean.exe' if os.name=='nt' else 'lean')
    version=execute([tool,'--version'])
    ck('pinned compiler version','version 4.32.1' in version)
    env=dict(os.environ); env['LEAN_PATH']=os.pathsep.join(libraries)
    lean_records={}
    for rel in ('verification/lean/Tect/PahOmc018.lean',m['lean']['path']):
        source=(ROOT/rel).read_text(encoding='utf-8')
        entry=next(x for x in registry['entrypoints'] if x['path']==rel)
        names=re.findall(r'(?m)^theorem\s+([A-Za-z0-9_]+)',source)
        ck('Lean pin:'+rel,sha(ROOT/rel)==entry['sha256'])
        ck('Lean declarations:'+rel,names==entry['declarations'])
        ck('Lean policy:'+rel,not any(t in source for t in ('sorry','admit','axiom','unsafe')))
        diagnostic=execute([tool,ROOT/rel],env=env,timeout=600)
        ck('fresh Lean no diagnostics:'+rel,not diagnostic)
        lean_records[rel]={'status':'PASS','declarations':names,'sha256':sha(ROOT/rel),'diagnostics':diagnostic}
    ck('current Lean declaration bridge',lean_records[m['lean']['path']]['declarations']==m['lean']['declarations'])
    ck('claim boundary',m['classification']=='auxiliary_support' and not m['active_gate_change'] and not m['physical_promotion'])
    ck('kernel boundary',m['kernel_claim']=='H_rad subset ker(Ebar); full kernel unclassified')
    return {'schema':'tect/pah-omc019-integrated/1.0','result_id':m['result_id'],'status':'PASS','checks':checks,
            'manifest_sha256':sha(MANIFEST),'code_sha256':sha(Path(__file__)), 'code_version':__version__,
            'base_commit':m['base_commit'],'run_hashes':run_hashes,'lane_counts':counts,
            'environment':{'python':platform.python_version(),'sympy':__import__('sympy').__version__},
            'lean':{'entrypoints':lean_records,'version':version,'dependencies':revisions,
                    'method':'Direct pinned compiler, existing read-only locked package cache; no shared build or lake update.'},
            'coverage':m['proof_coverage'],'non_claims':m['non_claims']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='pah019-replay-') as temp:
        folder=Path(temp); result=compute(folder,args.lean_cache)
        (folder/'integrated.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
        for out in sorted(folder.glob('*.json')):
            if args.check:
                assert out.read_bytes()==(RUN/out.name).read_bytes(),out.name+' replay mismatch'
            else:
                RUN.mkdir(parents=True,exist_ok=True)
                (RUN/out.name).write_bytes(out.read_bytes())
    print(f"PAH-OMC-019 INTEGRATED: PASS ({len(result['checks'])} checks; Lean PASS; replay={args.check})")


if __name__=='__main__':
    main()
