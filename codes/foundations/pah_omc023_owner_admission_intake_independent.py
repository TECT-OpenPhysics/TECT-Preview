#!/usr/bin/env python3
"""Independent manifest replay for PAH-OMC-023 owner admission."""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
SNAPSHOT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.4.json'
R554_RESULT=ROOT/'strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'
CONTRACT=ROOT/'strategy/pa-hyp/PAH-OMC-023-owner-authorized-successor-admission-contract-v1.json'
PINS={
 'strategy/pa-hyp/PAH-001-v1.json':'03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37',
 'strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json':'54329df2a6d3ca766f6ca24fbcc628263e6c7e8c2c0e8c8eba545f3508d75df7',
}
MARKERS=('pah-omc-020','source-authorized','owner_authorized','owner packet')
COMPLETE={'SOURCE_AUTHORIZED_COMPLETE','OWNER_AUTHORIZED_COMPLETE'}
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
def flags(path:Path,raw:bytes)->tuple[bool,bool,bool]:
 try:text=raw.decode('utf-8')
 except UnicodeDecodeError:return False,False,False
 marked=any(marker in text.lower() for marker in MARKERS); authorised=False; complete=False
 if path.suffix.lower()=='.json':
  try:value=json.loads(text)
  except json.JSONDecodeError:value=None
  if isinstance(value,dict):
   provenance=value.get('provenance'); authorised=isinstance(provenance,dict) and provenance.get('source_authorized_packet_present') is True
   status=value.get('status'); complete=isinstance(status,str) and status in COMPLETE
 return marked,authorised,complete
def main()->int:
 parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc023-owner-admission-intake/independent.json'); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
 rows=[]; snapshot=load(SNAPSHOT); result=load(R554_RESULT); contract=load(CONTRACT); records=snapshot.get('candidate_records',[])
 check(rows,'snapshot hash',digest(SNAPSHOT),'47b0879ff4c55fe3d60a11cd744d6920a3e3eb18bf923cdd4782fa7e7674b4e9',digest(SNAPSHOT)=='47b0879ff4c55fe3d60a11cd744d6920a3e3eb18bf923cdd4782fa7e7674b4e9')
 check(rows,'PAH parent hash',digest(ROOT/'strategy/pa-hyp/PAH-001-v1.json'),PINS['strategy/pa-hyp/PAH-001-v1.json'],digest(ROOT/'strategy/pa-hyp/PAH-001-v1.json')==PINS['strategy/pa-hyp/PAH-001-v1.json'])
 check(rows,'R-554 result hash',digest(R554_RESULT),PINS['strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'],digest(R554_RESULT)==PINS['strategy/pa-hyp/PAH-OMC-020-owner-search-v1.4-result-v1.json'])
 check(rows,'snapshot schema',snapshot.get('schema'),'tect/pah-omc020-owner-search-snapshot/1.0',snapshot.get('schema')=='tect/pah-omc020-owner-search-snapshot/1.0')
 check(rows,'snapshot status',snapshot.get('status'),'FIXED_SEARCH_SNAPSHOT',snapshot.get('status')=='FIXED_SEARCH_SNAPSHOT')
 check(rows,'source authorization false',snapshot.get('source_authorized_packet_present'),False,snapshot.get('source_authorized_packet_present') is False)
 check(rows,'record list',isinstance(records,list),'list',isinstance(records,list))
 paths=[r.get('path') for r in records] if isinstance(records,list) else []
 check(rows,'sorted unique paths',paths,sorted(set(paths)),paths==sorted(set(paths)))
 check(rows,'count derived',snapshot.get('candidate_path_count'),len(paths),snapshot.get('candidate_path_count')==len(paths))
 check(rows,'manifest digest',snapshot.get('manifest_sha256'),hashlib.sha256(canonical(records)).hexdigest(),snapshot.get('manifest_sha256')==hashlib.sha256(canonical(records)).hexdigest())
 authorised=[]; complete=[]
 for record in records:
  path=ROOT/record['path']; raw=path.read_bytes(); marked,is_auth,is_complete=flags(path,raw)
  check(rows,'marker '+record['path'],marked,True,marked)
  check(rows,'byte hash '+record['path'],digest(path),record['sha256'],digest(path)==record['sha256'])
  check(rows,'authorization '+record['path'],is_auth,record['authorized_marker'],is_auth==record['authorized_marker'])
  check(rows,'completion '+record['path'],is_complete,record['complete_marker'],is_complete==record['complete_marker'])
  if is_auth: authorised.append(record['path'])
  if is_complete: complete.append(record['path'])
 check(rows,'authorized paths empty',sorted(authorised),[],not authorised and snapshot.get('authorized_paths')==[])
 check(rows,'complete paths empty',sorted(complete),[],not complete and snapshot.get('complete_paths')==[])
 check(rows,'no dynamic fsck field','fsck' in json.dumps(snapshot).lower(),False,'fsck' not in json.dumps(snapshot).lower())
 check(rows,'R-554 hold result',result.get('verdict'),'HOLD_FOR_EVIDENCE',result.get('verdict')=='HOLD_FOR_EVIDENCE')
 check(rows,'contract reserved result',contract.get('reserved_result_id'),'R-560',contract.get('reserved_result_id')=='R-560')
 payload={'schema':'tect/pah-omc023-owner-admission-independent/1.0','audit_id':'PAH-OMC-023-OWNER-ADMISSION-INDEPENDENT-001','result_id':'R-560','task_id':'T-090','status':'PASS_INDEPENDENT_CURRENT_MANIFEST_HOLD','verdict':'HOLD_FOR_EVIDENCE','classification':'auxiliary_support','claim_bearing':False,'active_gate_change':False,'physical_promotion':False,'checks':rows,'checks_passed':len(rows),'source_hashes':{str(SNAPSHOT.relative_to(ROOT)):digest(SNAPSHOT),str(R554_RESULT.relative_to(ROOT)):digest(R554_RESULT),str(CONTRACT.relative_to(ROOT)):digest(CONTRACT),str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},'snapshot':{'snapshot_id':snapshot.get('snapshot_id'),'candidate_path_count':len(paths),'manifest_sha256':snapshot.get('manifest_sha256'),'authorized_paths':snapshot.get('authorized_paths'),'complete_paths':snapshot.get('complete_paths')},'finding':'An independent implementation recomputes the pinned current-byte manifest and all candidate hashes. It finds no authorized or complete owner packet; the result remains HOLD_FOR_EVIDENCE.','next_single_question':contract['next_single_question'],'non_claims':contract['non_claims'],'reproduction':'python -X utf8 codes/foundations/pah_omc023_owner_admission_intake_independent.py --check'}
 dest=args.output if args.output.is_absolute() else ROOT/args.output; encoded=atomic_json(dest,payload) if not args.check else (json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode('utf-8')
 if args.check and (not dest.is_file() or dest.read_bytes()!=encoded): raise SystemExit('PAH-OMC-023 independent replay mismatch')
 print(f'PAH-OMC-023 OWNER ADMISSION INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE'); return 0
if __name__=='__main__': raise SystemExit(main())