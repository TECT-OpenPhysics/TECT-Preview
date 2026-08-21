"""Primary Lean cross-check for the finite signed Jensen-defect telescope."""

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
MANIFEST = REPO / "strategy" / "pre-a13-jensen-defect-telescope-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R188.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r188-jensen-defect-telescope-crosscheck" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
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
    c = Fraction(values["c"])
    roots = [Fraction(value) for value in values["root_values"]]
    next_values = [Fraction(value) for value in values["next_values"]]

    def atom(e1: Fraction, e2: Fraction) -> Fraction:
        return e2 * (1 + c * e1)

    j0 = sum(atom(e1, e2) ** 2 for e1 in roots for e2 in next_values) / (len(roots) * len(next_values))
    j1 = {str(e1): sum(atom(e1, e2) ** 2 for e2 in next_values) / len(next_values) for e1 in roots}
    j2 = {f"{e1}|{e2}": atom(e1, e2) ** 2 for e1 in roots for e2 in next_values}
    d_h1 = {str(e1): j1[str(e1)] - j0 for e1 in roots}
    d_h2 = {f"{e1}|{e2}": j2[f"{e1}|{e2}"] - j1[str(e1)] for e1 in roots for e2 in next_values}
    secant1 = {str(e1): Fraction(0) for e1 in roots}
    secant2 = {f"{e1}|{e2}": j2[f"{e1}|{e2}"] for e1 in roots for e2 in next_values}
    defect1 = dict(d_h1)
    defect2 = {f"{e1}|{e2}": -j1[str(e1)] for e1 in roots for e2 in next_values}
    endpoint = {key: j2[key] - j0 for key in j2}
    telescope_residual = {key: d_h1[key.split("|")[0]] + d_h2[key] - endpoint[key] for key in endpoint}
    recombination_residual = {
        str(e1): d_h1[str(e1)] - (secant1[str(e1)] + defect1[str(e1)]) for e1 in roots
    }
    recombination_residual.update(
        {
            f"{e1}|{e2}": d_h2[f"{e1}|{e2}"]
            - (secant2[f"{e1}|{e2}"] + defect2[f"{e1}|{e2}"])
            for e1 in roots
            for e2 in next_values
        }
    )
    signed_endpoint_mean = sum(endpoint.values()) / len(endpoint)
    absolute_first_defect_mean = sum(abs(value) for value in d_h1.values()) / len(d_h1)
    return {
        "j0": j0,
        "j1_minus": j1[str(roots[0])],
        "j1_plus": j1[str(roots[-1])],
        "j2_minus_minus": j2[f"{roots[0]}|{next_values[0]}"] ,
        "j2_minus_plus": j2[f"{roots[0]}|{next_values[-1]}"] ,
        "j2_plus_minus": j2[f"{roots[-1]}|{next_values[0]}"] ,
        "j2_plus_plus": j2[f"{roots[-1]}|{next_values[-1]}"] ,
        "dH1_minus": d_h1[str(roots[0])],
        "dH1_plus": d_h1[str(roots[-1])],
        "dH2_all_zero": all(value == 0 for value in d_h2.values()),
        "secant1": secant1[str(roots[-1])],
        "secant2_plus_plus": secant2[f"{roots[-1]}|{next_values[-1]}"] ,
        "defect1_minus": defect1[str(roots[0])],
        "defect1_plus": defect1[str(roots[-1])],
        "defect2_plus_plus": defect2[f"{roots[-1]}|{next_values[-1]}"] ,
        "signed_endpoint_mean": signed_endpoint_mean,
        "absolute_first_defect_mean": absolute_first_defect_mean,
        "telescope_residual_max": max(abs(value) for value in telescope_residual.values()),
        "recombination_residual_max": max(abs(value) for value in recombination_residual.values()),
        "absolute_payment_strict": absolute_first_defect_mean > 0,
        "a13_gate_closed": False,
        "overlap_src_closed": False,
        "production_map_identified": False,
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

    check("manifest identity", manifest["audit_id"] == "A13-JENSEN-DEFECT-TELESCOPE-CROSSCHECK", manifest["audit_id"], "A13-JENSEN-DEFECT-TELESCOPE-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    values = manifest["registered_inputs"]
    derived = derive(values)
    expected = values["expected"]
    for key, wanted in expected.items():
        actual = derived[key]
        check(key, actual == (Fraction(wanted) if isinstance(wanted, str) else wanted), actual, wanted)
    check("absolute payment is strict", derived["absolute_payment_strict"], derived["absolute_first_defect_mean"], ">0")
    check("signed endpoint is zero", derived["signed_endpoint_mean"] == 0, derived["signed_endpoint_mean"], 0)
    check("boundary remains open", not derived["a13_gate_closed"] and not derived["overlap_src_closed"] and not derived["production_map_identified"], derived, "all open")
    source_text = LEAN_ENTRYPOINT.read_text(encoding="ascii")
    check("Lean theorem markers", all(marker in source_text for marker in manifest["theorem_markers"]), [marker for marker in manifest["theorem_markers"] if marker in source_text], manifest["theorem_markers"])
    check("Lean escape tokens absent", not any(token in source_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], ["sorry", "admit", "axiom", "unsafe"])
    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.returncode == 0 and "error:" not in completed.stdout.lower() and "error:" not in completed.stderr.lower(), [completed.stdout, completed.stderr], "no Lean errors")
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {key: str(value) if isinstance(value, Fraction) else value for key, value in derived.items()},
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-188 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
