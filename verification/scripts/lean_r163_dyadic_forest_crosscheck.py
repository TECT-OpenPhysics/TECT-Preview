"""Primary Lean cross-check for the exact R-163 dyadic-forest margins."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-r163-dyadic-forest-lean-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R163.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LAKE_MANIFEST = LEAN_DIR / "lake-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r163-dyadic-forest-crosscheck" / "primary.json"
FORBIDDEN = ("sorry", "admit", "axiom", "unsafe")


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def find_lake() -> str | None:
    home = Path.home()
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = home / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    for fallback in (home / ".elan" / "bin" / "lake.exe", home / ".elan" / "bin" / "lake"):
        if fallback.is_file():
            return str(fallback)
    return shutil.which("lake")


def f(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(str(value))


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    check(rows, "manifest identity", manifest["audit_id"] == "A13-R163-DYADIC-FOREST-LEAN-CROSSCHECK", manifest["audit_id"], "A13-R163-DYADIC-FOREST-LEAN-CROSSCHECK")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check(rows, "no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        actual = sha256(path) if path.is_file() else None
        check(rows, f"input {key} hash", path.is_file() and actual == item["sha256"], actual, item["sha256"])
    source = LEAN_ENTRYPOINT.read_text(encoding="ascii")
    check(rows, "Lean theorem markers", all(marker in source for marker in manifest["theorem_markers"]), [m for m in manifest["theorem_markers"] if m in source], manifest["theorem_markers"])
    check(rows, "Lean escape tokens absent", not any(re.search(rf"\b{token}\b", source) for token in FORBIDDEN), [], FORBIDDEN)
    r163_manifest = json.loads((REPO / manifest["inputs"]["r163_manifest"]["path"]).read_text(encoding="utf-8"))
    primary = json.loads((REPO / manifest["inputs"]["r163_primary_result"]["path"]).read_text(encoding="utf-8"))
    independent = json.loads((REPO / manifest["inputs"]["r163_independent_result"]["path"]).read_text(encoding="utf-8"))
    check(rows, "R-163 identity", r163_manifest["result_ledger_id"] == "R-163", r163_manifest["result_ledger_id"], "R-163")
    check(rows, "R-163 children PASS", primary.get("summary", {}).get("failed") == 0 and independent.get("summary", {}).get("failed") == 0, [primary.get("summary"), independent.get("summary")], "both failed=0")
    pd = primary["diagnostics"]
    idg = independent["diagnostics"]
    for key in ("origin_gap", "retained_gap", "reduced_action_hessian_floor", "owner_adverse_floor", "CM_D3_bound_at_r0"):
        check(rows, f"child diagnostic agreement {key}", pd[key] == idg[key], pd[key], idg[key])
    c = manifest["registered_constants"]
    origin = f(pd["origin_gap"])
    loss = f(c["origin_gap_loss"])
    retained = origin - loss
    check(rows, "retained gap derived", retained == f(c["retained_gap"]), str(retained), c["retained_gap"])
    check(rows, "retained gap exceeds target", retained > f(c["target_gap"]), str(retained), f"> {c['target_gap']}")
    headroom = f(c["epsilon_v_limit"]) - f(c["explicit_source_coefficient"])
    check(rows, "source headroom derived", headroom == f(c["coefficient_headroom"]), str(headroom), c["coefficient_headroom"])
    owner_floor = -2 * headroom - 2 * f(c["explicit_source_coefficient"])
    check(rows, "owner floor derived", owner_floor == f(c["owner_adverse_floor"]), str(owner_floor), c["owner_adverse_floor"])
    check(rows, "sextic window", f(pd["epsilon_6"]) < f(c["epsilon_6_limit"]), pd["epsilon_6"], f"< {c['epsilon_6_limit']}")
    check(rows, "recursive guard", (Fraction(100, 97) ** 4) < Fraction(13, 10), str(Fraction(100, 97) ** 4), "< 13/10")
    check(rows, "third derivative fixture", Fraction(27, 5) * Fraction(3, 2) / Fraction(1, 2) ** 5 == Fraction(1296, 5), "1296/5", "1296/5")
    lake = find_lake()
    check(rows, "lake available", lake is not None, lake, "pinned toolchain or PATH")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check(rows, "Lean compile", completed.returncode == 0, completed.returncode, 0)
    check(rows, "Lean stdout clean", completed.stdout.strip() == "", completed.stdout, "")
    check(rows, "Lean stderr clean", completed.stderr.strip() == "", completed.stderr, "")
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "origin_gap": str(origin),
            "retained_gap": str(retained),
            "source_headroom": str(headroom),
            "owner_adverse_floor": str(owner_floor),
            "epsilon_6": str(f(pd["epsilon_6"])),
            "recursive_guard": str(Fraction(100, 97) ** 4),
            "source_third_derivative": "1296/5",
        },
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PRIMARY R-163 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
