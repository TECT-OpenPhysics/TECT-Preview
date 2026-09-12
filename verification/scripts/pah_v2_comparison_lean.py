#!/usr/bin/env python3
"""Fresh pinned-kernel replay of comparison algebra, version 1.0.0.

Parameterized facts only. Not a full PAH/Morton formalization or a dynamics
theorem. Package revisions and entrypoint bytes are checked before compiling.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'verification/lean/Tect/PahV2Comparison.lean'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-comparison/lean.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cache,elan_home):
    reg = json.loads((ROOT/'verification/lean/registry.json').read_text(encoding='utf-8'))
    tc = reg['toolchain']
    for path,h in (('toolchain_file','toolchain_sha256'),('lakefile','lakefile_sha256'),('lockfile','lockfile_sha256')):
        assert sha(ROOT/tc[path]) == tc[h]
    entry = next(e for e in reg['entrypoints'] if e['path']==SOURCE.relative_to(ROOT).as_posix())
    assert sha(SOURCE) == entry['sha256']
    source = SOURCE.read_text(encoding='utf-8')
    for word in reg['source_policy']['forbidden_tokens']:
        assert not re.search(r'\b'+word+r'\b',source)
    assert re.findall(r'^theorem\s+(\w+)',source,re.M) == entry['declarations']
    lock = json.loads((ROOT/tc['lockfile']).read_text(encoding='utf-8'))
    revisions,libraries = {},[]
    for dep in lock['packages']:
        folder = cache/dep['name']
        cmd = ['git','-c',f'safe.directory={folder.as_posix()}','-C',str(folder),'rev-parse','HEAD']
        revision = subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',check=True).stdout.strip()
        assert revision == dep['rev'],dep['name']
        revisions[dep['name']] = revision
        lib = folder/'.lake/build/lib/lean'
        if lib.is_dir():
            libraries.append(str(lib))
    encoded = tc['toolchain'].replace('/','--').replace(':','---')
    exe = elan_home/'toolchains'/encoded/'bin/lean.exe'
    version = subprocess.run([str(exe),'--version'],capture_output=True,text=True,encoding='utf-8',check=True).stdout.strip()
    assert '4.32.1' in version
    env = os.environ.copy()
    env['LEAN_PATH'] = os.pathsep.join(libraries)
    proc = subprocess.run([str(exe),str(SOURCE)],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=240)
    assert proc.returncode == 0,proc.stdout+proc.stderr
    return {'schema':'tect/pah-v2-comparison-lean/1.0','status':'PASS_PARAMETERIZED_ALGEBRA',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'source_sha256':sha(SOURCE),'declarations':entry['declarations'],
            'toolchain':tc,'package_revisions':revisions,'compiler_version':version,
            'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,
            'equivalent_lake_command':'cd verification/lean; lake env lean Tect/PahV2Comparison.lean',
            'scope':'Integer prefix/floor/suffix identities, additive signed phase/path arithmetic, distance-coordinate injectivity and generic full pullback/inherited-sup-bound algebra.',
            'not_encoded':'Concrete grid and primorial construction, PAH full state type, map-to-formula equivalence, root assignment and direct-limit construction require the written admission proof and independent executable; no complete model Lean theorem is claimed.',
            'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'non_claims':'No Gibbs projectivity, generator agreement, limiting core, dynamics convergence or physical conclusion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    result = run(args.lean_cache,args.elan_home)
    if args.check:
        old = json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'} == {k:v for k,v in result.items() if k!='environment'}
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PAH-V2-COMPARISON LEAN: PASS',len(result['declarations']),'parameterized declarations')


if __name__ == '__main__':
    main()
