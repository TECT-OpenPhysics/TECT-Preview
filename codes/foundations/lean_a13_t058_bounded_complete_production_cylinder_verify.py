"""Integrated verifier for the T-058 bounded production-cylinder audit."""

from __future__ import annotations

import argparse
import ast
from datetime import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-t058-bounded-complete-production-cylinder-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a13_t058_bounded_complete_production_cylinder.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a13_t058_bounded_complete_production_cylinder_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r192-t058-bounded-complete-production-cylinder" / "integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def run_child(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, "-B", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {script}: {completed.stdout}\n{completed.stderr}")
    return {"stdout": completed.stdout, "stderr": completed.stderr, "payload": json.loads(output.read_text(encoding="utf-8"))}


def derive_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    rows = manifest["registered_inputs"]["slot_audit"]
    first = next((row["slot"] for row in rows if not row["mapped"]), None)
    reserve = manifest["registered_inputs"]["reserve_fixture"]
    a = F(reserve["cross_scale"])

    def qform(d: F) -> F:
        p = d - a
        return p - a - a + p

    temporal = manifest["registered_inputs"]["temporal_fixture"]
    s1, s2 = F(temporal["s1"]), F(temporal["s2"])
    h1, h2 = F(temporal["h1"]), F(temporal["h2"])
    pairing = s1 * h1 + s2 * h2
    wedge = s1 * h2 - s2 * h1
    total = (s1**2 + s2**2) * (h1**2 + h2**2)
    return {"slot_order": [row["slot"] for row in rows], "mapped_slots": [row["slot"] for row in rows if row["mapped"]], "complete_owner": all(row["mapped"] for row in rows), "first_missing_slot": first, "trial_verdict": "PASS_COMPLETE_OWNER" if first is None else "FAIL_FIRST_MISSING_PRODUCTION_MAP", "reserve_threshold_value": qform(F(reserve["threshold_diagonal"])), "reserve_below_value": qform(F(reserve["below_diagonal"])), "temporal_pairing": pairing, "temporal_wedge": wedge, "temporal_total": total, "temporal_gap": total - pairing**2, "douglas_identity": pairing**2 + wedge**2 == total, "a13_gate_closed": False, "sector_a_closed": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    expected = manifest["formal_integration"]["expected_counts"]
    check("identity", manifest["audit_id"] == "A13-T058-BOUNDED-COMPLETE-PRODUCTION-CYLINDER" and manifest["result_id"] == "R-192", [manifest["audit_id"], manifest["result_id"]], "R-192 identity")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    check("eight hostile mutations", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
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
    check("certificate scope", all(token in certificate for token in ("first missing production map", "R-183", "R-184", "R-191", "A13/T-050", "No R-192 PDF")), True, "scope tokens")
    independent_imports = imported_modules(INDEPENDENT)
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    check("independent stdlib imports", independent_imports <= stdlib, sorted(independent_imports - stdlib), [])
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    check("independent no primary import", "lean_a13_t058_bounded_complete_production_cylinder.py" not in independent_source and "importlib" not in independent_source, True, "no primary/dynamic import")
    derived = derive_from_manifest(manifest)
    oracle = manifest["test_oracles"]
    check("first missing slot", derived["first_missing_slot"] == oracle["first_failure_slot"], derived["first_missing_slot"], oracle["first_failure_slot"])
    check("trial failure", derived["trial_verdict"] == oracle["audit_verdict"], derived["trial_verdict"], oracle["audit_verdict"])
    check("reserve threshold", derived["reserve_threshold_value"] == F(oracle["reserve_threshold_value"]), derived["reserve_threshold_value"], oracle["reserve_threshold_value"])
    check("reserve below threshold", derived["reserve_below_value"] == F(oracle["reserve_below_value"]), derived["reserve_below_value"], oracle["reserve_below_value"])
    check("Douglas identity", derived["douglas_identity"] and derived["temporal_gap"] == F(oracle["douglas_gap"]), derived, {"identity": True, "gap": oracle["douglas_gap"]})
    check("owner incomplete", not derived["complete_owner"], derived["complete_owner"], False)
    check("A13 boundary", not derived["a13_gate_closed"] and not derived["sector_a_closed"], derived, "gates remain open")
    with tempfile.TemporaryDirectory(prefix="r192-verify-") as directory:
        temp = Path(directory)
        primary = run_child(PRIMARY, temp / "primary.json")
        independent = run_child(INDEPENDENT, temp / "independent.json")
    check("primary child", "PRIMARY R-192 LEAN PASS" in primary["stdout"], primary["stdout"], "PASS")
    check("independent child", "INDEPENDENT R-192 PASS" in independent["stdout"], independent["stdout"], "PASS")
    check("child derived agreement", primary["payload"]["derived"] == independent["payload"]["derived"], [primary["payload"]["derived"], independent["payload"]["derived"]], "equal")
    status = json.loads((REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "status.json").read_text(encoding="utf-8"))
    check("A13 gates remain open", set(status.get("open_gates", [])) == {"A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION", "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE"}, status.get("open_gates"), "both A13 gates")
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
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    check("result section", "### R-192 -- Bounded complete finite production-cylinder integration trial" in results_text, "R-192" in results_text, True)
    check("result boundary", all(token in results_text for token in ("first missing production map", "No R-192 PDF", "A13 gates remain open")), True, "scope tokens")
    summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
    # This verifier is a historical reader for EXP-000909.  Later append-only
    # packages legitimately increase the generated catalog and result counts;
    # requiring the old global total would turn reader drift into a false
    # theorem failure.  Keep the lower-bound sentinel so a stale or truncated
    # current surface still fails, while allowing monotone post-R-192 growth.
    current_catalog = summary.get("total")
    check("catalog count (append-only compatible)", isinstance(current_catalog, int) and current_catalog >= expected["catalog"], current_catalog, f">={expected['catalog']}")
    proof_map = json.loads((REPO / "verification" / "proof-evidence-map.json").read_text(encoding="utf-8"))
    current_results = len(proof_map.get("reusable_results", []))
    check("result count (append-only compatible)", current_results >= expected["results"], current_results, f">={expected['results']}")
    mutations = {
        "structural_not_production": manifest["registered_inputs"]["slot_audit"][0]["mapped"] is False,
        "complement_not_full": manifest["registered_inputs"]["slot_audit"][2]["mapped"] is False,
        "historical_low_retained": manifest["registered_inputs"]["slot_audit"][3]["mapped"] is False,
        "reserve_counterfixture": derived["reserve_below_value"] == F(-2),
        "douglas_gap": derived["temporal_gap"] == F(676),
        "no_gate_promotion": "does not close A13" in certificate or "does not close" in certificate,
        "hash_pins": all(item["sha256"] != "TO_BE_FILLED" for item in manifest["inputs"].values()) and all(item["sha256"] != "TO_BE_FILLED" for item in manifest["files"].values()),
        "lean_no_escape": not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")),
    }
    check("hostile mutation firewalls", all(mutations.values()), mutations, "all eight true")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": serial(derived), "recorded_at": datetime.now().isoformat() + "Z", "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED R-192 PASS {len(rows)}/{len(rows)} trial={derived['trial_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
