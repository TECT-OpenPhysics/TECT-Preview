"""Primary exact Lean cross-check for the finite two-root scalar owner."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-two-root-complete-scalar-owner-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R191.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r191-two-root-complete-scalar-owner" / "primary.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
    for candidate in (Path.home() / ".elan" / "bin" / "lake.exe", Path.home() / ".elan" / "bin" / "lake"):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def moments(ri: dict[str, Any], a: F, b: F) -> tuple[F, F]:
    m4c = ri["moment_coefficients"]
    m4 = F(m4c["a4_b4"]) * (a**4 + b**4) + F(m4c["a2b2"]) * a**2 * b**2
    m6c = ri["moment_coefficients"]
    m6 = (
        F(m6c["a6_b6"]) * (a**6 + b**6)
        + F(m6c["a4b2"]) * a**4 * b**2
        + F(m6c["a2b4"]) * a**2 * b**4
    )
    return m4, m6


def owner(ri: dict[str, Any], q1: F, q2: F, a: F, b: F) -> F:
    m4, m6 = moments(ri, a, b)
    c4 = F(ri["owner_coefficients"]["quartic"])
    c6 = F(ri["owner_coefficients"]["sextic"])
    return q1 * a**2 + q2 * b**2 + c4 * m4 + c6 * m6


def gradients(ri: dict[str, Any], q1: F, q2: F, a: F, b: F) -> tuple[F, F]:
    c = ri["moment_coefficients"]
    c44, c22 = F(c["a4_b4"]), F(c["a2b2"])
    c60, c42, c24 = F(c["a6_b6"]), F(c["a4b2"]), F(c["a2b4"])
    c4, c6 = F(ri["owner_coefficients"]["quartic"]), F(ri["owner_coefficients"]["sextic"])
    dm4_a = 4 * c44 * a**3 + 2 * c22 * a * b**2
    dm4_b = 4 * c44 * b**3 + 2 * c22 * a**2 * b
    dm6_a = 6 * c60 * a**5 + 4 * c42 * a**3 * b**2 + 2 * c24 * a * b**4
    dm6_b = 6 * c60 * b**5 + 2 * c42 * a**4 * b + 4 * c24 * a**2 * b**3
    return 2 * q1 * a + c4 * dm4_a + c6 * dm6_a, 2 * q2 * b + c4 * dm4_b + c6 * dm6_b


def stages(ri: dict[str, Any], h: F, r1: F, r2: F, f1: F, f2: F) -> list[tuple[F, F]]:
    beta = F(ri["incidence"]["feedback_gain"])
    g1 = h + r1
    g2 = h + beta * g1 + r2
    return [(h, h), (g1, h + beta * g1), (g1, g2), (g1 + f1, g2 + f2)]


def derive(manifest: dict[str, Any]) -> dict[str, Any]:
    ri = manifest["registered_inputs"]
    fixture = manifest["test_oracles"]["fixture"]
    q1, q2 = F(fixture["q1"]), F(fixture["q2"])
    h, r1, r2 = F(fixture["h"]), F(fixture["r1"]), F(fixture["r2"])
    f1, f2 = F(fixture["f1"]), F(fixture["f2"])
    points = stages(ri, h, r1, r2, f1, f2)
    energies = [owner(ri, q1, q2, *point) for point in points]
    increments = [energies[i + 1] - energies[i] for i in range(3)]
    endpoint_delta = energies[-1] - energies[0]
    ga, gb = gradients(ri, q1, q2, *points[-1])
    beta = F(ri["incidence"]["feedback_gain"])
    return {
        "moment_m4_at_one": moments(ri, F(1), F(1))[0],
        "moment_m6_at_one": moments(ri, F(1), F(1))[1],
        "stage_points": points,
        "stage_energies": energies,
        "stage_increments": increments,
        "endpoint_delta": endpoint_delta,
        "endpoint_gradient": (ga, gb),
        "dr1": ga + beta * gb,
        "dr2": gb,
        "df1": ga,
        "df2": gb,
        "telescope_exact": sum(increments, F(0)) == endpoint_delta,
        "intermediate_negative": any(value < 0 for value in increments),
        "endpoint_positive": endpoint_delta > 0,
        "r176_root_labels": manifest["registered_inputs"]["root_labels"],
        "r177_owner_order": manifest["registered_inputs"]["incidence"]["owner_order"],
        "r178_ordered_block_retained": True,
        "a13_gate_closed": False,
        "sector_a_closed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-TWO-ROOT-COMPLETE-SCALAR-OWNER", manifest["audit_id"], "A13-TWO-ROOT-COMPLETE-SCALAR-OWNER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    r176 = json.loads((REPO / manifest["inputs"]["r176_run"]["path"]).read_text(encoding="utf-8"))
    r177 = json.loads((REPO / manifest["inputs"]["r177_run"]["path"]).read_text(encoding="utf-8"))
    check("R-176 actual roots", r176["verdict"] == "PASS" and r176["derived"]["root_labels"] == manifest["registered_inputs"]["root_labels"], r176["derived"]["root_labels"], manifest["registered_inputs"]["root_labels"])
    check("R-177 incidence", r177["verdict"] == "PASS" and r177["derived"]["owner_order"] == manifest["registered_inputs"]["incidence"]["owner_order"], r177["derived"]["owner_order"], manifest["registered_inputs"]["incidence"]["owner_order"])
    derived = derive(manifest)
    oracle = manifest["test_oracles"]
    check("m4 moment", derived["moment_m4_at_one"] == F(oracle["moment_m4_at_one"]), derived["moment_m4_at_one"], oracle["moment_m4_at_one"])
    check("m6 moment", derived["moment_m6_at_one"] == F(oracle["moment_m6_at_one"]), derived["moment_m6_at_one"], oracle["moment_m6_at_one"])
    check("telescope", derived["telescope_exact"], derived["stage_increments"], "sum equals endpoint")
    check("stage increment fixture", derived["stage_increments"] == [F(value) for value in oracle["fixture"]["stage_increments"]], derived["stage_increments"], oracle["fixture"]["stage_increments"])
    check("endpoint positive fixture", derived["endpoint_positive"], derived["endpoint_delta"], ">0")
    check("intermediate sign firewall", derived["intermediate_negative"], derived["stage_increments"], "at least one negative stage")
    for key in ("endpoint_delta", "dr1", "dr2", "df1", "df2"):
        check(f"fixture {key}", derived[key] == F(oracle["fixture"][key]), derived[key], oracle["fixture"][key])
    check("A13 remains open", not derived["a13_gate_closed"] and not derived["sector_a_closed"], derived, "finite prerequisite only")
    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean markers", all(marker in source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape absence", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": derived,
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-191 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
