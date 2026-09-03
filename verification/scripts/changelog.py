#!/usr/bin/env python3
"""changelog.py -- JSONL-sourced CHANGELOG with a generated Markdown view and a
git-ignored full-text query cache.

Design (governance/changelog-db.md):
  * SOURCE OF TRUTH   changelog/log.jsonl   (append-only, one JSON object/line,
                      oldest-first; new entries appended at EOF).
  * COMPATIBILITY     CHANGELOG.md          (frozen through the declared v1
                      cutover so historical verifier hashes and prose searches
                      remain reproducible; it no longer grows).
  * GENERATED VIEW    changelog/INDEX.md    (compact current landing) plus
                      changelog/pages/YYYY-MM.md (post-cutover full bodies;
                      every new body appears in exactly one bounded page).
                      Never hand-edited; release_check enforces the whole set.
  * QUERY CACHE       changelog/.cache/changelog.db  (gitignored SQLite FTS5;
                      rebuildable from log.jsonl by `build-db`).

Truncation resilience (2026-06-23): the repo lives inside a Google-Drive-synced
folder that can corrupt files post-write. load() is tolerant (skips corrupted lines
with a stderr warning instead of crashing every command on one bad line); `verify`
strictly checks log.jsonl parses + contains every git-HEAD entry + CHANGELOG.md sync
(wired into release_check); `repair` recovers from git HEAD (union with valid
working-tree appends, dropping corrupted lines); build-db writes the .db atomically
(os.replace, no truncated cache on interrupt) and cleans stale temp artefacts; `add`
refuses to persist over a corrupted log (no silent data loss).

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
  1.0.1 (2026-07-20) honor --body when a non-interactive caller exposes an
        empty stdin stream; previously such calls silently emitted blank bodies.
  1.0.2 (2026-08-02) decode git-show output explicitly as UTF-8 and make the
        verification gate fail closed when the committed source is unavailable,
        undecodable, or malformed.
  1.0.3 (2026-08-09) preserve the exact committed JSONL prefix and line endings;
        append only the new compact record instead of reserializing history.
  1.1.0 (2026-08-10) freeze the legacy Markdown mirror and add a compact
        landing page, bounded single-copy pages, and a stable locator index.
"""
__version__ = "1.1.0"

import argparse, hashlib, json, os, re, shutil, sqlite3, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG  = REPO / "changelog" / "log.jsonl"
MD   = REPO / "CHANGELOG.md"
DBP  = REPO / "changelog" / ".cache" / "changelog.db"
PAGES = REPO / "changelog" / "pages"
LOCATORS = REPO / "changelog" / "locators"
INDEX = REPO / "changelog" / "index.json"
LANDING = REPO / "changelog" / "INDEX.md"
RECENT_COUNT = 25
PAGE_SIZE = 50
LOCATOR_SIZE = 100
CUTOVER_COUNT = 568
CUTOVER_COMMIT = "4db22f4ea94bb1a936d1a2e4b416aa2d6d1960d4"

LEGACY_PREAMBLE = (
    "# CHANGELOG — TECT (verification-first repository)\n\n"
    "One entry per accepted change set. Newest first. Entries reference claim IDs,\n"
    "not pillar counts.\n\n---\n\n"
)
LANDING_PREAMBLE = (
    "# TECT changelog index\n\n"
    "Compact generated reader surface. The append-only authority is\n"
    "`log.jsonl`. `../CHANGELOG.md` is a frozen compatibility volume through\n"
    f"record {CUTOVER_COUNT} / commit `{CUTOVER_COMMIT[:8]}` and no longer grows.\n"
    "Post-cutover full bodies live exactly once in bounded pages under `pages/`.\n\n"
)
SPLIT_RE = re.compile(r"(?m)^## \[")
DATE_RE  = re.compile(r"(\d{4}-\d{2}-\d{2})\s*$")
CLAIM_RE = re.compile(r"\b([A-F]\d+[A-Z]?-[A-Z0-9][A-Z0-9-]{2,})\b")
NEG_RE   = re.compile(r"\b((?:R|F|NG|AUDIT)-\d{4}-[0-9A-Za-z][0-9A-Za-z-]*)")


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent)); os.close(fd)
    with Path(tmp).open("w", encoding="utf-8", newline="") as stream:
        stream.write(text)
    os.replace(tmp, str(path))


