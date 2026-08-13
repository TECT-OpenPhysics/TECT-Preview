#!/usr/bin/env python3
"""Integrated verifier for the R-167 v2.7 proof-first package.

The verifier executes the primary SymPy engine and the non-importing
standard-library engine in isolated temporary outputs.  It compares only
declared semantic adapters and binds both results to the manifest oracle.
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
from collections import Counter
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-fixed-ritz-gevrey-two-truncation-and-"
    "raw-configuration-weyl-c0-boundary"
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
GATES = REPO / "claims/GATES.md"
RESULTS = REPO / "RESULTS-LEDGER.md"
NEGATIVES = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
CHANGELOG = REPO / "changelog/log.jsonl"
TODO = REPO / "todo/todo.json"
ROADMAP = REPO / "ROADMAP.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
THEOREM_MAP = REPO / "governance/sector-a-theorem-map.json"
PROOF_MAP_MD = REPO / "theory/proof-evidence-map.md"
PROOF_MAP_JSON = REPO / "verification/proof-evidence-map.json"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-integrated-{SLUG}/result.json"
)

EXP_ID = "EXP-000828"
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v2.7"
EXPECTED_PRIMARY_STAGED = 37
EXPECTED_PRIMARY_FORMAL = 38
EXPECTED_INDEPENDENT_STAGED = 24
EXPECTED_INDEPENDENT_FORMAL = 25
EXPECTED_CLOSED_GATE = (
    "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FIXED-RITZ-LOCAL-SW-GEVREY-TWO-"
    "ADMISSIBLE-OPTIMAL-SCALE-TRUNCATION-EXTENSIVE-GROUND-ENERGY-REMAINDER"
)
EXPECTED_NEGATIVES = [
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-GEVREY-TWO-ASYMPTOTIC-REMAINDER-"
    "AUTOMATIC-ALL-ORDER-SW-CONVERGENCE",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-"
    "HAMILTONIAN-POINT-NORM-C0",
]
EXPECTED_OPEN_PARENTS = [
    "PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-"
    "AND-CUTOFF-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-"
    "DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-"
    "COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


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
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
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


def execute_child(script: Path, *, staged: bool) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-v27-child-") as directory:
        output = Path(directory) / "result.json"
        command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
        if staged:
            command.append("--staged")
        completed = subprocess.run(
            command,
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        if completed.returncode != 0 or not output.is_file():
            raise AssertionError(
                f"child failed: {script.name}; rc={completed.returncode}; "
                f"stdout={completed.stdout!r}; stderr={completed.stderr!r}"
            )
        return json.loads(output.read_text(encoding="utf-8"))


def find_exploration() -> list[dict[str, Any]]:
    if not EXPLORATIONS.exists():
        return []
    return [
        record
        for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines()
        if (record := json.loads(line)).get("id") == EXP_ID
    ]


def stored_matches(path: Path, fresh: dict[str, Any]) -> bool:
    if not path.is_file():
        return False
    stored = json.loads(path.read_text(encoding="utf-8"))
    return stored == fresh


def proof_core(payload: dict[str, Any]) -> dict[str, Any]:
    projected = dict(payload)
    rows = [row for row in payload.get("assertions", []) if row.get("group") != "formal"]
    projected["assertions"] = rows
    projected["summary"] = {"passed": len(rows), "failed": 0, "total": len(rows)}
    return projected


def gate_section(text: str, gate_id: str) -> str:
    heading = re.compile(rf"(?m)^### \*\*{re.escape(gate_id)}\*\*\s*$")
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        return ""
    start = matches[0].start()
    following = re.search(r"(?m)^### \*\*", text[matches[0].end() :])
    end = matches[0].end() + following.start() if following else len(text)
    return text[start:end]


def h3_section(text: str, prefix: str) -> str:
    heading = re.compile(rf"(?m)^### {re.escape(prefix)}(?:\s|$)")
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        return ""
    start = matches[0].start()
    following = re.search(r"(?m)^### ", text[matches[0].end() :])
    end = matches[0].end() + following.start() if following else len(text)
    return text[start:end]


def run(*, staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    primary = execute_child(PRIMARY, staged=staged)
    independent = execute_child(INDEPENDENT, staged=staged)
    expected_primary = EXPECTED_PRIMARY_STAGED if staged else EXPECTED_PRIMARY_FORMAL
    expected_independent = (
        EXPECTED_INDEPENDENT_STAGED if staged else EXPECTED_INDEPENDENT_FORMAL
    )

    independent_imports: set[str] = set()
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_dynamic_import = False
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            independent_imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            independent_imports.add(node.module.split(".")[0])
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "__import__"
        ):
            independent_dynamic_import = True
    audit.check(
        "independent static import firewall",
        PRIMARY.stem not in independent_imports
        and independent_imports.issubset(set(sys.stdlib_module_names) | {"__future__"})
        and not independent_dynamic_import,
        sorted(independent_imports),
        "no primary module and no SymPy",
        "components",
    )
    primary_rows = primary.get("assertions", [])
    independent_rows = independent.get("assertions", [])
    audit.check(
        "component assertion row integrity",
        len(primary_rows) == expected_primary
        and len(independent_rows) == expected_independent
        and len({row.get("name") for row in primary_rows}) == len(primary_rows)
        and len({row.get("name") for row in independent_rows}) == len(independent_rows)
        and all(row.get("status") == "PASS" for row in primary_rows + independent_rows),
        (len(primary_rows), len(independent_rows)),
        (expected_primary, expected_independent),
        "components",
    )
    primary_names = {row["name"] for row in primary_rows}
    independent_names = {row["name"] for row in independent_rows}
    audit.check(
        "component semantic coverage",
        {
            "equivalent BDL remainder forms",
            "fixture smallness_beta",
            "fixture smallness_alpha",
            "fixture ground_condition",
            "Gevrey majorant sampled",
            "exact finite geometric remainders",
            "exponential moments are factorials",
            "Weyl packet phase equals pi",
            "Galilean endpoint bounded",
            "free relative expectation tends minus one",
        }.issubset(primary_names)
        and {
            "all smallness conditions",
            "zero-radius counterseries ratio",
            "independent Gevrey inequality sample",
            "exact Gevrey asymptotic remainder identity",
            "formal packet phase pi",
            "Gaussian overlap coefficient",
            "sharp unitary norm sandwich",
        }.issubset(independent_names),
        (sorted(primary_names), sorted(independent_names)),
        "required BDL/Gevrey/Weyl assertion names",
        "components",
    )

    audit.check(
        "component verdicts and exact totals",
        primary["verdict"] == independent["verdict"] == "PASS"
        and primary["summary"] == {
            "passed": expected_primary,
            "failed": 0,
            "total": expected_primary,
        }
        and independent["summary"] == {
            "passed": expected_independent,
            "failed": 0,
            "total": expected_independent,
        },
        (primary["summary"], independent["summary"]),
        (expected_primary, expected_independent),
        "components",
    )
    audit.check(
        "component schemas and versions",
        primary["result_number"] == RESULT_NUMBER
        and primary["result_version"] == RESULT_VERSION
        and primary["schema"].endswith("primary-result/1.0")
        and independent["schema"].endswith("independent-result/1.0"),
        (primary["schema"], independent["schema"]),
        "v2.7 primary/independent schemas",
        "components",
    )

    current_hashes = {
        path.relative_to(REPO).as_posix(): normalized_sha256(path)
        for path in (PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE)
    }
    audit.check(
        "primary source hash map",
        primary["source_hashes"]
        == {
            key: value
            for key, value in current_hashes.items()
            if key
            in {
                PRIMARY.relative_to(REPO).as_posix(),
                MANIFEST.relative_to(REPO).as_posix(),
                CERTIFICATE.relative_to(REPO).as_posix(),
            }
        },
        primary["source_hashes"],
        "current primary/manifest/certificate hashes",
        "freshness",
    )
    audit.check(
        "independent source hash map",
        independent["source_hashes"] == current_hashes,
        independent["source_hashes"],
        current_hashes,
        "freshness",
    )

    oracle = manifest["exact_fixture"]
    fixture_keys = (
        "x",
        "n_star",
        "rho",
        "ratio",
        "fixed_order_bound",
        "stretched_exponential_envelope",
        "fixed_to_envelope_ratio",
    )
    primary_fixture = primary["derived"]["truncation_fixture"]
    independent_fixture = independent["derived"]["truncation_fixture"]
    primary_fixture_adapter = {
        "x": primary_fixture["x"],
        "n_star": primary_fixture["n_star"],
        "rho": primary_fixture["rho"],
        "ratio": primary_fixture["ratio"],
        "fixed_order_bound": primary_fixture["fixed_order"],
        "stretched_exponential_envelope": primary_fixture["envelope"],
        "fixed_to_envelope_ratio": primary_fixture["fixed_to_envelope"],
    }
    for key in fixture_keys:
        expected = str(oracle[key])
        audit.check(
            f"cross fixture {key}",
            str(primary_fixture_adapter[key])
            == str(independent_fixture[key])
            == expected,
            (primary_fixture_adapter[key], independent_fixture[key]),
            expected,
            "cross-truncation",
        )
    audit.check(
        "cross carrier norm jump",
        primary["derived"]["weyl_norm_jump"]
        == independent["derived"]["weyl_norm_jump"]
        == "2",
        (
            primary["derived"]["weyl_norm_jump"],
            independent["derived"]["weyl_norm_jump"],
        ),
        ("2", "2"),
        "cross-weyl",
    )
    for field in (
        "standard_sw_optimal_scale_transfer",
        "all_order_convergence",
        "common_alpha_closed",
    ):
        audit.check(
            f"cross scope flag {field}",
            primary["derived"][field] is False
            and independent["derived"][field] is False,
            (primary["derived"][field], independent["derived"][field]),
            (False, False),
            "cross-scope",
        )

    audit.check(
        "manifest identity and correction chain",
        manifest["schema"].endswith("/1.0")
        and manifest["task_id"] == "T-054"
        and manifest["claim_context"] == "C6-SPACETIME-SIGNATURE"
        and manifest["claim_bearing"] is False
        and manifest["result_number"] == RESULT_NUMBER
        and manifest["result_version"] == RESULT_VERSION
        and manifest["exploration_id"] == EXP_ID
        and manifest["continues_exploration_id"] == "EXP-000827",
        (
            manifest["task_id"],
            manifest["claim_context"],
            manifest["result_version"],
            manifest["exploration_id"],
        ),
        ("T-054", "C6-SPACETIME-SIGNATURE", "v2.7", EXP_ID),
        "manifest",
    )
    expected_verification = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
        "primary_result": (
            f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-13-primary-{SLUG}/result.json"
        ),
        "independent_result": (
            f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-13-independent-{SLUG}/result.json"
        ),
        "integrated_result": (
            f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-13-integrated-{SLUG}/result.json"
        ),
    }
    audit.check(
        "manifest exact package and verification paths",
        manifest["package_id"]
        == "PA-CP1-ST8-Q3LOCK-FIXED-RITZ-GEVREY-TWO-TRUNCATION-AND-RAW-CONFIGURATION-WEYL-C0-BOUNDARY-v1"
        and manifest["package_version"] == "1.0.0"
        and manifest["verification"] == expected_verification,
        (manifest["package_id"], manifest["verification"]),
        ("exact v1 package", expected_verification),
        "manifest",
    )
    audit.check(
        "manifest one closure and two negatives",
        manifest["closed_gate_id"] == EXPECTED_CLOSED_GATE
        and manifest["negative_ids"] == EXPECTED_NEGATIVES
        and manifest["gate_resolution"]["closed_subgates"] == [EXPECTED_CLOSED_GATE]
        and manifest["gevrey_two_convergence_boundary"]["negative_id"]
        == manifest["negative_ids"][0]
        and manifest["raw_configuration_weyl_boundary"]["negative_id"]
        == manifest["negative_ids"][1],
        (
            manifest["gate_resolution"]["closed_subgates"],
            manifest["negative_ids"],
        ),
        "one ordered closure and two ordered negatives",
        "manifest",
    )
    audit.check(
        "manifest retains exactly five open parents",
        manifest["gate_resolution"]["retained_open_parents"] == EXPECTED_OPEN_PARENTS,
        manifest["gate_resolution"]["retained_open_parents"],
        EXPECTED_OPEN_PARENTS,
        "manifest",
    )
    audit.check(
        "literature scope and standard-SW firewall",
        "arXiv:1105.0675" in manifest["literature"]["primary"]
        and "Lemma 4.2" in manifest["literature"]["used_scope"]
        and "Eqs. (4.31)-(4.33)" in manifest["literature"]["used_scope"]
        and "not transferred automatically to standard SW"
        in manifest["fixed_ritz_local_sw"]["standard_sw_firewall"],
        manifest["literature"],
        "BDL Section 4.4 with fixed-order Section 4.5 firewall",
        "manifest",
    )
    audit.check(
        "exact proof-first lifecycle",
        manifest["checkpoint_synthesis"]
        == {
            "status": "DEFERRED UNTIL THE NEXT LOGICAL GATE-LEVEL CHECKPOINT",
            "pdf_issued": False,
            "workflow": (
                "Proof-first manifest, certificate, executable checks, formal "
                "authority and run JSON only; no per-lemma or intermediate PDF."
            ),
        },
        manifest["checkpoint_synthesis"],
        "exact three-field deferred lifecycle",
        "lifecycle",
    )

    certificate_tokens = (
        manifest["closed_gate_id"],
        *manifest["negative_ids"],
        "2alpha_M|Lambda||eta|",
        "16alpha_M|Lambda||eta|",
        "lim_(t->0,t!=0)||alpha_t(W_xi)-W_xi||=2",
        "fixed-M",
        "local-SW",
        "standard-SW",
        "No per-lemma or intermediate PDF is issued",
    )
    audit.check(
        "certificate exact theorem and boundary tokens",
        all(token in certificate for token in certificate_tokens)
        and "not claimed to be the exact discrete minimizer" in certificate
        and "does not prove that the actual Q3 series diverges" in certificate
        and "B_{\\rm env}" in certificate
        and "B_{\\rm opt}" not in certificate,
        [token for token in certificate_tokens if token not in certificate],
        [],
        "certificate",
    )
    audit.check(
        "manifest no-overclaim boundary",
        all(
            token in manifest["no_overclaim"]
            for token in (
                "neither a convergent all-order SW transformation",
                "physical-lambda-one",
                "standard-SW optimal-scale",
                "common alpha",
                "broken-sector GNS",
                "Round-1",
                "physical Sector A",
                "Pre-A",
            )
        ),
        manifest["no_overclaim"],
        "all required non-promotion tokens",
        "scope",
    )

    primary_result = REPO / manifest["verification"]["primary_result"]
    independent_result = REPO / manifest["verification"]["independent_result"]
    if staged:
        primary_store_ok = not primary_result.exists() or proof_core(
            json.loads(primary_result.read_text(encoding="utf-8"))
        ) == proof_core(primary)
        independent_store_ok = not independent_result.exists() or proof_core(
            json.loads(independent_result.read_text(encoding="utf-8"))
        ) == proof_core(independent)
    else:
        primary_store_ok = stored_matches(primary_result, primary)
        independent_store_ok = stored_matches(independent_result, independent)
    audit.check(
        "primary stored result lifecycle",
        primary_store_ok,
        primary_result.exists(),
        "absent-or-current staged; exact current formal",
        "stored",
    )
    audit.check(
        "independent stored result lifecycle",
        independent_store_ok,
        independent_result.exists(),
        "absent-or-current staged; exact current formal",
        "stored",
    )

    if not staged:
        explorations = find_exploration()
        expected_gates = [
            manifest["closed_gate_id"],
            *manifest["gate_resolution"]["retained_open_parents"],
        ]
        exploration_ok = (
            len(explorations) == 1
            and explorations[0].get("schema") == "tect/proof-exploration/1.0"
            and explorations[0].get("task_id") == "T-054"
            and explorations[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and explorations[0].get("verdict") == "advanced"
            and explorations[0].get("related")
            == [{"id": "EXP-000827", "relation": "continues"}]
            and explorations[0].get("formal_refs")
            == {
                "events": [],
                "negatives": manifest["negative_ids"],
                "results": [RESULT_NUMBER],
            }
            and explorations[0].get("gate_ids") == expected_gates
        )
        audit.check(
            "EXP-000828 exact semantics",
            exploration_ok,
            explorations,
            "one exact advanced continuation with ordered formal references",
            "formal",
        )
        gates_text = GATES.read_text(encoding="utf-8")
        child_section = gate_section(gates_text, manifest["closed_gate_id"])
        parent_sections = [
            gate_section(gates_text, parent)
            for parent in manifest["gate_resolution"]["retained_open_parents"]
        ]
        audit.check(
            "formal gate topology",
            bool(child_section)
            and re.search(r"(?m)^\*\*Status:\*\* CLOSED\b", child_section) is not None
            and all(
                section
                and re.search(r"(?m)^\*\*Status:\*\* OPEN\b", section) is not None
                for section in parent_sections
            ),
            manifest["gate_resolution"],
            "one CLOSED child and five unique parent headings",
            "formal",
        )
        negatives_text = NEGATIVES.read_text(encoding="utf-8")
        negative_sections = [
            h3_section(negatives_text, negative_id + " --")
            for negative_id in manifest["negative_ids"]
        ]
        audit.check(
            "formal negative authorities",
            all(negative_sections)
            and all(
                token in negative_sections[0]
                for token in (
                    "actual function",
                    "Gevrey-two asymptotic",
                    "radius is zero",
                    "does not prove that the actual Q3",
                )
            )
            and all(
                token in negative_sections[1]
                for token in (
                    "full Q3 Hamiltonian",
                    "lim_(t->0,t!=0)||alpha_t(W_xi)-W_xi||=2",
                    "point-norm",
                    "another carrier remain open",
                )
            ),
            [section[:160] for section in negative_sections],
            "two exact scoped detail sections",
            "formal",
        )
        results_text = RESULTS.read_text(encoding="utf-8")
        result_section = h3_section(results_text, "R-167 --")
        audit.check(
            "R-167 v2.7 formal authority",
            bool(result_section)
            and "R-167 v2.7" in result_section
            and EXP_ID in result_section
            and manifest["closed_gate_id"] in result_section
            and all(identifier in result_section for identifier in manifest["negative_ids"])
            and "No per-lemma or intermediate v2.7 PDF is issued" in result_section,
            result_section[:240],
            True,
            "formal",
        )
        todo_data = json.loads(TODO.read_text(encoding="utf-8"))
        task_matches = [item for item in todo_data.get("tasks", []) if item.get("id") == "T-054"]
        audit.check(
            "T-054 remains in progress with v2.7 boundary",
            len(task_matches) == 1
            and task_matches[0].get("status") == "in_progress"
            and EXP_ID in task_matches[0].get("note", "")
            and "R-167 v2.7" in task_matches[0].get("note", ""),
            task_matches,
            "one in-progress T-054 linked to EXP-000828/R-167 v2.7",
            "formal",
        )
        changelog_records = [
            json.loads(line)
            for line in CHANGELOG.read_text(encoding="utf-8").splitlines()
            if json.loads(line).get("id")
            == "20260813-r-167-v2-7-closes-fixed-ritz-local-sw-gevrey-tw"
        ]
        expected_notes = [
            MANIFEST.relative_to(REPO).as_posix(),
            CERTIFICATE.relative_to(REPO).as_posix(),
            "claims/GATES.md",
            "RESULTS-LEDGER.md",
        ]
        expected_scripts = [
            PRIMARY.relative_to(REPO).as_posix(),
            INDEPENDENT.relative_to(REPO).as_posix(),
            SCRIPT.relative_to(REPO).as_posix(),
        ]
        event_ok = (
            len(changelog_records) == 1
            and changelog_records[0].get("claim_ids")
            == ["C6-SPACETIME-SIGNATURE", EXP_ID, RESULT_NUMBER]
            and changelog_records[0].get("neg_results") == EXPECTED_NEGATIVES
            and changelog_records[0].get("notes") == expected_notes
            and changelog_records[0].get("scripts") == expected_scripts
            and ".pdf" not in changelog_records[0].get("raw", "")
            and ".tex.txt" not in changelog_records[0].get("raw", "")
            and "All five parent gates remain OPEN" in changelog_records[0].get("raw", "")
        )
        audit.check(
            "v2.7 theorem event exact and unique",
            event_ok,
            changelog_records,
            "one exact proof-first event with no PDF",
            "formal",
        )
        roadmap_text = ROADMAP.read_text(encoding="utf-8")
        strategy_text = STRATEGY_INDEX.read_text(encoding="utf-8")
        theorem_map = json.loads(THEOREM_MAP.read_text(encoding="utf-8"))
        audit.check(
            "roadmap strategy and theorem-map linkage",
            EXP_ID in roadmap_text
            and "No per-lemma or" in roadmap_text
            and "intermediate v2.7 PDF is issued" in roadmap_text
            and MANIFEST.name in strategy_text
            and EXP_ID in strategy_text
            and theorem_map.get("version") == "1.19.0"
            and theorem_map.get("research_priority", {}).get("closed_v2_7_scoped_gates")
            == [EXPECTED_CLOSED_GATE]
            and EXP_ID
            in theorem_map.get("research_priority", {}).get("latest_cp1_checkpoint", ""),
            theorem_map.get("research_priority", {}).get("latest_cp1_checkpoint"),
            "v2.7 linked across roadmap/index/map",
            "formal",
        )
        proof_md = PROOF_MAP_MD.read_text(encoding="utf-8")
        proof_json_text = PROOF_MAP_JSON.read_text(encoding="utf-8")
        audit.check(
            "generated proof-map linkage",
            all(
                token in proof_md and token in proof_json_text
                for token in (EXP_ID, EXPECTED_CLOSED_GATE, *EXPECTED_NEGATIVES)
            ),
            "generated linkage",
            True,
            "generated",
        )
        c6 = json.loads(C6_STATUS.read_text(encoding="utf-8"))
        audit.check(
            "C6 claim state unchanged",
            c6.get("tier") == "T1"
            and c6.get("lifecycle") == "ACTIVE"
            and c6.get("evidence_grade") == ["CONDITIONAL"]
            and c6.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            (c6.get("tier"), c6.get("lifecycle"), c6.get("evidence_grade"), c6.get("open_gates")),
            ("T1", "ACTIVE", ["CONDITIONAL"], ["C6-BCC-PREMISE-BLOCKED"]),
            "formal",
        )

    group_counts = Counter(row["group"] for row in audit.rows)
    return {
        "schema": f"tect/{SLUG}-integrated-result/1.0",
        "script_version": __version__,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "verdict": "PASS",
        "summary": {
            "passed": len(audit.rows),
            "failed": 0,
            "total": len(audit.rows),
        },
        "group_counts": dict(sorted(group_counts.items())),
        "derived": {
            "exact_fixture": {key: str(oracle[key]) for key in fixture_keys},
            "weyl_norm_jump": "2",
            "closed_gate_id": manifest["closed_gate_id"],
            "negative_ids": manifest["negative_ids"],
            "retained_open_parents": manifest["gate_resolution"]["retained_open_parents"],
            "standard_sw_optimal_scale_transfer": False,
            "all_order_convergence": False,
            "common_alpha_closed": False,
        },
        "component_summaries": {
            "primary": primary["summary"],
            "independent": independent["summary"],
        },
        "source_hashes": {
            path.relative_to(REPO).as_posix(): normalized_sha256(path)
            for path in (SCRIPT, PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"INTEGRATED PASS {summary['passed']}/{summary['total']}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
