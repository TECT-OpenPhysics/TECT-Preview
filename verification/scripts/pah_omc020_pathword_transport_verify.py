#!/usr/bin/env python3
"""Integrate the PAH-OMC-020 path-word primary, independent and hostile lanes."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_pathword_transport.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_pathword_transport_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_pathword_transport_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Pathword.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-pathword/integrated.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def execute(script: Path, output: Path) -> dict:
    py = os.environ.get("TECT_PYTHON") or shutil.which("python") or "python"
    process = subprocess.run(
        [py, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=240, check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def lean_executable() -> Path:
    candidates = list((Path.home() / ".elan" / "toolchains").glob("**/bin/lean.exe"))
    candidates += list((Path.home() / ".elan" / "toolchains").glob("**/bin/lean"))
    exact = [path for path in candidates if "v4.32.1" in str(path)]
    if exact:
        return exact[0]
    found = shutil.which("lean")
    if found:
        return Path(found)
    raise FileNotFoundError("Lean 4.32.1 executable not found")


def lean_compile(cache: Path) -> tuple[str, list[str]]:
    lean = lean_executable()
    package_root = cache
    if not package_root.is_dir():
        raise FileNotFoundError(f"Lean package cache not found: {package_root}")
    libraries = []
    for package in sorted(package_root.iterdir()):
        library = package / ".lake" / "build" / "lib" / "lean"
        if library.is_dir():
            libraries.append(str(library))
    env = dict(os.environ)
    env["LEAN_PATH"] = os.pathsep.join(libraries)
    process = subprocess.run(
        [str(lean), str(LEAN_SOURCE)], cwd=ROOT, env=env, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=600, check=False,
    )
    if process.returncode != 0 or process.stdout or process.stderr:
        raise RuntimeError(f"Lean diagnostics:\n{process.stdout}\n{process.stderr}")
    version = subprocess.run([str(lean), "--version"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=True).stdout.strip()
    return version, libraries


def run(output: Path, cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-pathword-integrated-") as directory:
        folder = Path(directory)
        primary = execute(PRIMARY, folder / "primary.json")
        independent = execute(INDEPENDENT, folder / "independent.json")
        hostile = execute(HOSTILE, folder / "hostile.json")
        lane_payloads = {"primary": primary, "independent": independent, "hostile": hostile}
        run_hashes = {name: digest(folder / f"{name}.json") for name in lane_payloads}
    checks = []

    def ck(name: str, ok: bool, actual: object, expected: object) -> None:
        if not ok:
            raise AssertionError(name)
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    ck("primary lane", primary["status"] == "PASS_PATHWORD_TRANSPORT", primary["status"], "PASS_PATHWORD_TRANSPORT")
    ck("independent lane", independent["status"] == "PASS_INDEPENDENT_PATHWORD", independent["status"], "PASS_INDEPENDENT_PATHWORD")
    ck("hostile lane", hostile["status"] == "PASS_HOSTILE_PATHWORD", hostile["status"], "PASS_HOSTILE_PATHWORD")
    ck("all lanes auxiliary", all(item["verdict"] == "AUXILIARY_SUPPORT" for item in lane_payloads.values()),
       [item["verdict"] for item in lane_payloads.values()], "AUXILIARY_SUPPORT")
    ck("all lanes claim-nonbearing", all(not item["claim_bearing"] for item in lane_payloads.values()),
       [item["claim_bearing"] for item in lane_payloads.values()], [False, False, False])
    ck("physical firewall", all(not item.get("physical_promotion", False) for item in lane_payloads.values()),
       [item.get("physical_promotion", False) for item in lane_payloads.values()], [False, False, False])
    ck("source-status leaves N2c open", primary["source_status"]["n2c_n4"] == "NOT_DISCHARGED",
       primary["source_status"]["n2c_n4"], "NOT_DISCHARGED")
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(independent_tree) if isinstance(node, ast.Import)
                for alias in node.names]
    ck("independent does not import primary", not any("pah_omc020_pathword_transport" in item for item in imports),
       imports, "no primary import")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next(item for item in registry["entrypoints"] if item["path"] ==
                 "verification/lean/Tect/PahOmc020Pathword.lean")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    declarations = [node.name for node in ast.parse("\n".join([])).body]  # no Python theorem parser shortcut
    del declarations
    import re
    lean_names = re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)", source)
    ck("Lean registry hash", entry["sha256"] == digest(LEAN_SOURCE), entry["sha256"], digest(LEAN_SOURCE))
    ck("Lean declarations registry", lean_names == entry["declarations"], lean_names, entry["declarations"])
    ck("Lean policy tokens", not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")),
       "clean", "clean")
    version, libraries = lean_compile(cache)
    ck("Lean fresh compile", True, version, "Lean 4.32.1")

    payload = {
        "schema": "tect/pah-omc020-pathword-integrated/1.0",
        "status": "PASS_PATHWORD_INTEGRATED",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "scripts": {
            "primary": {"path": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(PRIMARY)},
            "independent": {"path": str(INDEPENDENT.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(INDEPENDENT)},
            "hostile": {"path": str(HOSTILE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(HOSTILE)},
            "lean": {"path": str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/"),
                     "sha256": digest(LEAN_SOURCE), "version": version},
        },
        "run_hashes": run_hashes,
        "lane_counts": {name: len(item["checks"]) for name, item in lane_payloads.items()},
        "lean": {"libraries": len(libraries), "declarations": lean_names},
        "scope": "Exact non-radial PAH path-word transport and conditional connected-word factorial envelope; N2c/N4 attribution is not proved.",
        "next_single_question": "Can source OMC-004 incidence certify an n-uniform overlap constant and a coupling/Duhamel lemma from connected words to the actual boundary term?",
        "non_claims": [
            "No anchored-n semigroup convergence, N2a/N2b/N2c/N4, N2d or R-512 selection.",
            "No infinite-volume process, continuum or physical Pre-A/spacetime/QFT/gravity/Yang-Mills/mass-gap/TOE result.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_pathword_transport.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-pathword/primary.json",
            "independent": "python -X utf8 codes/foundations/pah_omc020_pathword_transport_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-pathword/independent.json",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_pathword_transport_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-pathword/hostile.json",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_pathword_transport_verify.py --check",
        },
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--lean-cache", type=Path,
                        default=ROOT / "verification/lean/.lake/packages")
    args = parser.parse_args()
    if args.check and not args.output.exists():
        raise SystemExit("integrated output missing for --check")
    with tempfile.TemporaryDirectory(prefix="pah020-pathword-replay-") as directory:
        replay = run(Path(directory) / "integrated.json", args.lean_cache)
    encoded = (json.dumps(replay, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 path-word integrated replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print("PAH-OMC-020 PATHWORD INTEGRATED: PASS (N2c/N4 attribution remains open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
