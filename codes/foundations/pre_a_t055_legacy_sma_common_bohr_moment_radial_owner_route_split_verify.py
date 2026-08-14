#!/usr/bin/env python3
"""Integrate and lifecycle-audit the R-169 v1.4 common-Bohr route split.

Purpose: compare exact SymPy and stdlib/Fraction derivations, enforce source
discipline, and audit the staged or formally integrated repository topology.
Convention: the corrected scalar Bohr owner is distinct from the finite-grid,
full-Hartree, current A1/P1, physical-empty, and stability owners.
Formula: f=(mu2/2)I+(lambda/2)K4 I^2+(gamma/3)K6 I^3, with
K4=N4/N2^2 and K6=N6/N2^3.
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


sys.dont_write_bytecode = True
__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
PRIMARY = REPO / "codes/foundations/pre_a_t055_legacy_sma_common_bohr_moment_radial_owner_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_t055_legacy_sma_common_bohr_moment_radial_owner_route_split_independent.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"
LEGACY_RECORD = REPO / "archive/legacy/registry/records/LEG-T055-COMMON-BOHR-FDECL-001.json"

CLOSED = ["PA-T055-LEGACY-SMA-COMMON-BOHR-MOMENT-RADIAL-OWNER-AND-PRODUCTION-ENDPOINT-AUDIT"]
OPEN = [
    "LEGACY-SELECTIVE-INDEX-AND-ON-DEMAND-REVALIDATION",
    "PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE",
    "PA-CP1-ST8-Q3LOCK-PHYSICAL-EMPTY-SPACE-REFERENCE",
    "C6-BCC-PREMISE-BLOCKED",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
REUSED_NEGATIVES = ["R-2026-06-23-b3-bcc-structural-selection"]
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


def result_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^### {re.escape(heading)}\b([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one result section {heading}, found {len(matches)}")
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
    scripts_dir = REPO / "verification/scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import build_catalog  # type: ignore[import-not-found]

    count = 0
    for path in build_catalog.real_files(REPO, skip_names=build_catalog.SKIP_NAMES):
        relative = str(path.relative_to(REPO)).replace("\\", "/")
        if relative in build_catalog.SKIP_PATHS or relative.startswith("verification/catalog/"):
            continue
        count += 1
    return count


def derivation_source(path: Path, tree: ast.Module) -> str:
    source = path.read_text(encoding="utf-8")
    candidates = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in {"derive_exact", "derive_fraction_exact"}
    ]
    if len(candidates) != 1:
        raise AssertionError(f"expected one derivation function in {path.name}")
    return ast.get_source_segment(source, candidates[0]) or ""


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
    forbidden_calls = {"float", "complex", "eval", "exec", "compile", "__import__"}
    nonstdlib_imports = {name for name in imports if name not in sys.stdlib_module_names and name != "__future__"}
    local_imports = {
        name for name in imports
        if "pre_a_t055_legacy_sma_common_bohr_moment_radial_owner_route_split" in name
    }
    audit.check("three ASTs parse", len(trees) == 3, len(trees), 3, "code")
    audit.check(
        "independent exact stdlib",
        not (forbidden_imports & imports)
        and not nonstdlib_imports
        and not local_imports
        and not (forbidden_calls & calls),
        {
            "imports": sorted(imports),
            "nonstdlib": sorted(nonstdlib_imports),
            "local": sorted(local_imports),
            "forbidden_calls": sorted(forbidden_calls & calls),
        },
        "stdlib/Fraction only; no local imports, float/complex/dynamic execution",
        "code",
    )
    for path, tree in trees.items():
        docstring = ast.get_docstring(tree) or ""
        audit.check(
            f"docstring contract {path.name}",
            all(token in docstring for token in ("Purpose:", "Convention:", "Formula:")),
            docstring.splitlines()[:4],
            "purpose/convention/formula",
            "code",
        )
    for path in PACKAGE_PATHS:
        data = path.read_bytes()
        format_ok = data.endswith(b"\n") and b"\r" not in data and all(byte < 128 for byte in data)
        audit.check(
            f"format {path.name}",
            format_ok,
            "ASCII LF final-LF" if format_ok else "bad format",
            "ASCII LF final-LF",
            "code",
        )
    primary_derivation = derivation_source(PRIMARY, trees[PRIMARY])
    independent_derivation = derivation_source(INDEPENDENT, trees[INDEPENDENT])
    audit.check(
        "derived-value masking firewall",
        "registered_inputs" in primary_derivation
        and "registered_inputs" in independent_derivation
        and "test_oracles" not in primary_derivation
        and "test_oracles" not in independent_derivation,
        "derivations read registered inputs only",
        "derivations read registered inputs only",
        "code",
    )


def staged_audit(audit: Audit, manifest: dict[str, Any]) -> None:
    authorities = "\n".join(
        (REPO / path).read_text(encoding="utf-8")
        for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "explorations/log.jsonl", "changelog/log.jsonl")
    )
    new_tokens = [manifest["exploration_id"], manifest["version"], *CLOSED]
    absent_paths = (PRIMARY_RESULT, INDEPENDENT_RESULT, DEFAULT_OUTPUT, LEGACY_RECORD)
    audit.check(
        "preformal authority absence",
        all(token not in authorities for token in new_tokens) and not any(path.exists() for path in absent_paths),
        "new authority tokens and owned outputs absent",
        "new authority tokens and owned outputs absent",
        "lifecycle",
    )
    current = live_counts()
    projected = dict(current)
    for key, delta in {"gates": 1, "explorations": 1, "events": 1}.items():
        projected[key] += delta
    projected["catalog"] = catalog_inventory_count() + int(not LEGACY_RECORD.exists()) + sum(
        not path.exists() for path in (PRIMARY_RESULT, INDEPENDENT_RESULT, DEFAULT_OUTPUT)
    )
    expected = manifest["formal_integration"]["expected_post_counts"]
    audit.check("preformal count projection", projected == expected, projected, expected, "lifecycle")


def formal_audit(audit: Audit, manifest: dict[str, Any], fresh_primary: dict[str, Any], fresh_independent: dict[str, Any]) -> None:
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    roadmap = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")

    closed_sections = [gate_section(gates, identifier) for identifier in CLOSED]
    open_sections = {identifier: gate_section(gates, identifier) for identifier in OPEN}
    audit.check(
        "one scoped common-Bohr child",
        all("EXP-000862" in value and "R-169 v1.4" in value and "CLOSED" in value for value in closed_sections),
        "one unique CLOSED scoped child",
        "one unique CLOSED scoped child",
        "formal",
    )
    audit.check(
        "legacy, interface and parents remain open",
        all(
            "EXP-000862" in value
            and "R-169 v1.4" in value
            and (
                "**Status:** OPEN" in value
                or (identifier == "C6-BCC-PREMISE-BLOCKED" and "**Discharge path:** BLOCKED" in value and "remain OPEN" in value)
            )
            for identifier, value in open_sections.items()
        ),
        "five unique OPEN annotations",
        "five unique OPEN annotations",
        "formal",
    )

    correction = negative_section(negatives, REUSED_NEGATIVES[0])
    correction_tokens = (
        "2026-08-14",
        "EXP-000862",
        "R-169 v1.4",
        "off-grid-confounded",
        "0 < BCC < FCC < HEX < LAM",
        "all four derivatives are nonzero",
        "LAM < HEX < FCC < BCC < 0",
        "full Reading-H Hartree",
        "physical-empty",
        "remains retired",
    )
    audit.check(
        "append-only B3 negative correction",
        all(token in correction for token in correction_tokens),
        [token for token in correction_tokens if token in correction],
        list(correction_tokens),
        "formal",
    )

    status = json.loads((REPO / "claims/B3-BCC-STRUCT/status.json").read_text(encoding="utf-8"))
    claim = (REPO / "claims/B3-BCC-STRUCT/claim.md").read_text(encoding="utf-8")
    status_blob = json.dumps(status, sort_keys=True)
    claim_tokens = (
        "EXP-000862",
        "off-grid-confounded",
        "0 < BCC < FCC < HEX < LAM",
        "all four derivatives are nonzero",
        "LAM < HEX < FCC < BCC < 0",
        "full Reading-H Hartree",
        "A1/P1",
        "physical-empty",
    )
    card_ok = (
        status.get("tier") == "T0"
        and status.get("lifecycle") == "REFUTED"
        and status.get("last_review") == "2026-08-14"
        and status.get("negative_result_ref") == REUSED_NEGATIVES[0]
        and all(token in status_blob and token in claim for token in claim_tokens)
    )
    audit.check("B3 claim-card correction", card_ok, {"lifecycle": status.get("lifecycle"), "tier": status.get("tier")}, "REFUTED/T0 with exact v1.4 correction", "formal")

    result_tokens = (
        "R-169 v1.4",
        "EXP-000862",
        "current proof-first authority",
        "R-169 v1.3 certificate",
        "prior proof-first authority",
        "No R-169 v1.4 PDF",
    )
    r169 = result_section(results, "R-169")
    audit.check("R-169 current authority", all(token in r169 for token in result_tokens), [token for token in result_tokens if token in r169], list(result_tokens), "formal")
    audit.check("roadmap and strategy linkage", all(token in roadmap and token in strategy_index for token in ("EXP-000862", "R-169 v1.4")), "both surfaces linked", "both surfaces linked", "formal")

    records = [record for record in parse_json_lines(REPO / "explorations/log.jsonl") if record.get("id") == "EXP-000862"]
    audit.check("unique EXP-000862", len(records) == 1, len(records), 1, "formal")
    record = records[0]
    topology_ok = (
        record.get("task_id") == "T-055"
        and record.get("verdict") == "advanced"
        and record.get("claim_ids") == manifest["claim_ids"]
        and record.get("gate_ids") == [*CLOSED, *OPEN]
        and record.get("related") == [{"id": "EXP-000860", "relation": "continues"}]
        and record.get("formal_refs", {}).get("results") == ["R-169"]
        and record.get("formal_refs", {}).get("negatives") == REUSED_NEGATIVES
        and record.get("formal_refs", {}).get("events") == []
    )
    audit.check("EXP exact topology", topology_ok, {key: record.get(key) for key in ("task_id", "verdict", "claim_ids", "gate_ids", "related", "formal_refs")}, "exact v1.4 exploration topology", "formal")

    events = parse_json_lines(REPO / "changelog/log.jsonl")
    contract = manifest["formal_integration"]
    matches = [(ordinal, event) for ordinal, event in enumerate(events, start=1) if event.get("id") == contract["event_id"]]
    unique_event = len(matches) == 1
    ordinal, event = matches[0] if unique_event else (None, {})
    exact_header = f"[{contract['event_title']}] - 2026-08-14"
    identity_ok = unique_event and ordinal == contract["event_ordinal"] and event.get("header") == exact_header
    audit.check("event 646 identity", identity_ok, {"total_events": len(events), "ordinal": ordinal, "id": event.get("id"), "header": event.get("header")}, {"ordinal": contract["event_ordinal"], "id": contract["event_id"], "header": exact_header}, "formal")
    linkage_ok = (
        event.get("claim_ids") == contract["event_claim_ids"]
        and event.get("keywords") == contract["event_keywords"]
        and event.get("notes") == contract["event_notes"]
        and event.get("scripts") == contract["event_scripts"]
        and event.get("neg_results") == []
    )
    audit.check("event exact linkage and no new negative", linkage_ok, {key: event.get(key) for key in ("claim_ids", "keywords", "notes", "scripts", "neg_results")}, "exact event linkage with empty neg_results", "formal")
    raw = event.get("raw", "")
    audit.check("event scope firewall", all(token in raw for token in contract["event_raw_tokens"]) and ".pdf" not in raw, [token for token in contract["event_raw_tokens"] if token in raw], "all scope tokens and no .pdf", "formal")

    theorem_map = json.loads((REPO / "governance/sector-a-theorem-map.json").read_text(encoding="utf-8"))
    priority = theorem_map["research_priority"]
    map_ok = (
        theorem_map.get("version") == contract["theorem_map_version"]
        and "EXP-000862" in priority.get("latest_cp1_checkpoint", "")
        and priority.get("closed_r169_v1_4_scoped_gates") == CLOSED
        and priority.get("open_r169_v1_4_interface_gates") == OPEN
        and priority.get("r169_v1_4_new_negatives") == []
        and priority.get("r169_v1_4_reused_negatives") == REUSED_NEGATIVES
    )
    audit.check("theorem map v1.39", map_ok, {"version": theorem_map.get("version"), "latest": priority.get("latest_cp1_checkpoint", "")[:60]}, "v1.39 exact arrays", "formal")

    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    matches = [task for task in tasks if task.get("id") == "T-055"]
    stable_task = len(matches) == 1 and matches[0].get("owner") and matches[0].get("note") and matches[0].get("gate") == "C6-BCC-PREMISE-BLOCKED"
    audit.check("stable T-055 routing", bool(stable_task), matches, "one owner/note/gate-stable T-055", "formal")

    legacy = json.loads(LEGACY_RECORD.read_text(encoding="utf-8"))
    expected_legacy = manifest["legacy_assessment"]
    legacy_blob = " ".join(json.dumps(legacy, sort_keys=True).split())
    legacy_scope_tokens = (
        "nine-source",
        "off-grid-confounded",
        "does not establish the sole cause",
        "different quadratic/Hartree owner",
        "not revalidate the broad lineage",
        "full Reading-H Hartree",
        "A1/P1",
        "physical-empty",
    )
    legacy_ok = (
        legacy.get("record_id") == expected_legacy["record_id"]
        and legacy.get("current_assessment") == "partially-reusable"
        and legacy.get("evidence_role") == "counterevidence"
        and legacy.get("source_ids") == expected_legacy["source_ids"]
        and legacy.get("pinned_source_ids_sha256") == expected_legacy["pinned_source_ids_sha256"]
        and legacy.get("claims") == expected_legacy["claims"]
        and legacy.get("gates") == expected_legacy["gates"]
        and legacy.get("status_axes") == {"extraction": "reviewed", "integration": "integrated", "preservation": "verified-copy", "revalidation": "pass"}
        and all(token in legacy_blob for token in legacy_scope_tokens)
    )
    audit.check("narrow legacy assessment", legacy_ok, {key: legacy.get(key) for key in ("record_id", "current_assessment", "evidence_role", "source_ids", "claims", "gates", "status_axes")}, "exact nine-source narrow assessment", "formal")

    legacy_check = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(REPO / "verification/scripts/legacy_research.py"), "build", "--check"],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    audit.check(
        "legacy assessment schema and generated views",
        legacy_check.returncode == 0,
        {"stdout": legacy_check.stdout[-800:], "stderr": legacy_check.stderr[-800:]},
        "legacy_research build --check exit 0",
        "formal",
    )

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
    with tempfile.TemporaryDirectory(prefix="r169-v14-") as directory:
        root = Path(directory)
        fresh_primary = run_child(PRIMARY, staged, root / "primary.json")
        fresh_independent = run_child(INDEPENDENT, staged, root / "independent.json")

    expected_mode = "staged" if staged else "formal"
    child_ok = (
        fresh_primary["verdict"] == fresh_independent["verdict"] == "PASS"
        and fresh_primary["mode"] == fresh_independent["mode"] == expected_mode
    )
    audit.check("child modes and verdicts", child_ok, {"primary": fresh_primary["mode"], "independent": fresh_independent["mode"]}, f"matching PASS {expected_mode}", "cross")

    common_keys = (
        "moments",
        "polynomial_coefficients",
        "fixed_values",
        "fixed_derivatives",
        "fixed_order",
        "radial_minimizers",
        "radial_minimum_energies",
        "root_brackets_millionths",
        "energy_brackets_millionths",
        "radial_order",
        "all_radial_energies_negative",
        "all_radial_minima_above_cap_marker",
        "amplitude_crosswalk",
        "hex_equal_shell",
        "hex_pair_angles",
        "offgrid_transcendence_form",
        "standard_cubic_torus_valuation_obstruction",
        "math396_grid_N",
        "shell_ratio_form",
    )
    agreement = {key: (fresh_primary["derived"].get(key), fresh_independent["derived"].get(key)) for key in common_keys}
    audit.check("independent exact agreement", all(left == right for left, right in agreement.values()), agreement, "all common exact fields agree", "cross")

    owner = manifest["owner_definition"]
    boundary = manifest["no_overclaim"]
    scope_ok = (
        "reconstructed corrected" in owner["construction"]
        and "not the obsolete Math396 coefficient table" in owner["provenance_firewall"]
        and "not the A1 side-16" in boundary
        and "No R-169 v1.4 PDF" in boundary
        and manifest["new_negative_ids"] == []
    )
    audit.check("owner and no-overclaim firewalls", scope_ok, scope_ok, True, "scope")

    hash_ok = (
        fresh_primary["source_hash"] == normalized_sha256(PRIMARY)
        and fresh_independent["source_hash"] == normalized_sha256(INDEPENDENT)
        and fresh_primary["manifest_hash"] == fresh_independent["manifest_hash"] == normalized_sha256(MANIFEST)
        and fresh_primary["certificate_hash"] == fresh_independent["certificate_hash"] == normalized_sha256(CERTIFICATE)
    )
    audit.check("owner and shared hashes", hash_ok, "all hashes current" if hash_ok else "hash drift", "all hashes current", "cross")
    source_discipline(audit)

    if staged:
        staged_audit(audit, manifest)
    else:
        formal_audit(audit, manifest, fresh_primary, fresh_independent)

    return {
        "schema": "tect/pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split-integrated/1.0",
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
