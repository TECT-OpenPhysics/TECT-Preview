#!/usr/bin/env python3
"""lint_claims.py — TECT claim-ledger validator and ledger/view generator.

Usage:
    python verification/scripts/lint_claims.py            # validate, exit 0/1
    python verification/scripts/lint_claims.py --render   # + write CLAIMS.md and archive/legacy/BY-CLAIM.md
    python verification/scripts/lint_claims.py --render --check
                                                          # + verify both generated files are in sync

Enforces governance/claim-standard.md §3-§4:
  schema completeness, enum validity, id/folder match, dependency existence,
  DAG acyclicity, tier-monotonicity/hypothesis rule, T7 prohibition checks,
  REFUTED cross-reference, ESTIMATOR error-bound statement, no-overclaim
  presence at T4+, gate/hypothesis registry membership (claims/GATES.md).

Generated files (never hand-edit):
  CLAIMS.md                  — master ledger by sector
  archive/legacy/BY-CLAIM.md — per-claim view of migrated archive evidence
Stdlib-only by design (CI-friendly).

Changelog:
  1.0.0 (2026-06-05) first issue: schema/DAG/monotonicity linter + CLAIMS.md render.
  1.1.0 (2026-06-05) added BY-CLAIM.md generated view + dual sync-check.
  1.2.0 (2026-06-05) version header added (code-versioning rule, naming §5).
"""
__version__ = "1.2.0"
__first_issued__ = "2026-06-05"
__version_issued__ = "2026-06-05"

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLAIMS_DIR = REPO / "claims"
GATES_FILE = CLAIMS_DIR / "GATES.md"
LEDGER = REPO / "CLAIMS.md"
BYCLAIM = REPO / "archive" / "legacy" / "BY-CLAIM.md"

TIERS = ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7"]
LIFECYCLES = {"ACTIVE", "SUPERSEDED", "REFUTED"}
GRADES = {"ANALYTIC", "EXACT", "EXECUTED", "ESTIMATOR", "INHERITED",
          "CONDITIONAL", "MATCHED", "INSERTED", "PREDICTED"}
SECTORS = set("ABCDEF")
REQUIRED = ["id", "title", "sector", "statement", "scope", "tier", "tier_scale",
            "lifecycle", "evidence_grade", "dependencies", "hypotheses",
            "open_gates", "falsifier", "reproduction", "legacy_pillar",
            "tier_legacy", "legacy_evidence", "t7_candidate", "no_overclaim",
            "next_action", "last_review"]


def tier_idx(t):
    return TIERS.index(t)


def load_registry():
    """Bold ALL-CAPS tokens in GATES.md are registered gate/hypothesis IDs."""
    if not GATES_FILE.exists():
        return set()
    text = GATES_FILE.read_text(encoding="utf-8")
    return set(re.findall(r"\*\*([A-Z][A-Z0-9-]+)\*\*", text))


