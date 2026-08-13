#!/usr/bin/env python3
"""Integrated verifier for the R-167 v3.4 route-split package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-dffr-hilbert-schmidt-uniformity-and-yarotskii-gap-route-split"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_dffr_hilbert_schmidt_uniformity_and_yarotskii_gap_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_dffr_hilbert_schmidt_uniformity_and_yarotskii_gap_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL = {
    "gates": REPO / "claims/GATES.md",
    "results": REPO / "RESULTS-LEDGER.md",
    "negatives": REPO / "negative-results/registry.md",
    "explorations": REPO / "explorations/log.jsonl",
    "changelog": REPO / "changelog/log.jsonl",
    "todo": REPO / "todo/todo.json",
    "roadmap": REPO / "ROADMAP.md",
    "strategy": REPO / "strategy/INDEX.md",
    "theorem_map": REPO / "governance/sector-a-theorem-map.json",
    "proof_map_md": REPO / "theory/proof-evidence-map.md",
    "proof_map_json": REPO / "verification/proof-evidence-map.json",
}
EXPECTED_CLOSED = [
    "PA-CP1-ST8-Q3LOCK-CONDITIONAL-M-UNIFORM-DFFR-HILBERT-SCHMIDT-SIMULTANEOUS-ENTRY-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-FIXED-RITZ-YAROTSKII-RELATIVE-SPLIT-AND-CONDITIONAL-PHASEWISE-GNS-GAP-REDUCTION",
]
EXPECTED_NEGATIVE = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-UNIFORM-RELATIVE-FORM-AND-OPERATOR-BLOCK-BOUNDS-AUTOMATIC-M-UNIFORM-DFFR-HILBERT-SCHMIDT-ENTRY"
]
EXPECTED_REUSED = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-DEFECT-AUTOMATIC-N-DEPENDENT-TWO-PHASE-RADIUS-ENTRY",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP",
]
EXPECTED_HISTORICAL_OPEN = ["PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION"]
EXPECTED_PARENTS = [
    "PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
EXPECTED_V33_CLOSED = [
    "PA-CP1-ST8-Q3LOCK-FIXED-RITZ-DFFR-TWO-LEVEL-QPS-LARGE-N-ZERO-SOURCE-TWO-PHASE-AND-GROUND-LIMIT"
]
EVENT_TITLE = "R-167 v3.4 DFFR Hilbert-Schmidt uniformity and conditional Yarotskii gap reductions"
EVENT_HEADER = f"[{EVENT_TITLE}] - 2026-08-13"
EVENT_ID = "20260813-r-167-v3-4-dffr-hilbert-schmidt-uniformity-and"
EVENT_KEYWORDS = [
    "DFFR-Hilbert-Schmidt-uniformity",
    "EXP-000838",
    "R-167-v3.4",
    "conditional-simultaneous-entry",
    "conditional-Yarotskii-GNS-gap",
    "exact-dimension-obstruction",
    "no-full-oscillator-passage",
    "no-parent-closure",
]


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


def execute_child(path: Path, staged: bool) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-v34-") as temporary:
        output = Path(temporary) / "result.json"
        command = [sys.executable, "-X", "utf8", str(path), "--output", str(output)]
        if staged:
            command.append("--staged")
        completed = subprocess.run(
            command,
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        if completed.returncode != 0:
            raise AssertionError(f"child failed {path.name}:\n{completed.stdout}\n{completed.stderr}")
        return json.loads(output.read_text(encoding="utf-8"))


def proof_core(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "package_id": payload.get("package_id"),
        "verdict": payload.get("verdict"),
        "derived": payload.get("derived"),
        "assertions": [row for row in payload.get("assertions", []) if row.get("group") != "formal"],
        "source_hashes": payload.get("source_hashes"),
    }


def markdown_h3_section(text: str, identifier: str) -> str:
    pattern = re.compile(rf"^### \*\*{re.escape(identifier)}\*\*\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        return ""
    following = re.search(r"^### \*\*", text[matches[0].end():], re.MULTILINE)
    end = matches[0].end() + following.start() if following else len(text)
    return text[matches[0].start():end]


def markdown_result_section(text: str, identifier: str) -> str:
    pattern = re.compile(rf"^### {re.escape(identifier)}\s+--.*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        return ""
    following = re.search(r"^### ", text[matches[0].end():], re.MULTILINE)
    end = matches[0].end() + following.start() if following else len(text)
    return text[matches[0].start():end]


def formal_counts(texts: dict[str, str]) -> dict[str, int]:
    result_rows = re.findall(r"^\| \[(R-\d+)\]\(#[^)]+\) \| .*? \| .*? \|$", texts["results"], re.MULTILINE)
    gate_rows = re.findall(r"^#{2,4}\s+\*\*([A-Z0-9][A-Z0-9-]+)\*\*\s*$", texts["gates"], re.MULTILINE)
    negative_rows = re.findall(
        r"^\| \[((?:R|F|NG|AUDIT)-[A-Za-z0-9-]+)\]\(#[^)]+\) \| .*? \| .*? \|$",
        texts["negatives"],
        re.MULTILINE,
    )
    claim_count = sum(1 for path in (REPO / "claims").glob("*/status.json") if not path.parent.name.startswith("_"))
    task_count = len(json.loads(texts["todo"]).get("tasks", []))
    catalog_total = int(json.loads((REPO / "verification/catalog/index.json").read_text(encoding="utf-8"))["total"])
    return {
        "claims": claim_count,
        "results": len(result_rows),
        "gates": len(gate_rows),
        "negatives": len(negative_rows),
        "explorations": len([line for line in texts["explorations"].splitlines() if line.strip()]),
        "events": len([line for line in texts["changelog"].splitlines() if line.strip()]),
        "tasks": task_count,
        "catalog": catalog_total,
    }


def ast_imports_and_dynamic(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec", "compile"}:
                dynamic.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "exec_module", "load_module"}:
                dynamic.append(node.func.attr)
    return {"imports": sorted(imports), "dynamic": dynamic}


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    normalized_certificate = " ".join(certificate.split())
    primary = execute_child(PRIMARY, staged)
    independent = execute_child(INDEPENDENT, staged)
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["schema"] == "tect/pre-a-q3lock-dffr-hs-uniformity-yarotskii-gap/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.4"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000838"
        and manifest["prior_exploration_id"] == "EXP-000837"
        and manifest["claim_bearing"] is False,
        (manifest["schema"], manifest["package_id"], manifest["version"], manifest["date"]),
        ("exact schema", SLUG, "R-167 v3.4", "2026-08-13"),
        "manifest",
    )
    audit.check(
        "manifest exact authority topology",
        manifest["closed_gate_ids"] == EXPECTED_CLOSED
        and manifest["negative_ids"] == EXPECTED_NEGATIVE
        and manifest["reused_negative_ids"] == EXPECTED_REUSED
        and manifest["historical_open_gate_ids"] == EXPECTED_HISTORICAL_OPEN
        and manifest["open_parent_gate_ids"] == EXPECTED_PARENTS,
        (
            manifest["closed_gate_ids"],
            manifest["negative_ids"],
            manifest["reused_negative_ids"],
            manifest["historical_open_gate_ids"],
            manifest["open_parent_gate_ids"],
        ),
        (EXPECTED_CLOSED, EXPECTED_NEGATIVE, EXPECTED_REUSED, EXPECTED_HISTORICAL_OPEN, EXPECTED_PARENTS),
        "manifest",
    )
    expected_paths = [
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in (PRIMARY, INDEPENDENT, SCRIPT, PRIMARY_RESULT, INDEPENDENT_RESULT, DEFAULT_OUTPUT)
    ]
    actual_paths = [
        manifest["verification"][key]
        for key in (
            "primary_script",
            "independent_script",
            "integrated_script",
            "primary_result",
            "independent_result",
            "integrated_result",
        )
    ]
    audit.check("manifest exact verification paths", actual_paths == expected_paths, actual_paths, expected_paths, "manifest")
    audit.check(
        "common onset and conditional theorem constants",
        "N_ref independent of M" in manifest["conditional_simultaneous_dffr_entry"]["family"]
        and "N>=N_ref" in manifest["conditional_simultaneous_dffr_entry"]["conclusion"]
        and "hypotheses, not consequences" in manifest["conditional_simultaneous_dffr_entry"]["uniform_theorem_constants"],
        manifest["conditional_simultaneous_dffr_entry"],
        "common onset, HS bounds and common theorem thresholds are hypotheses",
        "manifest",
    )
    audit.check(
        "proof-first lifecycle",
        manifest["checkpoint_synthesis"]
        == {
            "status": "DEFERRED UNTIL THE NEXT LOGICAL GATE-LEVEL CHECKPOINT",
            "pdf_issued": False,
            "workflow": "Proof-first manifest, certificate and three executable verifiers only. No v3.4 PDF is issued.",
        },
        manifest["checkpoint_synthesis"],
        "exact deferred no-PDF lifecycle",
        "manifest",
    )

    for label, payload, owner, expected_total in (
        ("primary", primary, PRIMARY, 22 if staged else 23),
        ("independent", independent, INDEPENDENT, 19 if staged else 20),
    ):
        rows = payload.get("assertions", [])
        names = [row.get("name") for row in rows]
        audit.check(
            f"{label} schema and total",
            payload.get("schema") == "tect/verification-run/1.0"
            and payload.get("package_id") == SLUG
            and payload.get("verdict") == "PASS"
            and payload.get("summary", {}).get("total") == expected_total,
            payload.get("summary"),
            expected_total,
            "children",
        )
        audit.check(
            f"{label} assertion rows complete",
            len(rows) == expected_total
            and len(names) == len(set(names))
            and all(row.get("status") == "PASS" for row in rows),
            (len(rows), len(set(names))),
            (expected_total, expected_total),
            "children",
        )
        owner_key = str(owner.relative_to(REPO)).replace("\\", "/")
        audit.check(
            f"{label} owner freshness",
            payload["source_hashes"].get(owner_key) == normalized_sha256(owner),
            payload["source_hashes"].get(owner_key),
            normalized_sha256(owner),
            "children",
        )

    audit.check(
        "independent exact cross derivation",
        primary["derived"] == independent["derived"] == manifest["exact_fixture"],
        (primary["derived"], independent["derived"]),
        manifest["exact_fixture"],
        "cross",
    )
    firewall = ast_imports_and_dynamic(INDEPENDENT)
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "math",
        "os",
        "tempfile",
        "fractions",
        "pathlib",
        "typing",
    }
    audit.check(
        "independent stdlib AST firewall",
        set(firewall["imports"]) <= allowed and not firewall["dynamic"],
        firewall,
        "stdlib allowlist and no dynamic execution",
        "independence",
    )
    audit.check(
        "independent source distinct",
        normalized_sha256(PRIMARY) != normalized_sha256(INDEPENDENT),
        normalized_sha256(INDEPENDENT),
        "different from primary",
        "independence",
    )
    source_text = PRIMARY.read_text(encoding="utf-8") + INDEPENDENT.read_text(encoding="utf-8")
    masked_literals = (
        '"K_N": "26"',
        '"paired": "3*sqrt(13)/260"',
        '"high_high_entry": "4/13"',
        '"epsilon": "3/1000"',
    )
    audit.check(
        "derived-number hardcode masking firewall",
        all(token not in source_text for token in masked_literals),
        [token for token in masked_literals if token in source_text],
        [],
        "independence",
    )
    theorem_tokens = (
        "Conditional simultaneous DFFR entry",
        "actual Hilbert--Schmidt constants in DFFR (5.21)",
        "one integer `N_ref` independent of `M`",
        "Exact Hilbert--Schmidt multiplicity obstruction",
        "a=alpha+epsilon/g",
        "b=epsilon+2 sqrt[epsilon(alpha L+epsilon)]",
        "Conditional fixed-Ritz Yarotskii phasewise-gap reduction",
        "are not automatically the Yarotskii branches",
    )
    audit.check(
        "certificate exact theorem contract",
        all(token in normalized_certificate for token in theorem_tokens),
        [token for token in theorem_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )
    boundary_tokens = (
        "no actual M-uniform DFFR entry for Q3",
        "no Yarotskii rectangle",
        "no DFFR/Yarotskii branch identity",
        "no full-oscillator phase passage",
        "All five active parent gates remain OPEN",
        EXPECTED_HISTORICAL_OPEN[0],
        "No v3.4 PDF is issued",
    )
    audit.check(
        "certificate exact no-overclaim contract",
        all(token in normalized_certificate for token in boundary_tokens),
        [token for token in boundary_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )

    stored_status: dict[str, str] = {}
    for label, path, fresh in (("primary", PRIMARY_RESULT, primary), ("independent", INDEPENDENT_RESULT, independent)):
        if path.exists():
            stored = json.loads(path.read_text(encoding="utf-8"))
            same = stored == fresh if not staged else proof_core(stored) == proof_core(fresh)
            stored_status[label] = "fresh" if same else "stale"
            audit.check(f"stored {label} freshness", same, stored_status[label], "fresh", "stored")
        elif staged:
            stored_status[label] = "absent-staged"
            audit.check(f"stored {label} staged lifecycle", True, stored_status[label], "allowed", "stored")
        else:
            raise AssertionError(f"stored result missing: {path}")

    if not staged:
        texts = {name: path.read_text(encoding="utf-8") for name, path in FORMAL.items()}
        records = [
            json.loads(line)
            for line in texts["explorations"].splitlines()
            if line.strip() and json.loads(line).get("id") == "EXP-000838"
        ]
        expected_gate_links = EXPECTED_CLOSED + EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS
        expected_negative_links = EXPECTED_NEGATIVE + EXPECTED_REUSED
        exploration_ok = (
            len(records) == 1
            and records[0].get("task_id") == "T-054"
            and records[0].get("verdict") == "advanced"
            and records[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and records[0].get("related") == [{"id": "EXP-000837", "relation": "continues"}]
            and records[0].get("gate_ids") == expected_gate_links
            and records[0].get("formal_refs", {}).get("negatives") == expected_negative_links
            and records[0].get("formal_refs", {}).get("results") == ["R-167"]
            and all(".pdf" not in ref and ".tex.txt" not in ref for ref in records[0].get("evidence_refs", []))
        )
        audit.check("EXP-000838 exact continuation", exploration_ok, records, "one exact proof-first record", "formal")

        child_sections = [markdown_h3_section(texts["gates"], gate) for gate in EXPECTED_CLOSED]
        child_ok = all(
            section
            and "**Status:** CLOSED" in section
            and "EXP-000838 / R-167 v3.4" in section
            and "CONDITIONAL" in section.upper()
            for section in child_sections
        )
        audit.check("two exact conditional CLOSED children", child_ok, [s[:300] for s in child_sections], "unique sections", "formal")

        open_sections = [markdown_h3_section(texts["gates"], gate) for gate in EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS]
        audit.check(
            "historical beta gate and five parents remain OPEN",
            all(
                section
                and re.search(r"^\*\*Status:\*\*.*\bOPEN\b", section, re.MULTILINE)
                and "EXP-000838 / R-167 v3.4" in section
                for section in open_sections
            ),
            [bool(section) for section in open_sections],
            [True] * 6,
            "formal",
        )

        negative_section = markdown_result_section(texts["negatives"], EXPECTED_NEGATIVE[0])
        negative_tokens = ("rank R_m=m^2", "operator norm", "Hilbert--Schmidt", "2m/(kappa+N^2)")
        audit.check(
            "new exact HS negative registered",
            bool(negative_section) and all(token in " ".join(negative_section.split()) for token in negative_tokens),
            negative_section[:500],
            negative_tokens,
            "formal",
        )
        audit.check(
            "three reused negatives preserved",
            all(markdown_result_section(texts["negatives"], identifier) for identifier in EXPECTED_REUSED),
            EXPECTED_REUSED,
            "all unique existing sections",
            "formal",
        )

        result_section = markdown_result_section(texts["results"], "R-167")
        result_ok = all(
            token in result_section
            for token in (
                "EXP-000838",
                "R-167 v3.4",
                "current proof-first authority",
                "conditional M-uniform DFFR",
                "Hilbert--Schmidt",
                "conditional Yarotskii",
                "R-167 v3.3 certificate",
                "R-167 v2.9 certificate",
                "remain the prior proof-first authority",
                "No v3.4 PDF",
            )
        )
        audit.check("R-167 v3.4 current authority", result_ok, "result tokens", "bounded R-167 section", "formal")

        todo_data = json.loads(texts["todo"])
        todo_records = [item for item in todo_data.get("tasks", []) if item.get("id") == "T-054"]
        audit.check(
            "T-054 remains in progress with v3.4",
            len(todo_records) == 1
            and todo_records[0].get("status") == "in_progress"
            and "EXP-000838" in todo_records[0].get("note", "")
            and "remain OPEN" in todo_records[0].get("note", ""),
            todo_records,
            "one linked in-progress task",
            "formal",
        )

        theorem_map = json.loads(texts["theorem_map"])
        research = theorem_map.get("research_priority", {})
        linkage_ok = (
            "EXP-000838" in texts["roadmap"]
            and "EXP-000838" in texts["strategy"]
            and theorem_map.get("version") == "1.26.0"
            and "EXP-000838" in research.get("latest_cp1_checkpoint", "")
            and research.get("closed_v3_4_scoped_gates") == EXPECTED_CLOSED
            and research.get("closed_v3_3_scoped_gates") == EXPECTED_V33_CLOSED
            and research.get("v3_4_exact_negative") == EXPECTED_NEGATIVE[0]
        )
        audit.check(
            "ROADMAP strategy theorem-map linkage",
            linkage_ok,
            (
                theorem_map.get("version"),
                research.get("closed_v3_4_scoped_gates"),
                research.get("closed_v3_3_scoped_gates"),
                research.get("v3_4_exact_negative"),
            ),
            ("1.26.0", EXPECTED_CLOSED, EXPECTED_V33_CLOSED, EXPECTED_NEGATIVE[0]),
            "formal",
        )

        events = [json.loads(line) for line in texts["changelog"].splitlines() if line.strip()]
        event_candidates = [
            event
            for event in events
            if "EXP-000838" in event.get("claim_ids", []) or "R-167-v3.4" in event.get("keywords", [])
        ]
        expected_notes = [
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
            "claims/GATES.md",
            "RESULTS-LEDGER.md",
            "negative-results/registry.md",
        ]
        event_ok = (
            len(events) == manifest["formal_integration_contract"]["event_id"] == 630
            and len(event_candidates) == 1
            and event_candidates[0] is events[-1]
            and event_candidates[0].get("id") == EVENT_ID
            and event_candidates[0].get("date") == "2026-08-13"
            and event_candidates[0].get("header") == EVENT_HEADER
            and event_candidates[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE", "EXP-000838", "R-167"]
            and event_candidates[0].get("keywords") == sorted(EVENT_KEYWORDS)
            and event_candidates[0].get("neg_results") == EXPECTED_NEGATIVE
            and event_candidates[0].get("notes") == expected_notes
            and event_candidates[0].get("scripts") == expected_paths[:3]
            and event_candidates[0].get("raw", "").startswith(f"## {EVENT_HEADER}\n\n")
            and ".pdf" not in event_candidates[0].get("raw", "")
            and ".tex.txt" not in event_candidates[0].get("raw", "")
            and all(
                token in event_candidates[0].get("raw", "")
                for token in (
                    "conditional M-uniform DFFR",
                    "Hilbert--Schmidt multiplicity obstruction",
                    "conditional fixed-Ritz Yarotskii",
                    "DFFR and Yarotskii branches are not identified",
                    "All five active parent gates remain OPEN",
                    "No v3.4 PDF is issued",
                )
            )
        )
        audit.check("unique proof-first event 630", event_ok, event_candidates, "one exact no-PDF event", "formal")

        generated_ok = all("EXP-000838" in texts[key] for key in ("proof_map_md", "proof_map_json"))
        audit.check("generated proof-evidence linkage", generated_ok, generated_ok, True, "formal")
        c6 = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
        c6_ok = (
            c6.get("tier") == "T1"
            and c6.get("lifecycle") == "ACTIVE"
            and c6.get("evidence_grade") == ["CONDITIONAL"]
            and c6.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"]
        )
        audit.check("C6 unchanged-tier firewall", c6_ok, c6, "T1 ACTIVE CONDITIONAL blocked", "formal")

        actual_counts = formal_counts(texts)
        expected_counts = manifest["formal_integration_contract"]["expected_post_formal_counts"]
        noncatalog_keys = tuple(key for key in expected_counts if key != "catalog")
        catalog_expected = expected_counts["catalog"]
        catalog_ok = (
            DEFAULT_OUTPUT.exists() and actual_counts["catalog"] == catalog_expected
        ) or (
            not DEFAULT_OUTPUT.exists()
            and actual_counts["catalog"] == catalog_expected - 1
            and actual_counts["catalog"] + 1 == catalog_expected
        )
        counts_ok = all(actual_counts[key] == expected_counts[key] for key in noncatalog_keys) and catalog_ok
        audit.check(
            "exact post-formal authority counts",
            counts_ok,
            {
                "actual": actual_counts,
                "integrated_output_exists": DEFAULT_OUTPUT.exists(),
                "catalog_after_this_output": actual_counts["catalog"] + (0 if DEFAULT_OUTPUT.exists() else 1),
            },
            expected_counts,
            "formal",
        )

    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": primary["derived"] | {"stored": stored_status},
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.4 INTEGRATED PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
