#!/usr/bin/env python3
"""Integrated replay for PAH-OMC-026."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc026-cut-set-packet-crosswalk"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-026-cut-set-packet-crosswalk-contract-v1.json"
RESULT = ROOT / "strategy/pa-hyp/PAH-OMC-026-cut-set-packet-crosswalk-result-v1.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc026CutSetPacketCrosswalk.lean"
SCRIPTS = {
    "primary": ROOT / "verification/scripts/pah_omc026_cut_set_packet_crosswalk.py",
    "independent": ROOT / "codes/foundations/pah_omc026_cut_set_packet_crosswalk_independent.py",
    "hostile": ROOT / "codes/foundations/pah_omc026_cut_set_packet_crosswalk_hostile.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def lake_path() -> Path | None:
    registry = load(REGISTRY)
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = base / name
        if candidate.is_file():
            return candidate
    return None


def lean_run(check_only: bool) -> dict[str, Any]:
    registry = load(REGISTRY)
    toolchain = registry["toolchain"]["toolchain"]
    lake = lake_path()
    if lake is None:
        payload = {"schema": "tect/pah-omc026-lean-run/1.0", "status": "UNAVAILABLE", "toolchain": toolchain, "source_hash": sha(LEAN)}
    else:
        worktree = ROOT / "verification/lean"
        canonical = Path("E:/Dev/TECT/verification/lean")
        if (worktree / ".lake/packages/mathlib").is_dir():
            cwd, source, scope = worktree, "Tect/PahOmc026CutSetPacketCrosswalk.lean", "lane-local-pinned-packages"
        elif (canonical / ".lake/packages/mathlib").is_dir():
            cwd, source, scope = canonical, str(LEAN), "read-only-canonical-pinned-packages"
        else:
            cwd, source, scope = worktree, "Tect/PahOmc026CutSetPacketCrosswalk.lean", "lane-local-missing-packages"
        env = os.environ.copy()
        if scope == "read-only-canonical-pinned-packages":
            env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory", "GIT_CONFIG_VALUE_0": "*"})
        proc = subprocess.run([str(lake), "env", "lean", source], cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        output = proc.stdout + proc.stderr
        payload = {"schema": "tect/pah-omc026-lean-run/1.0", "status": "PASS" if proc.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": proc.returncode, "toolchain": toolchain, "source_hash": sha(LEAN), "dependency_scope": scope}
    destination = RUN / "lean.json"
    encoded = atomic_json(destination, payload) if not check_only else (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if check_only and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-026 Lean replay mismatch")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN / "integrated.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    replay: dict[str, Any] = {}
    for name, script in SCRIPTS.items():
        output = RUN / f"{name}.json"
        command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
        if args.check:
            command.append("--check")
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        check(rows, f"{name} replay", proc.returncode, 0, proc.returncode == 0)
        replay[name] = {"returncode": proc.returncode, "stdout": proc.stdout.strip()[-300:]}
    lean = lean_run(args.check)
    check(rows, "Lean compile", lean.get("status"), "PASS", lean.get("status") == "PASS")
    contract = load(CONTRACT)
    result = load(RESULT)
    registry = load(REGISTRY)
    runs = {name: load(RUN / f"{name}.json") for name in SCRIPTS}
    check(rows, "result identity", result.get("result_id"), "R-566", result.get("result_id") == "R-566")
    check(rows, "result hold verdict", result.get("verdict"), "HOLD_FOR_EVIDENCE", result.get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "result claim firewall", result.get("claim_bearing"), False, result.get("claim_bearing") is False)
    check(rows, "result physical firewall", result.get("physical_promotion"), False, result.get("physical_promotion") is False)
    for name, run in runs.items():
        check(rows, f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(rows, f"{name} checks", all(item.get("status") == "PASS" for item in run.get("checks", [])), True, all(item.get("status") == "PASS" for item in run.get("checks", [])))
    check(rows, "contract source packet absent", contract["current_status"]["source_authorized_packet_present"], False, contract["current_status"]["source_authorized_packet_present"] is False)
    check(rows, "contract route hold", contract["current_status"]["PAH_OMC_020"], "HOLD_FOR_EVIDENCE", contract["current_status"]["PAH_OMC_020"] == "HOLD_FOR_EVIDENCE")
    check(rows, "Lean registry entry", any(item.get("path") == "verification/lean/Tect/PahOmc026CutSetPacketCrosswalk.lean" for item in registry.get("entrypoints", [])), True, any(item.get("path") == "verification/lean/Tect/PahOmc026CutSetPacketCrosswalk.lean" for item in registry.get("entrypoints", [])))
    payload = {
        "schema": "tect/pah-omc026-cut-set-packet-crosswalk-integrated/1.0",
        "audit_id": "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK-INTEGRATED-001",
        "result_id": "R-566",
        "contract_id": "PAH-OMC-026-CUT-SET-PACKET-CROSSWALK",
        "task_id": "T-093",
        "status": "PASS_INTEGRATED_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": rows,
        "checks_passed": len(rows),
        "replay": replay,
        "lean": lean,
        "source_hashes": {p.relative_to(ROOT).as_posix(): sha(p) for p in (CONTRACT, *SCRIPTS.values(), Path(__file__), LEAN, REGISTRY)},
        "child_run_hashes": {name: sha(RUN / f"{name}.json") for name in SCRIPTS},
        "lean_run_hash": sha(RUN / "lean.json"),
        "finding": "All replay roles agree that R-557 field completeness refines the R-565 cuts, while the coarse cuts alone do not admit a source packet or convergence.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "registry_entrypoints": len(registry.get("entrypoints", []))},
        "reproduction": "python -X utf8 verification/scripts/pah_omc026_cut_set_packet_crosswalk_verify.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-026 integrated replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-026 INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
