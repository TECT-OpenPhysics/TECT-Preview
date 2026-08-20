#!/usr/bin/env python3
"""Integrate and lifecycle-audit the R-169 v1.1 P1/BCC route split.

Purpose: run exact primary and stdlib-independent derivations, compare their
payloads, enforce source discipline, and audit staged or formal authority state.
Convention: only the explicit P1 BCC field is closed; the Reading-H-to-P1
interface, Round-1, and C6 remain open.
Formula: both lanes must agree on centers=periods=128, ||Psi_A||^2=49152|A|^2,
and the two separately inherited energy and radial R-157 margins.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-pinned-p1-bcc-periodic-realization-empty-reference-elimination-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
PRIMARY = REPO / "codes/foundations/pre_a_t055_pinned_p1_bcc_periodic_realization_empty_reference_elimination_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_t055_pinned_p1_bcc_periodic_realization_empty_reference_elimination_route_split_independent.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

CLOSED = "PA-T055-PINNED-P1-BCC-PERIODIC-REALIZATION-EMPTY-REFERENCE-EXCLUSION"
INTERFACE_OPEN = "PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE"
PARENT_OPEN = ["C6-BCC-PREMISE-BLOCKED", "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"]
REUSED_NEGATIVES = [
    "NG-2026-08-03-M1-PINNED-FUNCTIONAL-NONZERO-EQUILIBRIUM",
    "NG-2026-08-14-PRE-A-T055-COMMON-COUNTERTERM-BASIS-UNFIXED-FINITE-PARTS-AUTOMATIC-EMPTY-REFERENCE-SIGN",
]
PACKAGE_PATHS = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def parse_json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_child(path: Path, staged: bool, output: Path) -> dict[str, Any]:
    command = [sys.executable, "-B", "-X", "utf8", str(path)]
    if staged:
        command.append("--staged")
    command.extend(("--output", str(output)))
    completed = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed {path.name}\nstdout={completed.stdout}\nstderr={completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^### \*\*{re.escape(heading)}\*\*\s*$([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one section {heading}, found {len(matches)}")
    return matches[0]


def negative_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^### {re.escape(heading)}\b([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one negative {heading}, found {len(matches)}")
    return matches[0]


def historical_result_section(markdown: str) -> str:
    pattern = re.compile(r"^### R-169\b([\s\S]*?)(?=^### R-|\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one R-169 result section, found {len(matches)}")
    return matches[0]


def live_counts() -> dict[str, int]:
    summary = json.loads((REPO / "verification/catalog-summary.json").read_text(encoding="utf-8"))
    return {
        "claims": int(summary["claim_count"]),
        "results": int(json.loads((REPO / "results/index.json").read_text(encoding="utf-8"))["count"]),
        "gates": int(json.loads((REPO / "claims/gates-index.json").read_text(encoding="utf-8"))["count"]),
        "negatives": int(json.loads((REPO / "negative-results/index.json").read_text(encoding="utf-8"))["count"]),
        "explorations": len(parse_json_lines(REPO / "explorations/log.jsonl")),
        "events": len(parse_json_lines(REPO / "changelog/log.jsonl")),
        "tasks": len(json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]),
        "catalog": int(summary["total"]),
    }


def source_discipline(audit: Audit) -> None:
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    independent = trees[INDEPENDENT]
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(independent)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(independent)
        if isinstance(node, ast.ImportFrom)
    }
    calls = {
        node.func.id
        for node in ast.walk(independent)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_calls = {"float", "complex", "eval", "exec", "compile"}
    audit.check("three ASTs parse", len(trees) == 3, len(trees), 3, "code")
    audit.check("independent exact stdlib", not ({"sympy", "numpy", "scipy"} & imports) and not (forbidden_calls & calls), {"imports": sorted(imports), "forbidden": sorted(forbidden_calls & calls)}, "stdlib/Fraction and no dynamic or float calls", "code")
    for path in PACKAGE_PATHS:
        data = path.read_bytes()
        audit.check(f"format {path.name}", data.endswith(b"\n") and b"\r" not in data and all(byte < 128 for byte in data), "ASCII LF final-LF", "ASCII LF final-LF", "code")


def staged_audit(audit: Audit) -> None:
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    explorations = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")
    events = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["formal_integration"]["expected_post_counts"]
    events_json = parse_json_lines(REPO / "changelog/log.jsonl")
    matches = [(ordinal, event) for ordinal, event in enumerate(events_json, start=1) if event.get("id") == json.loads(MANIFEST.read_text(encoding="utf-8"))["formal_integration"]["event_id"]]
    if matches:
        current = live_counts()
        audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        audit.check("append-only current counts", all(current[key] >= int(expected[key]) for key in expected), current, expected, "lifecycle")
    else:
        audit.check("preformal authority absence", all(token not in gates + results + explorations + events for token in ("EXP-000852", "R-169 v1.1", CLOSED, INTERFACE_OPEN)), "new formal tokens absent", "new formal tokens absent", "lifecycle")
        current = live_counts()
        deltas = {"claims": 0, "results": 0, "gates": 2, "negatives": 0, "explorations": 1, "events": 1, "tasks": 0, "catalog": 8}
        projected = {key: current[key] + deltas[key] for key in current}
        audit.check("preformal count projection", projected == expected, projected, expected, "lifecycle")


def formal_audit(audit: Audit, manifest: dict[str, Any], fresh_primary: dict[str, Any], fresh_independent: dict[str, Any]) -> None:
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    roadmap = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")

    closed = section(gates, CLOSED)
    interface = section(gates, INTERFACE_OPEN)
    parents = [section(gates, gate) for gate in PARENT_OPEN]
    audit.check("one scoped closed child", "EXP-000852" in closed and "R-169 v1.1" in closed and "CLOSED" in closed, "unique CLOSED child", "unique CLOSED child", "formal")
    audit.check("one explicit open interface", "EXP-000852" in interface and "R-169 v1.1" in interface and "OPEN" in interface and "CLOSED" not in interface, "unique OPEN interface", "unique OPEN interface", "formal")
    audit.check("C6 and Round-1 remain open", all("EXP-000852" in value and "remain OPEN" in value for value in parents), "two OPEN annotations", "two OPEN annotations", "formal")
    audit.check("no new negative and reused links", manifest["new_negative_ids"] == [] and all(negative_section(negatives, value) for value in REUSED_NEGATIVES), "zero new, two reused", "zero new, two reused", "formal")
    r169_section = historical_result_section(results)
    audit.check("R-169 historical authority", all(token in r169_section for token in ("R-169 v1.1", "EXP-000852", "R-169 v1.4")), "v1.1 history and current successor", "v1.1 history and current successor", "formal")
    audit.check("roadmap and strategy linkage", all(token in roadmap and token in strategy_index for token in ("EXP-000852", "R-169 v1.1")), "both surfaces linked", "both surfaces linked", "formal")

    records = [record for record in parse_json_lines(REPO / "explorations/log.jsonl") if record.get("id") == "EXP-000852"]
    audit.check("unique EXP-000852", len(records) == 1, len(records), 1, "formal")
    record = records[0]
    audit.check("EXP topology", record.get("task_id") == "T-055" and record.get("verdict") == "advanced" and record.get("related") == [{"id": "EXP-000851", "relation": "continues"}] and record.get("formal_refs", {}).get("results") == ["R-157", "R-158", "R-169"] and record.get("formal_refs", {}).get("negatives") == REUSED_NEGATIVES, {key: record.get(key) for key in ("task_id", "verdict", "related", "formal_refs")}, "exact EXP topology", "formal")
    audit.check("EXP gate order", record.get("gate_ids") == [CLOSED, INTERFACE_OPEN, *PARENT_OPEN], record.get("gate_ids"), [CLOSED, INTERFACE_OPEN, *PARENT_OPEN], "formal")

    events = parse_json_lines(REPO / "changelog/log.jsonl")
    contract = manifest["formal_integration"]
    matches = [(ordinal, candidate) for ordinal, candidate in enumerate(events, start=1) if candidate.get("id") == contract["event_id"]]
    unique_event = len(matches) == 1
    ordinal, event = matches[0] if unique_event else (None, {})
    exact_header = f"[{contract['event_title']}] - 2026-08-14"
    audit.check("event 640 historical identity", unique_event and ordinal == contract["event_ordinal"] and event.get("id") == contract["event_id"] and event.get("header") == exact_header, {"total_events": len(events), "ordinal": ordinal, "id": event.get("id"), "header": event.get("header")}, {"ordinal": contract["event_ordinal"], "id": contract["event_id"], "header": exact_header}, "formal")
    audit.check("event exact linkage", event.get("claim_ids") == contract["event_claim_ids"] and event.get("keywords") == contract["event_keywords"] and event.get("notes") == contract["event_notes"] and event.get("scripts") == contract["event_scripts"], {key: event.get(key) for key in ("claim_ids", "keywords", "notes", "scripts")}, "exact claims/keywords/notes/scripts", "formal")
    audit.check("event no-new-negative scope", event.get("neg_results") == [] and all(token in event.get("raw", "") for token in contract["event_raw_tokens"]) and ".pdf" not in event.get("raw", ""), {"neg": event.get("neg_results"), "raw_tokens": [token for token in contract["event_raw_tokens"] if token in event.get("raw", "")]}, "no negatives, all raw tokens, no .pdf", "formal")

    theorem_map = json.loads((REPO / "governance/sector-a-theorem-map.json").read_text(encoding="utf-8"))
    priority = theorem_map["research_priority"]
    actual_version = tuple(int(part) for part in theorem_map.get("version", "0.0.0").split("."))
    required_version = tuple(int(part) for part in contract["theorem_map_version"].split("."))
    audit.check("theorem map historical arrays", actual_version >= required_version and priority.get("latest_cp1_checkpoint") and priority.get("closed_r169_v1_1_scoped_gates") == [CLOSED] and priority.get("open_r169_v1_1_interface_gates") == [INTERFACE_OPEN] and priority.get("r169_v1_1_reused_negatives") == REUSED_NEGATIVES, {"version": theorem_map.get("version"), "latest": priority.get("latest_cp1_checkpoint", "")[:20]}, "version at least v1.36 with exact arrays", "formal")

    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    matches = [task for task in tasks if task.get("id") == "T-055"]
    audit.check("stable T-055 routing", len(matches) == 1 and matches[0].get("owner") and matches[0].get("note") and matches[0].get("gate") == "C6-BCC-PREMISE-BLOCKED", matches, "one owner/note/gate-stable T-055", "formal")
    current_counts = live_counts()
    expected_counts = dict(contract["expected_post_counts"])
    audit.check("append-only post counts", all(current_counts[key] >= int(expected_counts[key]) for key in expected_counts), current_counts, expected_counts, "formal")

    stored_primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8"))
    audit.check("stored child freshness", stored_primary == fresh_primary and stored_independent == fresh_independent, "stored children exact fresh", "stored children exact fresh", "formal")


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="r169-v11-") as directory:
        root = Path(directory)
        fresh_primary = run_child(PRIMARY, staged, root / "primary.json")
        fresh_independent = run_child(INDEPENDENT, staged, root / "independent.json")

    audit.check("child modes and verdicts", fresh_primary["verdict"] == fresh_independent["verdict"] == "PASS" and fresh_primary["mode"] == fresh_independent["mode"] == ("staged" if staged else "formal"), {"primary": fresh_primary["mode"], "independent": fresh_independent["mode"]}, "matching PASS modes", "cross")
    audit.check("independent exact agreement", fresh_primary["derived"] == fresh_independent["derived"], fresh_primary["derived"], fresh_independent["derived"], "cross")
    transfer = manifest["perturbation_transfer"]
    audit.check("integrated perturbation semantic firewall", "above the reference" in transfer["value_conclusion"] and all(token not in transfer["value_conclusion"] for token in ("critical", "local", "metastable")) and "critical" in transfer["radial_conclusion"] and "local-minimum" in transfer["radial_conclusion"] and fresh_primary["derived"]["value_only_local_minimum_energy"] == manifest["test_oracles"]["value_only_local_minimum_energy"], {"value": transfer["value_conclusion"], "radial": transfer["radial_conclusion"], "fixture": fresh_primary["derived"]["value_only_local_minimum_energy"]}, "value sign and radial critical conclusions separated by exact counterfixture", "cross")
    audit.check("owner and shared hashes", fresh_primary["source_hash"] == normalized_sha256(PRIMARY) and fresh_independent["source_hash"] == normalized_sha256(INDEPENDENT) and fresh_primary["manifest_hash"] == fresh_independent["manifest_hash"] == normalized_sha256(MANIFEST) and fresh_primary["certificate_hash"] == fresh_independent["certificate_hash"] == normalized_sha256(CERTIFICATE), "all hashes current", "all hashes current", "cross")
    source_discipline(audit)
    if staged:
        staged_audit(audit)
    else:
        formal_audit(audit, manifest, fresh_primary, fresh_independent)

    return {
        "schema": "tect/pre-a-t055-pinned-p1-bcc-periodic-realization-integrated/1.0",
        "version": __version__,
        "mode": "staged" if staged else "formal",
        "assertions": len(audit.rows),
        "checks": audit.rows,
        "derived": fresh_primary["derived"],
        "child_assertions": {"primary": fresh_primary["assertions"], "independent": fresh_independent["assertions"]},
        "source_hash": normalized_sha256(SCRIPT),
        "source_hashes": {path.name: normalized_sha256(path) for path in PACKAGE_PATHS},
        "verdict": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"INTEGRATED PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
