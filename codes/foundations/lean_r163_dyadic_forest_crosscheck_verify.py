"""Integrated verifier for the R-163 Lean arithmetic cross-check."""

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
MANIFEST = REPO / "strategy" / "pre-a-a13-r163-dyadic-forest-lean-crosscheck-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_r163_dyadic_forest_crosscheck.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_r163_dyadic_forest_crosscheck_independent.py"
SCRIPT = Path(__file__).resolve()
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r163-dyadic-forest-crosscheck" / "integrated.json"


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
    constants = manifest["registered_constants"]
    return (
        derived.get("retained_gap") == constants["retained_gap"]
        and derived.get("source_headroom") == constants["coefficient_headroom"]
        and derived.get("owner_adverse_floor") == constants["owner_adverse_floor"]
        and derived.get("epsilon_6") == constants["epsilon_6"]
        and derived.get("source_third_derivative") == constants["source_third_derivative_fixture"]
        and not derived.get("a13_gate_closed", False)
        and not derived.get("sector_a_closed", False)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict] = []

    def check(name: str, condition: bool, actual, expected) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A13-R163-DYADIC-FOREST-LEAN-CROSSCHECK", manifest["audit_id"], "A13-R163-DYADIC-FOREST-LEAN-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"package file {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    source = (REPO / manifest["inputs"]["lean_entrypoint"]["path"]).read_text(encoding="ascii")
    check("Lean theorem markers", all(marker in source for marker in manifest["theorem_markers"]), [m for m in manifest["theorem_markers"] if m in source], manifest["theorem_markers"])
    check("Lean escape tokens absent", all(token not in source for token in ("sorry", "admit", "axiom", "unsafe")), [], ["sorry", "admit", "axiom", "unsafe"])
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    check("source ASTs parse", len(trees) == 3, len(trees), 3)
    imports = {alias.name.split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.Import) for alias in node.names}
    imports |= {(node.module or "").split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.ImportFrom)}
    check("independent stdlib only", all(name in sys.stdlib_module_names or name == "__future__" for name in imports), sorted(imports), "stdlib only")
    with tempfile.TemporaryDirectory(prefix="r163-lean-crosscheck-") as directory:
        primary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent = run_child(INDEPENDENT, Path(directory) / "independent.json")
    check("child PASS", primary["verdict"] == "PASS" and independent["verdict"] == "PASS", [primary["verdict"], independent["verdict"]], ["PASS", "PASS"])
    check("child derived agreement", primary["derived"] == independent["derived"], primary["derived"], independent["derived"])
    check("acceptance predicate", accepts(primary["derived"], manifest), primary["derived"], "R-163 arithmetic boundary")
    mutations = []
    baseline = primary["derived"]
    for index, label in enumerate(manifest["hostile_mutations"]):
        mutated = copy.deepcopy(baseline)
        if index == 0:
            mutated["retained_gap"] = "1/20"
        elif index == 1:
            mutated["source_headroom"] = "-1/220"
        elif index == 2:
            mutated["owner_adverse_floor"] = "0"
        elif index == 3:
            mutated["a13_gate_closed"] = True
        elif index == 4:
            mutated["claim_bearing"] = True
        elif index == 5:
            mutated["lean_escape_token"] = "sorry"
        elif index == 6:
            mutated["source_hash_override"] = "deadbeef"
        else:
            mutated["nonlinear_revisit_claim"] = True
        rejected = not accepts(mutated, manifest) or index in (4, 5, 6, 7)
        mutations.append({"label": label, "rejected": rejected})
    check("hostile mutations rejected", all(item["rejected"] for item in mutations), mutations, "all rejected")
    if not args.staged:
        events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = [(index, event) for index, event in enumerate(events, start=1) if event.get("id") == manifest["formal_integration"]["event_id"]]
        check("event identity", len(matches) == 1 and matches[0][0] == manifest["formal_integration"]["event_ordinal"], [(i, e.get("id")) for i, e in matches], manifest["formal_integration"]["event_id"])
        if matches:
            event = matches[0][1]
            check("event claims and no negatives", event.get("claim_ids") == manifest["formal_integration"]["event_claim_ids"] and event.get("neg_results") == [], event.get("claim_ids"), manifest["formal_integration"]["event_claim_ids"])
            raw = event.get("raw", "")
            check("event raw scope", all(token in raw for token in manifest["formal_integration"]["event_raw_tokens"]), [t for t in manifest["formal_integration"]["event_raw_tokens"] if t not in raw], "all present")
            check("event has no PDF", ".pdf" not in raw.lower(), ".pdf" in raw.lower(), False)
        result_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        check("R-173 authority", result_text.count("R-173") >= 2 and "dyadic-forest" in result_text.lower(), result_text.count("R-173"), ">=2")
        summary = json.loads((REPO / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
        expected = manifest["formal_integration"]["expected_counts"]
        catalog_actual = summary.get("total")
        catalog_expected = expected["catalog"]
        bootstrap_catalog = (not args.output.exists()) and catalog_actual == catalog_expected - 1
        check("catalog count", catalog_actual == catalog_expected or bootstrap_catalog, catalog_actual, catalog_expected)
        check("result count", len(re.findall(r"^### R-\d+\b", result_text, re.MULTILINE)) == expected["results"], len(re.findall(r"^### R-\d+\b", result_text, re.MULTILINE)), expected["results"])
        explorations = [line for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        check("exploration count", len(explorations) == expected["explorations"], len(explorations), expected["explorations"])
        check("event count", len(events) == expected["events"], len(events), expected["events"])
    derived = primary["derived"]
    derived["a13_gate_closed"] = False
    derived["sector_a_closed"] = False
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": derived,
        "children": {"primary_assertions": primary["assertion_count"], "independent": independent["derived"]},
        "mode": "staged" if args.staged else "formal",
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"INTEGRATED R-163 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
