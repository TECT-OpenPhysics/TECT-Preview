#!/usr/bin/env python3
"""bundle_coverage.py -- reproduction-bundle coverage report (governance/reproduction-bundle-policy.md sec.8).

Lists every result-bearing sub-proof folder, its owning claim's tier, and whether a
current reproduction bundle exists. A T5+ claim's folder with notes but no bundle is a
MANDATORY gap; a T4 folder without one is a RECOMMENDED gap; <=T3 needs none.

    python verification/scripts/bundle_coverage.py            # report
    python verification/scripts/bundle_coverage.py --build    # build all missing mandatory (T5+) bundles
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-10"

import json, re, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
RANK = {"T7":7,"T6":6,"T5":5,"T4":4,"T3":3,"T2":2,"T1":1,"T0":0}

def claim_tier(cid):
    p = REPO/"claims"/cid/"status.json"
    if p.exists():
        try:
            t = json.load(open(p)).get("tier","?")
            return t.split()[0] if t else "?"
        except Exception: pass
    return "?"

def has_bundle(folder):
    import json as _j
    bdir = REPO/folder/"bundle"
    if not bdir.exists(): return None, None
    for m in bdir.glob("*/MANIFEST.json"):
        try: note = _j.load(open(m)).get("note","")
        except Exception: note = ""
        try: rl=_j.load(open(m)).get("runlog",{})
        except Exception: rl={}
        bad=any(v.get("exit")!=0 or "FAIL" in v.get("pass_line","") for v in rl.values())
        g=("PUB" if "referee-package" in note else "DRAFT")
        return m.parent.relative_to(REPO).as_posix(), (g+"*" if bad else g)
    for _ in bdir.glob("*/expected"):
        return None, "partial"
    return None, None

def main():
    build = "--build" in sys.argv
    rows = []
    for notes in sorted((REPO/"claims").glob("*/*/notes")):
        folder = notes.parent
        cid = folder.relative_to(REPO/"claims").parts[0]
        sub = folder.name
        nnotes = len([n for n in notes.glob("*.tex.txt")
                      if not n.read_text().split("\n",1)[0].startswith("% SUPERSEDED")])
        if nnotes == 0: continue
        tier = claim_tier(cid)
        rank = RANK.get(tier, -1)
        req = "MANDATORY" if rank >= 5 else ("recommended" if rank == 4 else "-")
        # doc-only folders (headline note has no reproduction scripts) need no code bundle
        import re as _re
        live_notes=[n for n in notes.glob("*.tex.txt") if not n.read_text().split("\n",1)[0].startswith("% SUPERSEDED")]
        has_scripts=any(_re.search(r"Reproduction command:.*\.py", n.read_text()) for n in live_notes)
        b, grade = has_bundle(folder.relative_to(REPO).as_posix())
        if not has_scripts:
            req="-"  # doc-only
        st = (grade if b else ("partial" if grade=="partial" else ("GAP" if req!="-" else "n/a")))
        rows.append([cid, tier, sub, nnotes, req, st, b])
    # report
    print(f"{'claim':22} {'tier':4} {'sub-proof':22} {'notes':5} {'req':11} status")
    mand_gap = []
    for cid,tier,sub,nn,req,st,b in rows:
        print(f"{cid:22} {tier:4} {sub:22} {nn:5} {req:11} {st}" + (f"  {b}" if b else ""))
        if req=="MANDATORY" and (st in ("GAP","partial") or str(st).endswith("*")): mand_gap.append((cid,sub))
    print(f"\nPUBLISHED: {sum(1 for r in rows if r[5]==chr(80)+chr(85)+chr(66))}  DRAFT: {sum(1 for r in rows if r[5]==chr(68)+chr(82)+chr(65)+chr(70)+chr(84))}")
    print(f"\nMANDATORY (T5+) folders: {sum(1 for r in rows if r[4]=='MANDATORY')}; "
          f"with bundle: {sum(1 for r in rows if r[4]=='MANDATORY' and r[5] in ('PUB','DRAFT'))}; "
          f"GAPS: {len(mand_gap)}")
    if build and mand_gap:
        for cid,sub in mand_gap:
            folder = f"claims/{cid}/{sub}"
            print(f"\n=== building {folder} ===")
            r = subprocess.run([sys.executable, str(REPO/"verification/scripts/build_reproduction_bundle.py"),
                                "--folder", folder], cwd=REPO)
            print(f"  exit {r.returncode}")
    return 1 if mand_gap and not build else 0

if __name__ == "__main__":
    sys.exit(main())
