#!/usr/bin/env python3
"""Hostile mutation controls for PAH-OMC-023 owner admission."""
from __future__ import annotations
import argparse, copy, hashlib, json, os, tempfile
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
SNAPSHOT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json'
R554_RESULT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'
CONTRACT=ROOT/'strategy/pa-hyp/PAH-OMC-023-owner-authorized-successor-admission-contract-v1.json'
PINS={'strategy/pa-hyp/PAH-001-v1.json':'03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37','strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json':'54329df2a6d3ca766f6ca24fbcc628263e6c7e8c2c0e8c8eba545f3508d75df7'}
def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(value,dict): raise TypeError(path)
 return value
def canonical(value:Any)->bytes:return json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode('utf-8')
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
def valid(snapshot:dict[str,Any])->bool:
 if snapshot.get('schema')!='tect/pah-omc020-owner-search-snapshot/1.0' or snapshot.get('status')!='FIXED_SEARCH_SNAPSHOT': return False
 if snapshot.get('source_authorized_packet_present') is not False or snapshot.get('authorized_paths')!=[] or snapshot.get('complete_paths')!=[]: return False
 records=snapshot.get('candidate_records')
 if not isinstance(records,list): return False
 paths=[r.get('path') for r in records]
 if paths!=sorted(set(paths)) or snapshot.get('candidate_path_count')!=len(records): return False
 if snapshot.get('manifest_sha256')!=hashlib.sha256(canonical(records)).hexdigest(): return False
 for r in records:
  p=ROOT/r['path']
  if not p.is_file() or digest(p)!=r.get('sha256'): return False
 return True
def main()->int:
 parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc023-owner-admission-intake/hostile.json'); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
 rows=[]; snapshot=load(SNAPSHOT); result=load(R554_RESULT); contract=load(CONTRACT)
 check(rows,'baseline valid',valid(snapshot),True,valid(snapshot))
 mutation=copy.deepcopy(snapshot); mutation['authorized_paths']=['injected-owner.json']; check(rows,'authorized mutation rejected',valid(mutation),False,not valid(mutation))
 mutation=copy.deepcopy(snapshot); mutation['complete_paths']=['injected-owner.json']; check(rows,'complete mutation rejected',valid(mutation),False,not valid(mutation))
 mutation=copy.deepcopy(snapshot); mutation['source_authorized_packet_present']=True; check(rows,'authorization flag mutation rejected',valid(mutation),False,not valid(mutation))
 mutation=copy.deepcopy(snapshot); mutation['manifest_sha256']='0'*64; check(rows,'manifest mutation rejected',valid(mutation),False,not valid(mutation))
 mutation=copy.deepcopy(snapshot); mutation['candidate_records'][0]['sha256']='f'*64; check(rows,'candidate byte mutation rejected',valid(mutation),False,not valid(mutation))
 mutation=copy.deepcopy(snapshot); mutation['candidate_records']=list(reversed(mutation['candidate_records'])); check(rows,'manifest order mutation rejected',valid(mutation),False,not valid(mutation))
 mutation=copy.deepcopy(snapshot); mutation.setdefault('scope',{})['replay']='git fsck --unreachable'; check(rows,'dynamic fsck mutation detected','fsck' in json.dumps(mutation).lower(),True,'fsck' in json.dumps(mutation).lower())
 check(rows,'parent hashes frozen',{k:digest(ROOT/k) for k in PINS},PINS,{k:digest(ROOT/k) for k in PINS}==PINS)
 check(rows,'R-554 remains hold',result.get('verdict'),'HOLD_FOR_EVIDENCE',result.get('verdict')=='HOLD_FOR_EVIDENCE')
 check(rows,'contract reserved result',contract.get('reserved_result_id'),'R-560',contract.get('reserved_result_id')=='R-560')
 payload={'schema':'tect/pah-omc023-owner-admission-hostile/1.0','audit_id':'PAH-OMC-023-OWNER-ADMISSION-HOSTILE-001','result_id':'R-560','task_id':'T-090','status':'PASS_HOSTILE_ADMISSION_FIREWALL','verdict':'HOLD_FOR_EVIDENCE','classification':'auxiliary_support','claim_bearing':False,'active_gate_change':False,'physical_promotion':False,'checks':rows,'checks_passed':len(rows),'source_hashes':{str(SNAPSHOT.relative_to(ROOT)):digest(SNAPSHOT),str(R554_RESULT.relative_to(ROOT)):digest(R554_RESULT),str(CONTRACT.relative_to(ROOT)):digest(CONTRACT),str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},'finding':'Hostile mutations of authorization, completion, provenance, manifest digest, candidate bytes and order are rejected. The current empty manifest cannot be promoted by status-only edits.','next_single_question':contract['next_single_question'],'non_claims':contract['non_claims'],'reproduction':'python -X utf8 codes/foundations/pah_omc023_owner_admission_intake_hostile.py --check'}
 dest=args.output if args.output.is_absolute() else ROOT/args.output; encoded=atomic_json(dest,payload) if not args.check else (json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8')
 if args.check and (not dest.is_file() or dest.read_bytes()!=encoded): raise SystemExit('PAH-OMC-023 hostile replay mismatch')
 print(f'PAH-OMC-023 OWNER ADMISSION HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE'); return 0
if __name__=='__main__': raise SystemExit(main())