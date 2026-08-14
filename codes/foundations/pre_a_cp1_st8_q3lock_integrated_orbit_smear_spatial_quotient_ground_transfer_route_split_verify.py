#!/usr/bin/env python3
"""Cross-audit and formally integrate the R-167 v4.2 spatial quotient route.

The primary SymPy lane and independent stdlib/Fraction lane recompute the same
shell, product, quotient, kernel, and parity-ground fixtures. This verifier
also enforces exact source hashes, AST independence, oracle placement, the
five-file lifecycle, and EXP-000846/event-638/theorem-map topology.
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
SLUG = "pre-a-cp1-st8-q3lock-integrated-orbit-smear-spatial-quotient-ground-transfer-route-split"
CODE_STEM = "pre_a_cp1_st8_q3lock_integrated_orbit_smear_spatial_quotient_ground_transfer_route_split"
PRIMARY = REPO / f"codes/foundations/{CODE_STEM}.py"
INDEPENDENT = REPO / f"codes/foundations/{CODE_STEM}_independent.py"
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
    "PA-CP1-ST8-Q3LOCK-INTEGRATED-ORBIT-SMEAR-SHELL-CAUCHY-SPATIAL-QUOTIENT-AND-SAME-NET-GROUND-TRANSFER"
]
EXPECTED_REUSED = [
    "NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0",
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

EVENT_TITLE = "R-167 v4.2 integrated orbit-smear spatial quotient ground transfer route split"
EVENT_HEADER = f"[{EVENT_TITLE}] - 2026-08-14"
EVENT_ID = "20260814-r-167-v4-2-integrated-orbit-smear-spatial-quoti"
EVENT_KEYWORDS = [
    "EXP-000846",
    "R-167-v4.2",
    "integrated-toggle",
    "orbit-smear",
    "same-net-ground-transfer",
    "spatial-quotient",
    "summable-shell",
    "zero-source-categorical",
]

TEST_ORACLE_CHILD_TOTALS = {"primary": 13, "independent": 12}
TEST_ORACLE_DERIVED_LITERALS = {
    "1/4",
    "7/48",
    "3517/1001",
    "30",
    "3/4",
    "1/12",
    "1/8",
    "5/32",
    "1/2",
    "-1/2",
}
TEST_ORACLE_PREFORMAL_COUNTS = {
    "claims": 49,
    "results": 168,
    "gates": 195,
    "negatives": 367,
    "explorations": 845,
    "events": 637,
    "tasks": 54,
    "catalog": 3963,
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
    with tempfile.TemporaryDirectory(prefix="tect-v42-") as temporary:
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
    forbidden_literals: list[str] = []
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
            if isinstance(node.func, ast.Name) and node.func.id in {"float", "complex"}:
                forbidden_calls.append(node.func.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (float, complex)):
            forbidden_literals.append(repr(node.value))
    return {
        "imports": sorted(imports),
        "dynamic": dynamic,
        "forbidden_calls": forbidden_calls,
        "forbidden_literals": forbidden_literals,
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
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value in TEST_ORACLE_DERIVED_LITERALS
            and not any(start <= node.lineno <= end for start, end in spans)
        ):
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
        manifest["schema"] == "tect/pre-a-q3lock-integrated-orbit-smear-spatial-quotient-ground-transfer-route-split/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v4.2"
        and manifest["date"] == "2026-08-14"
        and manifest["exploration_id"] == "EXP-000846"
        and manifest["prior_exploration_id"] == "EXP-000845"
        and manifest["claim_bearing"] is False,
        (manifest["schema"], manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        ("exact schema", SLUG, "R-167 v4.2", "EXP-000846"),
        "manifest",
    )
    audit.check(
        "manifest authority topology",
        manifest["closed_gate_ids"] == EXPECTED_CLOSED
        and manifest["negative_ids"] == []
        and manifest["reused_negative_ids"] == EXPECTED_REUSED
        and manifest["historical_open_gate_ids"] == EXPECTED_HISTORICAL_OPEN
        and manifest["open_parent_gate_ids"] == EXPECTED_PARENTS,
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]),
        (EXPECTED_CLOSED, [], EXPECTED_REUSED),
        "manifest",
    )
    contract = manifest["formal_integration_contract"]
    expected_post_counts = {
        "claims": 49,
        "results": 168,
        "gates": 196,
        "negatives": 367,
        "explorations": 847,
        "events": 638,
        "tasks": 55,
        "catalog": 3971,
    }
    audit.check(
        "event and count contract",
        contract["event_ordinal"] == 638
        and contract["event_id"] == EVENT_ID
        and contract["event_title"] == EVENT_TITLE
        and contract["event_keywords"] == EVENT_KEYWORDS
        and contract["theorem_map_version"] == "1.34.0"
        and contract["expected_post_formal_counts"] == expected_post_counts,
        contract,
        "frozen event 638, map 1.34.0 and counts",
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

    actual_package_files = sorted(
        [path for path in (REPO / "strategy").glob(f"{SLUG}-*") if path.is_file()]
        + [path for path in (REPO / "codes/foundations").glob(f"{CODE_STEM}*.py") if path.is_file()]
    )
    expected_package_files = sorted([MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT])
    audit.check(
        "exact five-file proof-first package",
        actual_package_files == expected_package_files,
        [str(path.relative_to(REPO)) for path in actual_package_files],
        [str(path.relative_to(REPO)) for path in expected_package_files],
        "lifecycle",
    )
    audit.check(
        "proof-first lifecycle and scope",
        manifest["checkpoint_synthesis"]["pdf_issued"] is False
        and manifest["negative_ids"] == []
        and "does not prove those weights for exact Q3" in manifest["no_overclaim"]
        and "not proved to be a seed-indexed commuting local net" in manifest["no_overclaim"]
        and "no GNS spectral gap" in manifest["no_overclaim"]
        and "remain OPEN" in manifest["no_overclaim"],
        "conditional no-PDF spatial-subalgebra route",
        "conditional no-PDF spatial-subalgebra route",
        "manifest",
    )

    for label, payload, owner in (
        ("primary", primary, PRIMARY),
        ("independent", independent, INDEPENDENT),
    ):
        expected_total = TEST_ORACLE_CHILD_TOTALS[label] + (0 if staged else 1)
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
        for shared in (MANIFEST, CERTIFICATE):
            shared_key = str(shared.relative_to(REPO)).replace("\\", "/")
            audit.check(
                f"{label} {shared.name} freshness",
                payload["source_hashes"][shared_key] == normalized_sha256(shared),
                payload["source_hashes"][shared_key],
                normalized_sha256(shared),
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
        "os",
        "tempfile",
        "fractions",
        "pathlib",
        "typing",
    }
    audit.check(
        "independent stdlib exact AST firewall",
        set(independent_firewall["imports"]) <= allowed_independent
        and "sympy" not in independent_firewall["imports"]
        and not independent_firewall["dynamic"]
        and not independent_firewall["forbidden_calls"]
        and not independent_firewall["forbidden_literals"],
        independent_firewall,
        "stdlib allowlist/no SymPy/dynamic/float/complex",
        "independence",
    )
    primary_firewall = ast_firewall(PRIMARY)
    audit.check(
        "primary exact-arithmetic AST firewall",
        "sympy" in primary_firewall["imports"]
        and not primary_firewall["dynamic"]
        and not primary_firewall["forbidden_calls"]
        and not primary_firewall["forbidden_literals"],
        primary_firewall,
        "SymPy exact with no dynamic/float/complex",
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
        "certificate theorem/adversarial contract",
        all(
            token in certificate
            for token in (
                "Xi_Q",
                "Lambda(F) contains X",
                "onsite Q3 terms",
                "W_(F,xi)",
                "X=union_(j=1)^m supp(xi_j)",
                "weak-int_R",
                "F triangle G subset {e:r_X(e)>R}",
                "all-shape filter neighborhood",
                "product_(k!=j)||f_k||_1",
                "tilde(P)_F",
                "Gamma_L",
                "q_sp:A_H^0->B_sp",
                "||pi_L^0(k)||",
                "bar(omega)_sigma",
                "q_sp(b)!=0",
                "R-167 v3.0 Section 6 already proves",
                "Devil's-advocate and code-discipline audit",
                "External adversarial review is invited",
                "No v4.2 PDF is issued",
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

    texts = {name: path.read_text(encoding="utf-8") for name, path in FORMAL.items()}
    if staged:
        actual_counts = formal_counts(texts)
        audit.check(
            "exact preformal authority counts",
            actual_counts == TEST_ORACLE_PREFORMAL_COUNTS,
            actual_counts,
            TEST_ORACLE_PREFORMAL_COUNTS,
            "lifecycle",
        )
        theorem_map = json.loads(texts["theorem_map"])
        audit.check(
            "staged authority nonmutation firewall",
            "EXP-000846" not in texts["explorations"]
            and EVENT_ID not in texts["changelog"]
            and EXPECTED_CLOSED[0] not in texts["gates"]
            and theorem_map.get("version") == "1.33.0",
            ("EXP absent", "event absent", "gate absent", theorem_map.get("version")),
            ("EXP absent", "event absent", "gate absent", "1.33.0"),
            "lifecycle",
        )
    else:
        records = [
            json.loads(line)
            for line in texts["explorations"].splitlines()
            if line.strip() and json.loads(line).get("id") == "EXP-000846"
        ]
        expected_gate_links = EXPECTED_CLOSED + EXPECTED_HISTORICAL_OPEN + EXPECTED_PARENTS
        exploration_ok = (
            len(records) == 1
            and records[0].get("task_id") == "T-054"
            and records[0].get("verdict") == "advanced"
            and records[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and records[0].get("related") == [{"id": "EXP-000845", "relation": "continues"}]
            and records[0].get("gate_ids") == expected_gate_links
            and records[0].get("formal_refs", {}).get("negatives") == EXPECTED_REUSED
            and records[0].get("formal_refs", {}).get("results") == ["R-167"]
        )
        audit.check("EXP-000846 exact continuation", exploration_ok, records, "one exact proof-first record", "formal")

        child = markdown_h3_section(texts["gates"], EXPECTED_CLOSED[0])
        audit.check(
            "one exact scoped CLOSED child",
            bool(child) and "**Status:** CLOSED" in child and "EXP-000846 / R-167 v4.2" in child,
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
                and "EXP-000846 / R-167 v4.2" in section
                for section in open_sections
            ),
            [bool(section) for section in open_sections],
            [True] * 7,
            "formal",
        )
        audit.check(
            "three reused negatives preserved without new negative",
            all(markdown_result_section(texts["negatives"], identifier) for identifier in EXPECTED_REUSED),
            EXPECTED_REUSED,
            "three unique existing sections",
            "formal",
        )

        result = markdown_result_section(texts["results"], "R-167")
        audit.check(
            "R-167 v4.2 current authority",
            all(
                token in result
                for token in (
                    "EXP-000846",
                    "R-167 v4.2",
                    "current proof-first authority",
                    "R-167 v4.1 certificate",
                    "prior proof-first authority",
                    "No v4.2 PDF",
                )
            ),
            "result tokens",
            "bounded R-167 section",
            "formal",
        )
        todo = [item for item in json.loads(texts["todo"]).get("tasks", []) if item.get("id") == "T-054"]
        audit.check(
            "T-054 stable Round-1 routing",
            len(todo) == 1
            and todo[0].get("id") == "T-054"
            and todo[0].get("gate") == "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
            and bool(todo[0].get("owner"))
            and bool(todo[0].get("note")),
            todo,
            "one operator-owned task with stable Round-1 routing",
            "formal",
        )
        theorem_map = json.loads(texts["theorem_map"])
        research = theorem_map.get("research_priority", {})
        audit.check(
            "ROADMAP strategy theorem-map linkage",
            "EXP-000846" in texts["roadmap"]
            and "EXP-000846" in texts["strategy"]
            and theorem_map.get("version") == "1.34.0"
            and "EXP-000846" in research.get("latest_cp1_checkpoint", "")
            and research.get("closed_v4_2_scoped_gates") == EXPECTED_CLOSED
            and research.get("v4_2_reused_negatives") == EXPECTED_REUSED
            and research.get("v4_2_historical_open_gates") == EXPECTED_HISTORICAL_OPEN,
            (theorem_map.get("version"), research.get("closed_v4_2_scoped_gates")),
            ("1.34.0", EXPECTED_CLOSED),
            "formal",
        )

        events = [json.loads(line) for line in texts["changelog"].splitlines() if line.strip()]
        candidates = [
            event
            for event in events
            if "EXP-000846" in event.get("claim_ids", []) or "R-167-v4.2" in event.get("keywords", [])
        ]
        expected_notes = [
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
            "claims/GATES.md",
            "RESULTS-LEDGER.md",
        ]
        event_ok = (
            len(events) == contract["event_ordinal"] == 638
            and len(candidates) == 1
            and candidates[0] is events[-1]
            and candidates[0].get("id") == EVENT_ID
            and candidates[0].get("date") == "2026-08-14"
            and candidates[0].get("header") == EVENT_HEADER
            and candidates[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE", "EXP-000846", "R-167"]
            and candidates[0].get("keywords") == sorted(EVENT_KEYWORDS)
            and candidates[0].get("neg_results") == []
            and candidates[0].get("notes", [])[:4] == expected_notes
            and candidates[0].get("scripts") == expected_paths[:3]
            and ".pdf" not in candidates[0].get("raw", "")
            and all(
                token in " ".join(candidates[0].get("raw", "").split())
                for token in (
                    "integrated-toggle",
                    "spatial quotient",
                    "same-net kernel",
                    "ground pair",
                    "Both historical gates remain OPEN",
                    "No v4.2 PDF is issued",
                )
            )
        )
        audit.check("unique proof-first event 638", event_ok, candidates, "one exact no-PDF event", "formal")
        audit.check(
            "generated proof-evidence linkage",
            all("EXP-000846" in texts[key] for key in ("proof_map_md", "proof_map_json")),
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
        noncatalog = tuple(key for key in expected_post_counts if key != "catalog")
        catalog_ok = (
            DEFAULT_OUTPUT.exists() and actual_counts["catalog"] == expected_post_counts["catalog"]
        ) or (
            not DEFAULT_OUTPUT.exists() and actual_counts["catalog"] == expected_post_counts["catalog"] - 1
        )
        audit.check(
            "exact post-formal authority counts",
            all(actual_counts[key] == expected_post_counts[key] for key in noncatalog) and catalog_ok,
            {
                "actual": actual_counts,
                "integrated_output_exists": DEFAULT_OUTPUT.exists(),
                "catalog_after_this_output": actual_counts["catalog"] + (0 if DEFAULT_OUTPUT.exists() else 1),
            },
            expected_post_counts,
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-integrated-orbit-smear-spatial-quotient-integrated-run/1.0",
        "version": "R-167 v4.2",
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
