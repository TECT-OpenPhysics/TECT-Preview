"""Integrated verifier for the PAH-OMC-020 sequential gluing checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_sequential_gluing.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_sequential_gluing_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_sequential_gluing_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Gluing.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-sequential-gluing/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json":
        "cfb65eb769cc95fb4b5148fe2914c5b4405748c3b8d253a0ca938369914d8801",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json":
        "67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d",
    "strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json":
        "9013fe5337965478c2e91c84fa693eacf3dbd0d948a3b2cafb900332d8b9dd19",
}

LEAN_DECLARATIONS = [
    "three_term_budget",
    "budget_nonnegative",
    "epsilon_partition",
    "target_defect_required",
    "known_term_required",
    "fixed_n_j_order_fixture",
    "reversed_order_fixture",
    "source_oracle_is_not_zero",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_script(script: Path, output: Path) -> dict:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def lean_executable() -> Path:
    candidates = list((Path.home() / ".elan" / "toolchains").glob("**/bin/lean.exe"))
    candidates += list((Path.home() / ".elan" / "toolchains").glob("**/bin/lean"))
    exact = [candidate for candidate in candidates if "v4.32.1" in str(candidate)]
    if exact:
        return exact[0]
    found = shutil.which("lean")
    if found:
        return Path(found)
    raise FileNotFoundError("Lean 4.32.1 executable not found")


def compile_lean(cache: Path) -> tuple[str, str]:
    libraries: list[str] = []
    if cache.exists():
        for package in sorted(cache.iterdir()):
            library = package / ".lake" / "build" / "lib" / "lean"
            if library.is_dir():
                libraries.append(str(library))
    if not libraries:
        raise FileNotFoundError(f"No Lean package libraries found under {cache}")
    environment = dict(os.environ)
    environment["LEAN_PATH"] = os.pathsep.join(libraries)
    process = subprocess.run(
        [str(lean_executable()), str(LEAN_SOURCE)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        check=False,
    )
    diagnostics = (process.stdout + process.stderr).strip()
    if process.returncode != 0 or re.search(r"(?im)\berror:", diagnostics):
        raise RuntimeError(f"Lean diagnostics:\n{diagnostics}")
    version = subprocess.run(
        [str(lean_executable()), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    return version, diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--lean-cache",
        type=Path,
        default=ROOT / "verification/lean/.lake/packages",
    )
    args = parser.parse_args()

    checks: list[dict] = []

    def check(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    with tempfile.TemporaryDirectory(prefix="pah020-gluing-integrated-") as directory:
        folder = Path(directory)
        primary = run_script(PRIMARY, folder / "primary.json")
        independent = run_script(INDEPENDENT, folder / "independent.json")
        hostile = run_script(HOSTILE, folder / "hostile.json")
        lane_payloads = {"primary": primary, "independent": independent, "hostile": hostile}
        lane_hashes = {name: digest(folder / f"{name}.json") for name in lane_payloads}

    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(f"source hash {relative}", actual, expected, actual == expected)

    check("primary conditional status", primary["verdict"], "PASS_CONDITIONAL_GLUING_LEMMA", primary["verdict"] == "PASS_CONDITIONAL_GLUING_LEMMA")
    check("independent status", independent["verdict"], "PASS_CONDITIONAL_GLUING_LEMMA", independent["verdict"] == "PASS_CONDITIONAL_GLUING_LEMMA")
    check("hostile controls", hostile["verdict"], "PASS_HOSTILE_CONTROLS", hostile["verdict"] == "PASS_HOSTILE_CONTROLS")
    check("primary arithmetic count", primary["assertion_count"], 31, primary["assertion_count"] == 31)
    check("independent arithmetic count", independent["assertion_count"], 25, independent["assertion_count"] == 25)
    check("hostile arithmetic count", hostile["assertion_count"], 19, hostile["assertion_count"] == 19)
    check("target gap is explicit", any("target" in item.lower() for item in primary["missing_assumptions"]), True, any("target" in item.lower() for item in primary["missing_assumptions"]))
    check("uniform truncation gap is explicit", any("uniform truncation" in item.lower() for item in primary["missing_assumptions"]), True, any("uniform truncation" in item.lower() for item in primary["missing_assumptions"]))
    check("physical promotion remains false", primary["physical_promotion"], False, primary["physical_promotion"] is False)
    check("hostile mutation set is nonempty", len(hostile["rejected_mutations"]), 4, len(hostile["rejected_mutations"]) == 4)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/PahOmc020Gluing.lean"), None)
    check("Lean registry entry exists", entry is not None, True, entry is not None)
    check("Lean source hash is current", entry["sha256"] if entry else None, digest(LEAN_SOURCE), entry is not None and entry["sha256"] == digest(LEAN_SOURCE))
    registry_declarations = entry["declarations"] if entry else []
    check("Lean declarations are complete", registry_declarations, LEAN_DECLARATIONS, registry_declarations == LEAN_DECLARATIONS)
    lean_version, diagnostics = compile_lean(args.lean_cache)
    source_text = LEAN_SOURCE.read_text(encoding="utf-8")
    # A textual declaration check is intentionally conservative: the Lean
    # compiler above is authoritative, while this confirms every registered
    # theorem name occurs as a theorem declaration in the source.
    declaration_hits = [bool(re.search(rf"\btheorem\s+{re.escape(name)}\b", source_text)) for name in LEAN_DECLARATIONS]
    check("Lean declarations occur in source", declaration_hits, [True] * len(LEAN_DECLARATIONS), all(declaration_hits))
    check("Lean diagnostics contain no error", bool(re.search(r"(?im)\berror:", diagnostics)) if diagnostics else False, False, not re.search(r"(?im)\berror:", diagnostics))

    payload = {
        "schema": "tect/pah-omc020-sequential-gluing-integrated/1.0",
        "audit_id": "PAH-OMC-020-SEQUENTIAL-GLUING",
        "task_id": "T-076",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertions": checks,
        "assertion_count": len(checks),
        "lane_hashes": lane_hashes,
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "lean": {
            "path": str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "sha256": digest(LEAN_SOURCE),
            "version": lean_version,
            "declarations": LEAN_DECLARATIONS,
            "result": "PASS",
        },
        "conclusion": "The sequential compact-time gluing implication is proved at the stated conditional level. The source-owned uniform truncation bound and target-process/R-512 minimal-form defect needed to instantiate it are absent, so the parent PAH-OMC-020 objective remains HOLD_FOR_EVIDENCE.",
        "missing_assumptions": [
            "A source-authorized uniform K_(n,m) truncation bound for every bounded local cylinder and compact external-time horizon.",
            "A source-authorized D_n target-process/R-512 minimal-form defect tending to zero in anchored n.",
            "A common path-space or common-Hilbert realization to instantiate those bounds.",
        ],
        "non_claims": [
            "No PAH-OMC-020 anchored-n semigroup convergence theorem.",
            "No new PAH functional, rate, state, carrier, regulator, stochastic time or limit order.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
        "verification": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_sequential_gluing.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_sequential_gluing_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_sequential_gluing_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_sequential_gluing_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "result": f"Primary {primary['assertion_count']}/{primary['assertion_count']}, independent {independent['assertion_count']}/{independent['assertion_count']}, hostile {hostile['assertion_count']}/{hostile['assertion_count']}, integrated {len(checks)}/{len(checks)}, Lean PASS ({lean_version}).",
        },
        "next_single_question": "Can a source-authorized owner packet instantiate both K_(n,m) and D_n under the unchanged PAH-001 model?",
    }
    atomic_json(args.output, payload)
    print(f"PAH-OMC-020 SEQUENTIAL GLUING INTEGRATED: PASS {len(checks)}/{len(checks)}; scientific verdict HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
