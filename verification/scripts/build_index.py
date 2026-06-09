"""build_index.py -- reviewer-facing comprehensive proof-unit index.

Generates a two-level index so a reviewer can approach the theory top-down:

  claims/INDEX.md          master map: sector -> claim (tier, hypotheses, gates,
                           falsifier) -> sub-proofs (note counts, tier span).
  claims/<ID>/INDEX.md     per-claim: sub-proof -> note-lineage table with, for
                           each proof unit, its Result ID, current tier/status,
                           ONE-LINE statement of what it proves (the note footer
                           'Precise statement'), evidence grade, and next action.

The per-proof-unit data is parsed from the UNIFORM note footer that every TECT
note carries (Result ID / Precise statement / Evidence grade / Tier before /
after / Falsification gate / Next required action). Tier is the last T[0-7]
token in the footer 'Tier before / after' field (the 'after' tier), or the
claim tier when the note declares 'no tier change'.

Sub-proof grouping: if a claim has physical sub-proof folders
(claims/<ID>/<sub>/notes/), those are used. Otherwise the notes in the flat
claims/<ID>/notes/ are grouped by the descriptor-prefix taxonomy below (so the
index previews the proposed structure before any file is moved).

GENERATED FILE -- never hand-edit claims/INDEX.md or claims/<ID>/INDEX.md.
Regenerate after any notes/ or status.json change:
    python verification/scripts/build_index.py            # write
    python verification/scripts/build_index.py --check     # CI staleness gate
"""
__version__ = "1.0.1"  # 1.0.1 (2026-06-09): sort sub-proof folders by name, not by
#                       Path object -- WindowsPath compares case-insensitively while
#                       PosixPath is case-sensitive, which reordered mixed-case sub-
#                       folders (e.g. B1-RH-ENUM) and made the index falsely STALE on
#                       Windows after Linux generation (cross-OS reproducibility bug).

import os, re, sys, json, tempfile
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parents[2]
CLAIMS = REPO / "claims"

SECTORS = {
    "A": "Microscopic Foundation",
    "B": "Vacuum / Reading Selection",
    "C": "Spacetime / Lorentz / Gravity",
    "D": "Gauge / Matter / Topology",
    "E": "Spectrum / Couplings / Constants",
    "F": "Cosmology / Falsifiability",
}

# Provisional descriptor-prefix taxonomy (used only when a claim has no physical
# sub-proof folders yet). Order matters: first matching bucket wins.
TAXONOMY = {
    "B5-BEYOND-LAYER-BOUND": [
        ("DR-2",        ("dr2",)),
        ("SC-SCOPE",    ("scscope",)),
        ("STEP-5B",     ("beyond-layer-gershgorin", "rectangle-constant", "tadpole",
                         "sunset", "quartic", "dyadic-lift", "cross-pin", "third-cumulant")),
        ("H-LAYER-AUX", ("hlayer", "coherence", "hadmcoh")),
        ("T5-DOSSIER",  ("t5-assignment",)),
    ],
    "B1-RH-ENUM": [
        ("Reading-H",         ("reading", "t6")),
        ("ROBUSTNESS-MU2",    ("robustness",)),
        ("near-gap",          ("neargap",)),
        ("ESTIMATOR-UPGRADE", ("estimator", "twoshell", "g3pb")),
        ("enumerated",        ("enumerat", "useries")),
    ],
    "B2-PROPA-HLAYER": [
        ("Prop-A",       ("proposition-a",)),
        ("H-A0-removal", ("ha0",)),
        ("G-A0-DUI",     ("ga0",)),
    ],
}

FOOTER_LABELS = ["Result ID", "Precise statement", "Scope", "Dependencies",
                 "Evidence grade", "Reproduction command", "Expected output",
                 "Falsification gate", "Tier before / after",
                 "No-overclaim statement", "Next required action"]
_LABEL_RE = re.compile(r"^(" + "|".join(re.escape(l) for l in FOOTER_LABELS) + r"):\s*(.*)$")

def lineage_slug(fn):
    return re.sub(r"-\d{6}(-\d{6})?-v\d+\.\d+\.tex\.txt$", "", fn)

def vnum(fn):
    m = re.search(r"-v(\d+)\.(\d+)\.tex\.txt$", fn)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

