#!/usr/bin/env python3
"""Verify an extracted review package. Retain a trusted outer ZIP hash."""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath

SCOPE={'gaussian_reference':True,'fixed_volume':16,'fixed_floor':'1e-12',
       'interacting_Gibbs_measure':False,'A13_closure':False,'physical_vacuum':False,
       'external_mathematical_review':'NOT_PERFORMED','specialist_novelty_review':'NOT_PERFORMED',
       'actual_submission':'NOT_PERFORMED'}


def safe_name(name):
    if not isinstance(name,str) or not name or '\\' in name or ':' in name:
        raise ValueError('Unsafe member')
    path=PurePosixPath(name)
    if path.is_absolute() or any(x in ('','..','.') for x in name.split('/')):
        raise ValueError('Unsafe member')


def contract(manifest):
    if manifest.get('schema')!='tect/a6-a7-review-package/1.0' or manifest.get('scope')!=SCOPE:
        raise ValueError('Declared scientific or external-review scope changed')
    if not manifest.get('files'): raise ValueError('Empty inventory')
    for name in manifest['files']: safe_name(name)


def check(root):
    root=root.resolve(); manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
    contract(manifest)
    for name,expected in manifest['files'].items():
        path=root/name
        if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError('Missing or unsafe member: '+name)
        data=path.read_bytes()
        if len(data)!=expected['bytes'] or hashlib.sha256(data).hexdigest()!=expected['sha256']:
            raise ValueError('Changed member: '+name)
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    if actual != set(manifest['files'])|{'MANIFEST.json'}:
        raise ValueError('Uninventoried or absent files')
    return len(manifest['files'])


def self_test():
    base={'schema':'tect/a6-a7-review-package/1.0','scope':SCOPE,'files':{'fixture.txt':{}}}
    contract(base); rejected=0
    for key,value in (('physical_vacuum',True),('interacting_Gibbs_measure',True),
                      ('A13_closure',True),('external_mathematical_review','PASS')):
        changed=copy.deepcopy(base);changed['scope'][key]=value
        try: contract(changed)
        except ValueError: rejected+=1
        else: raise ValueError('False scope accepted')
    for name in ('../escape','/absolute','C:/drive','a\\b','a/./b'):
        try: safe_name(name)
        except ValueError: rejected+=1
        else: raise ValueError('Unsafe path accepted')
    return rejected


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    root=args.root or Path(__file__).resolve().parent
    if args.self_test: print('PACKAGE SELF-TEST: PASS',self_test(),'scope/path mutations rejected')
    print('PACKAGE INTEGRITY: PASS',check(root),'files; external review NOT PERFORMED')


if __name__=='__main__': main()
