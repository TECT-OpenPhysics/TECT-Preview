"""Integrated verifier for the R-183 diagonal reserve margin theorem."""

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
MANIFEST = REPO / "strategy" / "pre-a13-diagonal-reserve-margin-cross-hessian-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a13_diagonal_reserve_margin_cross_hessian.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a13_diagonal_reserve_margin_cross_hessian_independent.py"
SCRIPT = Path(__file__).resolve()
LEAN = REPO / "verification" / "lean" / "Tect" / "R183.lean"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def run_child(path: Path, output: Path) -> dict:
    completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(path), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {path.name}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def accepts(derived: dict, manifest: dict) -> bool:
    expected_threshold = manifest["registered_inputs"]["expected"]["isotropic_threshold"]
    expected_scale = manifest["registered_inputs"]["expected"]["active_cross_scale"]
    expected_below = manifest["registered_inputs"]["expected"]["below_fixture"]
    expected_remainder = manifest["registered_inputs"]["expected"]["asymmetric_remainder"]
    return (
        derived.get("active_cross_scale") == expected_scale
        and derived.get("feedback_gain") == "1/2"
        and derived.get("threshold") == expected_threshold
        and derived.get("below_threshold") == "15"
        and derived.get("asymmetric_reserves") == {"d1": "16", "d2": "24", "p": "8", "q": "16", "remainder": expected_remainder}
        and derived.get("threshold_matrix") == [["8", "8"], ["8", "8"]]
        and derived.get("threshold_pulled_matrix") == [["18", "12"], ["12", "8"]]
        and derived.get("asymmetric_pulled_matrix") == [["20", "16"], ["16", "16"]]
        and derived.get("threshold_quadratic") == "8*(x + y)**2"
        and derived.get("threshold_pulled_quadratic") == "2*(3*x + 2*y)**2"
        and derived.get("asymmetric_quadratic") == "8*(x**2 + 2*x*y + 2*y**2)"
        and derived.get("below_fixture") == expected_below
        and derived.get("pulled_subthreshold_fixture") == expected_below
        and derived.get("necessary_reserve_witness") == expected_remainder
        and derived.get("isotropic_positive") is True
        and derived.get("isotropic_subthreshold_negative") is True
        and derived.get("a13_gate_closed") is False
        and derived.get("sector_a_closed") is False
        and derived.get("authority_hashes_ok") is True
        and derived.get("lean_escape_tokens_absent") is True
        and derived.get("boundary_present") is True
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r183-diagonal-reserve-margin-cross-hessian" / "integrated.json")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict] = []

    def check(name: str, condition: bool, actual, expected) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A13-DIAGONAL-RESERVE-MARGIN-CROSS-HESSIAN", manifest["audit_id"], "A13-DIAGONAL-RESERVE-MARGIN-CROSS-HESSIAN")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"package file {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    source = LEAN.read_text(encoding="ascii")
    check("Lean theorem markers", all(marker in source for marker in manifest["theorem_markers"]), [m for m in manifest["theorem_markers"] if m in source], manifest["theorem_markers"])
    check("Lean escape tokens absent", not any(re.search(rf"\b{token}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), [], ["sorry", "admit", "axiom", "unsafe"])
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    check("source ASTs parse", len(trees) == 3, len(trees), 3)
    imports = {alias.name.split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.Import) for alias in node.names}
    imports |= {(node.module or "").split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.ImportFrom)}
    check("independent stdlib only", all(name in sys.stdlib_module_names or name == "__future__" for name in imports), sorted(imports), "stdlib only")
    with tempfile.TemporaryDirectory(prefix="r183-crosscheck-") as directory:
        primary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent = run_child(INDEPENDENT, Path(directory) / "independent.json")
    check("child PASS", primary["verdict"] == "PASS" and independent["verdict"] == "PASS", [primary["verdict"], independent["verdict"]], ["PASS", "PASS"])
    check("derived key agreement", set(primary["derived"]) == set(independent["derived"]), sorted(primary["derived"]), sorted(independent["derived"]))
    check("derived agreement", primary["derived"] == independent["derived"], primary["derived"], independent["derived"])
    check("acceptance predicate", accepts(primary["derived"], manifest), primary["derived"], "reserve margin theorem")
    baseline = primary["derived"]
    mutations: list[dict] = []
    for index, label in enumerate(manifest["hostile_mutations"]):
        mutated = copy.deepcopy(baseline)
        if index == 0:
            mutated["active_cross_scale"] = "7"
        elif index == 1:
            mutated["feedback_gain"] = "1"
        elif index == 2:
            mutated["threshold"] = "15"
        elif index == 3:
            mutated["asymmetric_reserves"]["remainder"] = "7"
        elif index == 4:
            mutated["necessary_reserve_witness"] = "0"
        elif index == 5:
            mutated["a13_gate_closed"] = True
        elif index == 6:
            mutated["sector_a_closed"] = True
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
            check("event keywords", event.get("keywords") == manifest["formal_integration"]["event_keywords"], event.get("keywords"), manifest["formal_integration"]["event_keywords"])
            check("event notes", event.get("notes") == manifest["formal_integration"]["event_notes"], event.get("notes"), manifest["formal_integration"]["event_notes"])
            check("event scripts", event.get("scripts") == manifest["formal_integration"]["event_scripts"], event.get("scripts"), manifest["formal_integration"]["event_scripts"])
            raw = event.get("raw", "")
            check("event raw scope", all(token in raw for token in manifest["formal_integration"]["event_raw_tokens"]), [t for t in manifest["formal_integration"]["event_raw_tokens"] if t not in raw], "all present")
            check("event no PDF", ".pdf" not in raw.lower(), ".pdf" in raw.lower(), False)
        results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        check("R-183 authority", results.count("R-183") >= 2 and "reserve margin" in results.lower(), results.count("R-183"), ">=2")
        check("strategy index authority", "R-183" in (REPO / "strategy/INDEX.md").read_text(encoding="utf-8"), True, True)
        expected = manifest["formal_integration"]["expected_counts"]
        summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
        catalog_actual = summary.get("total")
        bootstrap_catalog = (not args.output.exists()) and catalog_actual == expected["catalog"] - 1
        check("catalog count", catalog_actual == expected["catalog"] or bootstrap_catalog, catalog_actual, expected["catalog"])
        result_count = len(re.findall(r"^### R-\d+\b", results, re.MULTILINE))
        check("result count", result_count == expected["results"], result_count, expected["results"])
        explorations = [line for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        check("exploration count", len(explorations) == expected["explorations"], len(explorations), expected["explorations"])
        check("event count", len(events) == expected["events"], len(events), expected["events"])
        primary_path = REPO / manifest["formal_integration"]["primary_run_path"]
        independent_path = REPO / manifest["formal_integration"]["independent_run_path"]
        check("stored primary child", primary_path.is_file() and json.loads(primary_path.read_text(encoding="utf-8"))["verdict"] == "PASS", str(primary_path), "PASS result")
        check("stored independent child", independent_path.is_file() and json.loads(independent_path.read_text(encoding="utf-8"))["verdict"] == "PASS", str(independent_path), "PASS result")
        check("stored primary derived freshness", json.loads(primary_path.read_text(encoding="utf-8"))["derived"] == primary["derived"], True, True)
        check("stored independent derived freshness", json.loads(independent_path.read_text(encoding="utf-8"))["derived"] == independent["derived"], True, True)
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": primary["derived"], "children": {"primary_assertions": primary["assertion_count"], "independent_assertions": independent["assertion_count"]}, "mode": "staged" if args.staged else "formal", "boundary": manifest["boundary"]}
    if not args.no_store and not args.staged and args.output.exists():
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        check("stored integrated verdict", stored.get("verdict") == "PASS", stored.get("verdict"), "PASS")
        check("stored integrated derived freshness", stored.get("derived") == payload["derived"], stored.get("derived"), payload["derived"])
        check("stored integrated child freshness", stored.get("children") == payload["children"], stored.get("children"), payload["children"])
    if not args.no_store:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"INTEGRATED R-183 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