def parse_note(path):
    """Return dict: title, status, footer{label:value}."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    d = {"title": "", "status": "", "footer": {}, "superseded": text.lstrip().startswith("% SUPERSEDED")}
    m = re.search(r"% Title:\s*(.+)", text)
    if m:
        d["title"] = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"% Status:\s*(.+)", text)
    if m:
        d["status"] = re.sub(r"\s+", " ", m.group(1)).strip()
    # footer line-based parse
    cur = None
    for line in text.splitlines():
        mm = _LABEL_RE.match(line)
        if mm:
            cur = mm.group(1)
            d["footer"][cur] = mm.group(2).strip()
        elif cur and line.strip() and not line.strip().startswith(("%", r"\end", r"\begin")):
            # continuation line (indented value)
            if line.startswith((" ", "\t")):
                d["footer"][cur] = (d["footer"][cur] + " " + line.strip()).strip()
            else:
                cur = None
    return d

def tier_token(footer, claim_tier):
    raw = footer.get("Tier before / after", "")
    # a note that declares no tier change inherits its claim's tier (marked *),
    # even if the field mentions other claims' tiers (e.g. "B1 T6 unchanged").
    if re.search(r"no tier[ /-]?(change|flip|action)|tier unchanged|unchanged", raw, re.I):
        return f"{claim_tier}*" if claim_tier else "—"
    toks = re.findall(r"\bT[0-7]\b", raw)
    if toks:
        return toks[-1]
    return "—"

def shorten(s, n=120):
    s = re.sub(r"\s+", " ", s or "").strip()
    return (s[: n - 1] + "…") if len(s) > n else s

def sub_groups(cid, notes_files):
    """Return ordered list of (subproof_name, [filenames]) using physical folders
    if present, else the provisional prefix taxonomy."""
    cdir = CLAIMS / cid
    phys = [d for d in sorted(cdir.iterdir(), key=lambda p: p.name) if d.is_dir() and (d / "notes").exists()]
    if phys:
        groups = []
        for d in phys:
            fs = sorted(f.name for f in (d / "notes").glob("*.tex.txt"))
            groups.append((d.name, [(d / "notes" / f) for f in fs]))
        return groups, True
    rules = TAXONOMY.get(cid)
    if not rules:
        return ([("(all notes)", [cdir / "notes" / f for f in sorted(notes_files)])] if notes_files else []), False
    groups = {name: [] for name, _ in rules}
    for f in sorted(notes_files):
        s = lineage_slug(f)
        for name, prefixes in rules:
            if s.startswith(prefixes):
                groups[name].append(cdir / "notes" / f)
                break
    return [(name, groups[name]) for name, _ in rules if groups[name]], False

def current_versions(paths):
    by = {}
    for p in paths:
        by.setdefault(lineage_slug(p.name), []).append(p)
    out = []
    for slug, ps in by.items():
        cur = sorted(ps, key=lambda p: vnum(p.name))[-1]
        out.append((slug, cur, len(ps)))
    out.sort(key=lambda t: t[0])
    return out

def read_card(cid):
    f = CLAIMS / cid / "status.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None

def per_claim_index(cid):
    cdir = CLAIMS / cid
    card = read_card(cid) or {}
    claim_tier = card.get("tier", "")
    notes_dir = cdir / "notes"
    flat = [f.name for f in notes_dir.glob("*.tex.txt")] if notes_dir.exists() else []
    groups, physical = sub_groups(cid, flat)
    L = [f"# {cid} — proof-unit index", ""]
    L.append(f"**Claim**: {card.get('title','(see status.json)')}  ")
    L.append(f"**Tier**: {claim_tier or '—'} ({card.get('lifecycle','')})  ·  "
             f"**Hypotheses**: {', '.join(card.get('hypotheses',[])) or '—'}  ·  "
             f"**Open gates**: {', '.join(card.get('open_gates',[])) or '—'}")
    L.append("")
    L.append("> GENERATED by `build_index.py` — do not hand-edit. "
             "Each row is one proof unit (current note version). "
             "`Tier*` = inherits the claim tier (note declares no tier change). "
             + ("Sub-proofs are physical folders." if physical
                else "Sub-proofs are the **proposed** grouping (no files moved yet)."))
    L.append("")
    if card.get("statement"):
        L.append(f"**Selection statement.** {shorten(card['statement'], 320)}")
        L.append("")
    if card.get("falsifier"):
        L.append(f"**Falsifier.** {shorten(card['falsifier'], 280)}")
        L.append("")
    if not groups:
        L.append("_No notes yet (scaffold claim)._")
        L.append("")
    for name, paths in groups:
        cvs = current_versions(paths)
        tiers = []
        rows = []
        for slug, cur, nver in cvs:
            d = parse_note(cur)
            if not d:
                continue
            t = tier_token(d["footer"], claim_tier)
            tiers.append(t.rstrip("*"))
            pipe = lambda s: s.replace("|", "\\|")
            proves = pipe(shorten(d["footer"].get("Precise statement", "") or d["title"], 150))
            ev = pipe(shorten(d["footer"].get("Evidence grade", ""), 46))
            nxt = pipe(shorten(d["footer"].get("Next required action", ""), 90))
            vv = vnum(cur.name)
            rows.append(f"| `{slug}` | v{vv[0]}.{vv[1]} | {t} | {proves} | {ev} | {nxt} |")
        span = "/".join(sorted(set(t for t in tiers if t and t != "—"))) or "—"
        unit = "unit" if len(cvs) == 1 else "units"
        L.append(f"## {name}/  ·  {len(cvs)} proof {unit}  ·  tier span {span}")
        L.append("")
        L.append("| Proof unit | Cur | Tier | What it proves (footer: precise statement) | Evidence | Next action |")
        L.append("|---|---|---|---|---|---|")
        L.extend(rows)
        L.append("")
    L.append(f"<!-- generated {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')} by build_index.py v{__version__} -->")
    return "\n".join(L) + "\n"

def master_index():
    L = ["# TECT claims — reviewer index", ""]
    L.append("Top-down map of the proof of record. Start here, drill into a claim's "
             "`INDEX.md` for its sub-proofs, then into a note for the full argument.")
    L.append("")
    L.append("**How to read.** Tier vocabulary: `governance/tier-system.md` "
             "(T5 = closed within pinned scope; T6 = theorem modulo named hypotheses; "
             "T7 = discharged theorem). Reviewer guide: `REVIEWING.md`. "
             "Generated ledger: `CLAIMS.md`. Standalone results: `RESULTS-LEDGER.md`.")
    L.append("")
    L.append("> GENERATED by `build_index.py` — do not hand-edit.")
    L.append("")
    claim_dirs = sorted([d.name for d in CLAIMS.iterdir()
                         if d.is_dir() and not d.name.startswith("_")])
    for letter, sname in SECTORS.items():
        sec_claims = [c for c in claim_dirs if c.startswith(letter)]
        if not sec_claims:
            continue
        L.append(f"## Sector {letter} — {sname}")
        L.append("")
        L.append("| Claim | Tier | Hypotheses | Open gates | Sub-proofs (proof-unit count) | Detail |")
        L.append("|---|---|---|---|---|---|")
        for cid in sec_claims:
            card = read_card(cid)
            notes_dir = CLAIMS / cid / "notes"
            flat = [f.name for f in notes_dir.glob("*.tex.txt")] if notes_dir.exists() else []
            groups, physical = sub_groups(cid, flat)
            if groups:
                sub_str = ", ".join(f"{n} ({len(current_versions(ps))})" for n, ps in groups)
                detail = f"[INDEX]({cid}/INDEX.md)"
            else:
                sub_str = "_scaffold (no notes yet)_"
                detail = "—"
            if card:
                tier = card.get("tier", "—")
                hyp = ", ".join(card.get("hypotheses", [])) or "—"
                gates = ", ".join(card.get("open_gates", [])) or "—"
            else:
                tier = hyp = gates = "—"
            L.append(f"| `{cid}` | {tier} | {hyp} | {gates} | {sub_str} | {detail} |")
        L.append("")
    L.append(f"<!-- generated {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')} by build_index.py v{__version__} -->")
    return "\n".join(L) + "\n"

def atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, str(path))

def main():
    check = "--check" in sys.argv
    targets = {CLAIMS / "INDEX.md": master_index()}
    for d in sorted(CLAIMS.iterdir(), key=lambda p: p.name):
        if d.is_dir() and not d.name.startswith("_"):
            has_flat = (d / "notes").exists() and any((d / "notes").glob("*.tex.txt"))
            has_sub = any(d.glob("*/notes/*.tex.txt"))
            if has_flat or has_sub:
                targets[d / "INDEX.md"] = per_claim_index(d.name)
    stale = []
    for path, content in targets.items():
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        norm = lambda s: re.sub(r"<!-- generated.*?-->", "", s)
        if norm(old) != norm(content):
            stale.append(str(path.relative_to(REPO)))
            if not check:
                atomic_write(path, content)
    if check:
        if stale:
            print("INDEX STALE:", *stale, sep="\n  ")
            sys.exit(1)
        print("INDEX: up to date")
        sys.exit(0)
    print(f"INDEX: wrote {len(targets)} files ({len(stale)} changed)")
    for t in sorted(targets):
        print("  ", t.relative_to(REPO))

if __name__ == "__main__":
    main()
