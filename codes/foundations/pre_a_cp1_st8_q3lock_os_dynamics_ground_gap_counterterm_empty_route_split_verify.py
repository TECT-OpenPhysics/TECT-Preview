#!/usr/bin/env python3
"""Integrated freshness, independence, and repository audit for EXP-000790.

The default mode is release-strict: every component result and every formal
authority must exist and agree before this program exits successfully.  During
package assembly ``--staged`` writes an explicitly ``INCOMPLETE`` result that
names missing authorities; it never upgrades missing evidence to PASS.
"""

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
from typing import Any, Iterable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-counterterm-empty-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-ORDERED-OS-DYNAMICS-GROUND-GAP-CONTINUUM-EMPTY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-PHASEWISE-OS-KMS-ZERO-T-GROUND-CUSP-FULL-Q3-COUNTERTERM-AND-EMPTY-REFERENCE-SPLIT"
EXPLORATION_ID = "EXP-000790"
TASK_ID = "T-054"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE"
NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-DYNAMICS",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-CURRENT-COMMON-DYNAMICS-THEOREM-IMPORT-MISMATCH",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-PARTIAL-QUARTIC-COUNTERTERM-ALL-SCALE-CLOSURE",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-integrated-{SLUG}/result.json"

CORE_DERIVED_KEYS = (
    "reflection_positive_fixture",
    "zero_temperature_cusp_fixture",
    "quartic_invariant_labels",
    "quartic_orbit_sizes",
    "quartic_closure_ranks",
    "one_loop_coefficients_g2_gl_l2",
    "bare_quadratic_rank",
    "full_quadratic_rank",
    "gns_fixture",
    "reference_fixture",
)


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(portable_bytes(path)).hexdigest()


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
    """Collect all defects so staged output identifies every missing authority."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.failures: list[str] = []
        self.missing: list[str] = []

    def _row(self, name: str, status: str, actual: Any, expected: Any, group: str) -> None:
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": status,
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        self._row(name, "FAIL", actual, expected, group)
        self.failures.append(f"{group}: {name}")
        return False

    def require(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        self._row(name, "MISSING", actual, expected, group)
        self.missing.append(f"{group}: {name}")
        return False

    @property
    def verdict(self) -> str:
        if self.failures:
            return "FAIL"
        if self.missing:
            return "INCOMPLETE"
        return "PASS"


def load_json(path: Path, audit: Audit, label: str, *, authority: bool = True) -> dict[str, Any] | None:
    if not path.is_file():
        method = audit.require if authority else audit.check
        method(f"{label} exists", False, path, "file", "files")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} parses", False, error, "valid JSON", "files")
        return None
    audit.check(f"{label} parses", True, path, "valid JSON", "files")
    return payload


def jsonl_records(path: Path, audit: Audit, label: str) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path, "file", "formal")
        return None
    records: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {line_number} is not an object")
                records.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        audit.check(f"{label} parses", False, error, "valid JSONL objects", "formal")
        return None
    audit.check(f"{label} parses", True, len(records), ">=1 records", "formal")
    return records


def run_fresh(script: Path, output: Path, audit: Audit, label: str) -> tuple[dict[str, Any], bytes, str] | None:
    if not script.is_file():
        audit.require(f"{label} script exists", False, script, "file", "implementations")
        return None
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        timeout=360,
    )
    if completed.returncode != 0 or not output.is_file():
        detail = {
            "returncode": completed.returncode,
            "stdout": completed.stdout[-2000:],
            "stderr": completed.stderr[-2000:],
        }
        audit.check(f"{label} fresh execution", False, detail, "exit 0 and JSON", "implementations")
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} fresh JSON", False, error, "valid JSON", "implementations")
        return None
    audit.check(f"{label} fresh execution", True, completed.returncode, 0, "implementations")
    # The child prints its caller-selected output path after the PASS sentinel.
    # Persist only the stable sentinel so the integrated JSON is reproducible
    # across different temporary directories.
    stable_stdout = next(
        (line.strip() for line in completed.stdout.splitlines() if line.startswith("EXP-000790 ")),
        "",
    )
    return payload, portable_bytes(output), stable_stdout


def assertion_actual(payload: dict[str, Any], name: str) -> str | None:
    for row in payload.get("assertions", {}).get("rows", []):
        if row.get("name") == name:
            return str(row.get("actual"))
    return None


def validate_component(payload: dict[str, Any], label: str, manifest: dict[str, Any], audit: Audit) -> None:
    expected = {
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "scope": manifest.get("scope"),
        "verdict": "PASS",
    }
    for key, value in expected.items():
        audit.check(f"{label} {key}", payload.get(key) == value, payload.get(key), value, "implementations")
    assertions = payload.get("assertions", {})
    passed = assertions.get("passed")
    total = assertions.get("total")
    audit.check(f"{label} assertion summary", isinstance(total, int) and total > 0 and passed == total, {"passed": passed, "total": total}, "equal positive counts", "implementations")
    audit.check(
        f"{label} all assertion rows pass",
        all(row.get("status") == "PASS" for row in assertions.get("rows", [])) and len(assertions.get("rows", [])) == total,
        len(assertions.get("rows", [])),
        total,
        "implementations",
    )
    files = payload.get("files", {})
    audit.check(f"{label} manifest hash", files.get("manifest_sha256") == portable_sha256(MANIFEST), files.get("manifest_sha256"), portable_sha256(MANIFEST), "hashes")
    audit.check(f"{label} certificate hash", files.get("certificate_sha256") == portable_sha256(CERTIFICATE), files.get("certificate_sha256"), portable_sha256(CERTIFICATE), "hashes")
    source = INDEPENDENT if "independent" in label else PRIMARY
    expected_script = str(source.relative_to(REPO)).replace("\\", "/")
    audit.check(f"{label} script path", files.get("script") == expected_script, files.get("script"), expected_script, "hashes")


def validate_source_independence(audit: Audit) -> None:
    if not (PRIMARY.is_file() and INDEPENDENT.is_file()):
        audit.require("both sources available for AST audit", False, [PRIMARY.is_file(), INDEPENDENT.is_file()], [True, True], "independence")
        return
    primary_source = PRIMARY.read_text(encoding="utf-8")
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    try:
        primary_tree = ast.parse(primary_source)
        independent_tree = ast.parse(independent_source)
    except SyntaxError as error:
        audit.check("sources parse as Python AST", False, error, "valid AST", "independence")
        return

    imports: set[str] = set()
    dynamic_import_calls: list[str] = []
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec"}:
                dynamic_import_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "run_module", "run_path"}:
                dynamic_import_calls.append(node.func.attr)
    primary_module = PRIMARY.stem
    forbidden = {"numpy", "sympy", primary_module, "importlib"}
    audit.check("independent forbidden imports absent", not imports.intersection(forbidden), sorted(imports.intersection(forbidden)), [], "independence")
    audit.check("independent dynamic import/evaluation absent", not dynamic_import_calls, dynamic_import_calls, [], "independence")
    audit.check("independent source does not name primary module", primary_module not in independent_source, primary_module in independent_source, False, "independence")
    audit.check("independent AST differs from primary", ast.dump(independent_tree) != ast.dump(primary_tree), "different" if ast.dump(independent_tree) != ast.dump(primary_tree) else "same", "different", "independence")
    audit.check("independent source hash differs", portable_sha256(INDEPENDENT) != portable_sha256(PRIMARY), portable_sha256(INDEPENDENT), f"different from {portable_sha256(PRIMARY)}", "independence")


def compare_components(primary: dict[str, Any], independent: dict[str, Any], audit: Audit) -> None:
    pderived = primary.get("derived", {})
    iderived = independent.get("derived", {})
    for key in CORE_DERIVED_KEYS:
        audit.check(f"cross exact derived {key}", key in pderived and pderived.get(key) == iderived.get(key), iderived.get(key), pderived.get(key), "cross_core")

    labels = pderived.get("quartic_invariant_labels", [])
    orbit_sizes = pderived.get("quartic_orbit_sizes", {})
    audit.check("quartic invariant dimension", len(labels) == 19, len(labels), 19, "cross_core")
    audit.check("quartic monomial partition", sum(orbit_sizes.values()) == 330 if isinstance(orbit_sizes, dict) else False, sum(orbit_sizes.values()) if isinstance(orbit_sizes, dict) else orbit_sizes, 330, "cross_core")
    audit.check("Q3 automorphism count primary", assertion_actual(primary, "Q3 automorphism count") == "48", assertion_actual(primary, "Q3 automorphism count"), "48", "cross_core")
    independent_q3 = assertion_actual(independent, "Q3 automorphism count")
    audit.check("Q3 automorphism count independent", independent_q3 == "48", independent_q3, "48", "cross_core")
    audit.check("quartic closure ranks exact", pderived.get("quartic_closure_ranks") == [2, 4, 9, 19, 19], pderived.get("quartic_closure_ranks"), [2, 4, 9, 19, 19], "cross_core")
    audit.check("quadratic ranks exact", [pderived.get("bare_quadratic_rank"), pderived.get("full_quadratic_rank")] == [2, 4], [pderived.get("bare_quadratic_rank"), pderived.get("full_quadratic_rank")], [2, 4], "cross_core")


def require_text(path: Path, audit: Audit, label: str) -> str | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path, "file", "formal")
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        audit.check(f"{label} readable", False, error, "UTF-8 text", "formal")
        return None
    audit.check(f"{label} readable", True, len(text), ">0", "formal")
    return text


def require_unique_record(
    records: list[dict[str, Any]] | None,
    predicate: Any,
    label: str,
    audit: Audit,
) -> dict[str, Any] | None:
    if records is None:
        return None
    matches = [record for record in records if predicate(record)]
    if not matches:
        audit.require(f"{label} registered", False, 0, 1, "formal")
        return None
    if len(matches) != 1:
        audit.check(f"{label} unique", False, len(matches), 1, "formal")
        return None
    audit.check(f"{label} unique", True, 1, 1, "formal")
    return matches[0]


def validate_formal_authorities(manifest: dict[str, Any], audit: Audit) -> None:
    explorations = jsonl_records(REPO / "explorations/log.jsonl", audit, "exploration ledger")
    exploration = require_unique_record(explorations, lambda record: record.get("id") == EXPLORATION_ID, EXPLORATION_ID, audit)
    if exploration is not None:
        serialized = json.dumps(exploration, sort_keys=True)
        audit.check("exploration advanced", exploration.get("verdict") == "advanced", exploration.get("verdict"), "advanced", "formal")
        # PARENT_GATE is verified against claims/GATES.md below.  It is not a
        # governance gate ID accepted by exploration.py, so requiring it in
        # the append-only record would contradict the ledger schema.
        for needle in (RESULT_ID, NEXT_GATE, "EXP-000789", *NEGATIVE_IDS):
            audit.check(f"exploration links {needle}", needle in serialized, needle in serialized, True, "formal")

    negative_registry = require_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if negative_registry is not None:
        for negative_id in NEGATIVE_IDS:
            if negative_id in negative_registry:
                audit.check(f"negative registered {negative_id}", True, True, True, "formal")
            else:
                audit.require(f"negative registered {negative_id}", False, False, True, "formal")

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog ledger")
    changelog_entries = [] if changelog is None else [
        record for record in changelog
        if EXPLORATION_ID.lower() in json.dumps(record).lower()
    ]
    audit.check(
        f"changelog {EXPLORATION_ID} registered",
        bool(changelog_entries),
        len(changelog_entries),
        ">=1",
        "formal",
    )
    if changelog_entries:
        # Append-only provenance repairs may add a later linkage event.  Audit
        # the union rather than falsely demanding that the exploration ID occur
        # in exactly one changelog record.
        text = "\n".join(json.dumps(entry, sort_keys=True) for entry in changelog_entries)
        for needle in (RESULT_ID, f"strategy/{SLUG}-manifest.json"):
            audit.check(f"changelog links {needle}", needle in text, needle in text, True, "formal")

    gates = require_text(REPO / "claims/GATES.md", audit, "gate ledger")
    if gates is not None:
        for needle in (EXPLORATION_ID, RESULT_ID, PARENT_GATE, NEXT_GATE, "PARTIALLY RESOLVED"):
            if needle in gates:
                audit.check(f"gate ledger links {needle}", True, True, True, "formal")
            else:
                audit.require(f"gate ledger links {needle}", False, False, True, "formal")

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority")
    if todo is not None:
        matches = [task for task in todo.get("tasks", []) if task.get("id") == TASK_ID]
        audit.check("T-054 unique", len(matches) == 1, len(matches), 1, "formal")
        if len(matches) == 1:
            task = matches[0]
            task_text = json.dumps(task, sort_keys=True)
            audit.check("T-054 in progress", task.get("status") == "in_progress", task.get("status"), "in_progress", "formal")
            for needle in (EXPLORATION_ID, NEXT_GATE):
                if needle in task_text:
                    audit.check(f"T-054 links {needle}", True, True, True, "formal")
                else:
                    audit.require(f"T-054 links {needle}", False, False, True, "formal")

    strategy_index = require_text(REPO / "strategy/INDEX.md", audit, "strategy index")
    if strategy_index is not None:
        for needle in (f"{SLUG}-manifest.json", RESULT_ID, EXPLORATION_ID):
            if needle in strategy_index:
                audit.check(f"strategy index links {needle}", True, True, True, "formal")
            else:
                audit.require(f"strategy index links {needle}", False, False, True, "formal")

    proof_map_md = require_text(REPO / "theory/proof-evidence-map.md", audit, "proof map markdown")
    proof_map_json = require_text(REPO / "verification/proof-evidence-map.json", audit, "proof map JSON")
    if proof_map_md is not None and proof_map_json is not None:
        for needle in (EXPLORATION_ID, RESULT_ID, NEXT_GATE, *NEGATIVE_IDS):
            present = needle in proof_map_md and needle in proof_map_json
            if present:
                audit.check(f"proof maps link {needle}", True, [True, True], [True, True], "generated")
            else:
                audit.require(f"proof maps link {needle}", False, [needle in proof_map_md, needle in proof_map_json], [True, True], "generated")

    catalog_md = require_text(REPO / "CATALOG.md", audit, "catalog markdown")
    catalog_json = require_text(REPO / "verification/catalog.json", audit, "catalog JSON")
    if catalog_md is not None and catalog_json is not None:
        for path in (PRIMARY, INDEPENDENT, Path(__file__).resolve(), MANIFEST, CERTIFICATE):
            relative = str(path.relative_to(REPO)).replace("\\", "/")
            present = relative in catalog_md and relative in catalog_json
            if present:
                audit.check(f"catalogs link {relative}", True, [True, True], [True, True], "generated")
            else:
                audit.require(f"catalogs link {relative}", False, [relative in catalog_md, relative in catalog_json], [True, True], "generated")

    audit.check("manifest exploration", manifest.get("exploration_id") == EXPLORATION_ID, manifest.get("exploration_id"), EXPLORATION_ID, "formal")
    audit.check("manifest negative ids", manifest.get("negative_ids") == list(NEGATIVE_IDS), manifest.get("negative_ids"), list(NEGATIVE_IDS), "formal")
    verification = manifest.get("verification", {})
    expected_paths = {
        "primary": str(PRIMARY.relative_to(REPO)).replace("\\", "/"),
        "independent": str(INDEPENDENT.relative_to(REPO)).replace("\\", "/"),
        "integrated": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
    }
    for key, expected in expected_paths.items():
        audit.check(f"manifest verification path {key}", verification.get(key) == expected, verification.get(key), expected, "formal")


def validate_certificate_and_firewall(manifest: dict[str, Any], audit: Audit) -> None:
    certificate = require_text(CERTIFICATE, audit, "certificate")
    if certificate is not None:
        for phrase in (
            "phasewise, not common",
            "post-hoc direct sum",
            "strict zero-temperature source cusp",
            "19-dimensional",
            "necessary, not sufficient",
            "same Hamiltonian",
            "not physical empty space",
        ):
            audit.check(f"certificate phrase {phrase}", phrase in certificate, phrase in certificate, True, "certificate")

    status = load_json(REPO / "claims/C6-SPACETIME-SIGNATURE/status.json", audit, "C6 status", authority=False)
    if status is not None:
        audit.check("C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall")
        audit.check("C6 lifecycle unchanged", status.get("lifecycle") == "ACTIVE", status.get("lifecycle"), "ACTIVE", "claim_firewall")
        audit.check("C6 evidence unchanged", status.get("evidence_grade") == ["CONDITIONAL"], status.get("evidence_grade"), ["CONDITIONAL"], "claim_firewall")
        audit.check("C6 gate unchanged", status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"], status.get("open_gates"), ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    true_scope = (
        "phasewise_periodic_OS_reconstruction",
        "phasewise_stochastically_positive_beta_KMS",
        "fixed_lattice_zero_temperature_source_cusp",
        "full_AutQ3_Z2_quartic_invariant_dimension_19",
        "one_loop_closure_reaches_full_quartic_invariant_space",
        "full_quadratic_invariant_dimension_4",
        "same_H_finite_volume_finite_regulator_reference_identity",
    )
    false_scope = (
        "common_state_independent_real_time_dynamics",
        "common_alpha_KMS_identification",
        "distinct_algebraic_ground_states",
        "broken_sector_GNS_gap",
        "enlarged_counterterm_continuum_limit",
        "physical_empty_space_reference",
        "below_physical_empty_space",
        "C6_advanced",
        "Sector_A_complete",
        "Pre_A_complete",
    )
    scope = manifest.get("scope", {})
    for key in true_scope:
        audit.check(f"scope true {key}", scope.get(key) is True, scope.get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", scope.get(key) is False, scope.get(key), False, "scope")


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = load_json(MANIFEST, audit, "manifest", authority=False)
    if manifest is None:
        manifest = {}
    validate_certificate_and_firewall(manifest, audit)
    validate_source_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    fresh_bytes: dict[str, bytes] = {}
    stdout: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp790-") as temporary:
        temp = Path(temporary)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh(script, temp / f"{label}.json", audit, label)
            if result is not None:
                components[f"{label}_fresh"], fresh_bytes[label], stdout[label] = result

    for label, path in (("primary", PRIMARY_STORED), ("independent", INDEPENDENT_STORED)):
        stored = load_json(path, audit, f"{label} stored")
        if stored is not None:
            components[f"{label}_stored"] = stored
            if label in fresh_bytes:
                audit.check(f"{label} fresh/stored portable-byte equality", portable_bytes(path) == fresh_bytes[label], portable_sha256(path), hashlib.sha256(fresh_bytes[label]).hexdigest(), "freshness")
                audit.check(f"{label} fresh/stored semantic equality", stored == components[f"{label}_fresh"], "equal" if stored == components[f"{label}_fresh"] else "different", "equal", "freshness")

    for label, payload in components.items():
        validate_component(payload, label.replace("_", " "), manifest, audit)
    if "primary" in stdout:
        audit.check("primary stdout sentinel", "EXP-000790 PRIMARY PASS" in stdout["primary"], stdout["primary"], "EXP-000790 PRIMARY PASS", "implementations")
    if "independent" in stdout:
        audit.check("independent stdout sentinel", "EXP-000790 INDEPENDENT PASS" in stdout["independent"], stdout["independent"], "EXP-000790 INDEPENDENT PASS", "implementations")

    if "primary_fresh" in components and "independent_fresh" in components:
        compare_components(components["primary_fresh"], components["independent_fresh"], audit)
    else:
        audit.require("fresh primary/independent cross comparison", False, sorted(components), ["primary_fresh", "independent_fresh"], "cross_core")

    validate_formal_authorities(manifest, audit)

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    return {
        "schema": f"tect/{SLUG}-integrated/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "assertions": {
            "passed": passed,
            "total": len(audit.rows),
            "failed": len(audit.failures),
            "missing": len(audit.missing),
            "rows": audit.rows,
        },
        "component_assertions": {
            label: {
                "passed": payload.get("assertions", {}).get("passed"),
                "total": payload.get("assertions", {}).get("total"),
            }
            for label, payload in components.items()
        },
        "scope": manifest.get("scope"),
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST) if MANIFEST.is_file() else None,
            "certificate_sha256": portable_sha256(CERTIFICATE) if CERTIFICATE.is_file() else None,
            "primary_sha256": portable_sha256(PRIMARY) if PRIMARY.is_file() else None,
            "independent_sha256": portable_sha256(INDEPENDENT) if INDEPENDENT.is_file() else None,
            "integrated_sha256": portable_sha256(Path(__file__).resolve()),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
        },
        "verdict": audit.verdict,
        "missing_authorities": audit.missing,
        "failures": audit.failures,
        "boundary": manifest.get("no_overclaim"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true", help="write INCOMPLETE output without failing on missing authorities")
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(
        f"EXP-000790 INTEGRATED {payload['verdict']} "
        f"{summary['passed']}/{summary['total']} "
        f"failed={summary['failed']} missing={summary['missing']}"
    )
    print(args.output)
    if payload["verdict"] == "FAIL":
        raise SystemExit(1)
    if payload["verdict"] != "PASS" and not args.staged:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
