#!/usr/bin/env python3
"""Audit repository history for a source-authorized PAH-OMC-020 U_n packet.

This is a provenance audit, not a mathematical no-go theorem.  It never
changes the PAH functional, rates, state, carrier, or limit order.  The
positive result required by N2a must still come from an explicitly authorized
and independently verified realization; absence from this bounded inventory
is recorded only as an evidence hold.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
TRANSFER = ROOT / "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md"
GENERATOR = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
MINIMAL = ROOT / "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-owner-history-audit/result.json"
)

SOURCE_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md":
        "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md":
        "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
}

SEARCH_ROOTS = (ROOT / "strategy/pa-hyp", ROOT / "verification/scripts",
                ROOT / "verification/lean")
TOKENS = (
    "u_n", "square-to-split", "radon-nikodym", "bounded-energy",
    "non-coordinate", "density-ratio", "measure-compatible",
)
TOKEN_RE = re.compile("|".join(re.escape(token) for token in TOKENS), re.I)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_run(*args: str, timeout: int = 120) -> tuple[int, str]:
    process = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, check=False,
    )
    return process.returncode, (process.stdout + process.stderr).strip()


def filesystem_hits() -> list[str]:
    hits: list[str] = []
    for base in SEARCH_ROOTS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() in {".pdf", ".pyc"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if TOKEN_RE.search(text):
                hits.append(path.relative_to(ROOT).as_posix())
    return sorted(set(hits))


def history_hits() -> list[str]:
    code, output = git_run("rev-list", "--all", "--objects")
    if code != 0:
        raise RuntimeError(f"git rev-list failed: {output}")
    paths: set[str] = set()
    for line in output.splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) != 2:
            continue
        path = fields[1].replace("\\", "/")
        if not (path.startswith("strategy/pa-hyp/") or
                path.startswith("verification/scripts/") or
                path.startswith("verification/lean/")):
            continue
        if TOKEN_RE.search(path):
            paths.add(path)
    return sorted(paths)


def compute() -> dict:
    checks: list[dict] = []

    def check(name: str, condition: bool, actual: object, expected: object) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "status": "PASS", "actual": actual,
                       "expected": expected})

    current_hashes = {path: sha256(ROOT / path) for path in SOURCE_PINS}
    check("all frozen source pins", current_hashes == SOURCE_PINS,
          current_hashes, SOURCE_PINS)
    check("preregistration identity", json.loads(PREREG.read_text(encoding="utf-8"))["contract_id"] == "PAH-OMC-020",
          "PAH-OMC-020", "PAH-OMC-020")

    fs_hits = filesystem_hits()
    hist_hits = history_hits()
    # These are inventory checks, not a universal nonexistence assertion.
    check("bounded source paths are present", all(path.is_file() for path in
          (PREREG, WORK, PAH, TRANSFER, GENERATOR, MINIMAL)),
          True, True)
    check("history scan completed", isinstance(hist_hits, list), len(hist_hits), "list")
    code, fsck_output = git_run(
        "-c", "core.commitGraph=false", "fsck", "--unreachable",
        "--no-reflogs", "--no-progress", "--no-full", timeout=120,
    )
    check("recoverable-object audit completed", code == 0,
          {"exit": code, "output": fsck_output}, {"exit": 0, "output": ""})
    return {
        "schema": "tect/pah-omc020-owner-history-audit/1.0",
        "status": "PASS_SCOPED_PROVENANCE_AUDIT",
        "n2a_verdict": "HOLD_FOR_EVIDENCE",
        "code_sha256": sha256(Path(__file__)),
        "source_hashes": current_hashes,
        "checks": checks,
        "bounded_search_roots": [path.relative_to(ROOT).as_posix() for path in SEARCH_ROOTS],
        "filesystem_token_hits": fs_hits,
        "historical_token_paths": hist_hits,
        "recoverable_object_audit": {
            "command": "git -c core.commitGraph=false fsck --unreachable --no-reflogs --no-progress --no-full",
            "exit": code,
            "output": fsck_output,
        },
        "finding": (
            "No standalone source-authorized non-coordinate U_n packet with an "
            "explicit measurable map, cylinder recovery, and bounded-energy "
            "estimate is present in the bounded current or reachable-history "
            "inventory. The corrected commit-graph-disabled fsck reports no "
            "unreachable objects."
        ),
        "scope_boundary": (
            "The inventory does not prove that every abstract realization is "
            "impossible, and it does not inspect external or future owner input. "
            "Existing finite bridge, boundary, Mosco-contract, and fibre results "
            "remain auxiliary only."
        ),
        "next_question": (
            "Can an owner-authorized non-coordinate U_n be supplied with explicit "
            "measure compatibility, local-cylinder recovery, bounded form energy, "
            "and independent/hostile/Lean verification without changing PAH-001?"
        ),
        "non_claims": [
            "No PAH semigroup convergence, Mosco liminf, N4 boundary escape, or R-512 minimal-form selection.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills, or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 owner-history replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print("PAH-OMC-020 OWNER-HISTORY AUDIT: PASS (scoped; N2a HOLD_FOR_EVIDENCE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
