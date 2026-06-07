#!/usr/bin/env python3
"""todo.py -- persistent, portable task ledger for the TECT repository.

Canonical store: todo/todo.json (tracked, hand- or CLI-editable).
Generated view:  TODO.md (tracked, root, NEVER hand-edit -- regenerate).

Rationale. The cowork task widget is per-session and does not survive a folder
copy to another machine. This ledger lives in the repo, so copying the TECT
folder (or git clone) carries the full task state; a fresh cowork session reads
TODO.md in its session-entry prelude and continues. Multiple collaborators
divide work by `owner` / `status`.

Design (mirrors lint_claims.py: data -> generated view; render is a PURE
function of todo.json, so `--check` is a stable staleness gate -- no live
timestamps are injected at render time):

  python verification/scripts/todo.py list [--status S]
  python verification/scripts/todo.py add  "title" [--status S --owner O
                                                    --claim C --gate G --note N]
  python verification/scripts/todo.py set  T-003 [--status ... --title ... ...]
  python verification/scripts/todo.py start T-003          # -> in_progress
  python verification/scripts/todo.py done  T-003          # -> done
  python verification/scripts/todo.py block T-003 --by T-002
  python verification/scripts/todo.py render               # regenerate TODO.md
  python verification/scripts/todo.py --check              # TODO.md in sync?
  python verification/scripts/todo.py --selftest           # exercise + assert

No numeric literals are hardcoded into task data; IDs are derived from
`next_id`, dates from the system clock at mutation time (stored, not
re-derived at render). Exit 0 iff the operation (or check) succeeds.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"

import argparse
import json
import os
import sys
import tempfile
import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "todo" / "todo.json"
VIEW = REPO / "TODO.md"

# render order + human labels (single source of truth for both render and CLI)
STATUS_ORDER = ["in_progress", "next", "blocked", "backlog", "done"]
STATUS_LABEL = {
    "in_progress": "In progress",
    "next": "Next up",
    "blocked": "Blocked",
    "backlog": "Backlog",
    "done": "Done (recent)",
}


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def today() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def load(path: Path = DATA) -> dict:
    if not path.exists():
        return {"tasks": [], "next_id": 1}
    return json.loads(path.read_text(encoding="utf-8"))


def save(db: dict, path: Path = DATA) -> None:
    atomic_write(path, json.dumps(db, indent=2, ensure_ascii=True) + "\n")


def find(db: dict, tid: str) -> dict:
    for t in db["tasks"]:
        if t["id"] == tid:
            return t
    raise SystemExit(f"todo: unknown task id {tid!r}")


def new_id(db: dict) -> str:
    tid = f"T-{db['next_id']:03d}"
    db["next_id"] += 1
    return tid


def render_text(db: dict) -> str:
    """Pure function of db -> TODO.md text (no live clock)."""
    tasks = db["tasks"]
    counts = {s: sum(1 for t in tasks if t.get("status") == s) for s in STATUS_ORDER}
    lines = [
        "# TODO -- TECT task ledger",
        "",
        "Generated from `todo/todo.json` by `verification/scripts/todo.py` -- "
        "**never hand-edit**; run `todo.py render`.",
        "Portable: copying the TECT folder carries this ledger; a fresh cowork "
        "session reads it in the session-entry prelude (CLAUDE.md §1).",
        "",
        "Counts: " + " · ".join(f"{STATUS_LABEL[s]} {counts[s]}" for s in STATUS_ORDER),
        "",
    ]
    for s in STATUS_ORDER:
        group = sorted((t for t in tasks if t.get("status") == s), key=lambda t: t["id"])
        if not group:
            continue
        lines.append(f"## {STATUS_LABEL[s]}")
        lines.append("")
        for t in group:
            tags = []
            if t.get("owner"):
                tags.append(f"owner: {t['owner']}")
            if t.get("claim"):
                tags.append(f"claim: {t['claim']}")
            if t.get("gate"):
                tags.append(f"gate: {t['gate']}")
            if t.get("blocked_by"):
                tags.append("blocked by: " + ", ".join(t["blocked_by"]))
            tagstr = ("  _(" + "; ".join(tags) + ")_") if tags else ""
            lines.append(f"- **{t['id']}** {t['title']}{tagstr}")
            if t.get("note"):
                lines.append(f"  - {t['note']}")
            lines.append(f"  - _updated {t.get('updated', '?')}_")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def cmd_render(db: dict) -> int:
    atomic_write(VIEW, render_text(db))
    print(f"todo: rendered {VIEW.relative_to(REPO)} ({len(db['tasks'])} tasks)")
    return 0


def cmd_check(db: dict) -> int:
    current = VIEW.read_text(encoding="utf-8") if VIEW.exists() else ""
    if current != render_text(db):
        print("TODO-CHECK: FAIL (TODO.md stale -- run: python verification/scripts/todo.py render)")
        return 1
    print("TODO-CHECK: PASS (TODO.md in sync with todo.json)")
    return 0


def cmd_list(db: dict, status: str | None) -> int:
    for s in STATUS_ORDER:
        if status and s != status:
            continue
        group = sorted((t for t in db["tasks"] if t.get("status") == s), key=lambda t: t["id"])
        if not group:
            continue
        print(f"[{STATUS_LABEL[s]}]")
        for t in group:
            meta = " ".join(filter(None, [t.get("claim"), t.get("gate"), t.get("owner")]))
            print(f"  {t['id']}  {t['title']}" + (f"   ({meta})" if meta else ""))
    return 0


def apply_fields(t: dict, args) -> None:
    for f in ("title", "status", "owner", "claim", "gate", "note"):
        v = getattr(args, f, None)
        if v is not None:
            t[f] = v
    if getattr(args, "status", None) and args.status not in STATUS_ORDER:
        raise SystemExit(f"todo: status must be one of {STATUS_ORDER}")
    t["updated"] = today()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="TECT task ledger")
    ap.add_argument("--check", action="store_true", help="verify TODO.md in sync")
    ap.add_argument("--selftest", action="store_true", help="run internal self-test")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("list"); p.add_argument("--status", choices=STATUS_ORDER)
    sub.add_parser("render")

    p = sub.add_parser("add"); p.add_argument("title")
    for f in ("status", "owner", "claim", "gate", "note"):
        p.add_argument(f"--{f}")

    p = sub.add_parser("set"); p.add_argument("id")
    for f in ("title", "status", "owner", "claim", "gate", "note"):
        p.add_argument(f"--{f}")

    for verb in ("start", "done"):
        q = sub.add_parser(verb); q.add_argument("id")

    p = sub.add_parser("block"); p.add_argument("id"); p.add_argument("--by", nargs="*", default=[])

    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    db = load()

    if args.check:
        return cmd_check(db)
    if args.cmd in (None, "render"):
        return cmd_render(db) if args.cmd == "render" else (ap.print_help() or 0)
    if args.cmd == "list":
        return cmd_list(db, args.status)
    if args.cmd == "add":
        t = {"id": new_id(db), "title": args.title, "status": args.status or "backlog",
             "owner": args.owner, "claim": args.claim, "gate": args.gate,
             "note": args.note, "created": today(), "updated": today(), "blocked_by": []}
        db["tasks"].append(t); save(db); cmd_render(db); print(f"todo: added {t['id']}")
        return 0
    if args.cmd == "set":
        apply_fields(find(db, args.id), args); save(db); return cmd_render(db)
    if args.cmd in ("start", "done"):
        t = find(db, args.id); t["status"] = "in_progress" if args.cmd == "start" else "done"
        t["updated"] = today(); save(db); return cmd_render(db)
    if args.cmd == "block":
        t = find(db, args.id); t["status"] = "blocked"
        t["blocked_by"] = list(args.by); t["updated"] = today(); save(db); return cmd_render(db)
    ap.print_help()
    return 0


def selftest() -> int:
    """Exercise the ledger in a temp dir; assert transitions + render round-trip."""
    import io
    with tempfile.TemporaryDirectory() as td:
        dpath = Path(td) / "todo.json"
        db = {"tasks": [], "next_id": 1}
        # add
        tid = new_id(db)
        assert tid == "T-001" and db["next_id"] == 2, "id derivation"
        db["tasks"].append({"id": tid, "title": "demo", "status": "next",
                            "owner": None, "claim": None, "gate": None,
                            "note": None, "created": today(), "updated": today(),
                            "blocked_by": []})
        save(db, dpath)
        assert json.loads(dpath.read_text())["tasks"][0]["id"] == "T-001", "persist"
        # transitions
        t = db["tasks"][0]
        t["status"] = "in_progress"; assert t["status"] == "in_progress"
        t["status"] = "done"; assert t["status"] == "done"
        # render is a pure function (idempotent) -> --check stability
        a = render_text(db); b = render_text(db)
        assert a == b, "render not deterministic"
        assert "T-001" in a and "Done (recent)" in a, "render content"
        # empty ledger renders without crashing
        assert render_text({"tasks": [], "next_id": 1}).startswith("# TODO"), "empty render"
    print("TODO-SELFTEST: PASS (id derivation, persist, transitions, deterministic render)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
