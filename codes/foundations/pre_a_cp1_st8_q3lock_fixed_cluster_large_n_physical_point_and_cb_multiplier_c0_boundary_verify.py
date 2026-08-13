#!/usr/bin/env python3
"""Integrated staged/formal verifier for the R-167 v2.8 package."""

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
SLUG = "pre-a-cp1-st8-q3lock-fixed-cluster-large-n-physical-point-and-cb-multiplier-c0-boundary"
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-integrated-{SLUG}/result.json"

CLOSED_GATE = "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FIXED-COMPLETE-SPECTRAL-CLUSTER-RITZ-LARGE-N-PHYSICAL-LAMBDA-ONE-LOCAL-SW-STRETCHED-EXPONENTIAL-EXTENSIVE-REMAINDER"
NEGATIVE_ID = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0"
RETAINED_BOUNDARY_ID = "NG-2026-08-12-PRE-A-ST8-Q3LOCK-RITZ-CUTOFF-ORDINARY-BOUNDED-OPERATOR-SW-SMALLNESS-UNIFORMITY"
PRIOR_WEYL_NEGATIVE_ID = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-HAMILTONIAN-POINT-NORM-C0"
EXPECTED_OPEN_PARENTS = [
    "PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
]
EXPECTED_PRIMARY_STAGED = 30
EXPECTED_INDEPENDENT_STAGED = 24


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def execute(script: Path, staged: bool) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-v28-child-") as directory:
        output = Path(directory) / "result.json"
        command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
        if staged:
            command.append("--staged")
        completed = subprocess.run(command, cwd=REPO, check=False, capture_output=True, text=True, encoding="utf-8", timeout=120)
        if completed.returncode != 0 or not output.is_file():
            raise AssertionError(f"child failed {script.name}: rc={completed.returncode}; stdout={completed.stdout!r}; stderr={completed.stderr!r}")
        return json.loads(output.read_text(encoding="utf-8"))


def source_imports(path: Path) -> tuple[set[str], list[str]]:
    imports: set[str] = set()
    forbidden_calls: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "__import__",
                "compile",
                "eval",
                "exec",
            }:
                forbidden_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {
                "exec_module",
                "import_module",
                "load_module",
            }:
                forbidden_calls.append(node.func.attr)
    return imports, forbidden_calls


def exact_explorations() -> list[dict[str, Any]]:
    if not EXPLORATIONS.exists():
        return []
    return [record for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines() if (record := json.loads(line)).get("id") == "EXP-000831"]


def proof_core(payload: dict[str, Any]) -> dict[str, Any]:
    projected = dict(payload)
    rows = [row for row in payload.get("assertions", []) if row.get("group") != "formal"]
    projected["assertions"] = rows
    projected["summary"] = {"passed": len(rows), "failed": 0, "total": len(rows)}
    return projected


def stored_matches(path: Path, fresh: dict[str, Any]) -> bool:
    return path.is_file() and json.loads(path.read_text(encoding="utf-8")) == fresh


def gate_section(text: str, gate_id: str) -> str:
    heading = re.compile(rf"(?m)^### \*\*{re.escape(gate_id)}\*\*\s*$")
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        return ""
    following = re.search(r"(?m)^### \*\*", text[matches[0].end() :])
    end = matches[0].end() + following.start() if following else len(text)
    return text[matches[0].start() : end]


def h3_section(text: str, prefix: str) -> str:
    heading = re.compile(rf"(?m)^### {re.escape(prefix)}(?:\s|$)")
    matches = list(heading.finditer(text))
    if len(matches) != 1:
        return ""
    following = re.search(r"(?m)^### ", text[matches[0].end() :])
    end = matches[0].end() + following.start() if following else len(text)
    return text[matches[0].start() : end]