def _parse_lines(text):
    """Parse JSONL text -> (entries, bad_line_numbers). Never raises on a bad line.
    Drive can truncate log.jsonl mid-write; this isolates the damage."""
    entries, bad = [], []
    for i, ln in enumerate(text.splitlines(), start=1):
        if not ln.strip():
            continue
        try:
            entries.append(json.loads(ln))
        except json.JSONDecodeError:
            bad.append(i)
    return entries, bad


def _git_head_text(strict=False):
    """Exact committed log text, preserving historical JSON serialization."""
    import subprocess
    try:
        out = subprocess.run(["git", "show", "HEAD:changelog/log.jsonl"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="strict", cwd=str(REPO), timeout=30)
        if out.returncode != 0:
            if strict:
                detail = (out.stderr or "").strip()
                raise RuntimeError(
                    f"git show HEAD:changelog/log.jsonl exited {out.returncode}"
                    + (f": {detail}" if detail else "")
                )
            return ""
        return out.stdout
    except Exception as exc:
        if strict:
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError(
                f"cannot read git HEAD changelog as UTF-8: {exc}"
            ) from exc
        return ""


def _git_head_entries(strict=False):
    """Entries from the committed log.jsonl (git HEAD) -- the recovery source that
    Drive working-tree corruption cannot touch.  Recovery callers receive [] if
    git/blob is unavailable; the verification gate uses strict=True and fails
    closed instead."""
    try:
        text = _git_head_text(strict=strict)
        if not text:
            return []
        ents, bad = _parse_lines(text)
        if bad:
            if strict:
                raise RuntimeError(
                    f"git HEAD changelog contains unparseable line(s) at {bad}"
                )
            return []
        return ents
    except Exception as exc:
        if strict:
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError(
                f"cannot read git HEAD changelog as UTF-8: {exc}"
            ) from exc
        return []


def load():
    """Tolerant load: never crashes on a corrupted line (the historical failure mode
    where one Drive-truncated line broke every changelog command). Corruption is
    surfaced as a stderr warning; strict checking is `verify`, recovery is `repair`."""
    if not LOG.exists():
        return []
    entries, bad = _parse_lines(LOG.read_text(encoding="utf-8"))
    if bad:
        sys.stderr.write(f"[changelog] WARNING: skipped {len(bad)} corrupted line(s) in "
                         f"changelog/log.jsonl at {bad}; run 'changelog.py repair' "
                         f"(recovers from git HEAD).\n")
    return entries


def _encode_entry(entry):
    return json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n"


def save(entries):
    atomic_write(
        LOG,
        "".join(_encode_entry(entry) for entry in entries),
    )


def _meta(raw):
    return dict(claim_ids=sorted(set(CLAIM_RE.findall(raw))),
                neg_results=sorted(set(NEG_RE.findall(raw))))


def _slug(date, header):
    return f"{date.replace('-','')}-" + re.sub(r"[^a-z0-9]+", "-", header.lower())[:48].strip("-")


def _cell(value):
    return str(value or "—").replace("|", "\\|").replace("\n", " ")


def _page_name(ordinal):
    """Stable post-cutover page for a one-based ledger ordinal."""
    if ordinal <= CUTOVER_COUNT:
        return None
    start = CUTOVER_COUNT + 1 + ((ordinal - CUTOVER_COUNT - 1) // PAGE_SIZE) * PAGE_SIZE
    end = start + PAGE_SIZE - 1
    return f"{start:06d}-{end:06d}.md"


def _locator_name(ordinal):
    start = 1 + ((ordinal - 1) // LOCATOR_SIZE) * LOCATOR_SIZE
    end = start + LOCATOR_SIZE - 1
    return f"{start:06d}-{end:06d}.json"


def _legacy_render(entries):
    if len(entries) < CUTOVER_COUNT:
        raise ValueError(
            f"changelog has {len(entries)} entries; cutover requires {CUTOVER_COUNT}"
        )
    return LEGACY_PREAMBLE + "".join(
        entry["raw"] for entry in reversed(entries[:CUTOVER_COUNT])
    )


def _page_groups(entries):
    groups = {}
    for ordinal, entry in enumerate(entries, start=1):
        name = _page_name(ordinal)
        if name:
            groups.setdefault(name, []).append((ordinal, entry))
    return groups


def _locator_groups(entries):
    groups = {}
    for ordinal, entry in enumerate(entries, start=1):
        groups.setdefault(_locator_name(ordinal), []).append((ordinal, entry))
    return groups


def _render_landing(entries):
    groups = _page_groups(entries)
    lines = [LANDING_PREAMBLE.rstrip(), "",
             f"**{len(entries)} accepted events** · latest "
             f"{min(RECENT_COUNT, len(entries))} shown below · "
             "machine locator: `index.json`", "",
             "Search the complete authority without loading every page:", "",
             "```bash", "python verification/scripts/changelog.py search --text <phrase>",
             "```", "", "## Latest events", "",
             "| Date | Event | Claims | Full entry |", "|---|---|---|---|"]
    first_recent = max(1, len(entries) - RECENT_COUNT + 1)
    for ordinal in range(len(entries), first_recent - 1, -1):
        entry = entries[ordinal - 1]
        claims = ", ".join(entry.get("claim_ids", [])) or "—"
        page = _page_name(ordinal)
        target = f"pages/{page}#{entry['id']}" if page else "../CHANGELOG.md"
        label = "bounded page" if page else "legacy volume"
        lines.append(
            f"| {_cell(entry.get('date'))} | `{_cell(entry.get('id'))}` — "
            f"{_cell(entry.get('header'))} | {_cell(claims)} | "
            f"[{label}]({target}) |"
        )
    lines.extend(["", "## Post-cutover pages", "",
                  "Each full event body after the cutover occurs in exactly one page.", "",
                  "| Ordinals | Events | Page |", "|---|---:|---|"])
    if not groups:
        lines.append("| — | 0 | No post-cutover events yet |")
    for name, rows in sorted(groups.items(), reverse=True):
        lines.append(
            f"| {rows[0][0]}–{rows[-1][0]} | {len(rows)} | [{name}](pages/{name}) |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_page(name, rows):
    lines = [f"# TECT changelog — records {name[:-3]}", "",
             "<!-- AUTO-GENERATED by verification/scripts/changelog.py -->",
             "<!-- DO NOT HAND-EDIT. Authority: changelog/log.jsonl -->", "",
             f"**{len(rows)} events** · [compact index](../INDEX.md) · "
             "[machine locator](../index.json)", "", "---", ""]
    for _, entry in reversed(rows):
        lines.extend([f"<a id=\"{entry['id']}\"></a>", "", entry["raw"].rstrip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def _render_locator(name, rows):
    entries = []
    for ordinal, entry in rows:
        page = _page_name(ordinal)
        entries.append({
            "ordinal": ordinal,
            "id": entry["id"],
            "volume": (f"changelog/pages/{page}" if page else "CHANGELOG.md"),
            "anchor": (entry["id"] if page else None),
        })
    return json.dumps({
        "schema": "tect/changelog-locators/1.0",
        "range": name[:-5],
        "count": len(entries),
        "entries": entries,
    }, ensure_ascii=False, indent=2) + "\n"


def _index_payload(entries, locator_outputs):
    pages = _page_groups(entries)
    recent = [
        {
            "id": entry["id"],
            "date": entry.get("date", ""),
            "header": entry.get("header", ""),
            "claim_ids": entry.get("claim_ids", []),
        }
        for entry in reversed(entries[-RECENT_COUNT:])
    ]
    return {
        "schema": "tect/changelog-index/2.0",
        "authority": "changelog/log.jsonl",
        "cutover": {"records": CUTOVER_COUNT, "commit": CUTOVER_COMMIT,
                    "compatibility_volume": "CHANGELOG.md"},
        "total": len(entries),
        "recent_count": min(RECENT_COUNT, len(entries)),
        "recent": recent,
        "pages": [
            {"page": f"changelog/pages/{name}", "first_ordinal": rows_[0][0],
             "last_ordinal": rows_[-1][0], "count": len(rows_)}
            for name, rows_ in sorted(pages.items())
        ],
        "locators": [
            {
                "path": path.relative_to(REPO).as_posix(),
                "first_ordinal": rows_[0][0],
                "last_ordinal": rows_[-1][0],
                "count": len(rows_),
                "bytes": len(locator_outputs[path].encode("utf-8")),
                "sha256": hashlib.sha256(locator_outputs[path].encode("utf-8")).hexdigest(),
            }
            for name, rows_ in sorted(_locator_groups(entries).items())
            for path in [LOCATORS / name]
        ],
    }


def render_outputs(entries=None):
    entries = load() if entries is None else entries
    locator_outputs = {
        LOCATORS / name: _render_locator(name, rows)
        for name, rows in _locator_groups(entries).items()
    }
    outputs = {
        LANDING: _render_landing(entries),
        INDEX: json.dumps(
            _index_payload(entries, locator_outputs), ensure_ascii=False, indent=2
        ) + "\n",
        **locator_outputs,
    }
    for name, rows in _page_groups(entries).items():
        outputs[PAGES / name] = _render_page(name, rows)
    return outputs


def render(entries=None):
    entries = load() if entries is None else entries
    return _legacy_render(entries)


def _stale_page_paths(outputs):
    expected = {path.resolve() for path in outputs if path.parent == PAGES}
    actual = {path.resolve() for path in PAGES.glob("*.md")} if PAGES.exists() else set()
    return sorted(actual - expected)


def _stale_locator_paths(outputs):
    expected = {path.resolve() for path in outputs if path.parent == LOCATORS}
    actual = ({path.resolve() for path in LOCATORS.glob("*.json")}
              if LOCATORS.exists() else set())
    return sorted(actual - expected)


def _write_views(entries):
    outputs = render_outputs(entries)
    atomic_write(MD, _legacy_render(entries))
    for path, text in outputs.items():
        atomic_write(path, text)
    for path in _stale_page_paths(outputs):
        path.unlink()
    for path in _stale_locator_paths(outputs):
        path.unlink()
    return outputs


def cmd_render(args):
    entries = load()
    outputs = render_outputs(entries)
    if args.check:
        stale = []
        if not MD.exists() or MD.read_text(encoding="utf-8") != _legacy_render(entries):
            stale.append(MD)
        stale.extend(path for path, text in outputs.items()
                     if not path.exists() or path.read_text(encoding="utf-8") != text)
        stale.extend(_stale_page_paths(outputs))
        stale.extend(_stale_locator_paths(outputs))
        if stale:
            print("CHANGELOG-SYNC: FAIL -- generated changelog views are stale")
            for path in stale[:10]:
                print(f"  - {path.relative_to(REPO)}")
            print("  fix: python verification/scripts/changelog.py render")
            return 1
        print("CHANGELOG-SYNC: PASS")
        return 0
    _write_views(entries)
    print(f"CHANGELOG: preserved {CUTOVER_COUNT}-entry CHANGELOG.md + rendered "
          f"{len(entries)}-entry compact index + {len(_page_groups(entries))} body page(s) + "
          f"{len(_locator_groups(entries))} locator shard(s)")
    return 0


def cmd_add(args):
    if LOG.exists():
        _, bad = _parse_lines(LOG.read_text(encoding="utf-8"))
        if bad:
            print(f"changelog add: REFUSED -- changelog/log.jsonl has {len(bad)} corrupted line(s) "
                  f"at {bad}. Run 'changelog.py repair' first (recovers from git HEAD), then retry.")
            return 1
    stdin_body = sys.stdin.read() if not sys.stdin.isatty() else ""
    body = stdin_body if stdin_body else (args.body or "")
    body = body.rstrip("\n")
    raw = f"## [{args.title}] - {args.date}\n\n{body}\n\n"
    header = f"[{args.title}] - {args.date}"
    m = _meta(raw)
    entry = dict(id=_slug(args.date, header), date=args.date, header=header,
                 claim_ids=sorted(set((args.claims or []) + m["claim_ids"])),
                 keywords=sorted(set(args.keywords or [])),
                 neg_results=sorted(set((args.neg or []) + m["neg_results"])),
                 notes=args.notes or [], scripts=args.scripts or [], raw=raw)
    entries = load()
    if entry["id"] in {row.get("id") for row in entries}:
        print(f"changelog add: REFUSED -- duplicate event id {entry['id']}")
        return 1
    entries.append(entry)  # EOF == newest
    previous = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    if previous and not previous.endswith("\n"):
        previous += "\n"
    atomic_write(LOG, previous + _encode_entry(entry))
    _write_views(entries)
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
    DBP.parent.mkdir(parents=True, exist_ok=True)
    # clean stale temp artefacts left by interrupted builds (Drive/timeout)
    for pat in ("tmp*.db", "tmp*.db-journal", "*.db-journal"):
        for f in DBP.parent.glob(pat):
            try:
                f.unlink()
            except OSError:
                pass
    p, d = _build_local()
    ok = False
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=str(DBP.parent), suffix=".db"); os.close(fd)
        shutil.copyfile(p, tmp)        # copy local build onto the mount, then
        os.replace(tmp, str(DBP)); ok = True   # ATOMIC swap (no truncated .db on interrupt)
    except OSError as ex:
        print(f"  (cache not persisted to {DBP.relative_to(REPO)} on this filesystem: {ex}; "
              "local build OK -- the operator side persists it on local disk)")
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
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
    print("migrate: RETIRED -- changelog/log.jsonl is already authoritative; "
          "CHANGELOG.md is a frozen compatibility volume")
    return 1


def cmd_verify(args):
    """Strict integrity check (gate): log.jsonl fully parses, contains every
    committed (git HEAD) entry, and CHANGELOG.md is in sync. Detects Drive
    truncation/loss before it reaches a commit."""
    problems = []
    if not LOG.exists():
        print("CHANGELOG-VERIFY: FAIL -- changelog/log.jsonl missing"); return 1
    text = LOG.read_text(encoding="utf-8")
    entries, bad = _parse_lines(text)
    if bad:
        problems.append(f"{len(bad)} unparseable line(s) at {bad} (truncation/corruption)")
    try:
        head_text = _git_head_text(strict=True)
        head, head_bad = _parse_lines(head_text)
        if head_bad:
            raise RuntimeError(f"git HEAD changelog contains unparseable line(s) at {head_bad}")
    except RuntimeError as exc:
        head_text = ""
        head = []
        problems.append(f"committed changelog audit unavailable: {exc}")
    if head_text and not text.startswith(head_text):
        problems.append("working changelog does not preserve the committed byte prefix")
    ids = [entry.get("id") for entry in entries]
    cur_ids = set(ids)
    if len(cur_ids) != len(ids):
        problems.append(f"{len(ids) - len(cur_ids)} duplicate event id(s)")
    lost = [e.get("id") for e in head if e.get("id") not in cur_ids]
    if lost:
        problems.append(f"{len(lost)} committed entry/entries missing from working tree "
                        f"(e.g. {lost[:3]})")
    if len(entries) < CUTOVER_COUNT:
        problems.append(
            f"only {len(entries)} entries; compatibility cutover requires {CUTOVER_COUNT}"
        )
    else:
        if not MD.exists() or MD.read_text(encoding="utf-8") != _legacy_render(entries):
            problems.append("frozen CHANGELOG.md compatibility volume is stale")
        outputs = render_outputs(entries)
        stale = [path for path, expected in outputs.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != expected]
        stale.extend(_stale_page_paths(outputs))
        stale.extend(_stale_locator_paths(outputs))
        if stale:
            examples = [str(path.relative_to(REPO)) for path in stale[:3]]
            problems.append(f"generated compact changelog views are stale (e.g. {examples})")
    if problems:
        print("CHANGELOG-VERIFY: FAIL")
        for pr in problems:
            print(f"  - {pr}")
        print("  fix: python verification/scripts/changelog.py repair")
        return 1
    print(f"CHANGELOG-VERIFY: PASS ({len(entries)} entries)")
    return 0


def cmd_repair(args):
    """Recover changelog/log.jsonl from Drive truncation/corruption: union the
    committed git-HEAD entries with any valid working-tree-only (new, uncommitted)
    entries, drop corrupted lines, then re-write log.jsonl + CHANGELOG.md + db."""
    cur, bad = (_parse_lines(LOG.read_text(encoding="utf-8")) if LOG.exists() else ([], []))
    head_text = _git_head_text()
    head, head_bad = _parse_lines(head_text) if head_text else ([], [])
    if head_bad:
        head_text, head = "", []
    by_id, order = {}, []
    for e in head + cur:               # HEAD first (committed history), then new appends
        eid = e.get("id")
        if eid and eid not in by_id:
            by_id[eid] = e; order.append(eid)
    recovered = [by_id[i] for i in order]
    added = len([e for e in cur if e.get("id") not in {h.get("id") for h in head}])
    if head_text and not head_text.endswith("\n"):
        head_text += "\n"
    head_ids = {entry.get("id") for entry in head}
    new_entries = [entry for entry in cur if entry.get("id") not in head_ids]
    if head_text:
        atomic_write(LOG, head_text + "".join(_encode_entry(entry) for entry in new_entries))
    else:
        save(recovered)
    _write_views(recovered)
    build_db()
    print(f"changelog repair: {len(recovered)} entries restored "
          f"(git HEAD {len(head)} + {added} working-tree-only; dropped {len(bad)} corrupted line(s)). "
           f"log.jsonl + compatibility/compact views + db rebuilt atomically.")
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
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    sub.add_parser("repair").set_defaults(fn=cmd_repair)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
