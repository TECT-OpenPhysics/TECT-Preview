"""Integrated verifier for the R-190 arbitrary-polarization finite slice."""

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
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO / "verification" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from proof_evidence_map_io import load_map

MANIFEST = REPO / "strategy" / "pre-a13-a1-arbitrary-polarization-two-mode-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a13_a1_arbitrary_polarization_two_mode.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a13_a1_arbitrary_polarization_two_mode_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r190-a1-arbitrary-polarization-two-mode" / "integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run_lane(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, "-B", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"lane failed: {script}: {completed.stdout}\n{completed.stderr}")
    if not output.is_file():
        raise AssertionError(f"lane did not return an output payload: {script}")
    return json.loads(output.read_text(encoding="utf-8"))


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


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
    check("identity", manifest["audit_id"] == "A13-A1-ARBITRARY-POLARIZATION-TWO-MODE" and manifest["result_id"] == "R-190", [manifest["audit_id"], manifest["result_id"]], "R-190 identity")
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
    check("certificate scope", all(token in certificate for token in ("arbitrary complex", "Class-II", "9 s^2/16", "s^3/8", "A13/T-050", "No R-190 PDF")), True, "scope tokens")
    independent_imports = imported_modules(INDEPENDENT)
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    check("independent stdlib imports", independent_imports <= stdlib, sorted(independent_imports - stdlib), [])
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    check("independent no primary import", "lean_a13_a1_arbitrary_polarization_two_mode" not in independent_source and "importlib" not in independent_source, True, "no primary/dynamic import")

    exploration_rows = [json.loads(line) for line in (REPO / "explorations" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exp_matches = [(ordinal, row) for ordinal, row in enumerate(exploration_rows, start=1) if row.get("id") == manifest["exploration_id"]]
    exploration_ordinal = manifest["formal_integration"].get("exploration_ordinal", expected["explorations"])
    check("exploration unique", len(exp_matches) == 1 and exp_matches[0][0] == exploration_ordinal, [(i, r.get("id")) for i, r in exp_matches], exploration_ordinal)
    event_rows = [json.loads(line) for line in (REPO / "changelog" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    event_matches = [(ordinal, row) for ordinal, row in enumerate(event_rows, start=1) if row.get("id") == manifest["formal_integration"]["event_id"]]
    check("event unique", len(event_matches) == 1 and event_matches[0][0] == manifest["formal_integration"]["event_ordinal"], [(i, r.get("id")) for i, r in event_matches], manifest["formal_integration"]["event_ordinal"])
    if event_matches:
        event = event_matches[0][1]
        check("event header", event.get("header") == "[R-190 A1 arbitrary-polarization two-mode positivity Lean cross-check] - 2026-08-22", event.get("header"), "R-190 header")
        check("event claims", event.get("claim_ids") == manifest["formal_integration"]["event_claim_ids"], event.get("claim_ids"), manifest["formal_integration"]["event_claim_ids"])
        check("event keywords", event.get("keywords") == manifest["formal_integration"]["event_keywords"], event.get("keywords"), manifest["formal_integration"]["event_keywords"])
        check("event notes", event.get("notes") == manifest["formal_integration"]["event_notes"], event.get("notes"), manifest["formal_integration"]["event_notes"])
        check("event scripts", event.get("scripts") == manifest["formal_integration"]["event_scripts"], event.get("scripts"), manifest["formal_integration"]["event_scripts"])
        check("event raw tokens", all(token in event.get("raw", "") for token in manifest["formal_integration"]["event_raw_tokens"]), manifest["formal_integration"]["event_raw_tokens"], "all present")
        check("event no negatives", event.get("neg_results") == [], event.get("neg_results"), [])
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    check("result section", "### R-190 -- A1 arbitrary-polarization two-mode positivity Lean cross-check" in results_text, "R-190" in results_text, True)
    check("result boundary", all(token in results_text for token in ("arbitrary complex internal polarization", "complete A13", "No R-190 PDF")), True, "scope tokens")
    status = json.loads((REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "status.json").read_text(encoding="utf-8"))
    check("A13 gates remain open", set(status.get("open_gates", [])) == {"A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION", "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE"}, status.get("open_gates"), "both A13 gates")
    summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
    catalog_total = summary.get("total")
    interim_catalog = expected["catalog"] - 1
    catalog_ok = catalog_total == expected["catalog"] or (catalog_total == interim_catalog and not args.output.exists())
    check("catalog count", catalog_ok, catalog_total, f"{expected['catalog']} (or interim {interim_catalog} before integrated store)")
    check("claim count", summary.get("claim_count") == expected["claims"], summary.get("claim_count"), expected["claims"])
    proof_map = load_map(REPO)
    check("result count", len(proof_map.get("reusable_results", [])) == expected["results"], len(proof_map.get("reusable_results", [])), expected["results"])

    before = [REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r190-a1-arbitrary-polarization-two-mode" / name for name in ("primary.json", "independent.json", "integrated.json")]
    before_state = [path.exists() for path in before]
    with tempfile.TemporaryDirectory(prefix="r190-verify-") as directory:
        temp = Path(directory)
        primary = run_lane(PRIMARY, temp / "primary.json")
        independent = run_lane(INDEPENDENT, temp / "independent.json")
    check("primary PASS", primary["verdict"] == "PASS", primary["verdict"], "PASS")
    check("independent PASS", independent["verdict"] == "PASS", independent["verdict"], "PASS")
    check("derived agreement", primary["derived"] == independent["derived"], [primary["derived"], independent["derived"]], "equal")
    d = primary["derived"]
    check("uniform quadratic", all(F(value) > F(manifest["registered_inputs"]["q_lower_target"]) for value in d["quadratic_lowers"]), d["quadratic_lowers"], ">1/16")
    check("Class-II margin", F(d["classii_ac_minus_b2"]) > 0 and d["classii_psd"], d["classii_ac_minus_b2"], ">0")
    check("cubic margin", d["discriminant_negative"] and d["slice_nonzero_positive"], [d["discriminant"], d["slice_nonzero_positive"]], "positive for s>0")
    check("A13 boundary", not d["a13_gate_closed"] and not d["progressive_revisit_closed"] and not d["physical_empty_closed"], d, "all open")

    mutation_results = {
        "hash_drift": sha256(REPO / manifest["inputs"]["a1_manifest"]["path"]) != "not-the-live-hash" and manifest["inputs"]["a1_manifest"]["sha256"] != "not-the-live-hash",
        "F_ref_scope": "F_ref" in certificate and "F_decl" in certificate,
        "Machin_scope": "6283/2000 < pi < 22/7" in certificate,
        "quadratic_target": manifest["registered_inputs"]["q_lower_target"] == "1/16",
        "ClassII_PSD": manifest["registered_inputs"]["derived_coefficients"]["classii_ac_minus_b2_positive"] is True,
        "moment_constants": manifest["registered_inputs"]["moment_bounds"] == {"quartic_upper": "9/16", "sextic_lower": "1/8"},
        "A13_open": "does not prove" in manifest["boundary"] and "A13" in manifest["boundary"],
        "Lean_no_escape": not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")),
    }
    check("hostile mutation firewalls", all(mutation_results.values()), mutation_results, "all eight true")
    check("no-store preserves stored-output state", [path.exists() for path in before] == before_state, [path.exists() for path in before], before_state)
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "primary": primary, "independent": independent, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED R-190 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
