"""Integrated verifier for the R-176 A1 two-root covariance witnesses."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-a1-two-root-cholesky-covariance-witness-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a13_a1_two_root_cholesky_covariance_witness.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a13_a1_two_root_cholesky_covariance_witness_independent.py"
SCRIPT = Path(__file__).resolve()
LEAN = REPO / "verification" / "lean" / "Tect" / "R176.lean"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def run_child(path: Path, output: Path) -> dict:
    completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(path), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {path.name}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def accepts(derived: dict, manifest: dict) -> bool:
    return (
        derived.get("dimension") == str(manifest["registered_inputs"]["dimension"])
        and derived.get("first_kinetic_positive") is True
        and derived.get("second_kinetic_positive") is True
        and derived.get("both_actual_roots_instantiated") is True
        and derived.get("lower_cholesky_gram_identity") is True
        and derived.get("inverse_transpose_covariance_root_identity") is True
        and derived.get("duplicated_six_real_root_identity") is True
        and derived.get("root_kind") == "inverse-transpose of principal lower Cholesky factor"
        and derived.get("root_labels") == ["k", "2k"]
        and derived.get("root_pivots_positive") is True
        and derived.get("root_residuals_below_tolerance") is True
        and derived.get("a13_gate_closed") is False
        and derived.get("sector_a_closed") is False
        and derived.get("authority_hashes_ok") is True
        and derived.get("lean_escape_tokens_absent") is True
        and derived.get("boundary_present") is True
        and "A1" in manifest["boundary"]
        and "heat/root incidence" in manifest["boundary"]
        and "A13" in manifest["boundary"]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r176-a1-two-root-cholesky-covariance-witness" / "integrated.json")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict] = []

    def check(name: str, condition: bool, actual, expected) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A13-A1-TWO-ROOT-CHOLESKY-COVARIANCE-WITNESS", manifest["audit_id"], "A13-A1-TWO-ROOT-CHOLESKY-COVARIANCE-WITNESS")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"package file {key}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    source = LEAN.read_text(encoding="ascii")
    check("Lean theorem markers", all(marker in source for marker in manifest["theorem_markers"]), [m for m in manifest["theorem_markers"] if m in source], manifest["theorem_markers"])
    check("Lean escape tokens absent", not any(re.search(rf"\b{token}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), [], ["sorry", "admit", "axiom", "unsafe"])
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    check("source ASTs parse", len(trees) == 3, len(trees), 3)
    imports = {alias.name.split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.Import) for alias in node.names}
    imports |= {(node.module or "").split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.ImportFrom)}
    check("independent stdlib only", all(name in sys.stdlib_module_names or name == "__future__" for name in imports), sorted(imports), "stdlib only")

    with tempfile.TemporaryDirectory(prefix="r176-crosscheck-") as directory:
        primary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent = run_child(INDEPENDENT, Path(directory) / "independent.json")
    check("child PASS", primary["verdict"] == "PASS" and independent["verdict"] == "PASS", [primary["verdict"], independent["verdict"]], ["PASS", "PASS"])
    common = ("dimension", "first_kinetic_positive", "second_kinetic_positive", "both_actual_roots_instantiated", "lower_cholesky_gram_identity", "inverse_transpose_covariance_root_identity", "duplicated_six_real_root_identity", "root_kind", "root_labels", "root_pivots_positive", "root_residuals_below_tolerance", "a13_gate_closed", "sector_a_closed", "authority_hashes_ok", "lean_escape_tokens_absent", "boundary_present")
    check("derived agreement", all(primary["derived"].get(key) == independent["derived"].get(key) for key in common), {key: primary["derived"].get(key) for key in common}, {key: independent["derived"].get(key) for key in common})
    check("acceptance predicate", accepts(primary["derived"], manifest), primary["derived"], "actual A1 two-root covariance witness boundary")

    baseline = primary["derived"]
    mutations: list[dict] = []
    for index, label in enumerate(manifest["hostile_mutations"]):
        mutated = copy.deepcopy(baseline)
        if index == 0:
            mutated["both_actual_roots_instantiated"] = False
        elif index == 1:
            mutated["root_pivots_positive"] = False
        elif index == 2:
            mutated["root_kind"] = "supplied R-175 fixture"
        elif index == 3:
            mutated["authority_hashes_ok"] = False
        elif index == 4:
            mutated["a13_gate_closed"] = True
        elif index == 5:
            mutated["inverse_transpose_covariance_root_identity"] = False
        elif index == 6:
            mutated["second_kinetic_positive"] = False
        else:
            mutated["lean_escape_tokens_absent"] = False
        mutations.append({"label": label, "rejected": not accepts(mutated, manifest)})
    check("hostile mutations rejected", all(item["rejected"] for item in mutations), mutations, "all rejected")

    if not args.staged:
        events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = [(i, event) for i, event in enumerate(events, start=1) if event.get("id") == manifest["formal_integration"]["event_id"]]
        check("event identity", len(matches) == 1 and matches[0][0] == manifest["formal_integration"]["event_ordinal"], [(i, e.get("id")) for i, e in matches], manifest["formal_integration"]["event_id"])
        if matches:
            event = matches[0][1]
            check("event claims and no negatives", event.get("claim_ids") == manifest["formal_integration"]["event_claim_ids"] and event.get("neg_results") == [], event.get("claim_ids"), manifest["formal_integration"]["event_claim_ids"])
            raw = event.get("raw", "")
            check("event raw scope", all(token in raw for token in manifest["formal_integration"]["event_raw_tokens"]), [t for t in manifest["formal_integration"]["event_raw_tokens"] if t not in raw], "all present")
            check("event has no PDF", ".pdf" not in raw.lower(), ".pdf" in raw.lower(), False)
        results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        check("R-176 authority", results.count("R-176") >= 2 and "two-root principal Cholesky" in results, results.count("R-176"), ">=2")
        check("strategy index authority", "R-176" in (REPO / "strategy/INDEX.md").read_text(encoding="utf-8"), True, True)
        expected = manifest["formal_integration"]["expected_counts"]
        summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
        catalog_actual = summary.get("total")
        bootstrap_catalog = (not args.output.exists()) and catalog_actual == expected["catalog"] - 1
        check("catalog count", catalog_actual == expected["catalog"] or bootstrap_catalog, catalog_actual, expected["catalog"])
        check("result count", len(re.findall(r"^### R-\d+\b", results, re.MULTILINE)) == expected["results"], len(re.findall(r"^### R-\d+\b", results, re.MULTILINE)), expected["results"])
        explorations = [line for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        check("exploration count", len(explorations) == expected["explorations"], len(explorations), expected["explorations"])
        check("event count", len(events) == expected["events"], len(events), expected["events"])
        primary_path = REPO / manifest["formal_integration"]["primary_run_path"]
        independent_path = REPO / manifest["formal_integration"]["independent_run_path"]
        check("stored primary child", primary_path.is_file() and json.loads(primary_path.read_text(encoding="utf-8"))["verdict"] == "PASS", str(primary_path), "PASS result")
        check("stored independent child", independent_path.is_file() and json.loads(independent_path.read_text(encoding="utf-8"))["verdict"] == "PASS", str(independent_path), "PASS result")
        stored_primary = json.loads(primary_path.read_text(encoding="utf-8"))
        stored_independent = json.loads(independent_path.read_text(encoding="utf-8"))
        check("stored primary derived freshness", stored_primary.get("derived") == primary["derived"], stored_primary.get("derived"), primary["derived"])
        check("stored independent derived freshness", stored_independent.get("derived") == independent["derived"], stored_independent.get("derived"), independent["derived"])

    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": primary["derived"],
        "children": {"primary_assertions": primary["assertion_count"], "independent_assertions": independent["assertion_count"]},
        "mode": "staged" if args.staged else "formal",
        "boundary": manifest["boundary"],
    }
    if not args.staged and args.output.exists():
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        check("stored integrated verdict", stored.get("verdict") == "PASS", stored.get("verdict"), "PASS")
        check("stored integrated derived freshness", stored.get("derived") == payload["derived"], stored.get("derived"), payload["derived"])
        check("stored integrated child freshness", stored.get("children") == payload["children"], stored.get("children"), payload["children"])
    if not args.no_store:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"INTEGRATED R-176 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
