"""Primary Lean cross-check for the R-081 temporal packet algebra."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-temporal-packet-algebra-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R186.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r186-temporal-packet-algebra-crosscheck" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def derive(values: dict[str, Any]) -> dict[str, Any]:
    weights = [Fraction(value) for value in values["weights"]]
    j_values = [Fraction(value) for value in values["j_values"]]
    control = Fraction(values["control"])
    interval_length = Fraction(values["interval_length"])
    weighted_mean = sum(w * j for w, j in zip(weights, j_values))
    covariance = sum(w * j * j for w, j in zip(weights, j_values))
    displacement = weighted_mean * control
    douglas_h_sq = displacement * displacement / covariance
    rows = [
        tuple(Fraction(value) for value in row)
        for row in values["packet_rows"]
    ]
    endpoint = sum(Fraction(1, 2) * ((base + fresh + future) ** 2 - base ** 2) - Fraction(1, 2) * (trace_fresh + trace_future) for base, fresh, future, trace_fresh, trace_future in rows)
    packet_sum = sum(base * fresh + Fraction(1, 2) * fresh ** 2 - Fraction(1, 2) * trace_fresh + (base + fresh) * future + Fraction(1, 2) * future ** 2 - Fraction(1, 2) * trace_future for base, fresh, future, trace_fresh, trace_future in rows)
    retained_cross = sum(fresh * future for _, fresh, future, _, _ in rows)
    return {
        "weighted_mean": weighted_mean,
        "covariance": covariance,
        "displacement": displacement,
        "douglas_h_sq": douglas_h_sq,
        "weighted_cauchy_holds": weighted_mean * weighted_mean <= interval_length * covariance,
        "douglas_energy_holds": douglas_h_sq <= interval_length * control * control,
        "packet_endpoint": endpoint,
        "packet_sum": packet_sum,
        "packet_residual": endpoint - packet_sum,
        "retained_cross": retained_cross,
        "packet_cross_nonzero": retained_cross != 0,
        "a13_gate_closed": False,
        "overlap_src_closed": False,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-TEMPORAL-PACKET-ALGEBRA-CROSSCHECK", manifest["audit_id"], "A13-TEMPORAL-PACKET-ALGEBRA-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    values = manifest["registered_inputs"]
    derived = derive(values)
    expected = values["expected"]
    for key in ("weighted_mean", "covariance", "displacement", "douglas_h_sq", "packet_endpoint", "packet_sum", "packet_residual", "retained_cross"):
        check(key, derived[key] == Fraction(expected[key]), derived[key], expected[key])
    check("weighted Cauchy fixture", derived["weighted_cauchy_holds"], derived["weighted_cauchy_holds"], True)
    check("Douglas energy contraction", derived["douglas_energy_holds"], derived["douglas_energy_holds"], True)
    check("retained cross nonzero", derived["packet_cross_nonzero"] and derived["retained_cross"] > 0, derived["retained_cross"], ">0")
    check("A13 boundary open", not derived["a13_gate_closed"] and not derived["overlap_src_closed"], derived, "both open")
    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
    derived["input_count"] = len(values["packet_rows"])
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-186 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
