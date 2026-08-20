#!/usr/bin/env python3
"""Integrate and lifecycle-audit the R-169 v1.2 covariance-to-P1 split.

Purpose: compare exact SymPy and stdlib/Fraction derivations, enforce source
discipline, and audit staged or formal repository topology.
Convention: covariance/composite, mean-field, torus-shell, and full-energy
owners remain distinct; only two scoped interface children are closed.
Formula: both lanes must derive 16^3 I, the strict shell-(3,4) bracket,
the 8-versus-12 support obstruction, and the 43/108 sign crossing.
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
SLUG = "pre-a-t055-reading-h-covariance-to-p1-interface-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
PRIMARY = REPO / "codes/foundations/pre_a_t055_reading_h_covariance_to_p1_interface_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_t055_reading_h_covariance_to_p1_interface_route_split_independent.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

CLOSED = [
    "PA-T055-READING-H-COVARIANCE-MEAN-FIELD-TYPE-SEPARATION-AND-EQUIVARIANT-NONEXTRACTION",
    "PA-T055-READING-H-PINNED-P1-NONLINEAR-CONVENTION-AND-TORUS-COMMENSURABILITY-CROSSWALK",
]
OPEN = [
    "PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE",
    "C6-BCC-PREMISE-BLOCKED",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
NEW_NEGATIVES = [
    "NG-2026-08-14-PRE-A-T055-ISOTROPIC-GAUSSIAN-COVARIANCE-AUTOMATIC-NONZERO-BCC-MEAN-FIELD-EXTRACTION",
    "NG-2026-08-14-PRE-A-T055-READING-H-BCC-110-ON-SHELL-AUTOMATIC-SIDE16-TORUS-EMBEDDING",
    "NG-2026-08-14-PRE-A-T055-READING-H-SCALAR-CONSTANTS-AUTOMATIC-PINNED-P1-ENERGY-INTERTWINER",
]
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


def gate_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^### \*\*{re.escape(heading)}\*\*\s*$([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one gate section {heading}, found {len(matches)}")
    return matches[0]


def negative_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^### {re.escape(heading)}\b([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one negative section {heading}, found {len(matches)}")
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


def target_event_matches(manifest: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    """Locate this historical package by immutable event id, not by tail position."""
    event_id = manifest["formal_integration"]["event_id"]
    return [
        (ordinal, event)
        for ordinal, event in enumerate(parse_json_lines(REPO / "changelog/log.jsonl"), start=1)
        if event.get("id") == event_id
    ]


def historical_result_section(markdown: str) -> str:
    pattern = re.compile(r"^### R-169\b([\s\S]*?)(?=^### R-|\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one R-169 result section, found {len(matches)}")
    return matches[0]


def source_discipline(audit: Audit) -> None:
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    independent_tree = trees[INDEPENDENT]
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(independent_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(independent_tree)
        if isinstance(node, ast.ImportFrom)
    }
    calls = {
        node.func.id
        for node in ast.walk(independent_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_imports = {"sympy", "numpy", "scipy"}
    forbidden_calls = {"float", "complex", "eval", "exec", "compile"}
    audit.check("three ASTs parse", len(trees) == 3, len(trees), 3, "code")
    audit.check("independent exact stdlib", not (forbidden_imports & imports) and not (forbidden_calls & calls), {"imports": sorted(imports), "forbidden_calls": sorted(forbidden_calls & calls)}, "stdlib/Fraction only; no float/complex/dynamic execution", "code")
    for path in PACKAGE_PATHS:
        data = path.read_bytes()
        audit.check(f"format {path.name}", data.endswith(b"\n") and b"\r" not in data and all(byte < 128 for byte in data), "ASCII LF final-LF", "ASCII LF final-LF", "code")


def staged_audit(audit: Audit, manifest: dict[str, Any]) -> None:
    authorities = "\n".join(
        (REPO / path).read_text(encoding="utf-8")
        for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "negative-results/registry.md", "explorations/log.jsonl", "changelog/log.jsonl")
    )
    matches = target_event_matches(manifest)
    expected = manifest["formal_integration"]["expected_post_counts"]
    if matches:
        current = live_counts()
        audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        audit.check("append-only current counts", all(current[key] >= int(expected[key]) for key in expected), current, expected, "lifecycle")
    else:
        new_tokens = ["EXP-000858", "R-169 v1.2", *CLOSED, *NEW_NEGATIVES]
        audit.check("preformal authority absence", all(token not in authorities for token in new_tokens), "new authority tokens absent", "new authority tokens absent", "lifecycle")
        current = live_counts()
        deltas = {"claims": 0, "results": 0, "gates": 2, "negatives": 3, "explorations": 1, "events": 1, "tasks": 0, "catalog": 8}
        projected = {key: current[key] + deltas[key] for key in current}
        audit.check("preformal count projection", projected == expected, projected, expected, "lifecycle")


def formal_audit(audit: Audit, manifest: dict[str, Any], fresh_primary: dict[str, Any], fresh_independent: dict[str, Any]) -> None:
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    roadmap = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")

    closed_sections = [gate_section(gates, identifier) for identifier in CLOSED]
    open_sections = [gate_section(gates, identifier) for identifier in OPEN]
    audit.check("two scoped closed children", all("EXP-000858" in value and "R-169 v1.2" in value and "CLOSED" in value for value in closed_sections), "two unique CLOSED sections", "two unique CLOSED sections", "formal")
    audit.check("interface and parents remain open", all("EXP-000858" in value and "R-169 v1.2" in value and "OPEN" in value for value in open_sections), "three unique OPEN annotations", "three unique OPEN annotations", "formal")
    audit.check("new and reused negative authorities", all(negative_section(negatives, value) for value in [*NEW_NEGATIVES, *REUSED_NEGATIVES]), "three new and two reused sections", "three new and two reused sections", "formal")
    r169_section = historical_result_section(results)
    audit.check("R-169 historical authority", all(token in r169_section for token in ("R-169 v1.2", "EXP-000858", "R-169 v1.4")), "v1.2 history and current successor", "v1.2 history and current successor", "formal")
    audit.check("roadmap and strategy linkage", all(token in roadmap and token in strategy_index for token in ("EXP-000858", "R-169 v1.2")), "both surfaces linked", "both surfaces linked", "formal")

    records = [record for record in parse_json_lines(REPO / "explorations/log.jsonl") if record.get("id") == "EXP-000858"]
    audit.check("unique EXP-000858", len(records) == 1, len(records), 1, "formal")
    record = records[0]
    expected_claims = manifest["claim_ids"]
    expected_gates = [*CLOSED, *OPEN]
    expected_negatives = [*NEW_NEGATIVES, *REUSED_NEGATIVES]
    topology_ok = (
        record.get("task_id") == "T-055"
        and record.get("verdict") == "advanced"
        and record.get("claim_ids") == expected_claims
        and record.get("gate_ids") == expected_gates
        and record.get("related") == [{"id": "EXP-000857", "relation": "continues"}]
        and record.get("formal_refs", {}).get("results") == ["R-157", "R-169"]
        and record.get("formal_refs", {}).get("negatives") == expected_negatives
    )
    audit.check("EXP exact topology", topology_ok, {key: record.get(key) for key in ("task_id", "verdict", "claim_ids", "gate_ids", "related", "formal_refs")}, "exact v1.2 exploration topology", "formal")

    events = parse_json_lines(REPO / "changelog/log.jsonl")
    matches = [(ordinal, candidate) for ordinal, candidate in enumerate(events, start=1) if candidate.get("id") == manifest["formal_integration"]["event_id"]]
    unique_event = len(matches) == 1
    ordinal, event = matches[0] if unique_event else (None, {})
    contract = manifest["formal_integration"]
    exact_header = f"[{contract['event_title']}] - 2026-08-14"
    audit.check("event 641 historical identity", unique_event and ordinal == contract["event_ordinal"] and event.get("header") == exact_header, {"total_events": len(events), "ordinal": ordinal, "id": event.get("id"), "header": event.get("header")}, {"ordinal": contract["event_ordinal"], "id": contract["event_id"], "header": exact_header}, "formal")
    audit.check("event exact linkage", event.get("claim_ids") == contract["event_claim_ids"] and event.get("keywords") == contract["event_keywords"] and event.get("notes") == contract["event_notes"] and event.get("scripts") == contract["event_scripts"] and event.get("neg_results") == NEW_NEGATIVES, {key: event.get(key) for key in ("claim_ids", "keywords", "notes", "scripts", "neg_results")}, "exact event linkage", "formal")
    raw = event.get("raw", "")
    audit.check("event scope firewall", all(token in raw for token in contract["event_raw_tokens"] + NEW_NEGATIVES) and ".pdf" not in raw, [token for token in contract["event_raw_tokens"] if token in raw], "all raw tokens/new negatives and no .pdf", "formal")

    theorem_map = json.loads((REPO / "governance/sector-a-theorem-map.json").read_text(encoding="utf-8"))
    priority = theorem_map["research_priority"]
    actual_map_version = tuple(int(part) for part in theorem_map.get("version", "0.0.0").split("."))
    required_map_version = tuple(int(part) for part in contract["theorem_map_version"].split("."))
    map_ok = (
        actual_map_version >= required_map_version
        and priority.get("latest_cp1_checkpoint")
        and priority.get("closed_r169_v1_2_scoped_gates") == CLOSED
        and priority.get("open_r169_v1_2_interface_gates") == [OPEN[0]]
        and priority.get("r169_v1_2_new_negatives") == NEW_NEGATIVES
    )
    audit.check("theorem map v1.37", map_ok, {"version": theorem_map.get("version"), "latest": priority.get("latest_cp1_checkpoint", "")[:32]}, "v1.37 exact arrays", "formal")

    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    matches = [task for task in tasks if task.get("id") == "T-055"]
    stable_task = len(matches) == 1 and matches[0].get("owner") and matches[0].get("note") and matches[0].get("gate") == "C6-BCC-PREMISE-BLOCKED"
    audit.check("stable T-055 routing", stable_task, matches, "one owner/note/gate-stable T-055", "formal")

    current_counts = live_counts()
    expected_counts = dict(contract["expected_post_counts"])
    audit.check("append-only post counts", all(current_counts[key] >= int(expected_counts[key]) for key in expected_counts), current_counts, expected_counts, "formal")

    stored_primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8"))
    audit.check("stored child freshness", stored_primary == fresh_primary and stored_independent == fresh_independent, "stored children exact fresh", "stored children exact fresh", "formal")


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="r169-v12-") as directory:
        root = Path(directory)
        fresh_primary = run_child(PRIMARY, staged, root / "primary.json")
        fresh_independent = run_child(INDEPENDENT, staged, root / "independent.json")

    expected_mode = "staged" if staged else "formal"
    audit.check("child modes and verdicts", fresh_primary["verdict"] == fresh_independent["verdict"] == "PASS" and fresh_primary["mode"] == fresh_independent["mode"] == expected_mode, {"primary": fresh_primary["mode"], "independent": fresh_independent["mode"]}, f"matching PASS {expected_mode}", "cross")
    common_keys = (
        "phase_complete_fixture",
        "fixture_intensity",
        "covariance_at_zero",
        "p0_trace",
        "p0_rank",
        "p0_idempotent",
        "lift_norm_coefficient",
        "phase_field_origin",
        "phase_field_shift",
        "covariance_origin_invariant",
        "pi_bracket_width",
        "q0_above_shell_three_gap",
        "q0_below_shell_four_gap",
        "q0_strictly_between_shells",
        "commensurate_shell_count",
        "reading_h_bcc_count",
        "r169_v1_1_index_square",
        "nonlinear_crossing",
        "negative_defect",
        "positive_defect",
        "rescale_contradiction",
        "rescale_incompatible",
    )
    agreement = {key: (fresh_primary["derived"].get(key), fresh_independent["derived"].get(key)) for key in common_keys}
    audit.check("independent exact agreement", all(left == right for left, right in agreement.values()), agreement, "all common exact fields agree", "cross")
    audit.check("manifest type and energy firewalls", "not deterministic P1 fields" in manifest["reading_h_type_split"]["composite_embedding"] and "G_* alone cannot select" in manifest["equivariant_nonextraction"]["consequence"] and "No ordering of the full functionals follows" in manifest["nonlinear_convention_firewall"]["full_energy_firewall"], "three scope firewalls", "three scope firewalls", "cross")
    audit.check("owner and shared hashes", fresh_primary["source_hash"] == normalized_sha256(PRIMARY) and fresh_independent["source_hash"] == normalized_sha256(INDEPENDENT) and fresh_primary["manifest_hash"] == fresh_independent["manifest_hash"] == normalized_sha256(MANIFEST) and fresh_primary["certificate_hash"] == fresh_independent["certificate_hash"] == normalized_sha256(CERTIFICATE), "all hashes current", "all hashes current", "cross")
    source_discipline(audit)
    if staged:
        staged_audit(audit, manifest)
    else:
        formal_audit(audit, manifest, fresh_primary, fresh_independent)

    return {
        "schema": "tect/pre-a-t055-reading-h-covariance-to-p1-interface-integrated/1.0",
        "version": __version__,
        "mode": expected_mode,
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
