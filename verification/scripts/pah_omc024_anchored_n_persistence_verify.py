#!/usr/bin/env python3
"""Integrated replay for PAH-OMC-024.

The integrated lane reruns the three non-importing Python lanes, compiles the
registered Lean proposition with the pinned Lake executable, and records only
stable metadata.  It is an evidence gate, not a physical or continuum claim.
"""
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
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-024-anchored-n-persistence-contract-v1.json"
RESULT = ROOT / "strategy/pa-hyp/PAH-OMC-024-anchored-n-persistence-result-v1.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
R552 = ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc024Persistence.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
PRIMARY = ROOT / "verification/scripts/pah_omc024_anchored_n_persistence.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc024_anchored_n_persistence_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc024_anchored_n_persistence_hostile.py"


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
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def pinned_lake() -> Path | None:
    registry = load(REGISTRY)
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        path = candidate / name
        if path.is_file():
            return path
    return None


def lean_replay(check_only: bool) -> dict[str, Any]:
    lake = pinned_lake()
    registry = load(REGISTRY)
    toolchain = registry["toolchain"]["toolchain"]
    if lake is None:
        payload = {"schema": "tect/pah-omc024-lean-run/1.0", "status": "UNAVAILABLE", "command": "lake env lean Tect/PahOmc024Persistence.lean", "toolchain": toolchain, "source_hash": sha(LEAN)}
    else:
        worktree_lean = ROOT / "verification/lean"
        # The proof lane may not have a local .lake clone.  Reuse the
        # operator's already-pinned read-only package cache when available;
        # the source being compiled is still the current worktree file.
        canonical_lean = Path("E:/Dev/TECT/verification/lean")
        if (worktree_lean / ".lake/packages/mathlib").is_dir():
            lean_cwd = worktree_lean
            source_arg = "Tect/PahOmc024Persistence.lean"
            dependency_scope = "lane-local-pinned-packages"
        elif canonical_lean.joinpath(".lake/packages/mathlib").is_dir():
            lean_cwd = canonical_lean
            source_arg = str(LEAN)
            dependency_scope = "read-only-canonical-pinned-packages"
        else:
            lean_cwd = worktree_lean
            source_arg = "Tect/PahOmc024Persistence.lean"
            dependency_scope = "lane-local-missing-packages"
        lean_env = os.environ.copy()
        if dependency_scope == "read-only-canonical-pinned-packages":
            # Lake asks git to inspect the canonical package checkout.  The
            # desktop operator owns that read-only checkout, so pass a
            # process-local safe.directory exception instead of changing any
            # global git configuration.
            lean_env.update({
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "safe.directory",
                "GIT_CONFIG_VALUE_0": "*",
            })
        process = subprocess.run([str(lake), "env", "lean", source_arg], cwd=lean_cwd, env=lean_env, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        payload = {"schema": "tect/pah-omc024-lean-run/1.0", "status": "PASS" if process.returncode == 0 and "error:" not in (process.stdout + process.stderr).lower() else "FAIL", "returncode": process.returncode, "command": "lake env lean Tect/PahOmc024Persistence.lean", "toolchain": toolchain, "source_hash": sha(LEAN), "dependency_scope": dependency_scope}
    destination = RUN_DIR / "lean.json"
    encoded = atomic_json(destination, payload) if not check_only else (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if check_only and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-024 Lean replay mismatch")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    scripts = [("primary", PRIMARY), ("independent", INDEPENDENT), ("hostile", HOSTILE)]
    replay: dict[str, Any] = {}
    for name, script in scripts:
        output = RUN_DIR / f"{name}.json"
        command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
        if args.check:
            command.append("--check")
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        replay[name] = {"returncode": process.returncode, "command": f"python -X utf8 {script.relative_to(ROOT).as_posix()} --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc024-anchored-n-persistence/{name}.json"}
        check(rows, f"{name} replay", process.returncode, 0, process.returncode == 0)

    contract = load(CONTRACT)
    result = load(RESULT)
    runs = {name: load(RUN_DIR / f"{name}.json") for name, _ in scripts}
    lean = lean_replay(args.check)
    lean_run = load(RUN_DIR / "lean.json")
    check(rows, "contract identity", contract.get("contract_id"), "PAH-OMC-024", contract.get("contract_id") == "PAH-OMC-024")
    check(rows, "result identity", result.get("result_id"), "R-564", result.get("result_id") == "R-564")
    check(rows, "result hold verdict", result.get("verdict"), "HOLD_FOR_EVIDENCE", result.get("verdict") == "HOLD_FOR_EVIDENCE")
    check(rows, "result claim firewall", result.get("claim_bearing"), False, result.get("claim_bearing") is False)
    check(rows, "result physical firewall", result.get("physical_promotion"), False, result.get("physical_promotion") is False)
    for name, run in runs.items():
        check(rows, f"{name} hold verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        check(rows, f"{name} claim firewall", run.get("claim_bearing"), False, run.get("claim_bearing") is False)
        check(rows, f"{name} physical firewall", run.get("physical_promotion"), False, run.get("physical_promotion") is False)
        check(rows, f"{name} internal checks", all(item.get("status") == "PASS" for item in run.get("checks", [])), True, all(item.get("status") == "PASS" for item in run.get("checks", [])))
    check(rows, "Lean compile", lean_run.get("status"), "PASS", lean_run.get("status") == "PASS")
    check(rows, "Lean registry path", any(item.get("path") == "verification/lean/Tect/PahOmc024Persistence.lean" for item in load(REGISTRY).get("entrypoints", [])), True, any(item.get("path") == "verification/lean/Tect/PahOmc024Persistence.lean" for item in load(REGISTRY).get("entrypoints", [])))
    check(rows, "source bytes unchanged", sha(PAH001), "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37", sha(PAH001) == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37")
    check(rows, "prereg bytes unchanged", sha(PREREG), "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3", sha(PREREG) == "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3")
    expected_r552 = "44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee"
    actual_r552 = sha(R552)
    check(rows, "R-552 bytes unchanged", actual_r552, expected_r552, actual_r552 == expected_r552)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc024-anchored-n-persistence-integrated/1.0",
        "audit_id": "PAH-OMC-024-ANCHORED-N-PERSISTENCE-INTEGRATED-001",
        "result_id": "R-564",
        "contract_id": "PAH-OMC-024",
        "task_id": "T-091",
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
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha(path) for path in (PAH001, PREREG, R552, CONTRACT, PRIMARY, INDEPENDENT, HOSTILE, Path(__file__), LEAN, REGISTRY)},
        "child_run_hashes": {name: sha(RUN_DIR / f"{name}.json") for name, _ in scripts},
        "lean_run_hash": sha(RUN_DIR / "lean.json"),
        "finding": "All lanes agree on the scoped logical non-implication. The finite R-552 gap is compatible with geometric collapse, and no source-specific uniform estimate has been supplied.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "registry_entrypoints": len(load(REGISTRY).get("entrypoints", []))},
        "reproduction": "python -X utf8 verification/scripts/pah_omc024_anchored_n_persistence_verify.py --check",
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-024 integrated replay mismatch")
    print(f"PAH-OMC-024 INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
