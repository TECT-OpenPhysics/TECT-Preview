#!/usr/bin/env python3
"""Cross-audit and formally integrate the R-167 v4.1 GNS reduction.

The primary SymPy lane and independent stdlib/Fraction lane recompute the same
energy, form-core, parity, overlap, and source-gap fixtures. This verifier also
checks the EXP-000845/event-637 topology, lifecycle, hashes, and frozen counts.
"""

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


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-categorical-ground-bandlimited-gns-poincare-route-split"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_categorical_ground_bandlimited_gns_poincare_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_categorical_ground_bandlimited_gns_poincare_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

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
    "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-CATEGORICAL-GROUND-BANDLIMITED-GNS-ENERGY-FORM-CORE-AND-PARITY-POINCARE-REDUCTION"
]
EXPECTED_NEW_NEGATIVES = [
    "NG-2026-08-14-PRE-A-ST8-Q3LOCK-MESOSCOPIC-SOURCE-FULL-FINITE-GAP-AUTOMATIC-UNIFORM-POINCARE-TRANSFER"
]
EXPECTED_REUSED = [
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP"
]
EXPECTED_HISTORICAL_OPEN = [
    "PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION",
    "PA-CP1-ST8-Q3LOCK-DLR-TO-COMMON-ALPHA-KMS-IDENTIFICATION",
]
EXPECTED_PARENTS = [
    "PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
EVENT_TITLE = "R-167 v4.1 categorical ground bandlimited GNS Poincare route split"
EVENT_HEADER = f"[{EVENT_TITLE}] - 2026-08-14"
EVENT_ID = "20260814-r-167-v4-1-categorical-ground-bandlimited-gns-p"
EVENT_KEYWORDS = [
    "EXP-000845",
    "R-167-v4.1",
    "bandlimited-form-core",
    "categorical-ground",
    "finite-source-gap-collapse",
    "gns-poincare",
    "parity-gap-equality",
    "route-no-go",
]

# These derived strings may occur only inside labelled test-oracle assignments.
TEST_ORACLE_DERIVED_LITERALS = {
    "1/128",
    "3072",
    "9216",
    "13/36",
    "55/36",
    "55/13",
    "8/9",
    "24/25",
    "14/25",
    "49/625",
    "49/125",
}


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
    with tempfile.TemporaryDirectory(prefix="tect-v41-") as temporary:
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
        "derived": payload.get("derived"),
        "assertions": [row for row in payload.get("assertions", []) if row.get("group") != "formal"],
        "source_hashes": payload.get("source_hashes"),
    }


