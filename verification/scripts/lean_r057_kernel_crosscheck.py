"""Run the pinned Lean kernel cross-check for the exact R-057 arithmetic core.

The analytic inputs M_6 >= 8 and Q_6^2 >= 192 are owned by the hash-pinned
A12 package.  Lean checks only their ordered-field consequence and the exact
comparison with the registered source-only target; it does not reprove the
Riesz theorem or the analytic sharp-cube estimates.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
LEAN_DIR = REPO / "verification" / "lean"
ENTRYPOINT = LEAN_DIR / "Tect" / "R057.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
LAKEFILE = LEAN_DIR / "lakefile.toml"
LOCKFILE = LEAN_DIR / "lake-manifest.json"
A12_MANIFEST = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_sharp_cube_budget_obstruction_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A12-CLASSII-SOURCE-SQUARE-REDUCTION"
    / "runs"
    / "2026-08-21-lean-r057-kernel-crosscheck"
    / "result.json"
)
REGISTERED_A12_MANIFEST_SHA256 = "e16ad41f192505ca17a7c249705e30ec51771877505a9e833cd900e863580213"
THEOREM_MARKERS = (
    "boundary_product",
    "sharp_boundary_arithmetic",
    "production_target_gap",
)
FORBIDDEN_SOURCE_TOKENS = ("sorry", "admit", "axiom", "unsafe")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    candidates = []
    if os.name == "nt":
        candidates.extend((home / ".elan" / "bin" / "lake.exe", home / ".elan" / "bin" / "lake"))
    else:
        candidates.append(home / ".elan" / "bin" / "lake")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def check(condition: bool, name: str, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def decimal_marker(value: str) -> tuple[Fraction, str]:
    whole, fractional = value.split(".", 1)
    numerator = int(whole + fractional)
    denominator = 10 ** len(fractional)
    return Fraction(numerator, denominator), f"{numerator} / {denominator}"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    source_text = ENTRYPOINT.read_text(encoding="utf-8")
    manifest = json.loads(A12_MANIFEST.read_text(encoding="utf-8"))
    lake = find_lake()

    check(ENTRYPOINT.is_file(), "Lean entrypoint exists", str(ENTRYPOINT), True, rows)
    check(TOOLCHAIN.is_file(), "Lean toolchain pin exists", str(TOOLCHAIN), True, rows)
    check(LAKEFILE.is_file(), "Lakefile exists", str(LAKEFILE), True, rows)
    check(LOCKFILE.is_file(), "Lake dependency lock exists", str(LOCKFILE), True, rows)
    check(lake is not None, "lake executable is available", lake, "PATH or pinned local toolchain", rows)
    check(
        sha256(A12_MANIFEST) == REGISTERED_A12_MANIFEST_SHA256,
        "A12 sharp-budget manifest hash",
        sha256(A12_MANIFEST),
        REGISTERED_A12_MANIFEST_SHA256,
        rows,
    )
    check(
        manifest.get("schema") == "tect/a12-classii-sharp-cube-budget-obstruction-manifest/1.0",
        "R-057 authority schema",
        manifest.get("schema"),
        "tect/a12-classii-sharp-cube-budget-obstruction-manifest/1.0",
        rows,
    )
    target_decimal = str(manifest["budget"]["target_derived"])
    target_fraction, target_marker = decimal_marker(target_decimal)
    sharp_lower = int(manifest["budget"]["sharp_lower"])
    for key in ("a1_manifest", "a12_manifest", "a12_note"):
        reference = manifest["authority"][key]
        path = REPO / reference["path"]
        check(path.is_file() and sha256(path) == reference["sha256"], f"authority hash {key}", sha256(path) if path.is_file() else None, reference["sha256"], rows)
    check(
        all(marker in source_text for marker in THEOREM_MARKERS),
        "Lean theorem markers present",
        [marker for marker in THEOREM_MARKERS if marker in source_text],
        list(THEOREM_MARKERS),
        rows,
    )
    check(str(sharp_lower) in source_text, "sharp lower bridge marker", str(sharp_lower), True, rows)
    check(target_marker in source_text, "production target rational bridge marker", target_marker, True, rows)
    check(target_fraction < sharp_lower, "registered target below sharp lower", str(target_fraction), f"<{sharp_lower}", rows)
    forbidden_hits = [token for token in FORBIDDEN_SOURCE_TOKENS if re.search(rf"\b{token}\b", source_text)]
    check(forbidden_hits == [], "Lean escape tokens absent", forbidden_hits, [], rows)

    command = [lake, "env", "lean", str(ENTRYPOINT.relative_to(LEAN_DIR))]
    completed = subprocess.run(command, cwd=LEAN_DIR, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    check(completed.returncode == 0, "Lean kernel compile", completed.returncode, 0, rows)
    check(completed.stdout.strip() == "", "Lean stdout is clean", completed.stdout, "", rows)
    check(completed.stderr.strip() == "", "Lean stderr is clean", completed.stderr, "", rows)

    payload: dict[str, Any] = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "lean-kernel-crosscheck",
        "result_id": "R-057-LEAN-KERNEL-CROSSCHECK",
        "claim_ids": ["A12-CLASSII-SOURCE-SQUARE-REDUCTION"],
        "formal_refs": {"results": ["R-057"], "negatives": ["NG-2026-07-21-A12-SHARP-CUBE-SCALAR-BUDGET"], "events": []},
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
            "a12_manifest": sha256(A12_MANIFEST),
        },
        "sharp_lower": sharp_lower,
        "target_derived": target_decimal,
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": sys.version,
        "boundary": (
            "Kernel-checks only the exact ordered-field arithmetic consequence "
            "of the registered R-057 lower-bound inputs. It does not reprove "
            "the Riesz norm, the analytic sharp-cube estimates, the exact-B "
            "source, A11 log-Laplace, A13/T-050, physical-empty, or any limit."
        ),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        payload["artifact"] = str(output.relative_to(REPO)).replace("\\", "/")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"LEAN R-057 PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
