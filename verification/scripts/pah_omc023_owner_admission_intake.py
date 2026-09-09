#!/usr/bin/env python3
"""Primary current-environment replay for PAH-OMC-023 owner admission intake."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
SNAPSHOT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json'
R554_RESULT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'
CONTRACT=ROOT/'strategy/pa-hyp/PAH-OMC-023-owner-authorized-successor-admission-contract-v1.json'
HIST_RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.4'
CHILDREN=(
 ('primary',ROOT/'verification/scripts/pah_omc020_owner_packet_snapshot.py',HIST_RUN/'primary.json'),
 ('independent',ROOT/'codes/foundations/pah_omc020_owner_snapshot_v11_independent.py',HIST_RUN/'independent.json'),
 ('hostile',ROOT/'codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py',HIST_RUN/'hostile.json'),
)
PINS={
 'strategy/pa-hyp/PAH-001-v1.json':'03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37',
 'strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json':'54329df2a6d3ca766f6ca24fbcc628263e6c7e8c2c0e8c8eba545f3508d75df7',
}
def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(value,dict): raise TypeError(path)
 return value
def atomic_json(path:Path,payload:dict[str,Any])->bytes:
 encoded=(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8')
 path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as handle: handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
 return encoded
def check(rows:list[dict[str,Any]],name:str,actual:Any,expected:Any,ok:bool)->None:
 rows.append({'name':name,'status':'PASS' if ok else 'FAIL','actual':actual,'expected':expected})
 if not ok: raise AssertionError(name)
def canonical(value:Any)->bytes:return json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode('utf-8')
def stable_command(name:str)->str:
 if name=='primary': return 'python -X utf8 verification/scripts/pah_omc020_owner_packet_snapshot.py --snapshot strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json --output <frozen-v1.4-run>/primary.json --check'
 if name=='independent': return 'python -X utf8 codes/foundations/pah_omc020_owner_snapshot_v11_independent.py --snapshot strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json --output <frozen-v1.4-run>/independent.json --check'
 return 'python -X utf8 codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py --snapshot strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json --output <frozen-v1.4-run>/hostile.json --check'
def main()->int:
 parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc023-owner-admission-intake/primary.json'); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
 rows=[]; snapshot=load(SNAPSHOT); result=load(R554_RESULT); contract=load(CONTRACT)
 check(rows,'snapshot hash',digest(SNAPSHOT),'47b0879ff4c55fe3d60a11cd744d6920a3e3eb18bf923cdd4782fa7e7674b4e9',digest(SNAPSHOT)=='47b0879ff4c55fe3d60a11cd744d6920a3e3eb18bf923cdd4782fa7e7674b4e9')
 check(rows,'R-554 result hash',digest(R554_RESULT),PINS['strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'],digest(R554_RESULT)==PINS['strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'])
 check(rows,'contract identity',contract.get('reserved_result_id'),'R-560',contract.get('reserved_result_id')=='R-560')
 check(rows,'snapshot schema',snapshot.get('schema'),'tect/pah-omc020-owner-search-snapshot/1.0',snapshot.get('schema')=='tect/pah-omc020-owner-search-snapshot/1.0')
 check(rows,'snapshot fixed',snapshot.get('status'),'FIXED_SEARCH_SNAPSHOT',snapshot.get('status')=='FIXED_SEARCH_SNAPSHOT')
 records=snapshot.get('candidate_records'); check(rows,'candidate records list',isinstance(records,list),'list',isinstance(records,list))
 paths=[r.get('path') for r in records] if isinstance(records,list) else []
 check(rows,'candidate paths sorted unique',paths,sorted(set(paths)),paths==sorted(set(paths)))
 check(rows,'candidate count self-consistent',snapshot.get('candidate_path_count'),len(paths),snapshot.get('candidate_path_count')==len(paths))
 check(rows,'manifest digest',snapshot.get('manifest_sha256'),hashlib.sha256(canonical(records)).hexdigest(),snapshot.get('manifest_sha256')==hashlib.sha256(canonical(records)).hexdigest())
 check(rows,'source authorization absent',snapshot.get('source_authorized_packet_present'),False,snapshot.get('source_authorized_packet_present') is False)
 check(rows,'authorized set empty',snapshot.get('authorized_paths'),[],snapshot.get('authorized_paths')==[])
 check(rows,'complete set empty',snapshot.get('complete_paths'),[],snapshot.get('complete_paths')==[])
 replay={}
 for name,script,output in CHILDREN:
  command=[sys.executable,'-X','utf8',str(script),'--snapshot',str(SNAPSHOT),'--output',str(output),'--check']
  proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
  replay[name]={'returncode':proc.returncode,'command':stable_command(name)}
  check(rows,f'{name} historical child replay',proc.returncode,0,proc.returncode==0)
  child=load(output)
  check(rows,f'{name} hold verdict',child.get('verdict'),'HOLD_FOR_EVIDENCE',child.get('verdict')=='HOLD_FOR_EVIDENCE')
  check(rows,f'{name} checks pass',all(item.get('status')=='PASS' for item in child.get('checks',[])),True,all(item.get('status')=='PASS' for item in child.get('checks',[])))
  check(rows,f'{name} claim firewall',child.get('claim_bearing'),False,child.get('claim_bearing') is False)
  check(rows,f'{name} physical firewall',child.get('physical_promotion'),False,child.get('physical_promotion') is False)
 check(rows,'R-554 source status',result.get('verdict'),'HOLD_FOR_EVIDENCE',result.get('verdict')=='HOLD_FOR_EVIDENCE')
 check(rows,'R-554 exact scope retained',isinstance(result.get('exact_scope'),dict),True,isinstance(result.get('exact_scope'),dict))
 payload={'schema':'tect/pah-omc023-owner-admission-primary/1.0','audit_id':'PAH-OMC-023-OWNER-ADMISSION-PRIMARY-001','result_id':'R-560','task_id':'T-090','status':'PASS_CURRENT_ENVIRONMENT_REPLAY_HOLD','verdict':'HOLD_FOR_EVIDENCE','classification':'auxiliary_support','claim_bearing':False,'active_gate_change':False,'physical_promotion':False,'checks':rows,'checks_passed':len(rows),'replay':replay,'source_hashes':{str(SNAPSHOT.relative_to(ROOT)):digest(SNAPSHOT),str(R554_RESULT.relative_to(ROOT)):digest(R554_RESULT),str(CONTRACT.relative_to(ROOT)):digest(CONTRACT),str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},'snapshot':{'snapshot_id':snapshot.get('snapshot_id'),'candidate_path_count':len(paths),'manifest_sha256':snapshot.get('manifest_sha256'),'authorized_paths':snapshot.get('authorized_paths'),'complete_paths':snapshot.get('complete_paths')},'finding':'The current environment replays all three frozen R-554 child artifacts with canonicalized commands. The current-byte manifest still has no authorized or complete owner packet; this is HOLD_FOR_EVIDENCE, not a no-go.','next_single_question':contract['next_single_question'],'non_claims':contract['non_claims'],'reproduction':'python -X utf8 verification/scripts/pah_omc023_owner_admission_verify.py --check'}
 destination=args.output if args.output.is_absolute() else ROOT/args.output; encoded=atomic_json(destination,payload) if not args.check else (json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8')
 if args.check and (not destination.is_file() or destination.read_bytes()!=encoded): raise SystemExit('PAH-OMC-023 primary replay mismatch')
 print(f'PAH-OMC-023 OWNER ADMISSION PRIMARY: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE'); return 0
if __name__=='__main__': raise SystemExit(main())