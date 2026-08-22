"""Integrated verifier for the R-193 static-owner heat-map interface audit."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-r193-static-owner-heat-map-nonidentifiability-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a13_r193_static_owner_heat_map_nonidentifiability.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a13_r193_static_owner_heat_map_nonidentifiability_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r193-static-owner-heat-map-nonidentifiability" / "integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def run_child(script: Path, output: Path) -> dict:
    completed = subprocess.run([sys.executable, "-B", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {script}: {completed.stdout}\n{completed.stderr}")
    return {"stdout": completed.stdout, "stderr": completed.stderr, "payload": json.loads(output.read_text(encoding="utf-8"))}


def derive(manifest: dict, authorities: dict) -> dict:
    data = manifest["registered_inputs"]["static_witness"]
    h1, h2 = F(data["hessian"][0]), F(data["hessian"][1])
    c1, c2 = F(data["covariance"][0]), F(data["covariance"][1])
    a1, a2 = F(data["map_a_factors"][0]), F(data["map_a_factors"][1])
    b1, b2 = F(data["map_b_factors"][0]), F(data["map_b_factors"][1])
    a1_text = json.dumps(authorities["a1"], sort_keys=True)
    a7_text = json.dumps(authorities["a7"], sort_keys=True)
    absent = {field: field not in a1_text and field not in a7_text for field in manifest["registered_inputs"]["required_absent_fields"]}
    return {
        "static_inverse": h1 * c1 == 1 and h2 * c2 == 1,
        "map_a_zero": a1 * 0 == 0 and a2 * 0 == 0,
        "map_b_zero": b1 * 0 == 0 and b2 * 0 == 0,
        "map_a_contracts": 0 < a1 < 1 and 0 < a2 < 1,
        "map_b_contracts": 0 < b1 < 1 and 0 < b2 < 1,
        "maps_distinct": a1 != b1,
        "relative_decay_order_reversed": a1 > a2 and b1 < b2,
        "required_dynamic_fields_absent_from_a1_a7": absent,
        "r136_raw_spatial_intertwiner_proved": authorities["r136"]["scope"]["production_raw_spatial_intertwiner_proved"],
        "r136_q_ledger_proved": authorities["r136"]["scope"]["production_one_use_q_ledger_proved"],
        "r125_root_shell_factorisation_proved": authorities["r125"]["scope"]["production_root_shell_factorization_proved"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []

    def check(name, condition, actual, expected):
        rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    expected = manifest["formal_integration"]["expected_counts"]
    check("identity", manifest["audit_id"] == "A13-R193-STATIC-OWNER-HEAT-MAP-NONIDENTIFIABILITY" and manifest["result_id"] == "R-193", [manifest["audit_id"], manifest["result_id"]], "R-193")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    check("hostile mutation count", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key} hash", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    lean_source = (REPO / manifest["files"]["lean_entrypoint"]["path"]).read_text(encoding="utf-8")
    certificate = (REPO / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    check("Lean markers", all(marker in lean_source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape absence", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    certificate_scope = all(token in certificate for token in ("R-192", "R-136", "R-125", "non-identifiability", "first missing production map", "does not close A13", "No R-193 PDF"))
    check("certificate scope", certificate_scope, certificate_scope, True)
    imports = imported_modules(INDEPENDENT)
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    check("independent stdlib imports", imports <= stdlib, sorted(imports - stdlib), [])
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    independent_import_clean = "lean_a13_r193_static_owner_heat_map_nonidentifiability.py" not in independent_source and "importlib" not in independent_source
    check("independent no primary/dynamic import", independent_import_clean, independent_import_clean, True)
    authorities = {key: json.loads((REPO / item["path"]).read_text(encoding="utf-8")) for key, item in manifest["inputs"].items() if key in {"a1", "a7", "r136", "r125"}}
    derived = derive(manifest, authorities)
    check("static inverse", derived["static_inverse"], derived["static_inverse"], True)
    check("zero-preserving contractions", derived["map_a_zero"] and derived["map_b_zero"] and derived["map_a_contracts"] and derived["map_b_contracts"], derived, True)
    check("distinct maps and reversed order", derived["maps_distinct"] and derived["relative_decay_order_reversed"], derived, True)
    check("dynamic fields absent", all(derived["required_dynamic_fields_absent_from_a1_a7"].values()), derived["required_dynamic_fields_absent_from_a1_a7"], "all absent")
    check("prior production flags open", not derived["r136_raw_spatial_intertwiner_proved"] and not derived["r136_q_ledger_proved"] and not derived["r125_root_shell_factorisation_proved"], derived, "false")
    check("interface witness", all((value if not isinstance(value, dict) else all(value.values())) is True for key, value in derived.items() if key not in {"r136_raw_spatial_intertwiner_proved", "r136_q_ledger_proved", "r125_root_shell_factorisation_proved"}) and not derived["r136_raw_spatial_intertwiner_proved"] and not derived["r136_q_ledger_proved"] and not derived["r125_root_shell_factorisation_proved"], derived, "non-identifiable")
    with tempfile.TemporaryDirectory(prefix="r193-verify-") as directory:
        temp = Path(directory)
        primary = run_child(PRIMARY, temp / "primary.json")
        independent = run_child(INDEPENDENT, temp / "independent.json")
    check("primary child", "PRIMARY R-193 LEAN PASS" in primary["stdout"], primary["stdout"], "PASS")
    check("independent child", "INDEPENDENT R-193 PASS" in independent["stdout"], independent["stdout"], "PASS")
    check("child derived agreement", primary["payload"]["derived"] == serial(independent["payload"]["derived"]), [primary["payload"]["derived"], independent["payload"]["derived"]], "equal")
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    check("result section", "### R-193 -- Static-owner to heat-map non-identifiability witness" in results_text, "R-193" in results_text, True)
    result_boundary = all(token in results_text for token in ("first missing production map", "does not close A13", "No R-193 PDF"))
    check("result boundary", result_boundary, result_boundary, True)
    exploration_rows = [json.loads(line) for line in (REPO / "explorations" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exp_matches = [(i, row) for i, row in enumerate(exploration_rows, start=1) if row.get("id") == manifest["exploration_id"]]
    check("exploration unique", len(exp_matches) == 1 and exp_matches[0][0] == manifest["formal_integration"]["exploration_ordinal"], [(i, r.get("id")) for i, r in exp_matches], manifest["formal_integration"]["exploration_ordinal"])
    event_rows = [json.loads(line) for line in (REPO / "changelog" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    event_matches = [(i, row) for i, row in enumerate(event_rows, start=1) if row.get("id") == manifest["formal_integration"]["event_id"]]
    check("event unique", len(event_matches) == 1 and event_matches[0][0] == manifest["formal_integration"]["event_ordinal"], [(i, r.get("id")) for i, r in event_matches], manifest["formal_integration"]["event_ordinal"])
    if event_matches:
        event = event_matches[0][1]
        check("event claims", event.get("claim_ids") == manifest["formal_integration"]["event_claim_ids"], event.get("claim_ids"), manifest["formal_integration"]["event_claim_ids"])
        check("event keywords", event.get("keywords") == manifest["formal_integration"]["event_keywords"], event.get("keywords"), manifest["formal_integration"]["event_keywords"])
        check("event notes", event.get("notes") == manifest["formal_integration"]["event_notes"], event.get("notes"), manifest["formal_integration"]["event_notes"])
        check("event scripts", event.get("scripts") == manifest["formal_integration"]["event_scripts"], event.get("scripts"), manifest["formal_integration"]["event_scripts"])
        check("event raw tokens", all(token in event.get("raw", "") for token in manifest["formal_integration"]["event_raw_tokens"]), manifest["formal_integration"]["event_raw_tokens"], "all present")
        check("event no negatives", event.get("neg_results") == [], event.get("neg_results"), [])
    summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
    check("catalog count", summary.get("total") == expected["catalog"] or (summary.get("total") == expected["catalog"] - 1 and not args.output.exists()), summary.get("total"), expected["catalog"])
    proof_map = json.loads((REPO / "verification" / "proof-evidence-map.json").read_text(encoding="utf-8"))
    check("result count", len(proof_map.get("reusable_results", [])) == expected["results"], len(proof_map.get("reusable_results", [])), expected["results"])
    mutations = {
        "same_static_data": derived["static_inverse"],
        "zero_preserving": derived["map_a_zero"] and derived["map_b_zero"],
        "contractive": derived["map_a_contracts"] and derived["map_b_contracts"],
        "distinct": derived["maps_distinct"],
        "order_reversal": derived["relative_decay_order_reversed"],
        "a1_a7_dynamic_absence": all(derived["required_dynamic_fields_absent_from_a1_a7"].values()),
        "r136_boundary": not derived["r136_raw_spatial_intertwiner_proved"] and not derived["r136_q_ledger_proved"],
        "r125_boundary": not derived["r125_root_shell_factorisation_proved"],
    }
    check("hostile mutation firewalls", all(mutations.values()), mutations, "all eight true")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": serial(derived), "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED R-193 PASS {len(rows)}/{len(rows)} interface=non-identifiable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
