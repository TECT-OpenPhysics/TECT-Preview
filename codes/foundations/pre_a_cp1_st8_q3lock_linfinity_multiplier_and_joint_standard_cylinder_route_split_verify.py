#!/usr/bin/env python3
"""Integrated verifier for the R-167 v3.1 route split."""

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
SLUG = "pre-a-cp1-st8-q3lock-linfinity-multiplier-and-joint-standard-cylinder-route-split"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_linfinity_multiplier_and_joint_standard_cylinder_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_linfinity_multiplier_and_joint_standard_cylinder_route_split_independent.py"
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
    "PA-CP1-ST8-Q3LOCK-LINFINITY-CONFIGURATION-MULTIPLIER-ESSENTIAL-RANGE-FULL-HAMILTONIAN-NORM-JUMP-AND-JOINT-STANDARD-CYLINDER-SCALARITY"
]
EXPECTED_NEGATIVE = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0"
]
EXPECTED_HISTORICAL = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-HAMILTONIAN-POINT-NORM-C0",
]
EXPECTED_SUBSUMED_BOND = [
    "NG-2026-08-12-PRE-A-ST8-Q3LOCK-CANONICAL-ONE-SITE-COMPACT-CYLINDER-BOND-SUBFLOW-POINT-NORM-C0",
]
EXPECTED_PARENTS = [
    "PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
EVENT_TITLE = "R-167 v3.1 essential-range multiplier and joint cylinder scalarity"
EVENT_HEADER = f"[{EVENT_TITLE}] - 2026-08-13"
EVENT_ID = "20260813-r-167-v3-1-essential-range-multiplier-and-joint"
EVENT_KEYWORDS = [
    "EXP-000835",
    "R-167-v3.1",
    "essential-range",
    "joint-standard-cylinder",
    "linfinity-multiplier",
    "no-parent-closure",
    "point-norm-C0",
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
    with tempfile.TemporaryDirectory(prefix="tect-v31-") as temporary:
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


def independent_firewall() -> dict[str, Any]:
    tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
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
        "itertools",
        "pathlib",
        "typing",
    }
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
    return {"unapproved": sorted(imports - allowed), "dynamic": dynamic, "imports": sorted(imports)}


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    normalized_certificate = " ".join(certificate.split())
    primary = execute_child(PRIMARY, staged)
    independent = execute_child(INDEPENDENT, staged)
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["schema"] == "tect/pre-a-q3lock-linfinity-multiplier-joint-cylinder/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.1"
        and manifest["exploration_id"] == "EXP-000835"
        and manifest["prior_exploration_id"] == "EXP-000834"
        and manifest["claim_bearing"] is False,
        (manifest["schema"], manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        ("exact schema", SLUG, "R-167 v3.1", "EXP-000835"),
        "manifest",
    )
    audit.check(
        "manifest exact authority topology",
        manifest["closed_gate_ids"] == EXPECTED_CLOSED
        and manifest["negative_ids"] == EXPECTED_NEGATIVE
        and manifest["strictly_strengthened_historical_negative_ids"] == EXPECTED_HISTORICAL
        and manifest["historical_bond_negative_subsumed_by_v3_0_classification_ids"] == EXPECTED_SUBSUMED_BOND
        and manifest["open_parent_gate_ids"] == EXPECTED_PARENTS,
        (
            manifest["closed_gate_ids"],
            manifest["negative_ids"],
            manifest["strictly_strengthened_historical_negative_ids"],
            manifest["historical_bond_negative_subsumed_by_v3_0_classification_ids"],
            manifest["open_parent_gate_ids"],
        ),
        (EXPECTED_CLOSED, EXPECTED_NEGATIVE, EXPECTED_HISTORICAL, EXPECTED_SUBSUMED_BOND, EXPECTED_PARENTS),
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
        "proof-first lifecycle",
        manifest["checkpoint_synthesis"]
        == {
            "status": "DEFERRED UNTIL THE NEXT LOGICAL GATE-LEVEL CHECKPOINT",
            "pdf_issued": False,
            "workflow": "Proof-first manifest, certificate and three executable verifiers only. No v3.1 PDF is issued.",
        },
        manifest["checkpoint_synthesis"],
        "exact deferred no-PDF lifecycle",
        "manifest",
    )

    for label, payload, owner, expected_total in (
        ("primary", primary, PRIMARY, 35 if staged else 36),
        ("independent", independent, INDEPENDENT, 36 if staged else 37),
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

    source_texts = (PRIMARY.read_text(encoding="utf-8"), INDEPENDENT.read_text(encoding="utf-8"))
    for group in ("real_step", "complex_step", "galilean", "polynomial_translation", "joint_truth_table"):
        oracle = manifest["exact_fixture"][group]
        primary_projection = {key: primary["derived"][group].get(key) for key in oracle}
        independent_projection = {key: independent["derived"][group].get(key) for key in oracle}
        cross_ok = primary_projection == independent_projection == oracle
        if group == "polynomial_translation":
            polynomial = primary["derived"][group]
            expected_translation_factor = 1 + 2 ** max(polynomial["degree"] - 1, 0) * polynomial["segment_radius"] ** polynomial["degree"]
            cross_ok = (
                cross_ok
                and int(polynomial["translation_factor"]) == expected_translation_factor
                and all("quartic_sum_factor\": 8" not in text and "QUARTIC_SUM_FACTOR = 8" not in text for text in source_texts)
            )
        audit.check(
            f"cross exact {group}",
            cross_ok,
            (primary_projection, independent_projection),
            oracle,
            "cross",
        )

    firewall = independent_firewall()
    audit.check(
        "independent AST firewall",
        not firewall["unapproved"] and not firewall["dynamic"],
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
    proof_tokens = (
        "D_ess(f)",
        "Lebesgue points",
        "p_t = chi (y-x)/t",
        "Only this density identity is used",
        "s/t in [0,1]",
        "C_epsilon |t|/hbar",
        "eta; x,y; fixed epsilon",
        "intersection equals the scalar multiples",
        "strictly strengthens the v2.8",
        "background-uniform spatial norm bound",
        "No v3.1 PDF is issued",
    )
    audit.check(
        "certificate exact theorem contract",
        all(token in normalized_certificate for token in proof_tokens),
        [token for token in proof_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )
    audit.check(
        "certificate no-overclaim contract",
        all(
            token in normalized_certificate
            for token in (
                "not a classification of the full continuous-element algebra",
                "does not prove that a common thermodynamic action is impossible",
                "No exact-Q3 background-uniform bound",
                "All five active parent gates remain OPEN",
                "physical Sector A, or Pre-A",
            )
        ),
        "boundary tokens",
        "present",
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
        exploration_records = [json.loads(line) for line in texts["explorations"].splitlines() if line.strip()]
        records = [record for record in exploration_records if record.get("id") == "EXP-000835"]
        exploration_ok = (
            len(records) == 1
            and records[0].get("task_id") == "T-054"
            and records[0].get("verdict") == "advanced"
            and records[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and records[0].get("related") == [{"id": "EXP-000834", "relation": "continues"}]
            and records[0].get("gate_ids") == EXPECTED_CLOSED + EXPECTED_PARENTS
            and records[0].get("formal_refs", {}).get("negatives") == EXPECTED_NEGATIVE
            and records[0].get("formal_refs", {}).get("results") == ["R-167"]
            and all(".pdf" not in ref and ".tex.txt" not in ref for ref in records[0].get("evidence_refs", []))
        )
        audit.check("EXP-000835 exact continuation", exploration_ok, records, "one exact proof-first record", "formal")

        child_section = markdown_h3_section(texts["gates"], EXPECTED_CLOSED[0])
        audit.check(
            "one exact CLOSED child section",
            bool(child_section)
            and bool(re.search(r"^\*\*Status:\*\*\s*CLOSED\b", child_section, re.MULTILINE))
            and "EXP-000835 / R-167 v3.1" in child_section
            and "essential range" in child_section
            and "standard one-site cylinder" in child_section,
            child_section[:300],
            "unique exact CLOSED child",
            "formal",
        )
        parent_sections = [markdown_h3_section(texts["gates"], gate) for gate in EXPECTED_PARENTS]
        audit.check(
            "five exact OPEN parent sections",
            all(
                section
                and re.search(r"^\*\*Status:\*\*.*\bOPEN\b", section, re.MULTILINE)
                and "EXP-000835 / R-167 v3.1" in section
                for section in parent_sections
            ),
            [bool(section) for section in parent_sections],
            [True] * 5,
            "formal",
        )

        negative_section = markdown_result_section(texts["negatives"], EXPECTED_NEGATIVE[0])
        normalized_negative = " ".join(negative_section.split())
        negative_ok = bool(negative_section) and all(
            token in normalized_negative
            for token in (
                "essential-range",
                "Lebesgue",
                "liminf",
                "strictly strengthens",
                "does not prove common-alpha nonexistence",
            )
        )
        audit.check("negative exact strengthened detail", negative_ok, normalized_negative[:400], "scoped exact detail", "formal")
        audit.check(
            "historical negatives retained",
            all(texts["negatives"].count(identifier) >= 2 for identifier in EXPECTED_HISTORICAL + EXPECTED_SUBSUMED_BOND),
            {identifier: texts["negatives"].count(identifier) for identifier in EXPECTED_HISTORICAL + EXPECTED_SUBSUMED_BOND},
            "all historical records retained",
            "formal",
        )

        result_section = markdown_result_section(texts["results"], "R-167")
        audit.check(
            "R-167 v3.1 current authority",
            all(
                token in result_section
                for token in (
                    "EXP-000835",
                    "R-167 v3.1",
                    "current proof-first authority",
                    "essential-range",
                    "No v3.1 PDF",
                )
            ),
            "result tokens",
            "present in R-167 section",
            "formal",
        )

        todo_data = json.loads(texts["todo"])
        todo_records = [item for item in todo_data.get("tasks", []) if item.get("id") == "T-054"]
        audit.check(
            "T-054 remains in progress with v3.1",
            len(todo_records) == 1
            and todo_records[0].get("status") == "in_progress"
            and "EXP-000835" in todo_records[0].get("note", "")
            and "remain OPEN" in todo_records[0].get("note", ""),
            todo_records,
            "one linked in-progress task",
            "formal",
        )

        theorem_map = json.loads(texts["theorem_map"])
        research = theorem_map.get("research_priority", {})
        linkage_ok = (
            "EXP-000835" in texts["roadmap"]
            and "EXP-000835" in texts["strategy"]
            and theorem_map.get("version") == "1.23.0"
            and "EXP-000835" in research.get("latest_cp1_checkpoint", "")
            and research.get("closed_v3_1_scoped_gates") == EXPECTED_CLOSED
        )
        audit.check(
            "ROADMAP strategy theorem-map linkage",
            linkage_ok,
            (theorem_map.get("version"), research.get("closed_v3_1_scoped_gates")),
            ("1.23.0", EXPECTED_CLOSED),
            "formal",
        )

        events = [json.loads(line) for line in texts["changelog"].splitlines() if line.strip()]
        event_candidates = [
            event
            for event in events
            if "EXP-000835" in event.get("claim_ids", []) or "R-167-v3.1" in event.get("keywords", [])
        ]
        event_ok = (
            len(events) == manifest["formal_integration_contract"]["event_id"] == 627
            and len(event_candidates) == 1
            and event_candidates[0] is events[-1]
            and event_candidates[0].get("id") == EVENT_ID
            and event_candidates[0].get("date") == "2026-08-13"
            and event_candidates[0].get("header") == EVENT_HEADER
            and event_candidates[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE", "EXP-000835", "R-167"]
            and event_candidates[0].get("keywords") == sorted(EVENT_KEYWORDS)
            and event_candidates[0].get("neg_results") == EXPECTED_NEGATIVE
            and event_candidates[0].get("notes")
            == [
                str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
                str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
                "claims/GATES.md",
                "RESULTS-LEDGER.md",
            ]
            and event_candidates[0].get("scripts") == expected_paths[:3]
            and event_candidates[0].get("raw", "").startswith(f"## {EVENT_HEADER}\n\n")
            and ".pdf" not in event_candidates[0].get("raw", "")
            and ".tex.txt" not in event_candidates[0].get("raw", "")
            and all(
                token in event_candidates[0].get("raw", "")
                for token in (
                    "essential-range diameter",
                    "Lebesgue-point Galilean packets",
                    "joint standard one-site cylinder",
                    "strictly strengthens",
                    "All five active parent gates remain OPEN",
                    "No v3.1 PDF is issued",
                )
            )
        )
        audit.check("unique proof-first event 627", event_ok, event_candidates, "one exact no-PDF event", "formal")

        generated_ok = all("EXP-000835" in texts[key] for key in ("proof_map_md", "proof_map_json"))
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
        "derived": {
            group: primary["derived"][group]
            for group in ("real_step", "complex_step", "galilean", "polynomial_translation", "joint_truth_table")
        }
        | {"stored": stored_status},
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
    print(f"R-167 v3.1 INTEGRATED PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