def ast_firewall(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    dynamic: list[str] = []
    forbidden_calls: list[str] = []
    complex_literals: list[str] = []
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
            if isinstance(node.func, ast.Name) and node.func.id in {"float", "complex"}:
                forbidden_calls.append(node.func.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, complex):
            complex_literals.append(repr(node.value))
    return {
        "imports": sorted(imports),
        "dynamic": dynamic,
        "forbidden_calls": forbidden_calls,
        "complex_literals": complex_literals,
    }


def oracle_literal_violations(path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    spans: list[tuple[int, int]] = []
    for node in tree.body:
        names: list[str] = []
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [target.id for target in targets if isinstance(target, ast.Name)]
        if any(name.startswith("TEST_ORACLE_") for name in names):
            spans.append((node.lineno, node.end_lineno or node.lineno))
    violations: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in TEST_ORACLE_DERIVED_LITERALS:
            if not any(start <= node.lineno <= end for start, end in spans):
                violations.append({"line": node.lineno, "value": node.value})
    return violations


def markdown_h3_section(text: str, identifier: str) -> str:
    pattern = re.compile(rf"^### \*\*{re.escape(identifier)}\*\*\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        return ""
    following = re.search(r"^### \*\*", text[matches[0].end() :], re.MULTILINE)
    end = matches[0].end() + following.start() if following else len(text)
    return text[matches[0].start() : end]


def markdown_result_section(text: str, identifier: str) -> str:
    pattern = re.compile(rf"^### {re.escape(identifier)}\s+--.*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        return ""
    following = re.search(r"^### ", text[matches[0].end() :], re.MULTILINE)
    end = matches[0].end() + following.start() if following else len(text)
    return text[matches[0].start() : end]


def formal_counts(texts: dict[str, str]) -> dict[str, int]:
    results = re.findall(r"^\| \[(R-\d+)\]\(#[^)]+\) \| .*? \| .*? \|$", texts["results"], re.MULTILINE)
    gates = re.findall(r"^#{2,4}\s+\*\*([A-Z0-9][A-Z0-9-]+)\*\*\s*$", texts["gates"], re.MULTILINE)
    negatives = re.findall(
        r"^\| \[((?:R|F|NG|AUDIT)-[A-Za-z0-9-]+)\]\(#[^)]+\) \| .*? \| .*? \|$",
        texts["negatives"],
        re.MULTILINE,
    )
    claims = sum(1 for path in (REPO / "claims").glob("*/status.json") if not path.parent.name.startswith("_"))
    tasks = len(json.loads(texts["todo"]).get("tasks", []))
    catalog = int(json.loads((REPO / "verification/catalog/index.json").read_text(encoding="utf-8"))["total"])
    return {
        "claims": claims,
        "results": len(results),
        "gates": len(gates),
        "negatives": len(negatives),
        "explorations": len([line for line in texts["explorations"].splitlines() if line.strip()]),
        "events": len([line for line in texts["changelog"].splitlines() if line.strip()]),
        "tasks": tasks,
        "catalog": catalog,
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    primary = execute_child(PRIMARY, staged)
    independent = execute_child(INDEPENDENT, staged)
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["schema"] == "tect/pre-a-q3lock-categorical-ground-bandlimited-gns-poincare-route-split/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v4.1"
        and manifest["date"] == "2026-08-14"
        and manifest["exploration_id"] == "EXP-000845"
        and manifest["prior_exploration_id"] == "EXP-000844"
        and manifest["claim_bearing"] is False,
        (manifest["schema"], manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        ("exact schema", SLUG, "R-167 v4.1", "EXP-000845"),
        "manifest",
    )
    audit.check(
        "manifest authority topology",
        manifest["closed_gate_ids"] == EXPECTED_CLOSED
        and manifest["negative_ids"] == EXPECTED_NEW_NEGATIVES
        and manifest["reused_negative_ids"] == EXPECTED_REUSED
        and manifest["historical_open_gate_ids"] == EXPECTED_HISTORICAL_OPEN
        and manifest["open_parent_gate_ids"] == EXPECTED_PARENTS,
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]),
        (EXPECTED_CLOSED, EXPECTED_NEW_NEGATIVES, EXPECTED_REUSED),
        "manifest",
    )
    contract = manifest["formal_integration_contract"]
    audit.check(
        "event and count contract",
        contract["event_ordinal"] == 637
        and contract["event_id"] == EVENT_ID
        and contract["event_title"] == EVENT_TITLE
        and contract["event_keywords"] == EVENT_KEYWORDS
        and contract["theorem_map_version"] == "1.33.0"
        and contract["expected_post_formal_counts"] == {
            "claims": 49,
            "results": 168,
            "gates": 195,
            "negatives": 367,
            "explorations": 845,
            "events": 637,
            "tasks": 54,
            "catalog": 3963,
        },
        contract,
        "frozen event 637, map 1.33.0 and counts",
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
    audit.check("manifest verification paths", actual_paths == expected_paths, actual_paths, expected_paths, "manifest")
    audit.check(
        "proof-first lifecycle and no-overclaim",
        manifest["checkpoint_synthesis"]["pdf_issued"] is False
        and "no positive D_bl Poincare constant" in manifest["no_overclaim"]
        and "global L-dependent branch-switching obstruction" in manifest["no_overclaim"]
        and "not a phasewise target-gap no-go" in manifest["no_overclaim"]
        and "remain OPEN" in manifest["no_overclaim"],
        "scoped no-PDF T0 reduction",
        "scoped no-PDF T0 reduction",
        "manifest",
    )

    for label, payload, owner, staged_total in (
        ("primary", primary, PRIMARY, 16),
        ("independent", independent, INDEPENDENT, 13),
    ):
        expected_total = staged_total if staged else staged_total + 1
        rows = payload["assertions"]
        audit.check(
            f"{label} total and PASS",
            payload["summary"]["status"] == "PASS"
            and payload["summary"]["passed"] == expected_total
            and len(rows) == expected_total
            and all(row["status"] == "PASS" for row in rows),
            payload["summary"],
            expected_total,
            "children",
        )
        owner_key = str(owner.relative_to(REPO)).replace("\\", "/")
        audit.check(
            f"{label} owner freshness",
            payload["source_hashes"][owner_key] == normalized_sha256(owner),
            payload["source_hashes"][owner_key],
            normalized_sha256(owner),
            "children",
        )

    audit.check(
        "independent exact cross derivation",
        primary["derived"] == independent["derived"],
        primary["derived"],
        independent["derived"],
        "cross",
    )
    independent_firewall = ast_firewall(INDEPENDENT)
    allowed_independent = {
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
        "independent stdlib exact AST firewall",
        set(independent_firewall["imports"]) <= allowed_independent
        and not independent_firewall["dynamic"]
        and not independent_firewall["forbidden_calls"]
        and not independent_firewall["complex_literals"],
        independent_firewall,
        "stdlib allowlist/no dynamic/no float or complex",
        "independence",
    )
    primary_firewall = ast_firewall(PRIMARY)
    audit.check(
        "primary exact-arithmetic AST firewall",
        not primary_firewall["dynamic"]
        and not primary_firewall["forbidden_calls"]
        and not primary_firewall["complex_literals"],
        primary_firewall,
        "no dynamic/no float or complex",
        "independence",
    )
    oracle_violations = {
        "primary": oracle_literal_violations(PRIMARY),
        "independent": oracle_literal_violations(INDEPENDENT),
    }
    audit.check(
        "derived literals confined to test-oracle ledgers",
        not oracle_violations["primary"] and not oracle_violations["independent"],
        oracle_violations,
        {"primary": [], "independent": []},
        "independence",
    )
    audit.check(
        "independent source distinct",
        normalized_sha256(PRIMARY) != normalized_sha256(INDEPENDENT),
        normalized_sha256(INDEPENDENT),
        "different from primary",
        "independence",
    )
    audit.check(
        "certificate theorem and Fourier contract",
        all(
            token in certificate
            for token in (
                "hat g(nu)=int_R exp(+i nu t)g(t)dt",
                "hat g_R(H/hbar)",
                "closure_form(C_D)",
                "infimum over the empty orthogonal complement",
                "Delta_-^P=Delta_+^P",
                "32 sqrt(B_a)/(r_w^2 rho_*)",
                "No interchange is permitted",
                "does not refute a positive phasewise GNS gap",
                "No v4.1 PDF is issued",
            )
        ),
        "required tokens present",
        "required tokens present",
        "certificate",
    )

    stored_status: dict[str, str] = {}
    for label, path, fresh in (
        ("primary", PRIMARY_RESULT, primary),
        ("independent", INDEPENDENT_RESULT, independent),
    ):
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
            if line.strip() and json.loads(line).get("id") == "EXP-000845"
        ]
        expected_gate_links = EXPECTED_CLOSED + EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS
        exploration_ok = (
            len(records) == 1
            and records[0].get("task_id") == "T-054"
            and records[0].get("verdict") == "advanced"
            and records[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and records[0].get("related") == [{"id": "EXP-000844", "relation": "continues"}]
            and records[0].get("gate_ids") == expected_gate_links
            and records[0].get("formal_refs", {}).get("negatives") == EXPECTED_NEW_NEGATIVES + EXPECTED_REUSED
            and records[0].get("formal_refs", {}).get("results") == ["R-167"]
        )
        audit.check("EXP-000845 exact continuation", exploration_ok, records, "one exact proof-first record", "formal")

        child = markdown_h3_section(texts["gates"], EXPECTED_CLOSED[0])
        audit.check(
            "one exact scoped CLOSED child",
            bool(child) and "**Status:** CLOSED" in child and "EXP-000845 / R-167 v4.1" in child,
            child[:500],
            "unique closed section",
            "formal",
        )
        open_sections = [
            markdown_h3_section(texts["gates"], gate) for gate in EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS
        ]
        audit.check(
            "two historical gates and five parents remain OPEN",
            all(
                section
                and re.search(r"^\*\*Status:\*\*.*\bOPEN\b", section, re.MULTILINE)
                and "EXP-000845 / R-167 v4.1" in section
                for section in open_sections
            ),
            [bool(section) for section in open_sections],
            [True] * 7,
            "formal",
        )
        audit.check(
            "new and reused negatives exact",
            bool(markdown_result_section(texts["negatives"], EXPECTED_NEW_NEGATIVES[0]))
            and bool(markdown_result_section(texts["negatives"], EXPECTED_REUSED[0])),
            EXPECTED_NEW_NEGATIVES + EXPECTED_REUSED,
            "unique sections",
            "formal",
        )

        result = markdown_result_section(texts["results"], "R-167")
        audit.check(
            "R-167 v4.1 current authority",
            all(
                token in result
                for token in (
                    "EXP-000845",
                    "R-167 v4.1",
                    "current proof-first authority",
                    "R-167 v4.0 certificate",
                    "prior proof-first authority",
                    "No v4.1 PDF",
                )
            ),
            "result tokens",
            "bounded R-167 section",
            "formal",
        )
        todo = [item for item in json.loads(texts["todo"]).get("tasks", []) if item.get("id") == "T-054"]
        audit.check(
            "T-054 in progress with v4.1",
            len(todo) == 1
            and todo[0].get("status") == "in_progress"
            and "EXP-000845" in todo[0].get("note", "")
            and "remain OPEN" in todo[0].get("note", ""),
            todo,
            "one linked in-progress task",
            "formal",
        )
        theorem_map = json.loads(texts["theorem_map"])
        research = theorem_map.get("research_priority", {})
        audit.check(
            "ROADMAP strategy theorem-map linkage",
            "EXP-000845" in texts["roadmap"]
            and "EXP-000845" in texts["strategy"]
            and theorem_map.get("version") == "1.33.0"
            and "EXP-000845" in research.get("latest_cp1_checkpoint", "")
            and research.get("closed_v4_1_scoped_gates") == EXPECTED_CLOSED
            and research.get("v4_1_new_negatives") == EXPECTED_NEW_NEGATIVES
            and research.get("v4_1_reused_negatives") == EXPECTED_REUSED
            and research.get("v4_1_historical_open_gates") == EXPECTED_HISTORICAL_OPEN,
            (theorem_map.get("version"), research.get("closed_v4_1_scoped_gates")),
            ("1.33.0", EXPECTED_CLOSED),
            "formal",
        )

        events = [json.loads(line) for line in texts["changelog"].splitlines() if line.strip()]
        candidates = [
            event
            for event in events
            if "EXP-000845" in event.get("claim_ids", []) or "R-167-v4.1" in event.get("keywords", [])
        ]
        expected_notes = [
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
            "claims/GATES.md",
            "RESULTS-LEDGER.md",
        ]
        expected_scripts = expected_paths[:3]
        event_ok = (
            len(events) == contract["event_ordinal"] == 637
            and len(candidates) == 1
            and candidates[0] is events[-1]
            and candidates[0].get("id") == EVENT_ID
            and candidates[0].get("date") == "2026-08-14"
            and candidates[0].get("header") == EVENT_HEADER
            and candidates[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE", "EXP-000845", "R-167"]
            and candidates[0].get("keywords") == sorted(EVENT_KEYWORDS)
            and candidates[0].get("neg_results") == EXPECTED_NEW_NEGATIVES
            and candidates[0].get("notes", [])[:4] == expected_notes
            and candidates[0].get("scripts") == expected_scripts
            and ".pdf" not in candidates[0].get("raw", "")
            and all(
                token in " ".join(candidates[0].get("raw", "").split())
                for token in (
                    "centered bandlimited GNS form core",
                    "parity",
                    "full finite-source gap",
                    "does not refute a phasewise target gap",
                    "Both historical gates remain OPEN",
                    "No v4.1 PDF is issued",
                )
            )
        )
        audit.check("unique proof-first event 637", event_ok, candidates, "one exact no-PDF event", "formal")
        audit.check(
            "generated proof-evidence linkage",
            all("EXP-000845" in texts[key] for key in ("proof_map_md", "proof_map_json")),
            "generated links",
            "generated links",
            "formal",
        )

        c6 = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
        audit.check(
            "C6 unchanged-tier firewall",
            c6.get("tier") == "T1"
            and c6.get("lifecycle") == "ACTIVE"
            and c6.get("evidence_grade") == ["CONDITIONAL"]
            and c6.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            c6,
            "T1 ACTIVE CONDITIONAL blocked",
            "formal",
        )
        actual_counts = formal_counts(texts)
        expected_counts = contract["expected_post_formal_counts"]
        noncatalog = tuple(key for key in expected_counts if key != "catalog")
        catalog_ok = (
            DEFAULT_OUTPUT.exists() and actual_counts["catalog"] == expected_counts["catalog"]
        ) or (
            not DEFAULT_OUTPUT.exists() and actual_counts["catalog"] == expected_counts["catalog"] - 1
        )
        audit.check(
            "exact post-formal authority counts",
            all(actual_counts[key] == expected_counts[key] for key in noncatalog) and catalog_ok,
            {
                "actual": actual_counts,
                "integrated_output_exists": DEFAULT_OUTPUT.exists(),
                "catalog_after_this_output": actual_counts["catalog"] + (0 if DEFAULT_OUTPUT.exists() else 1),
            },
            expected_counts,
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-categorical-ground-bandlimited-gns-poincare-integrated-run/1.0",
        "version": "R-167 v4.1",
        "mode": "staged" if staged else "formal",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": {"common": primary["derived"], "stored": stored_status},
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
    print(f"INTEGRATED PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
