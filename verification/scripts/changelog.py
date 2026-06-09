#!/usr/bin/env python3
"""changelog.py -- JSONL-sourced CHANGELOG with a generated Markdown view and a
git-ignored full-text query cache.

Design (governance/changelog-db.md):
  * SOURCE OF TRUTH   changelog/log.jsonl   (append-only, one JSON object/line,
                      oldest-first; new entries appended at EOF).
  * GENERATED VIEW    CHANGELOG.md          (newest-first; == render(log.jsonl);
                      never hand-edited; release_check enforces sync).
  * QUERY CACHE       changelog/.cache/changelog.db  (gitignored SQLite FTS5;
                      rebuildable from log.jsonl by `build-db`).

Mirrors the repo's single-source-of-truth pattern (status.json->CLAIMS.md,
catalog.json->CATALOG.md, todo.json->TODO.md): a plaintext structured source, a
generated human view, and a rebuildable derived index. No binary enters git.

Header grammar (existing corpus): `## [<tag>]<optional text> <dash> <YYYY-MM-DD>`
where <dash> is '-' or em-dash. Entry boundaries are the column-0 `## [` lines;
losslessness rests on verbatim block storage, not on header parsing.

Usage:
  python verification/scripts/changelog.py render [--check]
  python verification/scripts/changelog.py add --title T --date D [--claims ...]
        [--neg ...] [--notes ...] [--scripts ...] [--keywords ...]   (body=stdin)
  python verification/scripts/changelog.py search [--claim ID] [--keyword KW]
        [--tier T] [--since YYYY-MM-DD] [--text PHRASE] [--fts] [--limit N]
  python verification/scripts/changelog.py build-db
  python verification/scripts/changelog.py migrate    (one-time MD->JSONL)

Changelog:
  1.0.0 (2026-06-09) first issue. JSONL source + generated MD + FTS5 query cache.
"""
__version__ = "1.0.0"

import argparse, json, os, re, shutil, sqlite3, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG  = REPO / "changelog" / "log.jsonl"
MD   = REPO / "CHANGELOG.md"
DBP  = REPO / "changelog" / ".cache" / "changelog.db"

PREAMBLE = (
    "# CHANGELOG — TECT (verification-first repository)\n\n"
    "One entry per accepted change set. Newest first. Entries reference claim IDs,\n"
    "not pillar counts.\n\n---\n\n"
)
SPLIT_RE = re.compile(r"(?m)^## \[")
DATE_RE  = re.compile(r"(\d{4}-\d{2}-\d{2})\s*$")
CLAIM_RE = re.compile(r"\b([A-F]\d+[A-Z]?-[A-Z0-9][A-Z0-9-]{2,})\b")
NEG_RE   = re.compile(r"\b((?:R|F|NG|AUDIT)-\d{4}-[0-9A-Za-z][0-9A-Za-z-]*)")


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent)); os.close(fd)
    Path(tmp).write_text(text, encoding="utf-8")
    os.replace(tmp, str(path))


def load():
    if not LOG.exists():
        return []
    return [json.loads(ln) for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]


