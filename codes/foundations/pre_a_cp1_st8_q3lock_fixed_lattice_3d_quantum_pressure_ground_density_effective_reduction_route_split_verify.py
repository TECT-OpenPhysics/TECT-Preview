#!/usr/bin/env python3
"""Integrated verifier for EXP773 fixed-lattice ST8/Q3LOCK thermodynamics."""

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
from typing import Any, Iterable


__version__ = "0.1.1"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY"
EXPLORATION_ID = "EXP-000780"
CHANGELOG_ID = "20260804-exp-000773-close-fixed-lattice-st8-q3lock-scala"
PARENT_EXPLORATIONS = {("EXP-000719", "continues"), ("EXP-000779", "continues")}
PARENT_IDS = [
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-CP1-CL8-Q3-SOURCE-PRESSURE-PHASE-DIAGNOSTIC-PHYSICAL-REFERENCE-AND-3D-PARENT-ROUTE-SPLIT-v0",
]
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-PARENT-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE"
NEGATIVE_IDS: list[str] = []
REUSED_NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-TRANSVERSE-ZERO-RESTRICTION-AS-INTERACTING-MARGINAL",
    "NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY",
    "NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR",
]
CLOSED_SUBGATES = [
    "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-OPEN-RECTANGLE-SOURCE-PRESSURE-AND-GROUND-DENSITY",
    "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-PERIODIC-CUBE-BOUNDARY-INDEPENDENCE",
    "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-UNIFORM-ZERO-TEMPERATURE-DENSITY-INTERCHANGE",
    "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-ADDITIVE-SCALAR-COVARIANCE",
]
OPEN_SUBGATES = [
    "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE",
    "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-GIBBS-AND-GROUND-STATE-CONSTRUCTION",
    "PA-CP1-ST8-Q3LOCK-TO-CL8-Q3-EFFECTIVE-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-INTERACTING-CONTINUUM-AND-COUNTERTERMS",
    "PA-CP1-ST8-Q3LOCK-PHYSICAL-EMPTY-SPACE-REFERENCE",
    "PA-PRE-A-C0-N1-N5-VALIDATION",
]
POSITIVE_SCOPE = (
    "exact_registered_unweighted_ST8_Q3LOCK_family",
    "fixed_block_origin_retained",
    "finite_volume_self_adjoint_compact_resolvent",
    "open_rectangular_source_pressure_limit",
    "open_rectangular_ground_energy_density_limit",
    "periodic_even_cube_source_pressure_limit",
    "periodic_even_cube_ground_energy_density_limit",
    "free_periodic_density_agreement",
    "source_pressure_locally_uniform_convex_global_Z2_even",
    "ground_density_locally_uniform_concave_global_Z2_even",
    "uniform_zero_temperature_density_interchange",
    "all_joint_beta_volume_scalar_density_paths",
    "additive_scalar_covariance",
    "source_free_classical_center_nonnegative",
)
FALSE_SCOPE = (
    "natural_collective_transverse_additive_factorization",
    "exact_3D_to_1plus1_effective_reduction",
    "thermodynamic_phase_transition",
    "spontaneous_Z2_breaking",
    "source_selected_tangent_states",
    "pure_ordered_infinite_volume_state",
    "KMS_or_ground_state_weak_limit",
    "uniform_spectral_gap",
    "clustering_or_correlation_limit",
    "continuum_regulator_removal",
    "Euclidean_4D_or_relativistic_QFT",
    "physical_empty_space_reference",
    "below_empty_space",
    "absolute_vacuum_energy_fixed",
    "fine_one_site_translation_restored",
    "physical_light_speed_derived",
    "event_horizon_or_cooling",
    "C0_closed",
    "N1_through_N5_closed",
    "C6_advanced",
    "CP1_complete",
    "Sector_A_complete",
    "Pre_A_complete",
)
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
ST8_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-st8-q3lock/result.json"
EXP772_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-{SLUG}/result.json"


def portable_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def canonical(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


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
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], tuple[int, int]]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=240,
    )
    if completed.returncode:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", completed.stdout.strip())
    if match is None:
        raise AssertionError(completed.stdout)
    return json.loads(output.read_text(encoding="utf-8")), (int(match.group(1)), int(match.group(2)))


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    result |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    return result


def assertion_row(payload: dict[str, Any], alternatives: Iterable[Iterable[str]]) -> dict[str, Any] | None:
    rows = payload.get("assertions", [])
    for fragments in alternatives:
        lowered = tuple(fragment.lower() for fragment in fragments)
        for row in rows:
            name = str(row.get("name", "")).lower()
            if all(fragment in name for fragment in lowered):
                return row
    return None


