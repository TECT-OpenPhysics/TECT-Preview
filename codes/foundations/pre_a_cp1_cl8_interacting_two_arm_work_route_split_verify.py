#!/usr/bin/env python3
"""Integrated publication verifier for the driven 1D CL8 interacting route."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-interacting-two-arm-work-route-split"
CANDIDATE_ID = "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-1D-Q3-DRIVEN-ALL-CUT-WORK-TRANSPORT-AND-DIRECT-ORDER-MICROCUT-NOGO"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_SCRIPT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT_SCRIPT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENT_PATHS = (
    REPO / "strategy/pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
    REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json",
)
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-integrated-{SLUG}/result.json"
C6_STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
TODO_JSON = REPO / "todo/todo.json"
CHANGELOG_JSONL = REPO / "changelog/log.jsonl"
CATALOG_MD = REPO / "CATALOG.md"
CATALOG_JSON = REPO / "verification/catalog.json"
PROOF_MAP_MD = REPO / "theory/proof-evidence-map.md"
PROOF_MAP_JSON = REPO / "verification/proof-evidence-map.json"
LINEAGE = REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md"
EXPECTED_PRIMARY_F0 = 141
EXPECTED_INDEPENDENT_F0 = 134
EXPECTED_PRIMARY_F1 = 126
EXPECTED_INDEPENDENT_F1 = 116
EXPECTED_EXPLORATION = "EXP-000749"
EXPECTED_NEGATIVE = "NG-2026-08-04-PRE-A-CP1-CL8-EXACT-ORDER-EVERY-MICROCUT-SIDEWAYS"
NEXT_GATE = "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER"


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_child(script: Path, output: Path, profile: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), "--profile", profile, "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {script.name} {profile}\nstdout={completed.stdout}\nstderr={completed.stderr}")
    return load_json(output)


def float_paths(value: Any, prefix: str = "root") -> list[str]:
    found: list[str] = []
    if isinstance(value, float):
        found.append(prefix)
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(float_paths(item, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(float_paths(item, f"{prefix}[{index}]"))
    return found


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def build_payload() -> dict[str, Any]:
    audit = Audit()
    required_files = (
        PRIMARY_SCRIPT, INDEPENDENT_SCRIPT, MANIFEST, CERTIFICATE, *PARENT_PATHS,
        PRIMARY_RESULT, INDEPENDENT_RESULT, C6_STATUS, NEGATIVE_REGISTRY,
        EXPLORATIONS, STRATEGY_INDEX, TODO_JSON, CHANGELOG_JSONL,
        CATALOG_MD, CATALOG_JSON, PROOF_MAP_MD, PROOF_MAP_JSON, LINEAGE,
    )
    for path in required_files:
        audit.check(f"required file {path.name}", path.is_file(), path.is_file(), True, "files")

    manifest = load_json(MANIFEST)
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    c6_status = load_json(C6_STATUS)
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    exploration_records = [json.loads(line) for line in EXPLORATIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")
    todo_data = load_json(TODO_JSON)
    changelog_records = [json.loads(line) for line in CHANGELOG_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    expected_parent_ids = [load_json(path)["candidate_id"] for path in PARENT_PATHS]

    with tempfile.TemporaryDirectory(prefix="tect-cl8-interacting-two-arm-") as directory:
        temporary = Path(directory)
        primary_f0 = run_child(PRIMARY_SCRIPT, temporary / "primary-f0.json", "f0")
        independent_f0 = run_child(INDEPENDENT_SCRIPT, temporary / "independent-f0.json", "f0")
        primary_f1 = run_child(PRIMARY_SCRIPT, temporary / "primary-f1.json", "f1")
        independent_f1 = run_child(INDEPENDENT_SCRIPT, temporary / "independent-f1.json", "f1")

    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    audit.check("stored primary fresh", stored_primary == primary_f0, sha256(PRIMARY_RESULT), "fresh rerun equality", "children")
    audit.check("stored independent fresh", stored_independent == independent_f0, sha256(INDEPENDENT_RESULT), "fresh rerun equality", "children")
    expected_counts = (
        ("primary f0", primary_f0, EXPECTED_PRIMARY_F0),
        ("independent f0", independent_f0, EXPECTED_INDEPENDENT_F0),
        ("primary f1", primary_f1, EXPECTED_PRIMARY_F1),
        ("independent f1", independent_f1, EXPECTED_INDEPENDENT_F1),
    )
    for label, child, expected in expected_counts:
        audit.check(f"{label} count", child["assertion_summary"] == {"passed": expected, "total": expected}, child["assertion_summary"], expected, "children")
        audit.check(f"{label} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "children")
        audit.check(f"{label} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "children")
        audit.check(f"{label} parents", child["parent_ids"] == expected_parent_ids, child["parent_ids"], expected_parent_ids, "children")
        audit.check(f"{label} claim nonbearing", child["claim_bearing"] is False, child["claim_bearing"], False, "children")
        audit.check(f"{label} next gate", child["next_gate"] == NEXT_GATE, child["next_gate"], NEXT_GATE, "children")
        audit.check(f"{label} no floats", float_paths(child) == [], float_paths(child), [], "children")
    audit.check("f0 cross agreement", primary_f0["cross_invariants"] == independent_f0["cross_invariants"], primary_f0["cross_invariants"], independent_f0["cross_invariants"], "cross")
    audit.check("f1 cross agreement", primary_f1["cross_invariants"] == independent_f1["cross_invariants"], primary_f1["cross_invariants"], independent_f1["cross_invariants"], "cross")
    audit.check("f0 q-only cross sign", primary_f0["cross_invariants"]["qonly_cross_coefficient"] == "3/64", primary_f0["cross_invariants"]["qonly_cross_coefficient"], "3/64", "cross")
    audit.check("f1 q-only cross sign", primary_f1["cross_invariants"]["qonly_cross_coefficient"] == "-7/360", primary_f1["cross_invariants"]["qonly_cross_coefficient"], "-7/360", "cross")
    audit.check("f0 and f1 differ", primary_f0["cross_invariants"] != primary_f1["cross_invariants"], [primary_f0["cross_invariants"]["profile"], primary_f1["cross_invariants"]["profile"]], ["f0", "f1"], "cross")
    audit.check("scope agreement", primary_f0["scope"] == independent_f0["scope"] == primary_f1["scope"] == independent_f1["scope"] == manifest["scope"], "all equal", "all equal", "cross")
    audit.check("negative agreement", primary_f0["negative_ids"] == independent_f0["negative_ids"] == [EXPECTED_NEGATIVE], primary_f0["negative_ids"], [EXPECTED_NEGATIVE], "cross")

    primary_imports = imported_roots(PRIMARY_SCRIPT)
    independent_imports = imported_roots(INDEPENDENT_SCRIPT)
    independent_text = INDEPENDENT_SCRIPT.read_text(encoding="utf-8")
    audit.check("scripts differ", sha256(PRIMARY_SCRIPT) != sha256(INDEPENDENT_SCRIPT), [sha256(PRIMARY_SCRIPT), sha256(INDEPENDENT_SCRIPT)], "different", "independence")
    audit.check("primary uses SymPy", "sympy" in primary_imports, sorted(primary_imports), "sympy", "independence")
    audit.check("independent no SymPy or NumPy", not independent_imports.intersection({"sympy", "numpy"}), sorted(independent_imports), "no sympy/numpy", "independence")
    audit.check("independent no primary import", PRIMARY_SCRIPT.stem not in independent_text, PRIMARY_SCRIPT.stem in independent_text, False, "independence")
    audit.check("independent Fraction", "from fractions import Fraction" in independent_text, "from fractions import Fraction" in independent_text, True, "independence")
    audit.check("independent sparse derivative", "def differentiate(" in independent_text and "def q3_polynomial(" in independent_text, ["def differentiate(" in independent_text, "def q3_polynomial(" in independent_text], [True, True], "independence")
    audit.check("independent forward Jet", "class Jet:" in independent_text, "class Jet:" in independent_text, True, "independence")
    audit.check("independent exact rank", "def rank(" in independent_text and "def determinant(" in independent_text, ["def rank(" in independent_text, "def determinant(" in independent_text], [True, True], "independence")
    for label, child, script in (("primary", primary_f0, PRIMARY_SCRIPT), ("independent", independent_f0, INDEPENDENT_SCRIPT)):
        audit.check(f"{label} script hash", child["source_sha256"]["script"] == sha256(script), child["source_sha256"]["script"], sha256(script), "hashes")
        audit.check(f"{label} manifest hash", child["source_sha256"]["manifest"] == sha256(MANIFEST), child["source_sha256"]["manifest"], sha256(MANIFEST), "hashes")
        audit.check(f"{label} certificate hash", child["source_sha256"]["certificate"] == sha256(CERTIFICATE), child["source_sha256"]["certificate"], sha256(CERTIFICATE), "hashes")

    audit.check("manifest candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    audit.check("manifest result narrowed", manifest["result_id"] == RESULT_ID and "PARENT-NOGO" not in manifest["result_id"], manifest["result_id"], RESULT_ID, "manifest")
    audit.check("manifest parents", manifest["parent_ids"] == expected_parent_ids, manifest["parent_ids"], expected_parent_ids, "manifest")
    audit.check("manifest T0", manifest["authority"].startswith("T0 "), manifest["authority"], "T0", "manifest")
    audit.check("manifest claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "manifest")
    audit.check("manifest negative", manifest["negative_ids"] == [EXPECTED_NEGATIVE], manifest["negative_ids"], [EXPECTED_NEGATIVE], "manifest")
    audit.check("driven status", manifest["gate_resolution"]["status"].startswith("DRIVEN WORK-AND-TRANSPORT BRANCH CLOSED IN INSERTED 1D"), manifest["gate_resolution"]["status"], "driven inserted 1D", "manifest")
    audit.check("next gate exact", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "manifest")
    audit.check("closed subgates narrowed", all("DRIVEN-1D" in item for item in manifest["gate_resolution"]["closed_subgates"]), manifest["gate_resolution"]["closed_subgates"], "all DRIVEN-1D", "manifest")
    audit.check("single-leg quantum drift", "single-leg Dhat_h" in manifest["quantum_forward_cut"]["local_unitary"], manifest["quantum_forward_cut"]["local_unitary"], "single-leg", "manifest")
    audit.check("projection determinant wording", "projection-block determinant" in manifest["local_interacting_gate"]["cross_determinants"], manifest["local_interacting_gate"]["cross_determinants"], "projection-block", "manifest")

    for section in range(1, 14):
        audit.check(f"certificate section {section}", f"## {section}." in certificate_text, f"## {section}." in certificate_text, True, "certificate")
    anchors = (
        "section-1-verdict-and-proof-boundary",
        "section-2-authorities-model-and-inserted-data",
        "section-3-exact-1d-q3-term-ownership",
        "section-4-local-driven-interacting-gate",
        "section-5-global-mixed-inverses",
        "section-6-open-rectangle-all-cut-theorem",
        "section-7-periodic-companion-and-ordering-boundary",
        "section-8-exact-work-ledger",
        "section-9-interacting-bh-cut-unitaries-and-density-transport",
        "section-10-direct-order-microcut-no-go",
        "section-11-gate-resolution-and-next-contract",
        "section-12-devils-advocate-audit",
        "section-13-reproduction",
    )
    for anchor in anchors:
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate_text, f'id="{anchor}"' in certificate_text, True, "certificate")
    phrases = (
        "sum_(j in Z/MZ) V_j=U_a",
        "four `D_h` shears",
        "det partial(N1)/partial(S1)=gamma^16",
        "binomial(m+n,m)",
        "sum_(target cut) I_nu-sum_(input arms) I_nu=sum_(v in ideal) W_v",
        "P dot g(Q)+g(Q) dot P",
        "rank is at most eight",
        NEXT_GATE,
    )
    for phrase in phrases:
        audit.check(f"certificate phrase {phrase}", phrase in certificate_text, phrase in certificate_text, True, "certificate")

    negative_anchor = EXPECTED_NEGATIVE.lower()
    audit.check("negative summary", f"[{EXPECTED_NEGATIVE}]" in registry_text, f"[{EXPECTED_NEGATIVE}]" in registry_text, True, "records")
    audit.check("negative section", f"### {EXPECTED_NEGATIVE}" in registry_text, f"### {EXPECTED_NEGATIVE}" in registry_text, True, "records")
    audit.check("negative anchor", f'id="{negative_anchor}"' in registry_text, f'id="{negative_anchor}"' in registry_text, True, "records")
    audit.check("negative direct scope", "This is not a no-go for all interacting characteristic circuits" in registry_text, "This is not a no-go for all interacting characteristic circuits" in registry_text, True, "records")
    manifest_ref = f"strategy/{SLUG}-manifest.json"
    matching = [record for record in exploration_records if record.get("id") == EXPECTED_EXPLORATION]
    audit.check("exploration exact id", len(matching) == 1, [record.get("id") for record in matching], [EXPECTED_EXPLORATION], "records")
    route = matching[0]
    audit.check("exploration evidence", any(reference.startswith(manifest_ref) for reference in route["evidence_refs"]), route["evidence_refs"], manifest_ref, "records")
    audit.check("exploration task", route["task_id"] == "T-054", route["task_id"], "T-054", "records")
    audit.check("exploration verdict", route["verdict"] == "advanced", route["verdict"], "advanced", "records")
    audit.check("exploration no formal gate", route["gate_ids"] == [], route["gate_ids"], [], "records")
    audit.check("exploration no formal result", route["formal_refs"]["results"] == [], route["formal_refs"]["results"], [], "records")
    audit.check("exploration negative", route["formal_refs"]["negatives"] == [EXPECTED_NEGATIVE], route["formal_refs"]["negatives"], [EXPECTED_NEGATIVE], "records")
    audit.check("exploration continues passive", route["related"] == [{"id": "EXP-000745", "relation": "continues"}], route["related"], [{"id": "EXP-000745", "relation": "continues"}], "records")
    audit.check("strategy index", f"{SLUG}-manifest.json" in index_text and "T0 inserted-1D driven interacting work/transport route" in index_text, f"{SLUG}-manifest.json" in index_text, True, "records")
    task = next(item for item in todo_data["tasks"] if item["id"] == "T-054")
    audit.check("TODO exploration", EXPECTED_EXPLORATION in task["note"], EXPECTED_EXPLORATION in task["note"], True, "records")
    audit.check("TODO next gate", NEXT_GATE in task["note"], NEXT_GATE in task["note"], True, "records")
    audit.check("TODO open bridge", "1D-to-3D Q3 parent bridge" in task["note"], "1D-to-3D Q3 parent bridge" in task["note"], True, "records")
    events = [record for record in changelog_records if manifest_ref in record.get("notes", [])]
    audit.check("one changelog event", len(events) == 1, [record.get("id") for record in events], "one", "records")
    audit.check("changelog negative", events[0]["neg_results"] == [EXPECTED_NEGATIVE], events[0]["neg_results"], [EXPECTED_NEGATIVE], "records")

    audit.check("C6 id", c6_status["id"] == "C6-SPACETIME-SIGNATURE", c6_status["id"], "C6-SPACETIME-SIGNATURE", "C6")
    audit.check("C6 tier", c6_status["tier"] == "T1", c6_status["tier"], "T1", "C6")
    audit.check("C6 lifecycle", c6_status["lifecycle"] == "ACTIVE", c6_status["lifecycle"], "ACTIVE", "C6")
    audit.check("C6 evidence", c6_status["evidence_grade"] == ["CONDITIONAL"], c6_status["evidence_grade"], ["CONDITIONAL"], "C6")
    audit.check("C6 gate", c6_status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], c6_status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "C6")

    true_scope = tuple(key for key, value in manifest["scope"].items() if value is True)
    false_scope = tuple(key for key, value in manifest["scope"].items() if value is False)
    audit.check("scope partition", len(true_scope) + len(false_scope) == len(manifest["scope"]), [len(true_scope), len(false_scope)], len(manifest["scope"]), "scope")
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    for required_false in (
        "original_3D_Q3LOCK_regulator", "inherited_CL8_DKD_dynamics_implemented",
        "controller_free_common_parent", "positive_common_invariant_established",
        "stationary_trace_class_Floquet_state_established", "physical_vacuum",
        "below_empty_space", "continuum_quantum_state", "Hadamard_state",
        "C0_closed", "N1_closed", "N2_closed", "N3_closed", "N4_closed", "N5_closed",
        "C6_advanced", "CP1_complete", "Pre_A_complete",
    ):
        audit.check(f"required false {required_false}", manifest["scope"][required_false] is False, manifest["scope"][required_false], False, "scope")

    catalog_text = CATALOG_MD.read_text(encoding="utf-8") + CATALOG_JSON.read_text(encoding="utf-8")
    proof_text = PROOF_MAP_MD.read_text(encoding="utf-8") + PROOF_MAP_JSON.read_text(encoding="utf-8")
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    public_paths = (
        f"strategy/{SLUG}-manifest.json", f"strategy/{SLUG}-certificate-260804.md",
        f"codes/foundations/{SLUG.replace('-', '_')}.py",
        f"codes/foundations/{SLUG.replace('-', '_')}_independent.py",
        f"codes/foundations/{SLUG.replace('-', '_')}_verify.py",
        f"2026-08-04-primary-{SLUG}", f"2026-08-04-independent-{SLUG}",
    )
    for item in public_paths:
        audit.check(f"catalog surface {item}", item in catalog_text, item in catalog_text, True, "generated")
    audit.check("proof map candidate", CANDIDATE_ID in proof_text, CANDIDATE_ID in proof_text, True, "generated")
    audit.check("proof map exploration", EXPECTED_EXPLORATION in proof_text, EXPECTED_EXPLORATION in proof_text, True, "generated")
    audit.check("proof map negative", EXPECTED_NEGATIVE in proof_text, EXPECTED_NEGATIVE in proof_text, True, "generated")
    audit.check("lineage primary", f"2026-08-04-primary-{SLUG}" in lineage_text, f"2026-08-04-primary-{SLUG}" in lineage_text, True, "generated")
    audit.check("lineage independent", f"2026-08-04-independent-{SLUG}" in lineage_text, f"2026-08-04-independent-{SLUG}" in lineage_text, True, "generated")

    forbidden = (
        "Pre-A is complete", "physical vacuum is selected", "below empty space is proved",
        "the inherited CL8 parent is proved", "the original three-dimensional Q3LOCK regulator is proved",
        "strict continuous-variable dual-unitarity is proved", "speed of light is derived",
    )
    public_text = manifest["statement"] + "\n" + manifest["no_overclaim"] + "\n" + certificate_text
    for phrase in forbidden:
        audit.check(f"no overclaim {phrase}", phrase not in public_text, phrase in public_text, False, "no_overclaim")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": expected_parent_ids,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "child_assertion_counts": {
            "primary_f0": EXPECTED_PRIMARY_F0,
            "independent_f0": EXPECTED_INDEPENDENT_F0,
            "primary_f1": EXPECTED_PRIMARY_F1,
            "independent_f1": EXPECTED_INDEPENDENT_F1,
        },
        "child_result_sha256": {"primary": sha256(PRIMARY_RESULT), "independent": sha256(INDEPENDENT_RESULT)},
        "authority_sha256": {str(path.relative_to(REPO)).replace("\\", "/"): sha256(path) for path in PARENT_PATHS},
        "cross_invariants": primary_f0["cross_invariants"],
        "hostile_cross_invariants": primary_f1["cross_invariants"],
        "scope": manifest["scope"],
        "negative_ids": [EXPECTED_NEGATIVE],
        "exploration_id": EXPECTED_EXPLORATION,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": NEXT_GATE,
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE),
            "primary_script": sha256(PRIMARY_SCRIPT), "independent_script": sha256(INDEPENDENT_SCRIPT),
            "negative_registry": sha256(NEGATIVE_REGISTRY), "explorations": sha256(EXPLORATIONS),
            "strategy_index": sha256(STRATEGY_INDEX), "todo_json": sha256(TODO_JSON),
            "changelog_jsonl": sha256(CHANGELOG_JSONL), "c6_status": sha256(C6_STATUS),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} integrated: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
