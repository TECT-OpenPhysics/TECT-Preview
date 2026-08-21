"""Run the pinned Lean kernel cross-check for the exact R-166 rational core."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "verification" / "lean"
ENTRYPOINT = LEAN_DIR / "Tect" / "R166.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LOCKFILE = LEAN_DIR / "lake-manifest.json"
CLAIM_DIR = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
R166_MANIFEST = CLAIM_DIR / "classii_sparse_production_owner_radial_gram_global_boundary_manifest.json"
A13_STATUS = CLAIM_DIR / "status.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-08-21-lean-r166-radial-gram-crosscheck" / "result.json"
REGISTERED_R166_MANIFEST_SHA256 = "0d47462595f35bd89d0e893fc517031fa9a471240f030be097b06f48b99b8377"
REGISTERED_A13_STATUS_SHA256 = "356ea6ec060cecc06df38712b2715ea32ec52dd8493ef4177bb840170a48c8dd"
THEOREM_MARKERS = (
    "global_lower_decomposition",
    "stronger_minus_four_fifths_margin",
    "derivative_root_bracket",
    "curvature_bracket",
    "two_harmonic_counterdirection",
    "rho_choice_and_downstream_constants",
    "rho_margin_target",
)
FORBIDDEN_SOURCE_TOKENS = ("sorry", "admit", "axiom", "unsafe")


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def find_lake() -> str | None:
    home = Path.home()
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    toolchain_bin = home / ".elan" / "toolchains" / encoded / "bin"
    local_name = "lake.exe" if os.name == "nt" else "lake"
    local_lake = toolchain_bin / local_name
    if local_lake.is_file():
        return str(local_lake)
    found = shutil.which("lake")
    if found:
        return found
    for candidate in (
        home / ".elan" / "bin" / "lake.exe",
        home / ".elan" / "bin" / "lake",
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def check(condition: bool, name: str, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def rational(value: str) -> Fraction:
    return Fraction(value)


def marker(value: Fraction) -> str:
    return f"{value.numerator} / {value.denominator}"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    source_text = ENTRYPOINT.read_text(encoding="utf-8")
    manifest = json.loads(R166_MANIFEST.read_text(encoding="utf-8"))
    primary_path = REPO / manifest["files"]["primary_result"]["path"]
    independent_path = REPO / manifest["files"]["independent_result"]["path"]
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    independent = json.loads(independent_path.read_text(encoding="utf-8"))
    lake = find_lake()

    check(ENTRYPOINT.is_file(), "Lean entrypoint exists", str(ENTRYPOINT), True, rows)
    check(TOOLCHAIN.is_file(), "Lean toolchain pin exists", str(TOOLCHAIN), True, rows)
    check(LAKEFILE.is_file(), "Lakefile exists", str(LAKEFILE), True, rows)
    check(LOCKFILE.is_file(), "Lake dependency lock exists", str(LOCKFILE), True, rows)
    check(lake is not None, "lake executable is available", lake, "PATH or pinned local toolchain", rows)
    manifest_sha = sha256(R166_MANIFEST)
    status_sha = sha256(A13_STATUS)
    check(manifest_sha == REGISTERED_R166_MANIFEST_SHA256, "R-166 manifest hash", manifest_sha, REGISTERED_R166_MANIFEST_SHA256, rows)
    check(status_sha == REGISTERED_A13_STATUS_SHA256, "A13 status hash", status_sha, REGISTERED_A13_STATUS_SHA256, rows)
    check(manifest.get("result_id") == "A13-CLASSII-SPARSE-PRODUCTION-OWNER-RADIAL-GRAM-GLOBAL-BOUNDARY", "R-166 identity", manifest.get("result_id"), "A13-CLASSII-SPARSE-PRODUCTION-OWNER-RADIAL-GRAM-GLOBAL-BOUNDARY", rows)
    check(manifest.get("result_ledger_id") == "R-166", "R-166 ledger identity", manifest.get("result_ledger_id"), "R-166", rows)
    check(manifest.get("tier") == "T4", "R-166 tier", manifest.get("tier"), "T4", rows)

    for key, reference in manifest["authorities"].items():
        path = REPO / reference
        expected = manifest["authority_hashes"][key]
        actual = sha256(path) if path.is_file() else None
        check(path.is_file() and actual == expected, f"authority hash {key}", actual, expected, rows)
    for key, reference in manifest["files"].items():
        path = REPO / reference["path"]
        expected = reference["sha256"]
        actual = sha256(path) if path.is_file() else None
        check(path.is_file() and actual == expected, f"file hash {key}", actual, expected, rows)

    check(all(marker_name in source_text for marker_name in THEOREM_MARKERS), "Lean theorem markers present", [m for m in THEOREM_MARKERS if m in source_text], list(THEOREM_MARKERS), rows)
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if re.search(rf"\b{token}\b", source_text)]
    check(forbidden_hits == [], "Lean escape tokens absent", forbidden_hits, [], rows)
    check(primary.get("status") == "PASS" and independent.get("status") == "PASS", "registered R-166 engines PASS", [primary.get("status"), independent.get("status")], ["PASS", "PASS"], rows)

    pdiag = primary["diagnostics"]
    idiag = independent["diagnostics"]
    shared_keys = (
        "global_lower_bound",
        "owner_margin_above_minus_4_5",
        "derivative_at_70",
        "derivative_at_71",
        "second_at_40",
        "second_at_41",
        "second_at_70",
        "rho",
        "rho_margin",
        "full_semiconvexity",
        "epsilon_v",
    )
    for key in shared_keys:
        check(pdiag[key] == idiag[key], f"primary/independent diagnostic {key}", pdiag[key], idiag[key], rows)

    lower = rational(pdiag["global_lower_bound"])
    strong_margin = rational(pdiag["owner_margin_above_minus_4_5"])
    owner_floor = rational(manifest["no_overclaim"].split("K_owner > ")[1].split("I/5")[0] + "/5")
    rho = rational(pdiag["rho"])
    rho_margin = rational(pdiag["rho_margin"])
    semiconvexity = rational(pdiag["full_semiconvexity"])
    epsilon_v = rational(pdiag["epsilon_v"])
    check(lower == -Fraction(332863942666997, 439505584128000), "global lower certificate", str(lower), "-332863942666997/439505584128000", rows)
    check(lower + Fraction(4, 5) == strong_margin and strong_margin > 0, "strong minus-four-fifths margin", str(strong_margin), ">0 and lower+4/5", rows)
    check(rational(pdiag["derivative_at_70"]) < 0 < rational(pdiag["derivative_at_71"]), "derivative root bracket", [pdiag["derivative_at_70"], pdiag["derivative_at_71"]], "negative,positive", rows)
    check(rational(pdiag["second_at_40"]) < 0 < rational(pdiag["second_at_41"]) and rational(pdiag["second_at_70"]) > 0, "curvature signs", [pdiag["second_at_40"], pdiag["second_at_41"], pdiag["second_at_70"]], "negative,positive,positive", rows)
    check(rho == Fraction(3, 20) and rho_margin > 0, "R-164 rho choice", str(rho), "3/20 with positive margin", rows)
    check(semiconvexity == Fraction(31, 220) and semiconvexity > Fraction(1, 10), "full semiconvexity", str(semiconvexity), "31/220 > 1/10", rows)
    check(epsilon_v == Fraction(367, 880) and epsilon_v > 0, "epsilon_v", str(epsilon_v), "367/880 > 0", rows)
    check(rational(pdiag["multi_harmonic_counterexample"]["ratio"]) == Fraction(3, 8), "two-harmonic ratio", pdiag["multi_harmonic_counterexample"]["ratio"], "3/8", rows)
    for value in (lower, strong_margin, rational(pdiag["derivative_at_70"]), rational(pdiag["derivative_at_71"]), rational(pdiag["second_at_40"]), rational(pdiag["second_at_41"]), rational(pdiag["second_at_70"]), rho, semiconvexity, epsilon_v):
        check(marker(value) in source_text, f"Lean rational marker {marker(value)}", marker(value), True, rows)

    command = [lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))]
    completed = subprocess.run(command, cwd=LEAN_DIR, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    check(completed.returncode == 0, "Lean kernel compile", completed.returncode, 0, rows)
    check(completed.stdout.strip() == "", "Lean stdout is clean", completed.stdout, "", rows)
    check(completed.stderr.strip() == "", "Lean stderr is clean", completed.stderr, "", rows)

    payload: dict[str, Any] = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "lean-kernel-crosscheck",
        "result_id": "R-166-LEAN-KERNEL-CROSSCHECK",
        "claim_ids": ["A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"],
        "formal_refs": {"results": ["R-166"], "negatives": ["NG-2026-08-04-A13-R166-DIRECT-HARMONIC-COERCIVITY-TENSORIZATION"], "events": []},
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "command": command,
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "source_hashes": {
            "toolchain": sha256(TOOLCHAIN),
            "lakefile": sha256(LAKEFILE),
            "lake_manifest": sha256(LOCKFILE),
            "entrypoint": sha256(ENTRYPOINT),
            "r166_manifest": manifest_sha,
            "a13_status": status_sha,
            "primary_result": sha256(primary_path),
            "independent_result": sha256(independent_path),
        },
        "registered_constants": {
            "global_lower_bound": str(lower),
            "strong_margin_above_minus_four_fifths": str(strong_margin),
            "rho": str(rho),
            "rho_margin": str(rho_margin),
            "full_semiconvexity": str(semiconvexity),
            "epsilon_v": str(epsilon_v),
            "two_harmonic_ratio": pdiag["multi_harmonic_counterexample"]["ratio"],
        },
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": sys.version,
        "boundary": (
            "Kernel-checks only exact rational consequences of the registered "
            "R-166 sparse-fibre certificate: the global lower decomposition, "
            "bracket signs, the scoped rho/semiconvexity constants, and the "
            "two-harmonic ratio. It does not prove the Pauli-Fierz analytic "
            "split, complete multi-root owner, progressive/revisit control, "
            "T-050/A13, Nelson/measure, removal, Sector-A, or any limit."
        ),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        payload["artifact"] = str(output.relative_to(REPO)).replace("\\", "/")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"LEAN R-166 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
