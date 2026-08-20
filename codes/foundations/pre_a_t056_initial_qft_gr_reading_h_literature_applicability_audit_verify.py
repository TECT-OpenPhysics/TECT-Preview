#!/usr/bin/env python3
"""Integrated verifier for the R-170 v1.0 applicability rollout.

It executes two independent record readers, compares their derived audit
matrix, enforces code and byte discipline, and checks either the preformal
staged topology or the exact integrated EXP/event/result/gate lifecycle.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True
__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t056-initial-qft-gr-reading-h-literature-applicability-audit"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
PRIMARY = REPO / "codes/foundations/pre_a_t056_initial_qft_gr_reading_h_literature_applicability_audit.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_t056_initial_qft_gr_reading_h_literature_applicability_audit_independent.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"
PACKAGE_PATHS = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def gate_section(markdown: str, gate: str) -> str:
    pattern = re.compile(rf"^### \*\*{re.escape(gate)}\*\*\s*$([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one gate section {gate}, found {len(matches)}")
    return matches[0]


def result_section(markdown: str, result_id: str) -> str:
    pattern = re.compile(rf"^### {re.escape(result_id)}\b([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one result section {result_id}, found {len(matches)}")
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


def catalog_inventory_count() -> int:
    script = REPO / "verification/scripts/build_catalog.py"
    specification = importlib.util.spec_from_file_location("t056_build_catalog", script)
    if specification is None or specification.loader is None:
        raise AssertionError("cannot load catalog builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    count = 0
    for path in module.real_files(REPO, skip_names=module.SKIP_NAMES):
        relative = str(path.relative_to(REPO)).replace("\\", "/")
        if relative in module.SKIP_PATHS or relative.startswith("verification/catalog/"):
            continue
        count += 1
    return count


def function_source(path: Path, tree: ast.Module, name: str) -> str:
    source = path.read_text(encoding="utf-8")
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise AssertionError(f"expected one {name} in {path.name}")
    return ast.get_source_segment(source, matches[0]) or ""


def source_discipline(audit: Audit, manifest: dict[str, Any]) -> None:
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
    nonstdlib = {name for name in imports if name not in sys.stdlib_module_names and name != "__future__"}
    local_stems = {PRIMARY.stem, SCRIPT.stem, INDEPENDENT.stem}
    local_imports = imports & local_stems
    forbidden_calls = {"float", "complex", "eval", "exec", "compile", "__import__"}
    audit.check("three ASTs parse", len(trees) == 3, len(trees), 3, "code")
    audit.check(
        "independent stdlib and no dynamic execution",
        not nonstdlib and not local_imports and not (calls & forbidden_calls),
        {"imports": sorted(imports), "nonstdlib": sorted(nonstdlib), "local": sorted(local_imports), "calls": sorted(calls & forbidden_calls)},
        "stdlib only; no local imports, float/complex/dynamic execution",
        "code",
    )
    primary_derivation = function_source(PRIMARY, trees[PRIMARY], "derive_records")
    independent_derivation = function_source(INDEPENDENT, trees[INDEPENDENT], "derive_independent")
    audit.check(
        "derived-value masking firewall",
        "test_oracles" not in primary_derivation and "test_oracles" not in independent_derivation,
        "derivations exclude test_oracles",
        "derivations exclude test_oracles",
        "code",
    )

    file_paths = [*PACKAGE_PATHS, *(REPO / row["path"] for row in manifest["audit_records"].values())]
    for path in file_paths:
        data = path.read_bytes()
        lines = data.splitlines()
        format_ok = (
            data.endswith(b"\n")
            and b"\r" not in data
            and all(byte < 128 for byte in data)
            and all(line == line.rstrip(b" \t") for line in lines)
        )
        audit.check(
            f"format {path.name}",
            format_ok,
            "ASCII LF final-LF no trailing whitespace" if format_ok else "format defect",
            "ASCII LF final-LF no trailing whitespace",
            "code",
        )


def semantic_record_contract(record_texts: dict[str, str], manifest: dict[str, Any]) -> bool:
    expected_dispositions = {
        claim: contract["overall_disposition"] for claim, contract in manifest["audit_records"].items()
    }
    expected_load = {
        claim: contract["load_bearing_allowed"] for claim, contract in manifest["audit_records"].items()
    }
    boundary_sentences = {
        "B1-RH-ENUM": "This record changes no B1 tier or lifecycle.",
        "C4-GRAVITY-1LOOP": "This record does not demote or promote C4.",
        "C5-NEWTON-G": "This record changes no C5 tier or lifecycle.",
        "C6-SPACETIME-SIGNATURE": "This record does not change the C6 T1/ACTIVE scaffold.",
    }
    for claim, text in record_texts.items():
        disposition = re.search(r"^\*\*Overall disposition:\*\*\s+`([^`]+)`", text, re.MULTILINE)
        load = re.search(r"^\*\*Load-bearing use:\*\*\s+(Yes|No)", text, re.MULTILINE)
        if disposition is None or load is None:
            return False
        root = next(
            (
                candidate
                for candidate in ("APPLIES-CONDITIONALLY", "DOES-NOT-APPLY", "NOT-YET-ASSESSED", "APPLIES")
                if disposition.group(1).startswith(candidate)
            ),
            None,
        )
        if root != expected_dispositions[claim] or (load.group(1) == "Yes") != expected_load[claim]:
            return False
        if not all(
            any(line.startswith(prefix) for line in text.splitlines())
            for prefix in manifest["record_contract"]["required_section_prefixes"]
        ):
            return False
        section = re.search(r"^## 6 Adversarial checks\s*$([\s\S]*?)(?=^## 7 )", text, re.MULTILINE)
        if section is None:
            return False
        labels = " ".join(re.findall(r"^- \*\*([^*]+?)\s+-\s+", section.group(1), re.MULTILINE)).lower()
        if not all(axis in labels for axis in ("convention", "domain", "limit")):
            return False
        if "status.json` is the live claim authority" not in text:
            return False
        if boundary_sentences[claim] not in text:
            return False
    b1 = record_texts["B1-RH-ENUM"]
    c4 = record_texts["C4-GRAVITY-1LOOP"]
    c5 = record_texts["C5-NEWTON-G"]
    c6 = record_texts["C6-SPACETIME-SIGNATURE"]
    return (
        "F_total[Q] > F_total[G_*]" in b1
        and "This target is not `F_total[G_*]-F_total[physical empty] < 0`." in b1
        and "candidate, not admitted, sources" in c4
        and "discovery evidence only" in c4
        and "explicitly non-exhaustive" in c4
        and "candidate, not admitted, sources" in c5
        and "incompatible `16 pi`, `32 pi`, and `64 pi` coefficients" in c5
        and "explicitly non-exhaustive" in c5
        and "for the present BCC-premised route; non-BCC alternatives remain `NOT-YET-ASSESSED`" in c6
        and "Stop the present BCC-premised inheritance route" in c6
        and not any(
            forbidden in "\n".join(record_texts.values())
            for forbidden in ("This record promotes", "physical conclusion follows", "This record restores B3")
        )
    )


def hostile_mutation_audit(audit: Audit, manifest: dict[str, Any]) -> None:
    originals = {
        claim: (REPO / contract["path"]).read_text(encoding="ascii")
        for claim, contract in manifest["audit_records"].items()
    }
    audit.check("unmutated semantic contract", semantic_record_contract(originals, manifest), True, True, "mutation")

    mutations: list[dict[str, str]] = []

    changed = dict(originals)
    changed["B1-RH-ENUM"] = changed["B1-RH-ENUM"].replace(
        "F_total[Q] > F_total[G_*]", "F_total[G_*] > F_total[physical empty]"
    )
    mutations.append(changed)

    changed = dict(originals)
    changed["C4-GRAVITY-1LOOP"] = changed["C4-GRAVITY-1LOOP"].replace(
        "candidate, not admitted, sources", "stable admitted sources"
    ).replace("discovery evidence only", "load-bearing primary evidence")
    mutations.append(changed)

    changed = dict(originals)
    changed["C5-NEWTON-G"] = changed["C5-NEWTON-G"].replace("**Load-bearing use:** No.", "**Load-bearing use:** Yes.")
    mutations.append(changed)

    changed = dict(originals)
    changed["C5-NEWTON-G"] = changed["C5-NEWTON-G"].replace(
        "incompatible `16 pi`, `32 pi`, and `64 pi` coefficients",
        "a uniquely settled `16 pi` normalization",
    )
    mutations.append(changed)

    changed = dict(originals)
    changed["C6-SPACETIME-SIGNATURE"] = changed["C6-SPACETIME-SIGNATURE"].replace(
        "`DOES-NOT-APPLY` for the present BCC-premised route; non-BCC alternatives remain `NOT-YET-ASSESSED`",
        "`DOES-NOT-APPLY` universally",
    )
    mutations.append(changed)

    changed = dict(originals)
    changed["B1-RH-ENUM"] = changed["B1-RH-ENUM"].replace(
        "`status.json` is the live claim authority", "`claim.md` is the live claim authority"
    )
    mutations.append(changed)

    changed = dict(originals)
    changed["C4-GRAVITY-1LOOP"] = "\n".join(
        line for line in changed["C4-GRAVITY-1LOOP"].splitlines() if not line.startswith("- **Domain/regularity")
    ) + "\n"
    mutations.append(changed)

    changed = dict(originals)
    changed["B1-RH-ENUM"] = changed["B1-RH-ENUM"].replace(
        "This record changes no B1 tier or lifecycle.", "This record promotes B1 and closes the physical route."
    )
    mutations.append(changed)

    declared = manifest["hostile_mutations"]
    if len(mutations) != len(declared):
        raise AssertionError(f"mutation suite mismatch: {len(mutations)} != {len(declared)}")
    results = {description: not semantic_record_contract(mutated, manifest) for description, mutated in zip(declared, mutations, strict=True)}
    audit.check("all declared hostile mutations rejected", all(results.values()), results, "all eight rejected", "mutation")


def staged_audit(audit: Audit, manifest: dict[str, Any]) -> None:
    authority_paths = (
        "claims/GATES.md",
        "RESULTS-LEDGER.md",
        "ROADMAP.md",
        "strategy/INDEX.md",
        "explorations/log.jsonl",
        "changelog/log.jsonl",
    )
    authorities = "\n".join((REPO / path).read_text(encoding="utf-8") for path in authority_paths)
    outputs = [REPO / manifest["artifacts"][name] for name in ("primary_result", "independent_result", "integrated_result")]
    new_tokens = (manifest["exploration_id"], manifest["version"], manifest["result_id"])
    audit.check(
        "preformal authority and output absence",
        all(token not in authorities for token in new_tokens) and not any(path.exists() for path in outputs),
        "new formal tokens and outputs absent",
        "new formal tokens and outputs absent",
        "lifecycle",
    )
    current = live_counts()
    projected = dict(current)
    projected["results"] += 1
    projected["explorations"] += 1
    projected["events"] += 1
    projected["catalog"] = catalog_inventory_count() + sum(not path.exists() for path in outputs)
    expected = manifest["formal_integration"]["expected_post_counts"]
    audit.check("preformal exact count projection", projected == expected, projected, expected, "lifecycle")


def formal_audit(
    audit: Audit,
    manifest: dict[str, Any],
    fresh_primary: dict[str, Any],
    fresh_independent: dict[str, Any],
) -> None:
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    roadmap = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")

    closed = gate_section(gates, manifest["closed_gate_ids"][0])
    closed_ok = all(
        token in closed
        for token in (
            manifest["exploration_id"],
            manifest["version"],
            manifest["closed_gate_status"][manifest["closed_gate_ids"][0]],
            "B1-RH-ENUM",
            "C4-GRAVITY-1LOOP",
            "C5-NEWTON-G",
            "C6-SPACETIME-SIGNATURE",
            "policy remains binding",
        )
    )
    audit.check("initial rollout gate scoped closure", closed_ok, "exact scoped closure" if closed_ok else closed, "EXP/R/CLOSED@INITIAL-FOUR-RECORDS and policy binding", "formal")

    open_state: dict[str, bool] = {}
    for gate in manifest["open_gate_ids"]:
        section = gate_section(gates, gate)
        status_open = "**Status:** OPEN" in section or "**Discharge path:** BLOCKED" in section or "remain OPEN" in section
        open_state[gate] = status_open and manifest["exploration_id"] in section and manifest["version"] in section
    audit.check("all residual routes remain open", all(open_state.values()), open_state, "all annotated EXP/R and OPEN/BLOCKED", "formal")

    r170 = result_section(results, manifest["result_id"])
    result_tokens = (
        manifest["version"],
        manifest["exploration_id"],
        "T0",
        "claim-nonbearing",
        "APPLIES",
        "NOT-YET-ASSESSED",
        "DOES-NOT-APPLY",
        "CLOSED@INITIAL-FOUR-RECORDS",
        "No R-170 v1.0 PDF",
    )
    audit.check("R-170 exact result scope", all(token in r170 for token in result_tokens), [token for token in result_tokens if token in r170], list(result_tokens), "formal")
    linkage_ok = all(token in roadmap and token in strategy_index for token in (manifest["exploration_id"], manifest["version"]))
    audit.check("roadmap and strategy linkage", linkage_ok, linkage_ok, True, "formal")

    explorations = [row for row in parse_json_lines(REPO / "explorations/log.jsonl") if row.get("id") == manifest["exploration_id"]]
    audit.check("unique applicability exploration", len(explorations) == 1, len(explorations), 1, "formal")
    exploration = explorations[0]
    exploration_ok = (
        exploration.get("task_id") == manifest["task_id"]
        and exploration.get("verdict") == "advanced"
        and exploration.get("claim_ids") == manifest["claim_ids"]
        and exploration.get("gate_ids") == [*manifest["closed_gate_ids"], *manifest["open_gate_ids"]]
        and exploration.get("related") == [{"id": manifest["prior_exploration_id"], "relation": "continues"}]
        and exploration.get("formal_refs") == {
            "results": [manifest["result_id"]],
            "negatives": manifest["reused_negative_ids"],
            "events": [],
        }
    )
    audit.check("EXP exact topology", exploration_ok, {key: exploration.get(key) for key in ("task_id", "verdict", "claim_ids", "gate_ids", "related", "formal_refs")}, "exact manifest topology", "formal")

    contract = manifest["formal_integration"]
    events = parse_json_lines(REPO / "changelog/log.jsonl")
    matches = [(ordinal, event) for ordinal, event in enumerate(events, start=1) if event.get("id") == contract["event_id"]]
    unique_event = len(matches) == 1
    ordinal, event = matches[0] if unique_event else (None, {})
    exact_header = f"[{contract['event_title']}] - {manifest['issued']}"
    event_identity = unique_event and ordinal == contract["event_ordinal"] and event.get("header") == exact_header
    audit.check("event 647 identity", event_identity, {"total": len(events), "ordinal": ordinal, "id": event.get("id"), "header": event.get("header")}, {"ordinal": contract["event_ordinal"], "id": contract["event_id"], "header": exact_header}, "formal")
    event_linkage = (
        event.get("claim_ids") == contract["event_claim_ids"]
        and event.get("keywords") == contract["event_keywords"]
        and event.get("notes") == contract["event_notes"]
        and event.get("scripts") == contract["event_scripts"]
        and event.get("neg_results") == []
    )
    audit.check("event exact linkage and no new negative", event_linkage, {key: event.get(key) for key in ("claim_ids", "keywords", "notes", "scripts", "neg_results")}, "manifest arrays and empty neg_results", "formal")
    raw = event.get("raw", "")
    event_scope = all(token in raw for token in contract["event_raw_tokens"]) and ".pdf" not in raw
    audit.check("event raw scope firewall", event_scope, [token for token in contract["event_raw_tokens"] if token in raw], "all tokens and no .pdf", "formal")

    theorem_map = json.loads((REPO / "governance/sector-a-theorem-map.json").read_text(encoding="utf-8"))
    priority = theorem_map["research_priority"]
    map_contract = contract["theorem_map_contract"]
    map_ok = (
        theorem_map.get("version") == contract["theorem_map_version"]
        and manifest["exploration_id"] in priority.get("latest_applicability_checkpoint", "")
        and manifest["version"] in priority.get("latest_applicability_checkpoint", "")
        and "EXP-000862" in priority.get("latest_cp1_checkpoint", "")
        and priority.get("closed_r170_v1_0_scoped_gates") == map_contract["closed_r170_v1_0_scoped_gates"]
        and priority.get("t056_initial_claim_dispositions") == map_contract["t056_initial_claim_dispositions"]
        and priority.get("t056_open_residual_routes") == map_contract["t056_open_residual_routes"]
        and priority.get("t056_new_negatives") == []
        and priority.get("t056_reused_negatives") == map_contract["t056_reused_negatives"]
    )
    audit.check("theorem map v1.40 exact applicability keys", map_ok, {"version": theorem_map.get("version"), "latest": priority.get("latest_applicability_checkpoint", "")}, "v1.40 and exact arrays; CP1 remains EXP862", "formal")

    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    matches = [task for task in tasks if task.get("id") == manifest["task_id"]]
    task_ok = (
        len(matches) == 1
        and matches[0].get("status") == "done"
        and matches[0].get("gate") == manifest["closed_gate_ids"][0]
        and matches[0].get("owner")
        and manifest["exploration_id"] in matches[0].get("note", "")
        and manifest["version"] in matches[0].get("note", "")
    )
    audit.check("T-056 done with exact linkage", bool(task_ok), matches, "unique done task with gate, owner, EXP and R", "formal")

    source_hashes = {name: raw_sha256(REPO / source["path"]) for name, source in manifest["source_authorities"].items()}
    pinned_hashes = {name: source["sha256"] for name, source in manifest["source_authorities"].items()}
    audit.check("formal authority pins unchanged", source_hashes == pinned_hashes, source_hashes, pinned_hashes, "formal")

    current_counts = live_counts()
    expected_counts = dict(contract["expected_post_counts"])
    if not DEFAULT_OUTPUT.exists():
        expected_counts["catalog"] -= 1
    audit.check("exact post counts", current_counts == expected_counts, current_counts, expected_counts, "formal")

    stored_primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8"))
    audit.check("stored child freshness", stored_primary == fresh_primary and stored_independent == fresh_independent, "stored children exact fresh", "stored children exact fresh", "formal")


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="r170-v10-") as directory:
        root = Path(directory)
        fresh_primary = run_child(PRIMARY, staged, root / "primary.json")
        fresh_independent = run_child(INDEPENDENT, staged, root / "independent.json")

    mode = "staged" if staged else "formal"
    child_ok = (
        fresh_primary.get("verdict") == fresh_independent.get("verdict") == "PASS"
        and fresh_primary.get("mode") == fresh_independent.get("mode") == mode
    )
    audit.check("child modes and verdicts", child_ok, {"primary": fresh_primary.get("mode"), "independent": fresh_independent.get("mode")}, f"matching PASS {mode}", "cross")

    common_keys = (
        "record_dispositions",
        "record_load_bearing",
        "crosswalk_row_counts",
        "crosswalk_status_counts",
        "load_bearing_blockers",
        "bounded_search_outcomes",
        "section_coverage",
        "adversarial_axis_counts",
        "stale_prose_firewalls",
        "record_hashes",
    )
    agreement = {key: (fresh_primary["derived"].get(key), fresh_independent["derived"].get(key)) for key in common_keys}
    audit.check("independent exact record agreement", all(left == right for left, right in agreement.values()), agreement, "all common derived fields agree", "cross")

    hash_ok = (
        fresh_primary["source_hash"] == normalized_sha256(PRIMARY)
        and fresh_independent["source_hash"] == normalized_sha256(INDEPENDENT)
        and fresh_primary["manifest_hash"] == fresh_independent["manifest_hash"] == normalized_sha256(MANIFEST)
        and fresh_primary["certificate_hash"] == fresh_independent["certificate_hash"] == normalized_sha256(CERTIFICATE)
    )
    audit.check("owner and shared hashes", hash_ok, "all current" if hash_ok else "hash drift", "all current", "cross")

    scope = manifest["no_overclaim"]
    scope_ok = (
        manifest["tier"] == "T0"
        and manifest["claim_bearing"] is False
        and manifest["new_negative_ids"] == []
        and manifest["closed_gate_status"] == {"LITERATURE-FIRST-APPLICABILITY-AUDIT": "CLOSED@INITIAL-FOUR-RECORDS"}
        and "policy remains binding" in scope
        and "No R-170 v1.0 PDF" in scope
    )
    audit.check("scope and closure qualifier", scope_ok, scope, "T0/nonbearing/scoped closure/policy binding/no PDF", "scope")
    source_discipline(audit, manifest)
    hostile_mutation_audit(audit, manifest)

    if staged:
        staged_audit(audit, manifest)
    else:
        formal_audit(audit, manifest, fresh_primary, fresh_independent)

    return {
        "schema": "tect/pre-a-t056-initial-qft-gr-reading-h-literature-applicability-audit-integrated/1.0",
        "version": __version__,
        "mode": mode,
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
