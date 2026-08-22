#!/usr/bin/env python3
"""Integrated verifier for R-171 with staged, formal, and mutation checks."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260821.md"
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
SCRIPT = Path(__file__).resolve()
PRIMARY_RESULT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-21-primary-actual-a7-plane-wave-endpoint-secant-sign-witness/result.json"
INDEPENDENT_RESULT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-21-independent-actual-a7-plane-wave-endpoint-secant-sign-witness/result.json"
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-21-integrated-actual-a7-plane-wave-endpoint-secant-sign-witness/result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def run_child(path: Path, staged: bool, output: Path) -> dict[str, Any]:
    command = [sys.executable, "-B", "-X", "utf8", str(path)]
    if staged:
        command.append("--staged")
    command.extend(("--output", str(output), "--no-store"))
    completed = subprocess.run(command, cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed {path.name}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def parse_json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def direct_inventory() -> int:
    specification = importlib.util.spec_from_file_location("r171_build_catalog", REPO / "verification/scripts/build_catalog.py")
    if specification is None or specification.loader is None:
        raise AssertionError("cannot load catalog builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    count = 0
    for path in module.real_files(REPO, skip_names=module.SKIP_NAMES):
        relative = path.relative_to(REPO).as_posix()
        if relative in module.SKIP_PATHS or relative.startswith("verification/catalog/"):
            continue
        count += 1
    return count


def authority_counts() -> dict[str, int]:
    summary = json.loads((REPO / "verification/catalog-summary.json").read_text(encoding="utf-8"))
    results = json.loads((REPO / "results/index.json").read_text(encoding="utf-8"))
    gates = json.loads((REPO / "claims/gates-index.json").read_text(encoding="utf-8"))
    negatives = json.loads((REPO / "negative-results/index.json").read_text(encoding="utf-8"))
    todo = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))
    return {
        "claims": int(summary["claim_count"]),
        "results": int(results["count"]),
        "gates": int(gates["count"]),
        "negatives": int(negatives["count"]),
        "explorations": len(parse_json_lines(REPO / "explorations/log.jsonl")),
        "events": len(parse_json_lines(REPO / "changelog/log.jsonl")),
        "tasks": len(todo["tasks"]),
    }


def accepts(derived: dict[str, Any]) -> bool:
    return (
        derived.get("mode_on_dual_lattice") is True
        and derived.get("wave_number_over_pi") == "1/8"
        and derived.get("endpoint_energy_sign") == "positive"
        and derived.get("zero_endpoint_energy") == "0"
        and derived.get("endpoint_secant_sign") == "negative"
        and derived.get("full_a13_closure") is False
        and derived.get("physical_vacuum_result") is False
        and "owner" not in derived
        and derived.get("pauli_currents", {}).get("S1") == {"q": "0", "J": "0", "K": "0"}
        and derived.get("pauli_currents", {}).get("S2") == {"q": "0", "J": "0", "K": "0"}
        and derived.get("pauli_currents", {}).get("S3") == {"q": "s^2/(s^2+eps)", "J": "2*d*s", "K": "2*eps*d*s/(s^2+eps)"}
        and all(isinstance(value, str) and value not in {"0", "-1"} for value in derived.get("bracket_polynomial_coefficients", []))
    )


def source_discipline(audit: Audit) -> None:
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(trees[INDEPENDENT])
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(trees[INDEPENDENT])
        if isinstance(node, ast.ImportFrom)
    }
    forbidden = {name for name in imports if name not in sys.stdlib_module_names and name != "__future__"}
    source = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("three ASTs parse", len(trees) == 3, len(trees), 3, "code")
    audit.check("independent stdlib-only", not forbidden and "pre_a_a7_actual_plane_wave_endpoint_secant_sign_witness.py" not in source, sorted(forbidden), [], "code")
    audit.check("independent no inexact conversion", "float(" not in source and "complex(" not in source, True, True, "code")


def mutation_firewall(audit: Audit, baseline: dict[str, Any], manifest: dict[str, Any]) -> None:
    cases: list[dict[str, Any]] = []
    for index, label in enumerate(manifest["hostile_mutations"]):
        mutated = copy.deepcopy(baseline)
        if index == 0:
            mutated["endpoint_secant_sign"] = "positive"
        elif index == 1:
            mutated["mode_on_dual_lattice"] = False
        elif index == 2:
            mutated["wave_number_over_pi"] = "1/7"
        elif index == 3:
            mutated["bracket_polynomial_coefficients"][0] = "0"
        elif index == 4:
            mutated["pauli_currents"]["S3"]["J"] = "0"
        elif index == 5:
            mutated["owner"] = "full-A1"
        elif index == 6:
            mutated["full_a13_closure"] = True
        else:
            mutated["physical_vacuum_result"] = True
        cases.append({"label": label, "rejected": not accepts(mutated)})
    audit.check("all hostile mutations rejected", all(item["rejected"] for item in cases), cases, "8 rejected", "adversarial")


def formal_checks(audit: Audit, manifest: dict[str, Any], staged: bool, no_store: bool) -> None:
    expected = manifest["formal_integration"]["expected_post_counts"]
    current = authority_counts()
    for key in ("claims", "results", "gates", "negatives", "explorations", "events", "tasks"):
        audit.check(f"authority lower bound {key}", current[key] >= int(expected[key]), current[key], f">={expected[key]}", "lifecycle")
    if staged:
        audit.check("staged canonical primary absent", not PRIMARY_RESULT.exists(), PRIMARY_RESULT.exists(), False, "lifecycle")
        audit.check("staged canonical independent absent", not INDEPENDENT_RESULT.exists(), INDEPENDENT_RESULT.exists(), False, "lifecycle")
        audit.check("staged canonical integrated absent", not DEFAULT_OUTPUT.exists(), DEFAULT_OUTPUT.exists(), False, "lifecycle")
        audit.check("staged inventory lower bound", direct_inventory() >= int(expected["catalog"]) - 3, direct_inventory(), f">={int(expected["catalog"]) - 3}", "lifecycle")
        return
    for path in (PRIMARY_RESULT, INDEPENDENT_RESULT):
        audit.check(f"stored child exists {path.name}", path.exists(), path.exists(), True, "lifecycle")
    output_exists = DEFAULT_OUTPUT.exists()
    audit.check("integrated self-absence allowance", True, output_exists, "absent on first store or present on freshness", "lifecycle")
    inventory_expected = int(expected["catalog"]) if output_exists else int(expected["catalog"]) - 1
    audit.check("formal inventory lower bound", direct_inventory() >= inventory_expected, direct_inventory(), f">={inventory_expected}", "lifecycle")
    if (REPO / "verification/catalog-summary.json").exists():
        summary = json.loads((REPO / "verification/catalog-summary.json").read_text(encoding="utf-8"))
        audit.check("generated catalog lower bound", int(summary["total"]) >= inventory_expected, summary["total"], f">={inventory_expected}", "lifecycle")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("manifest result identity", manifest["result_id"] == "R-171" and manifest["exploration_id"] == "EXP-000878", (manifest["result_id"], manifest["exploration_id"]), ("R-171", "EXP-000878"), "identity")
    audit.check("claim-bearing firewall", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("no new gate or negative", manifest["formal_integration"].get("new_negative_ids", []) == [] and "closed_gate_ids" not in manifest, manifest["formal_integration"].get("new_negative_ids", []), [], "scope")
    audit.check("event identity contract", manifest["formal_integration"]["event_ordinal"] == 658 and manifest["formal_integration"]["event_id"].startswith("20260821-r-171-"), (manifest["formal_integration"]["event_ordinal"], manifest["formal_integration"]["event_id"]), (658, "20260821-r-171-"), "identity")
    for key, expected in manifest["package_hashes"].items():
        if not expected:
            continue
        path = REPO / manifest["artifacts"][key]
        audit.check(f"package hash {key}", sha256(path) == expected, sha256(path), expected, "authority")
    for key, expected in manifest["inputs"].items():
        path = REPO / expected["path"]
        audit.check(f"input hash {key}", sha256(path) == expected["sha256"], sha256(path), expected["sha256"], "authority")
    text = CERTIFICATE.read_text(encoding="ascii")
    audit.check("certificate scope tokens", all(token in text for token in ("deterministic Class-II", "dual-lattice mode", "endpoint secant", "A13 and T-050 remain open", "not a physical state")), True, True, "scope")
    audit.check("certificate no lowercase pdf claim", ".pdf" not in text.lower(), ".pdf" in text.lower(), False, "scope")
    audit.check("certificate no physical closure", all(token in text for token in ("not a physical state", "A13 and T-050 remain open", "no R-171 v1.0 PDF")), True, True, "scope")
    with tempfile.TemporaryDirectory(prefix="r171-") as directory:
        primary = run_child(PRIMARY, args.staged, Path(directory) / "primary.json")
        independent = run_child(INDEPENDENT, args.staged, Path(directory) / "independent.json")
    audit.check("primary PASS", primary["verdict"] == "PASS", primary["verdict"], "PASS", "children")
    audit.check("independent PASS", independent["verdict"] == "PASS", independent["verdict"], "PASS", "children")
    audit.check("derived values agree", primary["derived"] == independent["derived"], primary["derived"], independent["derived"], "children")
    audit.check("acceptance predicate", accepts(primary["derived"]), True, True, "scope")
    source_discipline(audit)
    mutation_firewall(audit, primary["derived"], manifest)
    formal_checks(audit, manifest, args.staged, args.no_store)
    payload = {"schema": "tect/pre-a-a7-actual-plane-wave-endpoint-secant-sign-witness-integrated/1.0", "run_kind": "integrated", "result_id": "R-171", "verdict": "PASS", "assertion_count": len(audit.rows), "assertions": audit.rows, "derived": primary["derived"], "children": {"primary_assertions": primary["assertion_count"], "independent_assertions": independent["assertion_count"]}, "mode": "staged" if args.staged else "formal"}
    output = args.output or DEFAULT_OUTPUT
    if args.output is not None or not args.no_store:
        atomic_json(output, payload)
    print(f"INTEGRATED PASS {len(audit.rows)}/{len(audit.rows)} mode={'staged' if args.staged else 'formal'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