def exploration_record() -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == EXPLORATION_ID:
            return record
    raise AssertionError(f"missing {EXPLORATION_ID}")


def build_payload() -> dict[str, Any]:
    audit = Audit()
    required = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, ST8_PARENT, EXP772_PARENT)
    for path in required:
        audit.check(f"required file {path.name}", path.is_file(), str(path), "file", "files")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    audit.check("manifest schema", manifest["schema"] == f"tect/{SLUG}-manifest/0.1", manifest["schema"], f"tect/{SLUG}-manifest/0.1", "identity")
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("parent ids", manifest["parent_ids"] == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("reused negatives", manifest["reused_negative_ids"] == REUSED_NEGATIVE_IDS, manifest["reused_negative_ids"], REUSED_NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("task id", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("closed subgates", manifest["gate_resolution"]["closed_subgates"] == CLOSED_SUBGATES, manifest["gate_resolution"]["closed_subgates"], CLOSED_SUBGATES, "identity")
    audit.check("open subgates", manifest["gate_resolution"]["open_subgates"] == OPEN_SUBGATES, manifest["gate_resolution"]["open_subgates"], OPEN_SUBGATES, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")

    st8 = json.loads(ST8_PARENT.read_text(encoding="utf-8"))
    exp772 = json.loads(EXP772_PARENT.read_text(encoding="utf-8"))
    audit.check("ST8 parent identity", st8.get("candidate_id") == PARENT_IDS[0], st8.get("candidate_id"), PARENT_IDS[0], "parents")
    audit.check("ST8 parent passes", st8["assertions"]["passed"] == st8["assertions"]["total"], st8["assertions"], "all pass", "parents")
    audit.check("EXP772 parent identity", exp772.get("candidate_id") == PARENT_IDS[1] and exp772.get("exploration_id") == "EXP-000779", (exp772.get("candidate_id"), exp772.get("exploration_id")), (PARENT_IDS[1], "EXP-000779"), "parents")
    audit.check("EXP772 parent passes", exp772["assertion_summary"]["passed"] == exp772["assertion_summary"]["total"], exp772["assertion_summary"], "all pass", "parents")

    with tempfile.TemporaryDirectory(prefix="tect-exp773-") as directory:
        primary, primary_summary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent, independent_summary = run_child(INDEPENDENT, Path(directory) / "independent.json")
    summaries = {"primary": primary_summary, "independent": independent_summary}
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} all pass", summaries[label][0] == summaries[label][1], summaries[label], "all pass", "children")
        audit.check(f"{label} identity", (child.get("candidate_id"), child.get("result_id"), child.get("exploration_id")) == (CANDIDATE_ID, RESULT_ID, EXPLORATION_ID), (child.get("candidate_id"), child.get("result_id"), child.get("exploration_id")), (CANDIDATE_ID, RESULT_ID, EXPLORATION_ID), "children")
        audit.check(f"{label} scope", child.get("scope") == manifest["scope"], child.get("scope"), manifest["scope"], "children")
        audit.check(f"{label} next gate", child.get("next_gate") == NEXT_GATE, child.get("next_gate"), NEXT_GATE, "children")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    audit.check("stored primary fresh", canonical(primary_stored) == canonical(primary), portable_sha256(PRIMARY_STORED), "fresh", "stored")
    audit.check("stored independent fresh", canonical(independent_stored) == canonical(independent), portable_sha256(INDEPENDENT_STORED), "fresh", "stored")
    for label, child, source in (("primary", primary, PRIMARY), ("independent", independent, INDEPENDENT)):
        hashes = child["source_sha256"]
        audit.check(f"{label} script hash", hashes["script"] == portable_sha256(source), hashes["script"], portable_sha256(source), "stored")
        audit.check(f"{label} manifest hash", hashes["manifest"] == portable_sha256(MANIFEST), hashes["manifest"], portable_sha256(MANIFEST), "stored")
        audit.check(f"{label} certificate hash", hashes["certificate"] == portable_sha256(CERTIFICATE), hashes["certificate"], portable_sha256(CERTIFICATE), "stored")
        st8_key = "st8_parent" if label == "primary" else "ST8_parent"
        audit.check(f"{label} ST8 parent hash", hashes[st8_key] == portable_sha256(ST8_PARENT), hashes[st8_key], portable_sha256(ST8_PARENT), "stored")
        audit.check(f"{label} EXP772 parent hash", hashes["EXP772_parent"] == portable_sha256(EXP772_PARENT), hashes["EXP772_parent"], portable_sha256(EXP772_PARENT), "stored")

    independent_imports = imports(INDEPENDENT)
    audit.check("independent no primary import", PRIMARY.stem not in independent_imports, sorted(independent_imports), f"not {PRIMARY.stem}", "independence")
    audit.check("independent stdlib only", not ({"sympy", "mpmath", "numpy", "scipy"} & independent_imports), sorted(independent_imports), "stdlib only", "independence")
    audit.check("child source diversity", portable_sha256(PRIMARY) != portable_sha256(INDEPENDENT), portable_sha256(PRIMARY), portable_sha256(INDEPENDENT), "independence")

    coverage = {
        "source coercivity": (("source", "coerciv"), ("combined", "scalar", "coerciv")),
        "Q3 edge count": (("q3", "edge", "count"),),
        "seam count": (("seam", "count"),),
        "seam quartic absorption": (("edge", "quartic", "absorption"),),
        "Gaussian Q3 moment": (("gaussian", "q3", "moment"), ("gaussian", "pair", "q3")),
        "product trial": (("product", "trial"),),
        "min-max trace": (("trace", "scaled", "lower"),),
        "zero-temperature squeeze": (("zero-temperature", "squeeze"),),
        "source evenness": (("source", "global", "z2"), ("global", "source", "evenness")),
        "source derivative": (("source", "derivative"),),
        "scalar state invariance": (("scalar", "shift", "normalized"), ("scalar", "state", "invariance")),
        "collective quartic": (("collective", "quartic", "identity"),),
        "nonfactorization": (("mixed", "interaction"), ("transverse", "correction", "nonconstant")),
    }
    for label, child in (("primary", primary), ("independent", independent)):
        for topic, alternatives in coverage.items():
            audit.check(f"{label} coverage {topic}", assertion_row(child, alternatives) is not None, alternatives, "present", "coverage")
    audit.check("cross Q3 edge count", primary["derived"]["geometry"]["Q3_edges"] == independent["derived"]["geometry"]["Q3_edges"], primary["derived"]["geometry"]["Q3_edges"], independent["derived"]["geometry"]["Q3_edges"], "cross")
    audit.check("cross all semantic coverage", all(assertion_row(primary, alternatives) is not None and assertion_row(independent, alternatives) is not None for alternatives in coverage.values()), sorted(coverage), "both children", "cross")

    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT):
        audit.check(f"ASCII {path.name}", all(ord(character) < 128 for character in path.read_text(encoding="utf-8")), path.name, "ASCII", "hygiene")
    for phrase in (
        "Open-rectangle thermodynamic limits",
        "Periodic/open global-form comparison",
        "Uniform zero-temperature squeeze",
        "uniformly locally Lipschitz",
        "not a physical-vacuum normalization",
        "does not exclude every possible reduction",
        "No priority claim",
        "This proves Pre-A",
    ):
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "certificate")

    for key in POSITIVE_SCOPE:
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in FALSE_SCOPE:
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("exact scope keyset", set(manifest["scope"]) == set(POSITIVE_SCOPE) | set(FALSE_SCOPE), sorted(manifest["scope"]), sorted(set(POSITIVE_SCOPE) | set(FALSE_SCOPE)), "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

    index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index", MANIFEST.name in index and CERTIFICATE.name in index, (MANIFEST.name, CERTIFICATE.name), "indexed", "records")
    matrix = (REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md").read_text(encoding="utf-8")
    audit.check("prior-art matrix", EXPLORATION_ID in matrix and "fixed-lattice" in matrix.lower(), EXPLORATION_ID, "recorded", "records")
    exploration = exploration_record()
    audit.check("exploration verdict", exploration.get("verdict") == "advanced", exploration.get("verdict"), "advanced", "records")
    audit.check("exploration task", exploration.get("task_id") == "T-054", exploration.get("task_id"), "T-054", "records")
    audit.check("exploration claim context", exploration.get("claim_ids") == ["C6-SPACETIME-SIGNATURE"], exploration.get("claim_ids"), ["C6-SPACETIME-SIGNATURE"], "records")
    audit.check("exploration related parents", PARENT_EXPLORATIONS <= {(item.get("id"), item.get("relation")) for item in exploration.get("related", [])}, exploration.get("related"), PARENT_EXPLORATIONS, "records")
    formal = exploration.get("formal_refs", {})
    audit.check("exploration no result card", formal.get("results", []) == [], formal.get("results"), [], "records")
    audit.check("exploration reused negatives", set(formal.get("negatives", [])) == set(REUSED_NEGATIVE_IDS), formal.get("negatives"), REUSED_NEGATIVE_IDS, "records")
    audit.check("exploration next gate", NEXT_GATE in exploration.get("next_action", ""), exploration.get("next_action"), NEXT_GATE, "records")

    todo = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))
    task_matches = [item for item in todo["tasks"] if item["id"] == "T-054"]
    audit.check("T-054 unique", len(task_matches) == 1, len(task_matches), 1, "records")
    audit.check("T-054 in progress", task_matches[0]["status"] == "in_progress", task_matches[0]["status"], "in_progress", "records")
    # The live umbrella task note advances as T-054 moves to later candidate
    # audits.  Historical route ownership and the successor gate are frozen in
    # the append-only exploration record checked above, not in that mutable note.
    changelog_records = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()]
    changelog_matches = [item for item in changelog_records if item.get("id") == CHANGELOG_ID]
    audit.check("changelog unique", len(changelog_matches) == 1, len(changelog_matches), 1, "records")
    changelog = changelog_matches[0]
    audit.check("changelog claim context", set(changelog.get("claim_ids", [])) == {"C6-SPACETIME-SIGNATURE", "C6-BCC-PREMISE-BLOCKED"}, changelog.get("claim_ids"), ["C6-SPACETIME-SIGNATURE", "C6-BCC-PREMISE-BLOCKED"], "records")
    audit.check("changelog notes", {MANIFEST.relative_to(REPO).as_posix(), CERTIFICATE.relative_to(REPO).as_posix()} <= set(changelog.get("notes", [])), changelog.get("notes"), "certificate and manifest", "records")
    audit.check("changelog scripts", {PRIMARY.relative_to(REPO).as_posix(), INDEPENDENT.relative_to(REPO).as_posix(), SCRIPT.relative_to(REPO).as_posix()} <= set(changelog.get("scripts", [])), changelog.get("scripts"), "three scripts", "records")
    audit.check("changelog no new negative", changelog.get("neg_results", []) == [], changelog.get("neg_results"), [], "records")

    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    audit.check("parent gate registered", PARENT_GATE in gates and "PARTIALLY RESOLVED" in gates[gates.index(PARENT_GATE) : gates.index(PARENT_GATE) + 3000], PARENT_GATE, "partially resolved", "records")
    audit.check("next gate registered", NEXT_GATE in gates, NEXT_GATE, "registered", "records")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in REUSED_NEGATIVE_IDS:
        audit.check(f"reused negative {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")

    lineage = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent"):
        audit.check(f"lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage, kind, "present", "records")
    if DEFAULT_OUTPUT.is_file():
        audit.check("lineage integrated", f"runs/2026-08-04-integrated-{SLUG}/" in lineage, "integrated", "present", "records")

    catalog_texts = [
        (REPO / "CATALOG.md").read_text(encoding="utf-8"),
        (REPO / "verification/catalog.json").read_text(encoding="utf-8"),
    ]
    proof_map_texts = [
        (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8"),
        "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((REPO / "verification/proof-evidence-map").glob("*.json"))
        ),
    ]
    generated_paths = [MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT, PRIMARY_STORED, INDEPENDENT_STORED]
    if DEFAULT_OUTPUT.is_file():
        generated_paths.append(DEFAULT_OUTPUT)
    for path in generated_paths:
        token = path.relative_to(REPO).as_posix()
        audit.check(f"catalog markdown {path.name}", token in catalog_texts[0], token, "catalogued", "generated")
        audit.check(f"catalog json {path.name}", token in catalog_texts[1], token, "catalogued", "generated")
    for token in (EXPLORATION_ID, PARENT_GATE, NEXT_GATE, MANIFEST.name, CERTIFICATE.name, *REUSED_NEGATIVE_IDS):
        audit.check(f"proof map markdown {token}", token in proof_map_texts[0], token, "mapped", "generated")
        audit.check(f"proof map json {token}", token in proof_map_texts[1], token, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": NEGATIVE_IDS,
        "reused_negative_ids": REUSED_NEGATIVE_IDS,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": NEXT_GATE,
        "script_version": __version__,
        "source_sha256": {
            "script": portable_sha256(SCRIPT),
            "manifest": portable_sha256(MANIFEST),
            "certificate": portable_sha256(CERTIFICATE),
            "primary": portable_sha256(PRIMARY),
            "independent": portable_sha256(INDEPENDENT),
            "st8_parent": portable_sha256(ST8_PARENT),
            "EXP772_parent": portable_sha256(EXP772_PARENT),
        },
        "child_summaries": {key: {"passed": value[0], "total": value[1]} for key, value in summaries.items()},
        "cross": {"Q3_edges": primary["derived"]["geometry"]["Q3_edges"], "coverage": sorted(coverage)},
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
