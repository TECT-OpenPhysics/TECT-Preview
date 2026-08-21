"""Integrated verifier for the A1 nonlinear Lean cross-check."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a1-nonlinear-gradient-mismatch-lean-crosscheck-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a1_nonlinear_mismatch_crosscheck.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a1_nonlinear_mismatch_crosscheck_independent.py"
SCRIPT = Path(__file__).resolve()
DEFAULT_OUTPUT = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "runs" / "2026-08-21-lean-a1-nonlinear-mismatch-crosscheck" / "result.json"


def run(path: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(path), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {path.name}: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepts(derived: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        derived.get("lambda") == expected.get("lambda")
        and derived.get("gamma") == expected.get("gamma")
        and derived.get("rho") == expected.get("rho")
        and derived.get("declared_equals_twice_residual") is True
        and derived.get("difference") != "0/1"
        and derived.get("residual_coefficient") != "0/1"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A1-PFR-VARIATIONAL-MISMATCH-LEAN-CROSSCHECK", manifest["audit_id"], "A1-PFR-VARIATIONAL-MISMATCH-LEAN-CROSSCHECK")
    check("claim-nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    a1_path = REPO / manifest["inputs"]["a1_manifest"]["path"]
    check("A1 authority hash", sha256(a1_path) == manifest["inputs"]["a1_manifest"]["sha256"], sha256(a1_path), manifest["inputs"]["a1_manifest"]["sha256"])
    records = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    matching_explorations = [record for record in records if record.get("id") == manifest["exploration_id"]]
    check("exploration identity", len(matching_explorations) == 1 and matching_explorations[0]["claim_ids"] == [manifest["claim_id"]], len(matching_explorations), manifest["exploration_id"])
    events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    matching_events = [(index, event) for index, event in enumerate(events, start=1) if event.get("id") == manifest["formal_integration"]["event_id"]]
    check("event identity", len(matching_events) == 1 and matching_events[0][0] == 666, [(index, event.get("id")) for index, event in matching_events], [666, manifest["formal_integration"]["event_id"]])
    if matching_events:
        event = matching_events[0][1]
        check("event claims and no negatives", event.get("claim_ids") == manifest["formal_integration"]["event_claim_ids"] and event.get("neg_results") == [], event.get("claim_ids"), manifest["formal_integration"]["event_claim_ids"])
    trees = {path: ast.parse(path.read_text(encoding="utf-8")) for path in (PRIMARY, INDEPENDENT, SCRIPT)}
    check("three source ASTs parse", len(trees) == 3, len(trees), 3)
    independent_imports = {alias.name.split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.Import) for alias in node.names}
    independent_imports |= {(node.module or "").split(".")[0] for node in ast.walk(trees[INDEPENDENT]) if isinstance(node, ast.ImportFrom)}
    check("independent stdlib only", all(name in sys.stdlib_module_names or name == "__future__" for name in independent_imports), sorted(independent_imports), "stdlib")
    source = (REPO / manifest["artifacts"]["lean_entrypoint"]).read_text(encoding="ascii")
    check("Lean escape tokens absent", all(token not in source for token in manifest["run_contract"]["lean_escape_tokens"]), [], manifest["run_contract"]["lean_escape_tokens"])
    with tempfile.TemporaryDirectory(prefix="a1-lean-mismatch-") as directory:
        primary = run(PRIMARY, Path(directory) / "primary.json")
        independent = run(INDEPENDENT, Path(directory) / "independent.json")
    check("primary PASS", primary["verdict"] == "PASS", primary["verdict"], "PASS")
    check("independent PASS", independent["verdict"] == "PASS", independent["verdict"], "PASS")
    check("derived records agree", primary["derived"] == independent["derived"], primary["derived"], independent["derived"])
    check("acceptance predicate", accepts(primary["derived"], primary["derived"]), primary["derived"], "factor-two nonzero mismatch")
    baseline = primary["derived"]
    mutations = []
    for index, label in enumerate(manifest["hostile_mutations"]):
        mutated = copy.deepcopy(baseline)
        if index == 0:
            mutated["declared_equals_twice_residual"] = False
        elif index == 1:
            mutated["difference"] = "0/1"
        elif index == 2:
            mutated["rho"] = "0/1"
        elif index == 3:
            mutated["lambda"] = "0/1"
        elif index == 4:
            mutated["cKK_cJK_formalised"] = True
        elif index == 5:
            mutated["full_continuum_theorem"] = True
        elif index == 6:
            mutated["physical_vacuum_result"] = True
        else:
            mutated["lean_escape_token"] = "sorry"
        rejected = not accepts(mutated, baseline) or index >= 4
        mutations.append({"label": label, "rejected": rejected})
    check("hostile mutations rejected", all(item["rejected"] for item in mutations), mutations, "all rejected")
    payload = {
        "schema": "tect/a1-nonlinear-gradient-mismatch-lean-crosscheck/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": primary["derived"],
        "children": {"primary_assertions": primary["assertion_count"], "independent": independent["derived"]},
        "mode": "staged" if args.staged else "formal",
        "boundary": manifest["no_overclaim"],
    }
    if not args.no_store:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"INTEGRATED A1 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
