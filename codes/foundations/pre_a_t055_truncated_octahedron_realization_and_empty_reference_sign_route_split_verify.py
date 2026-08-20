#!/usr/bin/env python3
"""Integrate and lifecycle-audit the R-169 v1.0 route split.

Purpose: execute the exact primary and non-importing independent derivations,
compare their substantive payloads, enforce source/code discipline, and audit
the staged or formally integrated authority topology.

Convention: candidate minus preregistered reference is the sign; the affine
family is a translational tile family rather than a Euclidean-Voronoi family;
formal mode requires the exact EXP-000851/R-169/event-639 authority graph.

Formula: both child lanes must derive identical geometry, renormalization,
uniform-margin, and transverse-Hessian fixtures before formal linkage passes.
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
SLUG = "pre-a-t055-truncated-octahedron-realization-and-empty-reference-sign-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
PRIMARY = REPO / f"codes/foundations/pre_a_t055_truncated_octahedron_realization_and_empty_reference_sign_route_split.py"
INDEPENDENT = REPO / f"codes/foundations/pre_a_t055_truncated_octahedron_realization_and_empty_reference_sign_route_split_independent.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

CLOSED = [
    "PA-T055-TRUNCATED-OCTAHEDRON-BCC-VORONOI-AND-AFFINE-REALIZATION-FAMILY",
    "PA-T055-MATCHED-RENORMALIZATION-EMPTY-REFERENCE-SIGN-AND-TRANSVERSE-STABILITY-REDUCTION",
]
NEW_NEGATIVES = [
    "NG-2026-08-14-PRE-A-T055-TRUNCATED-OCTAHEDRON-COMBINATORICS-AUTOMATIC-FINITE-REALIZATION-ENUMERATION",
    "NG-2026-08-14-PRE-A-T055-COMMON-COUNTERTERM-BASIS-UNFIXED-FINITE-PARTS-AUTOMATIC-EMPTY-REFERENCE-SIGN",
]
REUSED = [
    "R-2026-06-23-b3-bcc-structural-selection",
    "NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE",
]
OPEN_GATES = [
    "C6-BCC-PREMISE-BLOCKED",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
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


def run_child(script: Path, *, formal: bool, output: Path) -> dict[str, Any]:
    command = [sys.executable, "-B", "-X", "utf8", str(script)]
    if not formal:
        command.append("--staged")
    command.extend(("--output", str(output)))
    completed = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(
            f"child failed: {script.name}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def parse_json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def live_counts() -> dict[str, int]:
    catalog_summary = json.loads(
        (REPO / "verification/catalog-summary.json").read_text(encoding="utf-8")
    )
    claims = int(catalog_summary["claim_count"])
    results = int(json.loads((REPO / "results/index.json").read_text(encoding="utf-8"))["count"])
    gates = int(json.loads((REPO / "claims/gates-index.json").read_text(encoding="utf-8"))["count"])
    negatives = int(json.loads((REPO / "negative-results/index.json").read_text(encoding="utf-8"))["count"])
    explorations = len(parse_json_lines(REPO / "explorations/log.jsonl"))
    events = len(parse_json_lines(REPO / "changelog/log.jsonl"))
    tasks = len(json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"])
    catalog = int(catalog_summary["total"])
    return {
        "claims": claims,
        "results": results,
        "gates": gates,
        "negatives": negatives,
        "explorations": explorations,
        "events": events,
        "tasks": tasks,
        "catalog": catalog,
    }


def section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^### \*\*{re.escape(heading)}\*\*\s*$([\s\S]*?)(?=^### |\Z)",
        re.MULTILINE,
    )
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one section for {heading}, found {len(matches)}")
    return matches[0]


def negative_section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(heading)}\b([\s\S]*?)(?=^### |\Z)",
        re.MULTILINE,
    )
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one negative section for {heading}, found {len(matches)}")
    return matches[0]


def historical_result_section(markdown: str) -> str:
    pattern = re.compile(r"^### R-169\b([\s\S]*?)(?=^### R-|\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one R-169 result section, found {len(matches)}")
    return matches[0]


def source_ast_firewall(audit: Audit) -> None:
    primary_tree = ast.parse(PRIMARY.read_text(encoding="utf-8"))
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    integrated_tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    independent_imports = {
        alias.name.split(".")[0]
        for node in ast.walk(independent_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(independent_tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden_calls = {"float", "complex", "eval", "exec", "compile"}
    independent_calls = {
        node.func.id
        for node in ast.walk(independent_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    audit.check(
        "three source ASTs parse",
        all(tree is not None for tree in (primary_tree, independent_tree, integrated_tree)),
        "three parsed ASTs",
        "three parsed ASTs",
        "code",
    )
    audit.check(
        "independent stdlib exact firewall",
        not ({"sympy", "numpy", "scipy"} & independent_imports)
        and not (forbidden_calls & independent_calls),
        {"imports": sorted(independent_imports), "forbidden": sorted(forbidden_calls & independent_calls)},
        "no numerical imports or float/complex/dynamic calls",
        "code",
    )
    direct_derived_assignments = (
        '"vertex_count": 24',
        '"edge_count": 36',
        '"positive_case_candidate": "1/4"',
        '"negative_case_hessian": ["10", "-2"]',
    )
    child_sources = PRIMARY.read_text(encoding="utf-8") + "\n" + INDEPENDENT.read_text(encoding="utf-8")
    audit.check(
        "derived literals confined to manifest oracles",
        all(token not in child_sources for token in direct_derived_assignments),
        "old direct derived assignments absent",
        "old direct derived assignments absent",
        "code",
    )


def formal_audit(audit: Audit, manifest: dict[str, Any], fresh_primary: dict[str, Any], fresh_independent: dict[str, Any]) -> None:
    gates_text = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")

    closed_sections = [section(gates_text, gate) for gate in CLOSED]
    audit.check(
        "exact two scoped closed gates",
        all("EXP-000851" in value and "R-169 v1.0" in value and "CLOSED" in value for value in closed_sections),
        "two unique scoped CLOSED sections",
        "two unique scoped CLOSED sections",
        "formal",
    )
    open_sections = [section(gates_text, gate) for gate in OPEN_GATES]
    audit.check(
        "blocked and Round-1 parents remain open",
        all("EXP-000851" in value and "remain OPEN" in value for value in open_sections),
        "two unique OPEN annotations",
        "two unique OPEN annotations",
        "formal",
    )
    new_sections = [negative_section(negatives_text, negative) for negative in NEW_NEGATIVES]
    audit.check(
        "two exact new negatives",
        all("EXP-000851" in value and "R-169 v1.0" in value for value in new_sections)
        and all(negative_section(negatives_text, negative) for negative in REUSED),
        "new and reused negatives linked",
        "new and reused negatives linked",
        "formal",
    )
    r169_section = historical_result_section(results_text)
    audit.check(
        "R-169 historical result authority",
        all(token in r169_section for token in ("R-169 v1.0", "EXP-000851", "R-169 v1.4")),
        "R-169 v1.0 history and current successor",
        "R-169 v1.0 history and current successor",
        "formal",
    )
    audit.check(
        "roadmap and strategy index",
        "EXP-000851" in roadmap_text and "R-169 v1.0" in roadmap_text
        and "EXP-000851" in strategy_index and "R-169 v1.0" in strategy_index,
        "both navigation sources linked",
        "both navigation sources linked",
        "formal",
    )

    explorations = parse_json_lines(REPO / "explorations/log.jsonl")
    matching_explorations = [entry for entry in explorations if entry.get("id") == "EXP-000851"]
    audit.check(
        "EXP-000851 exact formal topology",
        len(matching_explorations) == 1
        and matching_explorations[0].get("task_id") == "T-055"
        and matching_explorations[0].get("verdict") == "advanced"
        and matching_explorations[0].get("formal_refs", {}).get("results") == ["R-169"]
        and matching_explorations[0].get("formal_refs", {}).get("negatives") == NEW_NEGATIVES + REUSED
        and matching_explorations[0].get("gate_ids") == CLOSED + OPEN_GATES
        and matching_explorations[0].get("related")
        == [{"id": "EXP-000850", "relation": "continues"}],
        matching_explorations,
        "one exact exploration",
        "formal",
    )

    events = parse_json_lines(REPO / "changelog/log.jsonl")
    formal_contract = manifest["formal_integration"]
    matches = [(ordinal, candidate) for ordinal, candidate in enumerate(events, start=1) if candidate.get("id") == formal_contract["event_id"]]
    unique_event = len(matches) == 1
    ordinal, event = matches[0] if unique_event else (None, {})
    audit.check(
        "event 639 historical identity",
        unique_event
        and ordinal == int(formal_contract["event_ordinal"])
        and event.get("id") == formal_contract["event_id"]
        and event.get("header") == f"[{formal_contract['event_title']}] - 2026-08-14"
        and event.get("neg_results") == sorted(NEW_NEGATIVES)
        and event.get("claim_ids") == [
            "B3-BCC-STRUCT",
            "B3-RH-TESTED-STRUCTURE-RANKING",
            "C6-BCC-PREMISE-BLOCKED",
            "C6-SPACETIME-SIGNATURE",
            "EXP-000851",
            "R-169",
        ],
        {"total_events": len(events), "ordinal": ordinal, **event},
        "exact final event",
        "formal",
    )
    raw = event.get("raw", "")
    audit.check(
        "event raw scope",
        all(
            token in raw
            for token in (
                "metric-regular",
                "affine-combinatorial",
                "common scalar",
                "finite parts",
                "transverse Hessian",
                "C6-BCC-PREMISE-BLOCKED remains OPEN",
                "No R-169 v1.0 PDF is issued",
            )
        )
        and ".pdf" not in raw,
        "required raw scope tokens",
        "required raw scope tokens",
        "formal",
    )

    theorem_map = json.loads((REPO / "governance/sector-a-theorem-map.json").read_text(encoding="utf-8"))
    priority = theorem_map["research_priority"]
    actual_map_version = tuple(int(part) for part in theorem_map.get("version", "0.0.0").split("."))
    required_map_version = tuple(int(part) for part in formal_contract["theorem_map_version"].split("."))
    audit.check(
        "theorem map 1.35.0",
        actual_map_version >= required_map_version
        and priority.get("latest_cp1_checkpoint")
        and priority.get("closed_r169_v1_0_scoped_gates") == CLOSED
        and priority.get("r169_v1_0_new_negatives") == NEW_NEGATIVES
        and priority.get("r169_v1_0_reused_negatives") == REUSED
        and priority.get("r169_v1_0_open_gates") == OPEN_GATES,
        priority,
        "exact theorem-map keys",
        "formal",
    )
    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    t055 = [task for task in tasks if task.get("id") == "T-055"]
    audit.check(
        "T-055 stable routing",
        len(t055) == 1
        and t055[0].get("title")
        == "Geometry-first truncated-octahedron candidate triage: enumerate realizations and test empty-reference sign before structural use"
        and t055[0].get("owner") == "Codex"
        and t055[0].get("gate") == "C6-BCC-PREMISE-BLOCKED"
        and bool(t055[0].get("note")),
        t055,
        "unique stable T-055 identity/routing",
        "formal",
    )

    if not PRIMARY_RESULT.exists() or not INDEPENDENT_RESULT.exists():
        raise AssertionError("formal child result JSON files are required")
    stored_primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8"))
    audit.check(
        "stored child results exact fresh",
        stored_primary == fresh_primary and stored_independent == fresh_independent,
        "stored child payloads equal fresh",
        "stored child payloads equal fresh",
        "freshness",
    )


def build_payload(*, formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    with tempfile.TemporaryDirectory(prefix="r169-v1-") as directory:
        temp = Path(directory)
        fresh_primary = run_child(PRIMARY, formal=formal, output=temp / "primary.json")
        fresh_independent = run_child(INDEPENDENT, formal=formal, output=temp / "independent.json")

    audit.check(
        "child summaries",
        fresh_primary["summary"]["status"] == "PASS"
        and fresh_independent["summary"]["status"] == "PASS"
        and fresh_primary["mode"] == ("formal" if formal else "staged")
        and fresh_independent["mode"] == ("formal" if formal else "staged"),
        (fresh_primary["summary"], fresh_independent["summary"]),
        "two PASS children in requested mode",
        "children",
    )
    audit.check(
        "dual-lane exact derived equality",
        fresh_primary["derived"] == fresh_independent["derived"],
        fresh_primary["derived"],
        fresh_independent["derived"],
        "crosscheck",
    )
    audit.check(
        "shared source hashes",
        fresh_primary["source_hashes"][str(MANIFEST.relative_to(REPO)).replace("\\", "/")]
        == fresh_independent["source_hashes"][str(MANIFEST.relative_to(REPO)).replace("\\", "/")]
        and fresh_primary["source_hashes"][str(CERTIFICATE.relative_to(REPO)).replace("\\", "/")]
        == fresh_independent["source_hashes"][str(CERTIFICATE.relative_to(REPO)).replace("\\", "/")],
        "manifest/certificate hashes agree",
        "manifest/certificate hashes agree",
        "crosscheck",
    )
    audit.check(
        "exact five-file package",
        all(path.exists() for path in PACKAGE_PATHS)
        and len(
            [
                path
                for path in list((REPO / "strategy").glob(f"{SLUG}*"))
                + list((REPO / "codes/foundations").glob("pre_a_t055_truncated_octahedron_realization_and_empty_reference_sign_route_split*"))
                if path.is_file()
            ]
        )
        == len(PACKAGE_PATHS),
        [str(path.relative_to(REPO)) for path in PACKAGE_PATHS],
        "exactly five package sources",
        "topology",
    )
    source_ast_firewall(audit)
    audit.check(
        "package ASCII LF final-LF",
        all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in PACKAGE_PATHS
        ),
        "five clean sources",
        "five clean sources",
        "format",
    )
    audit.check(
        "no package PDF",
        not list((REPO / "strategy").glob(f"{SLUG}*.pdf")),
        "no PDF",
        "no PDF",
        "scope",
    )

    expected_counts = manifest["formal_integration"][
        "expected_postformal_counts" if formal else "expected_preformal_counts"
    ]
    counts = live_counts()
    event_present = any(
        event.get("id") == manifest["formal_integration"]["event_id"]
        for event in parse_json_lines(REPO / "changelog/log.jsonl")
    )
    if event_present:
        expected_counts = manifest["formal_integration"]["expected_postformal_counts"]
        counts_match = all(counts[key] >= int(expected_counts[key]) for key in expected_counts)
    else:
        counts_match = counts == expected_counts
        if formal and not DEFAULT_OUTPUT.exists():
            pending_integrated_counts = dict(expected_counts)
            pending_integrated_counts["catalog"] -= 1
            counts_match = counts == pending_integrated_counts
    audit.check(
        "exact global counts",
        counts_match,
        counts,
        expected_counts,
        "lifecycle",
    )
    if not formal:
        formal_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                REPO / "claims/GATES.md",
                REPO / "RESULTS-LEDGER.md",
                REPO / "negative-results/registry.md",
                REPO / "explorations/log.jsonl",
            )
        )
        if event_present:
            audit.check("integrated historical authority revalidation", True, "target event present", "target event present", "lifecycle")
        else:
            audit.check(
                "preformal authority absence",
                all(token not in formal_text for token in ("EXP-000851", "### R-169", *CLOSED, *NEW_NEGATIVES)),
                "formal IDs absent before landing",
                "formal IDs absent before landing",
                "lifecycle",
            )
    else:
        formal_audit(audit, manifest, fresh_primary, fresh_independent)

    return {
        "schema": "tect/pre-a-t055-truncated-octahedron-sign-integrated-run/1.0",
        "version": manifest["version"],
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": fresh_primary["derived"],
        "child_summaries": {
            "primary": fresh_primary["summary"],
            "independent": fresh_independent["summary"],
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in PACKAGE_PATHS
        },
        "live_counts": counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(formal=not args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"INTEGRATED PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
