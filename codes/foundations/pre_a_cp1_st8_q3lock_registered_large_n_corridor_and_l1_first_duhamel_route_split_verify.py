#!/usr/bin/env python3
"""Integrated verifier for the R-167 v3.6 proof-first package."""

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
SLUG = "pre-a-cp1-st8-q3lock-registered-large-n-corridor-and-l1-first-duhamel-route-split"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_registered_large_n_corridor_and_l1_first_duhamel_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_registered_large_n_corridor_and_l1_first_duhamel_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-integrated-{SLUG}/result.json"
)
PRIMARY_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-primary-{SLUG}/result.json"
)
INDEPENDENT_RESULT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-independent-{SLUG}/result.json"
)
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
    "PA-CP1-ST8-Q3LOCK-REGISTERED-LARGE-N-CORRIDOR-FULL-OSCILLATOR-DLR-COEXISTENCE-GROUND-ORDER-CUSP-AND-TIME-ZERO-TANGENT-SPECIALIZATION",
    "PA-CP1-ST8-Q3LOCK-POSITIVE-TIME-TRACE-RITZ-REMOVAL-PLUS-L1-DOMINATED-FIRST-DUHAMEL-INTEGRAL-REDUCTION",
]
EXPECTED_NEGATIVES = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION"
]
EXPECTED_REUSED = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-NORM-SEPARATED-PARITY-KMS-PAIRS-AUTOMATIC-DISTINCT-GROUND-LIMITS",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-SPECTRAL-GAP",
]
EXPECTED_HISTORICAL_OPEN = [
    "PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION"
]
EXPECTED_PARENTS = [
    "PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
EVENT_TITLE = (
    "R-167 v3.6 registered corridor full-oscillator phases and L1 Duhamel reduction"
)
EVENT_HEADER = f"[{EVENT_TITLE}] - 2026-08-13"
EVENT_ID = "20260813-r-167-v3-6-registered-corridor-full-oscillator"
EVENT_KEYWORDS = [
    "EXP-000840",
    "R-167-v3.6",
    "DLR-coexistence",
    "full-oscillator",
    "ground-order",
    "large-N-corridor",
    "no-parent-closure",
    "short-time-L1",
]


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def execute_child(path: Path, staged: bool) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-v36-") as temporary:
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
            raise AssertionError(
                f"child failed {path.name}:\n{completed.stdout}\n{completed.stderr}"
            )
        return json.loads(output.read_text(encoding="utf-8"))


def proof_core(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "derived": payload.get("derived"),
        "assertions": [
            row
            for row in payload.get("assertions", [])
            if row.get("group") != "formal"
        ],
        "source_hashes": payload.get("source_hashes"),
    }


def common_derived(payload: dict[str, Any]) -> dict[str, Any]:
    derived = payload["derived"]
    return {
        "corridor": {
            key: derived["corridor"][key]
            for key in (
                "theta_Q",
                "A0",
                "rho_squared_upper",
                "beta_upper",
                "strict_beta_margin",
                "ground_lower",
                "A0_above_I3_upper",
                "ground_lower_positive",
            )
        },
        "duhamel": {
            key: derived["duhamel"][key]
            for key in (
                "cross_trace_norm",
                "holder_bound_squared",
                "Ritz_tail",
                "holder_factor_identity",
                "holder_strict",
            )
        },
        "short_time": {
            key: derived["short_time"][key]
            for key in (
                "full_trace",
                "partial_trace",
                "tail",
                "small_time_power",
                "scaled_limit",
                "locally_L1",
                "fixed_beta_cross_trace",
            )
        },
    }


def ast_firewall(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "__import__",
                "eval",
                "exec",
                "compile",
            }:
                dynamic.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "import_module",
                "exec_module",
                "load_module",
            }:
                dynamic.append(node.func.attr)
    return {"imports": sorted(imports), "dynamic": dynamic}


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
    result_rows = re.findall(
        r"^\| \[(R-\d+)\]\(#[^)]+\) \| .*? \| .*? \|$",
        texts["results"],
        re.MULTILINE,
    )
    gate_rows = re.findall(
        r"^#{2,4}\s+\*\*([A-Z0-9][A-Z0-9-]+)\*\*\s*$",
        texts["gates"],
        re.MULTILINE,
    )
    negative_rows = re.findall(
        r"^\| \[((?:R|F|NG|AUDIT)-[A-Za-z0-9-]+)\]\(#[^)]+\) \| .*? \| .*? \|$",
        texts["negatives"],
        re.MULTILINE,
    )
    claim_count = sum(
        1
        for path in (REPO / "claims").glob("*/status.json")
        if not path.parent.name.startswith("_")
    )
    task_count = len(json.loads(texts["todo"]).get("tasks", []))
    catalog_total = int(
        json.loads(
            (REPO / "verification/catalog/index.json").read_text(encoding="utf-8")
        )["total"]
    )
    return {
        "claims": claim_count,
        "results": len(result_rows),
        "gates": len(gate_rows),
        "negatives": len(negative_rows),
        "explorations": len(
            [line for line in texts["explorations"].splitlines() if line.strip()]
        ),
        "events": len(
            [line for line in texts["changelog"].splitlines() if line.strip()]
        ),
        "tasks": task_count,
        "catalog": catalog_total,
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    primary = execute_child(PRIMARY, staged)
    independent = execute_child(INDEPENDENT, staged)
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["schema"]
        == "tect/pre-a-q3lock-registered-large-n-corridor-l1-first-duhamel/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.6"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000840"
        and manifest["prior_exploration_id"] == "EXP-000839"
        and manifest["claim_bearing"] is False,
        (
            manifest["schema"],
            manifest["package_id"],
            manifest["version"],
            manifest["exploration_id"],
        ),
        ("exact schema", SLUG, "R-167 v3.6", "EXP-000840"),
        "manifest",
    )
    audit.check(
        "manifest authority topology",
        manifest["closed_gate_ids"] == EXPECTED_CLOSED
        and manifest["negative_ids"] == EXPECTED_NEGATIVES
        and manifest["reused_negative_ids"] == EXPECTED_REUSED
        and manifest["historical_open_gate_ids"] == EXPECTED_HISTORICAL_OPEN
        and manifest["open_parent_gate_ids"] == EXPECTED_PARENTS,
        (
            manifest["closed_gate_ids"],
            manifest["negative_ids"],
            manifest["reused_negative_ids"],
        ),
        (EXPECTED_CLOSED, EXPECTED_NEGATIVES, EXPECTED_REUSED),
        "manifest",
    )
    expected_paths = [
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in (
            PRIMARY,
            INDEPENDENT,
            SCRIPT,
            PRIMARY_RESULT,
            INDEPENDENT_RESULT,
            DEFAULT_OUTPUT,
        )
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
    audit.check(
        "manifest verification paths",
        actual_paths == expected_paths,
        actual_paths,
        expected_paths,
        "manifest",
    )
    audit.check(
        "manifest theorem firewalls",
        "exact full-oscillator" in manifest["registered_corridor"]["finite_beta_conclusion"]
        and "not identify the DFFR Ritz branches" in manifest["registered_corridor"]["novelty_boundary"]
        and "conditional first-coefficient reduction" in manifest["l1_first_duhamel_reduction"]["boundary"]
        and "does not refute existence" in manifest["short_time_obstruction"]["firewall"]
        and "remain OPEN" in manifest["no_overclaim"],
        "scope firewalls present",
        "scope firewalls present",
        "manifest",
    )
    audit.check(
        "proof-first lifecycle",
        manifest["checkpoint_synthesis"]["pdf_issued"] is False
        and manifest["checkpoint_synthesis"]["status"]
        == "DEFERRED UNTIL THE NEXT LOGICAL GATE-LEVEL CHECKPOINT",
        manifest["checkpoint_synthesis"],
        "deferred no-PDF",
        "manifest",
    )

    expected_totals = {"primary": (17, 18), "independent": (21, 22)}
    for label, payload, owner in (
        ("primary", primary, PRIMARY),
        ("independent", independent, INDEPENDENT),
    ):
        expected_total = expected_totals[label][0 if staged else 1]
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
        common_derived(primary) == common_derived(independent),
        common_derived(primary),
        common_derived(independent),
        "cross",
    )
    firewall = ast_firewall(INDEPENDENT)
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
        "stdlib allowlist/no dynamic execution",
        "independence",
    )
    audit.check(
        "independent source distinct",
        normalized_sha256(PRIMARY) != normalized_sha256(INDEPENDENT),
        normalized_sha256(INDEPENDENT),
        "different from primary",
        "independence",
    )
    source_text = PRIMARY.read_text(encoding="utf-8") + INDEPENDENT.read_text(
        encoding="utf-8"
    )
    masked_literals = (
        '"beta_upper": "4896/2741"',
        '"strict_beta_margin": "189/13705"',
        '"ground_lower": "8/3-sqrt(102)/10"',
        '"full_trace": "2"',
        '"partial_trace": "13/8"',
        '"tail": "3/8"',
    )
    audit.check(
        "derived-number hardcode firewall",
        all(token not in source_text for token in masked_literals),
        [token for token in masked_literals if token in source_text],
        [],
        "independence",
    )
    theorem_tokens = (
        "4896\\over2741",
        "m_{L,N}^2",
        "not promoted here to algebraic ground states",
        "g_\\beta\\notin L^1",
        "does not refute the existence",
        "All five active parent gates",
        "No v3.6 PDF is issued",
    )
    audit.check(
        "certificate theorem and scope contract",
        all(token in certificate for token in theorem_tokens),
        [token for token in theorem_tokens if token not in certificate],
        [],
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
            audit.check(
                f"stored {label} freshness",
                same,
                stored_status[label],
                "fresh",
                "stored",
            )
        elif staged:
            stored_status[label] = "absent-staged"
            audit.check(
                f"stored {label} staged lifecycle",
                True,
                stored_status[label],
                "allowed",
                "stored",
            )
        else:
            raise AssertionError(f"stored result missing: {path}")

    if not staged:
        texts = {name: path.read_text(encoding="utf-8") for name, path in FORMAL.items()}
        records = [
            json.loads(line)
            for line in texts["explorations"].splitlines()
            if line.strip() and json.loads(line).get("id") == "EXP-000840"
        ]
        expected_gate_links = EXPECTED_CLOSED + EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS
        expected_negative_links = EXPECTED_NEGATIVES + EXPECTED_REUSED
        exploration_ok = (
            len(records) == 1
            and records[0].get("task_id") == "T-054"
            and records[0].get("verdict") == "advanced"
            and records[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and records[0].get("related")
            == [{"id": "EXP-000839", "relation": "continues"}]
            and records[0].get("gate_ids") == expected_gate_links
            and records[0].get("formal_refs", {}).get("negatives")
            == expected_negative_links
            and records[0].get("formal_refs", {}).get("results") == ["R-167"]
        )
        audit.check(
            "EXP-000840 exact continuation",
            exploration_ok,
            records,
            "one exact proof-first record",
            "formal",
        )

        child_sections = [
            markdown_h3_section(texts["gates"], gate) for gate in EXPECTED_CLOSED
        ]
        audit.check(
            "two exact scoped CLOSED children",
            all(
                section
                and "**Status:** CLOSED" in section
                and "EXP-000840 / R-167 v3.6" in section
                for section in child_sections
            ),
            [section[:300] for section in child_sections],
            "unique closed sections",
            "formal",
        )
        open_sections = [
            markdown_h3_section(texts["gates"], gate)
            for gate in EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS
        ]
        audit.check(
            "historical beta gate and five parents remain OPEN",
            all(
                section
                and re.search(r"^\*\*Status:\*\*.*\bOPEN\b", section, re.MULTILINE)
                and "EXP-000840 / R-167 v3.6" in section
                for section in open_sections
            ),
            [bool(section) for section in open_sections],
            [True] * 6,
            "formal",
        )
        negative_section = markdown_result_section(
            texts["negatives"], EXPECTED_NEGATIVES[0]
        )
        audit.check(
            "exact short-time negative",
            negative_section
            and all(
                token in " ".join(negative_section.split())
                for token in (
                    "pointwise positive-time",
                    "not locally L1",
                    "fixed-beta cross integrand",
                    "does not reject",
                )
            ),
            negative_section[:700],
            "one narrow exact negative",
            "formal",
        )
        audit.check(
            "reused negatives preserved",
            all(
                markdown_result_section(texts["negatives"], identifier)
                for identifier in EXPECTED_REUSED
            ),
            EXPECTED_REUSED,
            "unique existing sections",
            "formal",
        )

        result_section = markdown_result_section(texts["results"], "R-167")
        audit.check(
            "R-167 v3.6 current authority",
            all(
                token in result_section
                for token in (
                    "EXP-000840",
                    "R-167 v3.6",
                    "current proof-first authority",
                    "N>=2",
                    "beta>=9/5",
                    "R-167 v3.5 certificate",
                    "prior proof-first authority",
                    "No v3.6 PDF",
                )
            ),
            "result tokens",
            "bounded R-167 section",
            "formal",
        )
        todo_data = json.loads(texts["todo"])
        todo_records = [
            item for item in todo_data.get("tasks", []) if item.get("id") == "T-054"
        ]
        audit.check(
            "T-054 in progress with v3.6",
            len(todo_records) == 1
            and todo_records[0].get("status") == "in_progress"
            and "EXP-000840" in todo_records[0].get("note", "")
            and "remain OPEN" in todo_records[0].get("note", ""),
            todo_records,
            "one linked in-progress task",
            "formal",
        )
        theorem_map = json.loads(texts["theorem_map"])
        research = theorem_map.get("research_priority", {})
        audit.check(
            "ROADMAP strategy theorem-map linkage",
            "EXP-000840" in texts["roadmap"]
            and "EXP-000840" in texts["strategy"]
            and theorem_map.get("version") == "1.28.0"
            and "EXP-000840" in research.get("latest_cp1_checkpoint", "")
            and research.get("closed_v3_6_scoped_gates") == EXPECTED_CLOSED
            and research.get("v3_6_exact_negative") == EXPECTED_NEGATIVES[0],
            (
                theorem_map.get("version"),
                research.get("closed_v3_6_scoped_gates"),
                research.get("v3_6_exact_negative"),
            ),
            ("1.28.0", EXPECTED_CLOSED, EXPECTED_NEGATIVES[0]),
            "formal",
        )

        events = [
            json.loads(line) for line in texts["changelog"].splitlines() if line.strip()
        ]
        candidates = [
            event
            for event in events
            if "EXP-000840" in event.get("claim_ids", [])
            or "R-167-v3.6" in event.get("keywords", [])
        ]
        expected_notes = [
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
            "claims/GATES.md",
            "RESULTS-LEDGER.md",
            "negative-results/registry.md",
        ]
        event_ok = (
            len(events) == manifest["formal_integration_contract"]["event_ordinal"]
            == 632
            and len(candidates) == 1
            and candidates[0] is events[-1]
            and candidates[0].get("id") == EVENT_ID
            and candidates[0].get("date") == "2026-08-13"
            and candidates[0].get("header") == EVENT_HEADER
            and candidates[0].get("claim_ids")
            == ["C6-SPACETIME-SIGNATURE", "EXP-000840", "R-167"]
            and candidates[0].get("keywords") == sorted(EVENT_KEYWORDS)
            and candidates[0].get("neg_results") == EXPECTED_NEGATIVES
            and candidates[0].get("notes") == expected_notes
            and candidates[0].get("scripts") == expected_paths[:3]
            and ".pdf" not in candidates[0].get("raw", "")
            and ".tex.txt" not in candidates[0].get("raw", "")
            and all(
                token in candidates[0].get("raw", "")
                for token in (
                    "N>=2",
                    "beta>=9/5",
                    "full-oscillator",
                    "first Duhamel",
                    "All five active parent gates remain OPEN",
                    "No v3.6 PDF is issued",
                )
            )
        )
        audit.check(
            "unique proof-first event 632",
            event_ok,
            candidates,
            "one exact no-PDF event",
            "formal",
        )
        audit.check(
            "generated proof-evidence linkage",
            all("EXP-000840" in texts[key] for key in ("proof_map_md", "proof_map_json")),
            "generated links",
            "generated links",
            "formal",
        )
        c6 = json.loads(
            (REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(
                encoding="utf-8"
            )
        )
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
        expected_counts = manifest["formal_integration_contract"][
            "expected_post_formal_counts"
        ]
        noncatalog = tuple(key for key in expected_counts if key != "catalog")
        catalog_expected = expected_counts["catalog"]
        catalog_ok = (
            DEFAULT_OUTPUT.exists() and actual_counts["catalog"] == catalog_expected
        ) or (
            not DEFAULT_OUTPUT.exists()
            and actual_counts["catalog"] == catalog_expected - 1
        )
        audit.check(
            "exact post-formal authority counts",
            all(actual_counts[key] == expected_counts[key] for key in noncatalog)
            and catalog_ok,
            {
                "actual": actual_counts,
                "integrated_output_exists": DEFAULT_OUTPUT.exists(),
                "catalog_after_this_output": actual_counts["catalog"]
                + (0 if DEFAULT_OUTPUT.exists() else 1),
            },
            expected_counts,
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-registered-large-n-corridor-l1-first-duhamel-integrated-run/1.0",
        "version": "R-167 v3.6",
        "mode": "staged" if staged else "formal",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": common_derived(primary) | {"stored": stored_status},
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
    print(
        f"INTEGRATED PASS {payload['summary']['passed']}/{payload['summary']['passed']} "
        f"mode={payload['mode']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
