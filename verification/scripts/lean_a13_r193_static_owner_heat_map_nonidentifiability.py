"""Primary Lean/Fraction audit for the R-193 production-map interface witness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-r193-static-owner-heat-map-nonidentifiability-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R193.lean"
TOOLCHAIN = LEAN_ROOT / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r193-static-owner-heat-map-nonidentifiability" / "primary.json"


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


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


def pinned_lean() -> Path | None:
    encoded = TOOLCHAIN.read_text(encoding="utf-8").strip().replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / ("lean.exe" if os.name == "nt" else "lean")
    return candidate if candidate.is_file() else None


def compile_lean() -> subprocess.CompletedProcess[str]:
    lean = pinned_lean()
    if lean is None:
        return subprocess.CompletedProcess([], 1, "", "pinned lean executable missing")
    search = [LEAN_ROOT / ".lake" / "build" / "lib" / "lean"]
    packages = LEAN_ROOT / ".lake" / "packages"
    if packages.is_dir():
        search.extend(p / ".lake" / "build" / "lib" / "lean" for p in packages.iterdir() if (p / ".lake" / "build" / "lib" / "lean").is_dir())
    env = os.environ.copy()
    env["LEAN_PATH"] = os.pathsep.join(str(path) for path in search if path.is_dir())
    return subprocess.run([str(lean), "Tect/R193.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False, env=env)


def derive(manifest: dict[str, Any], authorities: dict[str, Any]) -> dict[str, Any]:
    data = manifest["registered_inputs"]["static_witness"]
    h1, h2 = F(data["hessian"][0]), F(data["hessian"][1])
    c1, c2 = F(data["covariance"][0]), F(data["covariance"][1])
    a1, a2 = F(data["map_a_factors"][0]), F(data["map_a_factors"][1])
    b1, b2 = F(data["map_b_factors"][0]), F(data["map_b_factors"][1])
    static_inverse = h1 * c1 == 1 and h2 * c2 == 1
    map_a_zero = (a1 * 0, a2 * 0) == (0, 0)
    map_b_zero = (b1 * 0, b2 * 0) == (0, 0)
    map_a_contracts = 0 < a1 < 1 and 0 < a2 < 1
    map_b_contracts = 0 < b1 < 1 and 0 < b2 < 1
    map_distinct = (a1 * 1, a2 * 0) != (b1 * 1, b2 * 0)
    order_reversed = a1 > a2 and b1 < b2
    required_fields = manifest["registered_inputs"]["required_absent_fields"]
    a1_text = json.dumps(authorities["a1"], sort_keys=True)
    a7_text = json.dumps(authorities["a7"], sort_keys=True)
    absent = {field: field not in a1_text and field not in a7_text for field in required_fields}
    return {
        "static_inverse": static_inverse,
        "map_a_zero": map_a_zero,
        "map_b_zero": map_b_zero,
        "map_a_contracts": map_a_contracts,
        "map_b_contracts": map_b_contracts,
        "maps_distinct": map_distinct,
        "relative_decay_order_reversed": order_reversed,
        "required_dynamic_fields_absent_from_a1_a7": absent,
        "r136_raw_spatial_intertwiner_proved": authorities["r136"]["scope"]["production_raw_spatial_intertwiner_proved"],
        "r136_q_ledger_proved": authorities["r136"]["scope"]["production_one_use_q_ledger_proved"],
        "r125_root_shell_factorisation_proved": authorities["r125"]["scope"]["production_root_shell_factorization_proved"],
        "interface_nonidentifiable": static_inverse and map_a_zero and map_b_zero and map_a_contracts and map_b_contracts and map_distinct and order_reversed and all(absent.values()) and not authorities["r136"]["scope"]["production_raw_spatial_intertwiner_proved"] and not authorities["r136"]["scope"]["production_one_use_q_ledger_proved"] and not authorities["r125"]["scope"]["production_root_shell_factorization_proved"],
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

    check("identity", manifest["audit_id"] == "A13-R193-STATIC-OWNER-HEAT-MAP-NONIDENTIFIABILITY" and manifest["result_id"] == "R-193", [manifest["audit_id"], manifest["result_id"]], "R-193 identity")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key} hash", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    lean_source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean markers", all(marker in lean_source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape absence", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    completed = compile_lean()
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    authorities = {key: json.loads((REPO / item["path"]).read_text(encoding="utf-8")) for key, item in manifest["inputs"].items() if key in {"a1", "a7", "r136", "r125"}}
    derived = derive(manifest, authorities)
    check("static inverse", derived["static_inverse"], derived["static_inverse"], True)
    check("both zero maps", derived["map_a_zero"] and derived["map_b_zero"], derived, "both zero-preserving")
    check("both contractions", derived["map_a_contracts"] and derived["map_b_contracts"], derived, "both coordinate contractions")
    check("distinct maps", derived["maps_distinct"], derived["maps_distinct"], True)
    check("reversed order", derived["relative_decay_order_reversed"], derived["relative_decay_order_reversed"], True)
    check("dynamic fields absent", all(derived["required_dynamic_fields_absent_from_a1_a7"].values()), derived["required_dynamic_fields_absent_from_a1_a7"], "all absent")
    check("prior production flags remain open", not derived["r136_raw_spatial_intertwiner_proved"] and not derived["r136_q_ledger_proved"] and not derived["r125_root_shell_factorisation_proved"], derived, "all false")
    check("interface witness", derived["interface_nonidentifiable"], derived["interface_nonidentifiable"], True)
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(), "lean_stdout": completed.stdout, "lean_stderr": completed.stderr, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-193 LEAN PASS {len(rows)}/{len(rows)} interface={derived['interface_nonidentifiable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
