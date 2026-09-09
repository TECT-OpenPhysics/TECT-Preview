#!/usr/bin/env python3
"""Integrated canonical-path replay for PAH-OMC-023 owner admission."""
from __future__ import annotations
import argparse, ast, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
RUN_DIR=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc023-owner-admission-intake'
CONTRACT=ROOT/'strategy/pa-hyp/PAH-OMC-023-owner-authorized-successor-admission-contract-v1.json'
PRIMARY=ROOT/'verification/scripts/pah_omc023_owner_admission_intake.py'
INDEPENDENT=ROOT/'codes/foundations/pah_omc023_owner_admission_intake_independent.py'
HOSTILE=ROOT/'codes/foundations/pah_omc023_owner_admission_intake_hostile.py'
SNAPSHOT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json'
def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(value,dict): raise TypeError(path)
 return value
def atomic_json(path:Path,payload:dict[str,Any])->bytes:
 encoded=(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8'); path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as h: h.write(encoded); h.flush(); os.fsync(h.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
 return encoded
def check(rows:list[dict[str,Any]],name:str,actual:Any,expected:Any,ok:bool)->None:
 rows.append({'name':name,'status':'PASS' if ok else 'FAIL','actual':actual,'expected':expected})
 if not ok: raise AssertionError(name)
def no_import(path:Path)->bool:
 tree=ast.parse(path.read_text(encoding='utf-8'),filename=str(path)); forbidden=('pah_omc023_owner_admission','verification.scripts','codes.foundations')
 for node in ast.walk(tree):
  names=[]
  if isinstance(node,ast.Import): names=[x.name for x in node.names]
  elif isinstance(node,ast.ImportFrom): names=[node.module or '']
  if any(any(token in name for token in forbidden) for name in names): return False
 return True
def stable(name:str)->str:
 if name=='primary': return 'python -X utf8 verification/scripts/pah_omc023_owner_admission_intake.py --output <run>/primary.json'
 if name=='independent': return 'python -X utf8 codes/foundations/pah_omc023_owner_admission_intake_independent.py --output <run>/independent.json'
 return 'python -X utf8 codes/foundations/pah_omc023_owner_admission_intake_hostile.py --output <run>/hostile.json'
def main()->int:
 parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=RUN_DIR/'integrated.json'); parser.add_argument('--check',action='store_true'); args=parser.parse_args(); RUN_DIR.mkdir(parents=True,exist_ok=True)
 rows=[]; replay={}
 for name,script in (('primary',PRIMARY),('independent',INDEPENDENT),('hostile',HOSTILE)):
  output=RUN_DIR/f'{name}.json'; command=[sys.executable,'-X','utf8',str(script),'--output',str(output)] + (['--check'] if args.check else [])
  proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace'); replay[name]={'returncode':proc.returncode,'command':stable(name)}; check(rows,f'{name} current replay',proc.returncode,0,proc.returncode==0)
 contract=load(CONTRACT); snapshot=load(SNAPSHOT); runs={n:load(RUN_DIR/f'{n}.json') for n in ('primary','independent','hostile')}
 check(rows,'contract reserved result',contract.get('reserved_result_id'),'R-560',contract.get('reserved_result_id')=='R-560')
 check(rows,'snapshot authorization absent',snapshot.get('source_authorized_packet_present'),False,snapshot.get('source_authorized_packet_present') is False)
 check(rows,'snapshot authorized empty',snapshot.get('authorized_paths'),[],snapshot.get('authorized_paths')==[])
 check(rows,'snapshot complete empty',snapshot.get('complete_paths'),[],snapshot.get('complete_paths')==[])
 for name,run in runs.items():
  check(rows,f'{name} hold verdict',run.get('verdict'),'HOLD_FOR_EVIDENCE',run.get('verdict')=='HOLD_FOR_EVIDENCE')
  check(rows,f'{name} claim firewall',run.get('claim_bearing'),False,run.get('claim_bearing') is False)
  check(rows,f'{name} gate firewall',run.get('active_gate_change'),False,run.get('active_gate_change') is False)
  check(rows,f'{name} physical firewall',run.get('physical_promotion'),False,run.get('physical_promotion') is False)
  check(rows,f'{name} all checks pass',all(item.get('status')=='PASS' for item in run.get('checks',[])),True,all(item.get('status')=='PASS' for item in run.get('checks',[])))
 check(rows,'independent non-importing',no_import(INDEPENDENT),True,no_import(INDEPENDENT)); check(rows,'hostile non-importing',no_import(HOSTILE),True,no_import(HOSTILE))
 payload={'schema':'tect/pah-omc023-owner-admission-integrated/1.0','audit_id':'PAH-OMC-023-OWNER-ADMISSION-INTEGRATED-001','result_id':'R-560','task_id':'T-090','status':'PASS_CURRENT_ENVIRONMENT_REPLAY_HOLD','verdict':'HOLD_FOR_EVIDENCE','classification':'auxiliary_support','claim_bearing':False,'active_gate_change':False,'physical_promotion':False,'checks':rows,'checks_passed':len(rows),'replay':replay,'source_hashes':{str(CONTRACT.relative_to(ROOT)):digest(CONTRACT),str(SNAPSHOT.relative_to(ROOT)):digest(SNAPSHOT),str(PRIMARY.relative_to(ROOT)):digest(PRIMARY),str(INDEPENDENT.relative_to(ROOT)):digest(INDEPENDENT),str(HOSTILE.relative_to(ROOT)):digest(HOSTILE),str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},'child_run_hashes':{n:digest(RUN_DIR/f'{n}.json') for n in ('primary','independent','hostile')},'snapshot':{'snapshot_id':snapshot.get('snapshot_id'),'candidate_path_count':snapshot.get('candidate_path_count'),'manifest_sha256':snapshot.get('manifest_sha256'),'authorized_paths':snapshot.get('authorized_paths'),'complete_paths':snapshot.get('complete_paths')},'finding':'Canonicalized current-environment replay passes for all three lanes. The R-554 manifest still contains no authorized or complete owner packet, so admission remains HOLD_FOR_EVIDENCE. The historical integrated mismatch was a path-provenance mismatch, not a mathematical contradiction.','next_single_question':contract['next_single_question'],'non_claims':contract['non_claims'],'reproduction':'python -X utf8 verification/scripts/pah_omc023_owner_admission_verify.py --check'}
 destination=args.output if args.output.is_absolute() else ROOT/args.output; encoded=atomic_json(destination,payload) if not args.check else (json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8')
 if args.check and (not destination.is_file() or destination.read_bytes()!=encoded): raise SystemExit('PAH-OMC-023 integrated replay mismatch')
 print(f'PAH-OMC-023 OWNER ADMISSION INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE'); return 0
if __name__=='__main__': raise SystemExit(main())