def run(staged: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    primary = execute(PRIMARY, staged)
    independent = execute(INDEPENDENT, staged)
    audit = Audit()

    expected_primary = EXPECTED_PRIMARY_STAGED + (0 if staged else 1)
    expected_independent = EXPECTED_INDEPENDENT_STAGED + (0 if staged else 1)
    audit.check("child verdicts", primary["verdict"] == independent["verdict"] == "PASS", (primary["verdict"], independent["verdict"]), ("PASS", "PASS"), "components")
    audit.check("child exact totals", primary["summary"]["total"] == expected_primary and independent["summary"]["total"] == expected_independent, (primary["summary"], independent["summary"]), (expected_primary, expected_independent), "components")
    audit.check("child unique passing rows", all(row["status"] == "PASS" for row in primary["assertions"] + independent["assertions"]) and len({row["name"] for row in primary["assertions"]}) == expected_primary and len({row["name"] for row in independent["assertions"]}) == expected_independent, (len(primary["assertions"]), len(independent["assertions"])), (expected_primary, expected_independent), "components")

    imports, forbidden_calls = source_imports(INDEPENDENT)
    allowed_imports = {
        "__future__",
        "argparse",
        "ast",
        "decimal",
        "fractions",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "sys",
        "tempfile",
        "typing",
    }
    firewall = (
        imports == allowed_imports
        and imports.issubset(set(sys.stdlib_module_names) | {"__future__"})
        and PRIMARY.stem not in imports
        and not forbidden_calls
    )
    audit.check(
        "independent import firewall",
        firewall,
        {"imports": sorted(imports), "forbidden_calls": sorted(forbidden_calls)},
        {"imports": sorted(allowed_imports), "forbidden_calls": []},
        "components",
    )

    primary_names = {row["name"] for row in primary["assertions"]}
    independent_names = {row["name"] for row in independent["assertions"]}
    audit.check(
        "component semantic coverage",
        {
            "coordinate square identity",
            "periodic strength base",
            "smallness factor",
            "synthetic threshold margin",
            "synthetic admissible order",
            "synthetic ratio below one eighth",
            "synthetic fixed-order fraction",
            "cosine smoothed gap",
            "multiplier lower theorem token",
            "real exact theorem token",
            "Ritz role firewall",
            "physical word firewall",
        }.issubset(primary_names)
        and {
            "exact fixture strength_ceiling",
            "exact fixture smallness_factor",
            "exact fixture order_denominator",
            "exact fixture square_margin",
            "exact fixture n_star",
            "exact fixture ratio_square",
            "exact fixture fixed_order",
            "Gaussian cosine gap",
            "real oscillation",
            "certificate semantic ledger",
        }.issubset(independent_names),
        (sorted(primary_names), sorted(independent_names)),
        "required large-N, multiplier and scope assertion names",
        "components",
    )

    current_hashes = {path.relative_to(REPO).as_posix(): normalized_sha256(path) for path in (PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE)}
    expected_primary_hashes = {key: value for key, value in current_hashes.items() if key != INDEPENDENT.relative_to(REPO).as_posix()}
    audit.check("primary current hashes", primary["source_hashes"] == expected_primary_hashes, primary["source_hashes"], expected_primary_hashes, "freshness")
    audit.check("independent current hashes", independent["source_hashes"] == current_hashes, independent["source_hashes"], current_hashes, "freshness")

    pfix = primary["derived"]["large_n_fixture"]
    ifix = independent["derived"]["large_n_fixture"]
    adapters = {
        "coordinate_constant": (pfix["coordinate_constant"], ifix["coordinate_constant"], "10"),
        "bond_base": (pfix["bond_base"], ifix["bond_base"], "20"),
        "strength_ceiling": (pfix["strength_ceiling"], ifix["strength_ceiling"], "121"),
        "smallness_factor": (pfix["smallness_factor"], ifix["smallness_factor"], "3872"),
        "order_denominator": (pfix["order_denominator"], ifix["order_denominator"], "968"),
        "envelope_prefactor": (pfix["envelope_prefactor"], ifix["envelope_prefactor"], "1936"),
        "threshold_square_margin": (pfix["threshold_square_margin"], ifix["square_margin"], "113"),
        "n_star": (str(pfix["n_star"]), ifix["n_star"], "2"),
        "fixed_order_bound": (pfix["fixed_order_bound"], f"{ifix['fixed_order']} |Lambda|", "7086244/1874161 |Lambda|"),
    }
    for key, values in adapters.items():
        audit.check(f"cross fixture {key}", values[0] == values[1] == values[2], values[:2], values[2], "cross")

    pscope = {key: primary["derived"][key] for key in ("uniform_in_M", "full_oscillator_cutoff_removed", "standard_sw_growing_order", "common_alpha_closed")}
    iscope = {key: independent["derived"][key] for key in pscope}
    audit.check("cross no-overclaim flags", pscope == iscope == {key: False for key in pscope}, (pscope, iscope), "all false", "scope")

    expected_verification = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
        "primary_result": f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-13-primary-{SLUG}/result.json",
        "independent_result": f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-13-independent-{SLUG}/result.json",
        "integrated_result": f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-13-integrated-{SLUG}/result.json",
    }
    audit.check("manifest identity", manifest["schema"] == f"tect/{SLUG}/1.0" and manifest["package_id"] == "PA-CP1-ST8-Q3LOCK-FIXED-CLUSTER-LARGE-N-PHYSICAL-POINT-AND-CB-MULTIPLIER-C0-BOUNDARY-v1" and manifest["package_version"] == "1.0.0" and manifest["result_number"] == "R-167" and manifest["result_version"] == "v2.8" and manifest["exploration_id"] == "EXP-000831" and manifest["continues_exploration_id"] == "EXP-000828" and manifest["claim_bearing"] is False, (manifest["result_version"], manifest["exploration_id"], manifest["continues_exploration_id"]), ("v2.8", "EXP-000831", "EXP-000828"), "manifest")
    audit.check("manifest exact IDs", manifest["closed_gate_id"] == CLOSED_GATE and manifest["negative_ids"] == [NEGATIVE_ID] and manifest["retained_boundary_id"] == RETAINED_BOUNDARY_ID and manifest["gate_resolution"]["closed_subgates"] == [CLOSED_GATE] and manifest["gate_resolution"]["retained_open_parents"] == EXPECTED_OPEN_PARENTS, (manifest["closed_gate_id"], manifest["negative_ids"], manifest["retained_boundary_id"], manifest["gate_resolution"]), (CLOSED_GATE, [NEGATIVE_ID], RETAINED_BOUNDARY_ID, EXPECTED_OPEN_PARENTS), "manifest")
    audit.check("manifest exact paths", manifest["verification"] == expected_verification, manifest["verification"], expected_verification, "manifest")
    low_high = manifest["fixed_complete_spectral_cluster_ritz"]["low_high_split"]
    audit.check("manifest fixed-cluster role", "finite onsite Ritz Hilbert space is ran Pi_(M,N)" in low_high and "rank two" in low_high and "infinite complement is not part" in low_high, low_high, "Pi Ritz; P rank two", "manifest")
    audit.check("manifest uniformized BDL witnesses", "Rerunning the BDL majorant" in manifest["physical_point_bound"]["uniform_bdl_witnesses"] and "common to all N" in manifest["physical_point_bound"]["uniform_bdl_witnesses"], manifest["physical_point_bound"]["uniform_bdl_witnesses"], "proof-uniformized witnesses", "manifest")
    audit.check("manifest multiplier supersession", "strictly strengthens" in manifest["configuration_multiplier_boundary"]["nonduplication"] and "immutable history" in manifest["configuration_multiplier_boundary"]["nonduplication"], manifest["configuration_multiplier_boundary"]["nonduplication"], "strict strengthening with immutable history", "manifest")
    audit.check("deferred no-PDF lifecycle", manifest["checkpoint_synthesis"] == {"status": "DEFERRED UNTIL THE NEXT LOGICAL GATE-LEVEL CHECKPOINT", "pdf_issued": False, "workflow": "Proof-first manifest, certificate, executable checks, formal authority and run JSON only; no per-lemma or intermediate PDF."} and "No per-lemma or intermediate v2.8 PDF is issued" in certificate, manifest["checkpoint_synthesis"], "exact deferred three-field record; no PDF", "scope")
    audit.check("certificate exact Hamiltonian identity", "H_(M,N)(1)=Pi_Lambda[H_N-|Lambda|epsilon_(0,N)]Pi_Lambda" in certificate, "identity present" if "H_(M,N)(1)=" in certificate else "missing", "exact restricted endpoint identity", "certificate")

    primary_result = REPO / manifest["verification"]["primary_result"]
    independent_result = REPO / manifest["verification"]["independent_result"]
    if staged:
        primary_store_ok = not primary_result.exists() or proof_core(json.loads(primary_result.read_text(encoding="utf-8"))) == proof_core(primary)
        independent_store_ok = not independent_result.exists() or proof_core(json.loads(independent_result.read_text(encoding="utf-8"))) == proof_core(independent)
    else:
        primary_store_ok = stored_matches(primary_result, primary)
        independent_store_ok = stored_matches(independent_result, independent)
    audit.check("primary stored result lifecycle", primary_store_ok, primary_result.exists(), "absent-or-current staged; exact current formal", "lifecycle")
    audit.check("independent stored result lifecycle", independent_store_ok, independent_result.exists(), "absent-or-current staged; exact current formal", "lifecycle")

    if not staged:
        explorations = exact_explorations()
        expected_gates = [CLOSED_GATE, *EXPECTED_OPEN_PARENTS]
        exploration_ok = (
            len(explorations) == 1
            and explorations[0].get("schema") == "tect/proof-exploration/1.0"
            and explorations[0].get("task_id") == "T-054"
            and explorations[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
            and explorations[0].get("verdict") == "advanced"
            and explorations[0].get("related") == [{"id": "EXP-000828", "relation": "continues"}]
            and explorations[0].get("formal_refs")
            == {
                "events": [],
                "negatives": [NEGATIVE_ID, RETAINED_BOUNDARY_ID],
                "results": ["R-167"],
            }
            and explorations[0].get("gate_ids") == expected_gates
            and "No v2.8 PDF is issued" in explorations[0].get("boundary", "")
            and "full oscillator" in explorations[0].get("next_action", "")
        )
        audit.check("EXP-000831 exact formal record", exploration_ok, explorations, "one exact advanced continuation of EXP-000828", "formal")

        gates_text = GATES.read_text(encoding="utf-8")
        child_section = gate_section(gates_text, CLOSED_GATE)
        parent_sections = [gate_section(gates_text, parent) for parent in EXPECTED_OPEN_PARENTS]
        audit.check(
            "formal gate topology",
            bool(child_section)
            and re.search(r"(?m)^\*\*Status:\*\* CLOSED\b", child_section) is not None
            and "EXP-000831 / R-167 v2.8" in child_section
            and all(
                section
                and re.search(r"(?m)^\*\*Status:\*\* OPEN\b", section) is not None
                and "EXP-000831 / R-167 v2.8" in section
                for section in parent_sections
            ),
            [child_section[:120], *[section[:120] for section in parent_sections]],
            "one CLOSED child and five annotated OPEN parents",
            "formal",
        )

        negatives_text = NEGATIVES.read_text(encoding="utf-8")
        negative_section = h3_section(negatives_text, NEGATIVE_ID + " --")
        prior_weyl_section = h3_section(negatives_text, PRIOR_WEYL_NEGATIVE_ID + " --")
        audit.check(
            "formal multiplier negative and retained history",
            bool(negative_section)
            and all(
                token in negative_section
                for token in (
                    "liminf_(t->0,t!=0)||alpha_t(M_f)-M_f||>=diam f(R^d)",
                    "osc(f)=sup f-inf f",
                    "strictly strengthens",
                    "another carrier",
                )
            )
            and bool(prior_weyl_section)
            and "lim_(t->0,t!=0)||alpha_t(W_xi)-W_xi||=2" in prior_weyl_section,
            (negative_section[:180], prior_weyl_section[:180]),
            "new C_b boundary plus immutable v2.7 Weyl authority",
            "formal",
        )

        results_text = RESULTS.read_text(encoding="utf-8")
        result_section = h3_section(results_text, "R-167 --")
        audit.check(
            "R-167 v2.8 formal authority",
            bool(result_section)
            and "R-167 v2.8" in result_section
            and "EXP-000831" in result_section
            and CLOSED_GATE in result_section
            and NEGATIVE_ID in result_section
            and "No v2.8 PDF is issued" in result_section
            and "All five parent gates remain OPEN" in result_section
            and "**Proven in:** C6 / [R-167 v2.8 certificate]" in result_section
            and "R-167 v2.7 certificate" in result_section
            and "remain the prior proof-first authority" in result_section
            and "remain the latest issued R-167 evidence" in result_section,
            result_section[:240],
            "exact v2.8 proof-first result section",
            "formal",
        )

        todo_data = json.loads(TODO.read_text(encoding="utf-8"))
        task_matches = [item for item in todo_data.get("tasks", []) if item.get("id") == "T-054"]
        audit.check(
            "T-054 remains in progress with v2.8 boundary",
            len(task_matches) == 1
            and task_matches[0].get("status") == "in_progress"
            and "EXP-000831 / R-167 v2.8" in task_matches[0].get("note", "")
            and "full oscillator" in task_matches[0].get("note", ""),
            task_matches,
            "one in-progress T-054 linked to EXP-000831/R-167 v2.8",
            "formal",
        )

        expected_event_header = (
            "[R-167 v2.8 closes fixed-cluster large-N physical-point local-SW remainder "
            "and strengthens the configuration-multiplier boundary] - 2026-08-13"
        )
        changelog_records = [
            json.loads(line)
            for line in CHANGELOG.read_text(encoding="utf-8").splitlines()
            if json.loads(line).get("header") == expected_event_header
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
            and changelog_records[0].get("claim_ids") == ["C6-SPACETIME-SIGNATURE", "EXP-000831", "R-167"]
            and changelog_records[0].get("neg_results") == [NEGATIVE_ID]
            and changelog_records[0].get("notes") == expected_notes
            and changelog_records[0].get("scripts") == expected_scripts
            and ".pdf" not in changelog_records[0].get("raw", "")
            and ".tex.txt" not in changelog_records[0].get("raw", "")
            and "All five parents remain OPEN" in changelog_records[0].get("raw", "")
            and "No v2.8 PDF is issued" in changelog_records[0].get("raw", "")
        )
        audit.check("v2.8 theorem event exact and unique", event_ok, changelog_records, "one exact proof-first event with no PDF", "formal")

        roadmap_text = ROADMAP.read_text(encoding="utf-8")
        strategy_text = STRATEGY_INDEX.read_text(encoding="utf-8")
        theorem_map = json.loads(THEOREM_MAP.read_text(encoding="utf-8"))
        audit.check(
            "roadmap strategy and theorem-map linkage",
            "EXP-000831 / R-167 v2.8" in roadmap_text
            and "No v2.8 PDF is issued" in roadmap_text
            and MANIFEST.name in strategy_text
            and "EXP-000831" in strategy_text
            and theorem_map.get("version") == "1.20.0"
            and theorem_map.get("research_priority", {}).get("closed_v2_8_scoped_gates") == [CLOSED_GATE]
            and "EXP-000831 / R-167 v2.8" in theorem_map.get("research_priority", {}).get("latest_cp1_checkpoint", ""),
            theorem_map.get("research_priority", {}).get("latest_cp1_checkpoint"),
            "v2.8 linked across roadmap/index/map",
            "formal",
        )

        proof_md = PROOF_MAP_MD.read_text(encoding="utf-8")
        proof_json_text = PROOF_MAP_JSON.read_text(encoding="utf-8")
        audit.check(
            "generated proof-map linkage",
            all(token in proof_md and token in proof_json_text for token in ("EXP-000831", CLOSED_GATE, NEGATIVE_ID)),
            "generated linkage",
            True,
            "formal",
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
        "result_number": "R-167",
        "result_version": "v2.8",
        "verdict": "PASS",
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "component_summaries": {"primary": primary["summary"], "independent": independent["summary"]},
        "group_counts": dict(sorted(group_counts.items())),
        "derived": {
            "closed_gate_id": CLOSED_GATE,
            "negative_ids": [NEGATIVE_ID],
            "fixed_order_bound": pfix["fixed_order_bound"],
            "uniform_in_M": False,
            "full_oscillator_cutoff_removed": False,
            "standard_sw_growing_order": False,
            "common_alpha_closed": False,
        },
        "source_hashes": {path.relative_to(REPO).as_posix(): normalized_sha256(path) for path in (SCRIPT, PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE)},
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
    print(f"INTEGRATED PASS {payload['summary']['passed']}/{payload['summary']['total']}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