def save(entries):
    atomic_write(LOG, "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries))


def _meta(raw):
    return dict(claim_ids=sorted(set(CLAIM_RE.findall(raw))),
                neg_results=sorted(set(NEG_RE.findall(raw))))


def _slug(date, header):
    return f"{date.replace('-','')}-" + re.sub(r"[^a-z0-9]+", "-", header.lower())[:48].strip("-")


def render(entries=None):
    entries = load() if entries is None else entries
    return PREAMBLE + "".join(e["raw"] for e in reversed(entries))  # oldest-first storage -> newest-first view


def cmd_render(args):
    out = render()
    if args.check:
        cur = MD.read_text(encoding="utf-8") if MD.exists() else ""
        if cur != out:
            print("CHANGELOG-SYNC: FAIL -- CHANGELOG.md is out of sync with changelog/log.jsonl")
            print("  fix: python verification/scripts/changelog.py render")
            return 1
        print("CHANGELOG-SYNC: PASS")
        return 0
    atomic_write(MD, out)
    print(f"CHANGELOG: rendered {len(load())} entries -> CHANGELOG.md")
    return 0


def cmd_add(args):
    body = sys.stdin.read() if not sys.stdin.isatty() else (args.body or "")
    body = body.rstrip("\n")
    raw = f"## [{args.title}] - {args.date}\n\n{body}\n\n"
    header = f"[{args.title}] - {args.date}"
    m = _meta(raw)
    entry = dict(id=_slug(args.date, header), date=args.date, header=header,
                 claim_ids=sorted(set((args.claims or []) + m["claim_ids"])),
                 keywords=sorted(set(args.keywords or [])),
                 neg_results=sorted(set((args.neg or []) + m["neg_results"])),
                 notes=args.notes or [], scripts=args.scripts or [], raw=raw)
    entries = load(); entries.append(entry); save(entries)  # EOF == newest
    atomic_write(MD, render())
    print(f"changelog: added {entry['id']} ({len(entries)} entries)")
    return 0


def cmd_search(args):
    if args.fts:
        return _search_fts(args)
    res = []
    for e in reversed(load()):  # newest-first
        if args.claim and args.claim not in e.get("claim_ids", []):
            continue
        hay = (" ".join(e.get("keywords", [])) + " " + e["raw"]).lower()
        if args.keyword and args.keyword.lower() not in hay:
            continue
        if args.tier and args.tier not in e["raw"]:
            continue
        if args.since and e["date"] < args.since:
            continue
        if args.text and args.text.lower() not in e["raw"].lower():
            continue
        res.append(e)
        if args.limit and len(res) >= args.limit:
            break
    for e in res:
        cl = ",".join(e.get("claim_ids", [])) or "-"
        print(f"{e['date']}  [{cl}]  {e.get('header','')}")
        if e.get("neg_results"):
            print(f"            neg: {','.join(e['neg_results'])}")
    print(f"\n{len(res)} match(es).")
    return 0


def _build_local():
    """Build the FTS5 index on LOCAL disk (sqlite cannot operate on some virtual
    mounts) and return (db_path, temp_dir)."""
    d = tempfile.mkdtemp(prefix="cl_fts_")
    p = os.path.join(d, "changelog.db")
    con = sqlite3.connect(p)
    con.execute("CREATE VIRTUAL TABLE cl USING fts5(id, date, header, claims, negs, body)")
    for e in load():
        con.execute("INSERT INTO cl VALUES (?,?,?,?,?,?)",
                    (e.get("id", ""), e["date"], e.get("header", ""), " ".join(e.get("claim_ids", [])),
                     " ".join(e.get("neg_results", [])), e["raw"]))
    con.commit(); con.close()
    return p, d


def build_db():
    p, d = _build_local()
    DBP.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(p, str(DBP)); ok = True
    except OSError as ex:
        print(f"  (cache not persisted to {DBP.relative_to(REPO)} on this filesystem: {ex}; "
              "local build OK -- the operator side persists it on local disk)")
        ok = False
    shutil.rmtree(d, ignore_errors=True)
    return ok


def _search_fts(args):
    p, d = _build_local()  # query a fresh local build (mount-safe)
    con = sqlite3.connect(p)
    q = args.text or args.keyword or args.claim or '""'
    rows = con.execute("SELECT date, claims, header FROM cl WHERE cl MATCH ? ORDER BY date DESC LIMIT ?",
                       (q, args.limit or 50)).fetchall()
    for dd, cl, h in rows:
        print(f"{dd}  [{cl or '-'}]  {h}")
    print(f"\n{len(rows)} match(es) [fts].")
    con.close()
    shutil.rmtree(d, ignore_errors=True)
    return 0


def cmd_build_db(args):
    build_db()
    print(f"changelog: built FTS5 cache ({len(load())} entries) -> {DBP.relative_to(REPO)} (gitignored)")
    return 0


def cmd_migrate(args):
    src = MD.read_text(encoding="utf-8")
    m = SPLIT_RE.search(src)
    if not m:
        print("migrate: no entries found"); return 1
    pre = src[:m.start()]
    if pre != PREAMBLE:
        print("migrate: PREAMBLE mismatch -- fix the constant. repr(file preamble):")
        print(repr(pre)); return 1
    starts = [mm.start() for mm in SPLIT_RE.finditer(src)]
    entries, undated = [], []  # file order == newest-first
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(src)
        blk = src[s:e]
        first = blk.split("\n", 1)[0]
        dm = DATE_RE.search(first)
        date = dm.group(1) if dm else ""
        if not dm:
            undated.append(first[:70])
        header = first[3:].strip()  # drop "## "
        meta = _meta(blk)
        entries.append(dict(id=_slug(date or "00000000", header), date=date, header=header,
                            claim_ids=meta["claim_ids"], keywords=[], neg_results=meta["neg_results"],
                            notes=[], scripts=[], raw=blk))
    if undated:
        print(f"migrate: WARNING {len(undated)} header(s) without a trailing date (stored, date=''):")
        for u in undated[:5]:
            print(f"    {u}")
    save(list(reversed(entries)))  # store oldest-first
    out = render()
    if out != src:
        for i, (a, b) in enumerate(zip(out, src)):
            if a != b:
                print(f"migrate: ROUND-TRIP MISMATCH @ {i}: out={out[i:i+40]!r} src={src[i:i+40]!r}"); break
        else:
            print(f"migrate: length diff out={len(out)} src={len(src)}")
        return 1
    print(f"migrate: {len(entries)} entries -> changelog/log.jsonl; render == CHANGELOG.md (LOSSLESS)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render"); r.add_argument("--check", action="store_true"); r.set_defaults(fn=cmd_render)
    a = sub.add_parser("add")
    for opt in ("--title", "--date"):
        a.add_argument(opt, required=True)
    for opt in ("--claims", "--neg", "--notes", "--scripts", "--keywords"):
        a.add_argument(opt, nargs="*")
    a.add_argument("--body"); a.set_defaults(fn=cmd_add)
    s = sub.add_parser("search")
    for opt in ("--claim", "--keyword", "--tier", "--since", "--text"):
        s.add_argument(opt)
    s.add_argument("--fts", action="store_true"); s.add_argument("--limit", type=int, default=0)
    s.set_defaults(fn=cmd_search)
    sub.add_parser("build-db").set_defaults(fn=cmd_build_db)
    sub.add_parser("migrate").set_defaults(fn=cmd_migrate)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
