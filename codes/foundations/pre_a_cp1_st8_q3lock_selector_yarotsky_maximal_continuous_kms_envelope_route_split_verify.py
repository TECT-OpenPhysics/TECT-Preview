#!/usr/bin/env python3
"""Integrated verifier for the R-167 v2.9 selector/continuous-core split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-selector-yarotsky-maximal-continuous-kms-envelope-route-split"
PRIMARY = REPO / f"codes/foundations/pre_a_cp1_st8_q3lock_selector_yarotsky_maximal_continuous_kms_envelope_route_split.py"
INDEPENDENT = REPO / f"codes/foundations/pre_a_cp1_st8_q3lock_selector_yarotsky_maximal_continuous_kms_envelope_route_split_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-integrated-{SLUG}/result.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = {
    "gates": REPO / "claims/GATES.md",
    "results": REPO / "RESULTS-LEDGER.md",
    "negatives": REPO / "negative-results/registry.md",
    "explorations": REPO / "explorations/log.jsonl",
    "changelog": REPO / "changelog/log.jsonl",
    "todo": REPO / "todo/todo.json",
    "roadmap": REPO / "ROADMAP.md",
    "strategy": REPO / "strategy/INDEX.md",
    "theorem_map": REPO / "governance/sector-a-theorem-map.json",
}


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def execute_child(path: Path, staged: bool) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-v29-") as temporary:
        output = Path(temporary) / "result.json"
        command = [sys.executable, "-X", "utf8", str(path), "--output", str(output)]
        if staged:
            command.append("--staged")
        result = subprocess.run(command, cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=120)
        if result.returncode != 0:
            raise AssertionError(f"child failed {path.name}: {result.stdout}\n{result.stderr}")
        return json.loads(output.read_text(encoding="utf-8"))


def assertion_core(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "package_id": payload.get("package_id"),
        "verdict": payload.get("verdict"),
        "derived": payload.get("derived"),
        "rows": [row for row in payload.get("assertions", []) if row.get("group") != "formal"],
        "source_hashes": payload.get("source_hashes"),
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    primary = execute_child(PRIMARY, staged)
    independent = execute_child(INDEPENDENT, staged)
    audit = Audit()

    audit.check("child verdicts", primary["verdict"] == independent["verdict"] == "PASS", (primary["verdict"], independent["verdict"]), ("PASS", "PASS"), "children")
    audit.check("child assertion integrity", all(row["status"] == "PASS" for payload in (primary, independent) for row in payload["assertions"]), (primary["summary"], independent["summary"]), "all PASS", "children")
    audit.check("child source freshness", primary["source_hashes"][str(PRIMARY.relative_to(REPO)).replace("\\", "/")] == normalized_sha256(PRIMARY) and independent["source_hashes"][str(INDEPENDENT.relative_to(REPO)).replace("\\", "/")] == normalized_sha256(INDEPENDENT), (primary["source_hashes"], independent["source_hashes"]), "current", "children")

    for key in ("selector", "radius", "categorical"):
        audit.check(f"independent exact {key}", primary["derived"][key] == independent["derived"][key], (primary["derived"][key], independent["derived"][key]), "exact equality", "cross")
    audit.check("manifest exact selector", primary["derived"]["selector"] == manifest["exact_fixture"]["selector"], primary["derived"]["selector"], manifest["exact_fixture"]["selector"], "cross")
    audit.check("manifest exact radius", primary["derived"]["radius"] == manifest["exact_fixture"]["radius"], primary["derived"]["radius"], manifest["exact_fixture"]["radius"], "cross")
    audit.check("manifest exact categorical", primary["derived"]["categorical"] == manifest["exact_fixture"]["categorical"], primary["derived"]["categorical"], manifest["exact_fixture"]["categorical"], "cross")

    audit.check("manifest four and three", len(manifest["closed_gate_ids"]) == 4 and len(manifest["negative_ids"]) == 3, (len(manifest["closed_gate_ids"]), len(manifest["negative_ids"])), (4, 3), "manifest")
    audit.check(
        "manifest five OPEN parents",
        len(manifest["open_parent_gate_ids"]) == 5
        and "all five active parent gates remain OPEN" in manifest["no_overclaim"],
        manifest["open_parent_gate_ids"],
        "five explicitly OPEN",
        "manifest",
    )
    audit.check("certificate exact star gap", "g_{*,N}(u)=\\min" in certificate and "3\\beta_N\\over u" in certificate, "gap/form tokens", "present", "certificate")
    audit.check("certificate common-alpha firewall", "categorical" in certificate and "all-shape Cauchy" in certificate and "parent gates remain OPEN" in certificate, "scope tokens", "present", "certificate")

    stored_status: dict[str, str] = {}
    for label, path, fresh in (("primary", PRIMARY_RESULT, primary), ("independent", INDEPENDENT_RESULT, independent)):
        if path.exists():
            stored = json.loads(path.read_text(encoding="utf-8"))
            same = stored == fresh if not staged else assertion_core(stored) == assertion_core(fresh)
            stored_status[label] = "fresh" if same else "stale"
            audit.check(f"stored {label} fresh", same, stored_status[label], "fresh", "stored")
        elif staged:
            stored_status[label] = "absent-staged"
            audit.check(f"stored {label} staged absence", True, stored_status[label], "allowed", "stored")
        else:
            raise AssertionError(f"stored {label} result missing: {path}")

    if not staged:
        texts = {name: path.read_text(encoding="utf-8") for name, path in FORMAL_PATHS.items()}
        audit.check("EXP-000833 unique", texts["explorations"].count('"id":"EXP-000833"') == 1 and '"relation":"continues"' in texts["explorations"], texts["explorations"].count('"id":"EXP-000833"'), 1, "formal")
        audit.check("four CLOSED gate sections", all(texts["gates"].count(f"### **{gate}**") == 1 and "CLOSED" in texts["gates"].split(f"### **{gate}**", 1)[1].split("### **", 1)[0] for gate in manifest["closed_gate_ids"]), manifest["closed_gate_ids"], "unique CLOSED", "formal")
        audit.check("five parents retained OPEN", all(texts["gates"].count(f"### **{gate}**") == 1 and "OPEN" in texts["gates"].split(f"### **{gate}**", 1)[1].split("### **", 1)[0] for gate in manifest["open_parent_gate_ids"]), manifest["open_parent_gate_ids"], "unique OPEN", "formal")
        audit.check("three negative authorities", all(texts["negatives"].count(f"### {negative} --") == 1 for negative in manifest["negative_ids"]), manifest["negative_ids"], "unique detail", "formal")
        audit.check("R-167 v2.9 current", "R-167 v2.9" in texts["results"] and "EXP-000833" in texts["results"] and "No v2.9 PDF" in texts["results"], "result tokens", "present", "formal")
        audit.check("T-054 and roadmap", "EXP-000833" in texts["todo"] and "EXP-000833" in texts["roadmap"], "EXP-000833", "linked", "formal")
        audit.check("strategy and theorem map", "EXP-000833" in texts["strategy"] and "EXP-000833" in texts["theorem_map"], "EXP-000833", "linked", "formal")
        audit.check("unique theorem event", texts["changelog"].count("R-167 v2.9") == 1 and ".pdf" not in texts["changelog"].split("R-167 v2.9", 1)[1].split("\n", 1)[0], texts["changelog"].count("R-167 v2.9"), 1, "formal")

    payload = {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": {"selector": primary["derived"]["selector"], "radius": primary["derived"]["radius"], "categorical": primary["derived"]["categorical"], "stored": stored_status},
        "source_hashes": {str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path) for path in (SCRIPT, PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE)},
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v2.9 INTEGRATED PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
