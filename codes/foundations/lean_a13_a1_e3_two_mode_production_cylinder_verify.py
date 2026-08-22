"""Integrated verifier for the R-189 finite production-cylinder package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO / "verification" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from proof_evidence_map_io import load_map

MANIFEST = REPO / "strategy" / "pre-a13-a1-e3-two-mode-production-cylinder-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a13_a1_e3_two_mode_production_cylinder.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a13_a1_e3_two_mode_production_cylinder_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r189-a1-e3-two-mode-production-cylinder" / "integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run_lane(script: Path, output: Path) -> dict[str, Any]:
    command = [sys.executable, "-B", str(script), "--output", str(output)]
    completed = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"lane failed: {script}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A13-A1-E3-TWO-MODE-PRODUCTION-CYLINDER", manifest["audit_id"], "A13-A1-E3-TWO-MODE-PRODUCTION-CYLINDER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    check("hostile mutation contract", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        if item["sha256"]:
            check(f"file {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    source = (REPO / manifest["files"]["lean_entrypoint"]["path"]).read_text(encoding="utf-8")
    check("Lean markers", all(marker in source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape absence", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    expected = manifest["formal_integration"]["expected_counts"]
    exploration_rows = [json.loads(line) for line in (REPO / "explorations" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exp_matches = [(ordinal, row) for ordinal, row in enumerate(exploration_rows, start=1) if row.get("id") == manifest["exploration_id"]]
    exploration_ordinal = manifest["formal_integration"].get("exploration_ordinal", expected["explorations"])
    check("exploration unique", len(exp_matches) == 1 and exp_matches[0][0] == exploration_ordinal, [(i, r.get("id")) for i, r in exp_matches], exploration_ordinal)
    event_rows = [json.loads(line) for line in (REPO / "changelog" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    event_matches = [(ordinal, row) for ordinal, row in enumerate(event_rows, start=1) if row.get("id") == manifest["formal_integration"]["event_id"]]
    check("event unique and ordinal", len(event_matches) == 1 and event_matches[0][0] == manifest["formal_integration"]["event_ordinal"], [(i, r.get("id")) for i, r in event_matches], manifest["formal_integration"]["event_ordinal"])
    if event_matches:
        event = event_matches[0][1]
        check("event header", event.get("header") == "[R-189 A1 e3 two-mode production-cylinder positivity Lean cross-check] - 2026-08-22", event.get("header"), "R-189 header")
        check("event claims", event.get("claim_ids") == manifest["formal_integration"]["event_claim_ids"], event.get("claim_ids"), manifest["formal_integration"]["event_claim_ids"])
        check("event keywords", event.get("keywords") == manifest["formal_integration"]["event_keywords"], event.get("keywords"), manifest["formal_integration"]["event_keywords"])
        check("event notes", event.get("notes") == manifest["formal_integration"]["event_notes"], event.get("notes"), manifest["formal_integration"]["event_notes"])
        check("event scripts", event.get("scripts") == manifest["formal_integration"]["event_scripts"], event.get("scripts"), manifest["formal_integration"]["event_scripts"])
        check("event raw tokens", all(token in event.get("raw", "") for token in manifest["formal_integration"]["event_raw_tokens"]), manifest["formal_integration"]["event_raw_tokens"], "all present")
        check("event no negatives", event.get("neg_results") == [], event.get("neg_results"), [])
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    check("result section", "### R-189 -- A1 e3 two-mode production-cylinder positivity Lean cross-check" in results_text, "R-189" in results_text, True)
    check("result boundary", all(token in results_text for token in ("A13's two gates remain", "No new negative", "No R-189 PDF")), True, "scope tokens")
    summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
    check("catalog count", summary.get("total") == expected["catalog"], summary.get("total"), expected["catalog"])
    check("claim count", summary.get("claim_count") == expected["claims"], summary.get("claim_count"), expected["claims"])
    proof_map = load_map(REPO)
    result_count = len(proof_map.get("reusable_results", []))
    check("result count", result_count == expected["results"], result_count, expected["results"])
    with tempfile.TemporaryDirectory(prefix="r189-verify-") as directory:
        temp = Path(directory)
        primary = run_lane(PRIMARY, temp / "primary.json")
        independent = run_lane(INDEPENDENT, temp / "independent.json")
    check("primary PASS", primary["verdict"] == "PASS", primary["verdict"], "PASS")
    check("independent PASS", independent["verdict"] == "PASS", independent["verdict"], "PASS")
    check("derived agreement", primary["derived"] == independent["derived"], [primary["derived"], independent["derived"]], "equal")
    d = primary["derived"]
    check("q bounds", d["q1_lower_gt_target"] and d["q2_lower_gt_target"], [d["q1_lower"], d["q2_lower"]], ">1/10")
    check("positive slice only", d["slice_nonzero_positive"] and not d["a13_gate_closed"], d, "A13 open")
    check("R-189 boundary", all(token in manifest["boundary"] for token in ("e3", "A13", "continuum")), manifest["boundary"], "scope tokens")
    mutation_results = {
        "claim_bearing": manifest["claim_bearing"] is False,
        "shell_disabled": d["eta_shell"] == "0",
        "f_ref_boundary": d["F_ref_not_F_decl"],
        "q_target": d["lower_q"] == "1/10",
        "classii_scope": d["classii_e3_zero"],
        "mixed_terms": "mixed t,u" in manifest["purpose"] or "mixed t,u" in manifest["boundary"],
        "a13_open": not d["a13_gate_closed"],
        "lean_no_escape": not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")),
    }
    check("hostile mutation firewalls", all(mutation_results.values()), mutation_results, "all true")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "primary": primary, "independent": independent, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED R-189 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
