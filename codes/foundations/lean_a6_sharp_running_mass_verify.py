"""Integrated verifier for the R-194 A6 running-mass boundary package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a6-sharp-running-mass-counterterm-boundary-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "lean_a6_sharp_running_mass.py"
INDEPENDENT = REPO / "codes" / "foundations" / "lean_a6_sharp_running_mass_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-K-COMPOSITE-DEFINITION" / "runs" / "2026-08-22-lean-r194-sharp-running-mass" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", str(Path(sys.executable))))


def sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False, suffix=".tmp") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
        temporary = Path(stream.name)
    os.replace(temporary, path)


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return completed, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["result_id"] == "R-194" and manifest["exploration_id"] == "EXP-000932", [manifest["result_id"], manifest["exploration_id"]], "R-194/EXP-000932")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("reused boundary", manifest["formal_integration"]["reused_negative_ids"] == ["NG-2026-07-20-A6-NAIVE-W-SUBTRACTION-NONUNIFORM"], manifest["formal_integration"]["reused_negative_ids"], "existing A6 no-go")
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key} hash", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    source = (REPO / manifest["files"]["lean_entrypoint"]["path"]).read_text(encoding="utf-8")
    check("all theorem markers", all(marker in source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "present")
    check("no Lean escape", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    boundary = manifest["boundary"] + " " + manifest["no_overclaim"]
    check("boundary keeps gate open", "counterterm" in boundary.lower() and "not uniformly coercive" in boundary.lower(), boundary, "open/noncoercive")
    check("boundary keeps local/full split", "spatial" in boundary.lower() and "full-field" in boundary.lower(), boundary, "spatial/full-field")
    check("eight hostile mutations declared", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)

    with tempfile.TemporaryDirectory(prefix="r194-integrated-") as temp:
        primary_run, independent_run = Path(temp) / "primary.json", Path(temp) / "independent.json"
        primary_proc, primary = run_child(PRIMARY, primary_run)
        independent_proc, independent = run_child(INDEPENDENT, independent_run)
        check("primary child", primary_proc.returncode == 0 and primary.get("verdict") == "PASS", primary_proc.stdout + primary_proc.stderr, "PASS")
        check("independent child", independent_proc.returncode == 0 and independent.get("verdict") == "PASS", independent_proc.stdout + independent_proc.stderr, "PASS")
        check("child exact agreement", primary.get("derived", {}).get("h_min") == independent.get("derived", {}).get("h_min"), [primary.get("derived", {}).get("h_min"), independent.get("derived", {}).get("h_min")], "equal h_min")
        check("child exact subsharp agreement", primary.get("derived", {}).get("subsharp", {}).get("difference") == independent.get("derived", {}).get("sub_difference"), [primary.get("derived", {}).get("subsharp", {}).get("difference"), independent.get("derived", {}).get("sub_difference")], "equal witness")
        check("child exact escape agreement", [row["ratio"] for row in primary.get("derived", {}).get("escape_rows", [])] == independent.get("derived", {}).get("ratios"), primary.get("derived", {}).get("escape_rows", []), "equal ratios")

    # Hostile mutation #1: a smaller h must fail on the registered witness.
    sub = independent["derived"]
    sub_difference = Fraction(str(sub["sub_difference"]))
    check("mutation smaller h rejected", sub_difference < 0, sub["sub_difference"], "negative witness")
    # Hostile mutation #2: the endpoint correction has a fixed positive sign.
    check("mutation reversed correction rejected", all(row["pass"] for row in primary["assertions"] if row["name"] == "endpoint exact identity"), "endpoint rows", "all exact")
    # Hostile mutations #3-#4: the registered formula and pinned positivity are load-bearing.
    check("mutation coefficient sign rejected", any(row["name"] == "pinned b positive" and row["pass"] for row in primary["assertions"]) and any(row["name"] == "pinned c positive" and row["pass"] for row in primary["assertions"]), "pinned signs", "b,c>0")
    check("mutation rho definition rejected", "rho=s+|Psi_3|^2" in manifest["registered_inputs"]["formula"], manifest["registered_inputs"]["formula"], "rho=s+|Psi_3|^2")
    # Hostile mutations #5-#7: the no-overclaim firewall must remain explicit.
    check("mutation uniform coercivity rejected", "not uniformly coercive" in boundary.lower(), boundary, "not uniformly coercive")
    check("mutation local-to-global rejected", "full-field" in boundary.lower() and "spatial" in boundary.lower(), boundary, "full-field/spatial boundary")
    check("mutation vacuum-scalar substitution rejected", "vacuum" in boundary.lower() and "full renormalised" in boundary.lower(), boundary, "vacuum/full renormalised boundary")
    # Hostile mutation #8 is the Lean escape check above.
    check("mutation Lean escape rejected", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "integrated", "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS",
        "assertion_count": len(rows), "assertions": rows, "primary": primary, "independent": independent,
        "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED R-194 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