def load_cards(errors):
    cards = {}
    for d in sorted(CLAIMS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        sj, cm = d / "status.json", d / "claim.md"
        if not sj.exists():
            errors.append(f"{d.name}: missing status.json")
            continue
        try:
            card = json.loads(sj.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{d.name}: status.json parse error: {e}")
            continue
        if not cm.exists() or not cm.read_text(encoding="utf-8").strip():
            errors.append(f"{d.name}: claim.md missing or empty")
        if card.get("id") != d.name:
            errors.append(f"{d.name}: id field '{card.get('id')}' != folder name")
        cards[d.name] = card
    return cards


def check_card(c, cards, registry, errors):
    cid = c.get("id", "?")
    for f in REQUIRED:
        if f not in c:
            errors.append(f"{cid}: missing required field '{f}'")
            return
    if c["tier"] not in TIERS:
        errors.append(f"{cid}: invalid tier '{c['tier']}'")
        return
    if c["tier_scale"] != "TSv2":
        errors.append(f"{cid}: tier_scale must be 'TSv2'")
    if c["lifecycle"] not in LIFECYCLES:
        errors.append(f"{cid}: invalid lifecycle '{c['lifecycle']}'")
    if c["sector"] not in SECTORS:
        errors.append(f"{cid}: invalid sector '{c['sector']}'")
    if not c["evidence_grade"] or not set(c["evidence_grade"]) <= GRADES:
        errors.append(f"{cid}: evidence_grade invalid: {c['evidence_grade']}")
    rep = c["reproduction"]
    if not isinstance(rep, dict) or rep.get("status") not in {"PACKAGE-PENDING", "AVAILABLE"}:
        errors.append(f"{cid}: reproduction.status must be PACKAGE-PENDING|AVAILABLE")

    for dep in c["dependencies"] + c.get("soft_dependencies", []):
        if dep not in cards:
            errors.append(f"{cid}: dependency '{dep}' does not exist")
    for g in c["open_gates"]:
        if g not in registry:
            errors.append(f"{cid}: open gate '{g}' not registered in GATES.md")
    for h in c["hypotheses"]:
        if h not in registry:
            errors.append(f"{cid}: hypothesis '{h}' not registered in GATES.md")

    # Tier monotonicity / hypothesis rule (claim-standard §4.4)
    if tier_idx(c["tier"]) >= tier_idx("T6"):
        weak = [d for d in c["dependencies"]
                if d in cards and tier_idx(cards[d]["tier"]) < tier_idx("T6")]
        if weak and not c["hypotheses"]:
            errors.append(f"{cid}: T6+ with sub-T6 hard deps {weak} but no named hypotheses")

    # T7 prohibition (claim-standard §4.5)
    if c["tier"] == "T7":
        if rep.get("status") != "AVAILABLE":
            errors.append(f"{cid}: T7 requires reproduction package AVAILABLE")
        if c["t7_candidate"]:
            errors.append(f"{cid}: T7 with t7_candidate flag set")
        if any(str(p).startswith("legacy:") for p in c["legacy_evidence"]):
            errors.append(f"{cid}: T7 with unresolved legacy: evidence pointers")

    if c["lifecycle"] == "REFUTED" and not c.get("negative_result_ref"):
        errors.append(f"{cid}: REFUTED requires negative_result_ref")

    if "ESTIMATOR" in c["evidence_grade"]:
        blob = (c["scope"] + " " + c.get("notes", "")).lower()
        if "bound" not in blob:
            errors.append(f"{cid}: ESTIMATOR grade requires error-bound statement in scope/notes")

    if tier_idx(c["tier"]) >= tier_idx("T4") and not c["no_overclaim"].strip():
        errors.append(f"{cid}: no_overclaim required at T4+")


def check_dag(cards, errors):
    state = {}

    def visit(n, stack):
        if state.get(n) == 1:
            return
        if state.get(n) == 0:
            errors.append(f"dependency cycle: {' -> '.join(stack + [n])}")
            return
        state[n] = 0
        for d in cards[n]["dependencies"]:
            if d in cards:
                visit(d, stack + [n])
        state[n] = 1

    for n in cards:
        visit(n, [])


def render(cards):
    today = _dt.date.today().isoformat()
    counts = {t: 0 for t in TIERS}
    for c in cards.values():
        counts[c["tier"]] += 1
    t7c = sum(1 for c in cards.values() if c["t7_candidate"])
    refuted = sum(1 for c in cards.values() if c["lifecycle"] == "REFUTED")
    tier_line = " · ".join(f"{t}: {counts[t]}" for t in TIERS if counts[t])

    L = []
    L.append("# CLAIMS — Master Ledger")
    L.append("")
    L.append("<!-- AUTO-GENERATED by verification/scripts/lint_claims.py --render -->")
    L.append("<!-- DO NOT HAND-EDIT. Source of truth: claims/*/status.json -->")
    L.append("")
    L.append(f"Generated: {today}")
    L.append("")
    L.append(f"**{len(cards)} claims** · {tier_line} · T7-candidates: {t7c} · refuted: {refuted}")
    L.append("")
    L.append("Tier scale TSv2 (`governance/tier-system.md`). A claim is exactly as strong")
    L.append("as its registered tier, scope, and hypotheses — never stronger. Falsifiers,")
    L.append("reproduction commands, and history live on the claim cards.")
    L.append("")
    sector_names = {"A": "Microscopic Foundation", "B": "Vacuum / Reading Selection",
                    "C": "Spacetime / Lorentz / Gravity", "D": "Gauge / Matter / Topology",
                    "E": "Spectrum / Couplings / Constants", "F": "Cosmology / Falsifiability"}
    for s in "ABCDEF":
        group = [c for c in cards.values() if c["sector"] == s]
        if not group:
            continue
        L.append(f"## Sector {s} — {sector_names[s]}")
        L.append("")
        L.append("| Claim | Title | Tier | Lifecycle | Evidence | Hypotheses | Open gates |")
        L.append("|---|---|---|---|---|---|---|")
        for c in sorted(group, key=lambda x: x["id"]):
            tier = c["tier"] + (" (T7-cand.)" if c["t7_candidate"] else "")
            hyp = ", ".join(c["hypotheses"]) or "—"
            gates = ", ".join(c["open_gates"]) or "—"
            ev = ", ".join(c["evidence_grade"])
            L.append(f"| [{c['id']}](claims/{c['id']}/claim.md) | {c['title']} "
                     f"| {tier} | {c['lifecycle']} | {ev} | {hyp} | {gates} |")
        L.append("")
    L.append("## Reading rules")
    L.append("")
    L.append("- **T5** results are closed *only within their pinned scope* (scope string on the card).")
    L.append("- **T6** results are theorems *modulo the listed hypotheses* (registry: `claims/GATES.md`).")
    L.append("- **T7-cand.** marks legacy-proved results awaiting a TSv2 verification package — entered at T6 by the no-auto-T7 rule.")
    L.append("- Gate status and priorities: `claims/GATES.md` · roadmap: `ROADMAP.md`.")
    L.append("")
    return "\n".join(L) + "\n"


def render_by_claim(cards):
    today = _dt.date.today().isoformat()
    L = []
    L.append("# archive/legacy — evidence by claim (generated view)")
    L.append("")
    L.append("<!-- AUTO-GENERATED by verification/scripts/lint_claims.py --render -->")
    L.append("<!-- DO NOT HAND-EDIT. Source of truth: claims/*/status.json -->")
    L.append("")
    L.append(f"Generated: {today}")
    L.append("")
    L.append("Physical layout is per-tag (`notes/<Tag>/`, `scripts/`, `artefacts/<Tag>/`;")
    L.append("see `INDEX.md`) because one legacy file may serve several claims. This view")
    L.append("answers the reverse lookup: for each claim, every migrated archive file it")
    L.append("cites, plus its reproduction command. Unresolved `legacy:` pointers are")
    L.append("listed so migration debt is visible per claim.")
    L.append("")
    any_row = False
    for c in sorted(cards.values(), key=lambda x: x["id"]):
        arch = [p for p in c["legacy_evidence"] if str(p).startswith("archive/")]
        pend = [p for p in c["legacy_evidence"] if str(p).startswith("legacy:")]
        if not arch and not pend:
            continue
        any_row = True
        L.append(f"## {c['id']} — {c['title']}  ({c['tier']})")
        L.append("")
        if arch:
            for p in arch:
                L.append(f"- `{p}`")
        if pend:
            for p in pend:
                L.append(f"- UNRESOLVED `{p}`")
        cmd = c["reproduction"].get("command")
        if cmd:
            L.append("")
            L.append(f"Reproduction: `{cmd}`")
        L.append("")
    if not any_row:
        L.append("_(no archive-citing claims yet)_")
        L.append("")
    return "\n".join(L) + "\n"


def _sync(path, content, check, label):
    strip = lambda s: [l for l in s.splitlines() if not l.startswith("Generated:")]
    if check:
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if strip(old) != strip(content):
            print(f"RENDER-CHECK: FAIL — {label} out of sync; run --render and commit")
            return False
        print(f"RENDER-CHECK: PASS — {label} in sync")
        return True
    path.write_text(content, encoding="utf-8")
    print(f"RENDERED: {path}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true", help="write generated files")
    ap.add_argument("--check", action="store_true",
                    help="with --render: fail if generated files are out of sync (date line ignored)")
    args = ap.parse_args()

    errors = []
    registry = load_registry()
    if not registry:
        errors.append("GATES.md missing or contains no registered gate IDs")
    cards = load_cards(errors)
    for c in cards.values():
        check_card(c, cards, registry, errors)
    check_dag(cards, errors)

    if errors:
        print(f"LINT: FAIL ({len(errors)} error(s))")
        for e in errors:
            print(f"  ERR {e}")
        return 1

    print(f"LINT: PASS ({len(cards)} claims, {len(registry)} registered gates/hypotheses)")

    if args.render:
        ok = _sync(LEDGER, render(cards), args.check, "CLAIMS.md")
        ok = _sync(BYCLAIM, render_by_claim(cards), args.check, "BY-CLAIM.md") and ok
        if not ok:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
