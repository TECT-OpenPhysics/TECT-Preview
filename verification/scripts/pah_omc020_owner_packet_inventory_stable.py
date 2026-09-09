#!/usr/bin/env python3
"""Deterministic provenance audit for the PAH-OMC-020 owner packet.

The earlier owner-history artefact embedded the complete output of ``git
fsck``.  That output changes when a proof lane accumulates dangling objects,
so its replay hash was not stable.  This audit deliberately records only
source hashes and a sorted reachable-history path inventory.  It is a
provenance check, not a mathematical nonexistence theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
R525 = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-inventory-stable/result.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json":
        "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json":
        "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json":
        "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
}

SEARCH_ROOTS = (
    ROOT / "strategy/pa-hyp",
    ROOT / "verification/scripts",
    ROOT / "verification/lean",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def iter_text_files() -> Iterable[Path]:
    for base in SEARCH_ROOTS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() not in {".pdf", ".pyc"}:
                yield path


def reachable_paths() -> list[str]:
    process = subprocess.run(
        ["git", "rev-list", "--all", "--objects"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stdout + process.stderr)
    prefixes = ("strategy/pa-hyp/", "verification/scripts/", "verification/lean/")
    paths = set()
    for line in process.stdout.splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) == 2 and fields[1].replace("\\", "/").startswith(prefixes):
            paths.add(fields[1].replace("\\", "/"))
    return sorted(paths)


def owner_packet_markers() -> dict[str, list[str]]:
    """Return deterministic current-file markers, without declaring absence."""
    token_paths: list[str] = []
    authorized_paths: list[str] = []
    complete_paths: list[str] = []
    for path in iter_text_files():
        relative = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lowered = text.lower()
        if "pah-omc-020" in lowered or "source-authorized" in lowered:
            token_paths.append(relative)
        if path.suffix.lower() != ".json":
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        provenance = obj.get("provenance")
        if isinstance(provenance, dict) and provenance.get("source_authorized_packet_present") is True:
            authorized_paths.append(relative)
        status = obj.get("status")
        if isinstance(status, str) and status in {"SOURCE_AUTHORIZED_COMPLETE", "OWNER_AUTHORIZED_COMPLETE"}:
            complete_paths.append(relative)
    return {
        "token_paths": sorted(set(token_paths)),
        "authorized_paths": sorted(set(authorized_paths)),
        "complete_paths": sorted(set(complete_paths)),
    }


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": actual,
            "expected": expected,
        })
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    current = {relative: sha256(ROOT / relative) for relative in PINS}
    check("frozen PAH source hashes", current, PINS, current == PINS)

    pah = load_json(PAH)
    prereg = load_json(PREREG)
    intake = load_json(INTAKE)
    candidate = load_json(CANDIDATE)
    r525 = load_json(R525)

    check("PAH identity", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    check("temporal contract identity", prereg.get("contract_id"), "PAH-OMC-020", prereg.get("contract_id") == "PAH-OMC-020")
    intake_provenance = intake.get("provenance", {})
    check(
        "intake is not an owner packet",
        intake_provenance.get("source_authorized_packet_present"),
        False,
        intake_provenance.get("source_authorized_packet_present") is False,
    )
    check(
        "intake remains contract-only",
        intake.get("status"),
        "INTAKE_CONTRACT_ONLY",
        intake.get("status") == "INTAKE_CONTRACT_ONLY",
    )
    candidate_provenance = candidate.get("provenance", {})
    check(
        "R-525 candidate remains researcher-owned",
        candidate.get("status"),
        "RESEARCHER_OWNED_CANDIDATE_ONLY",
        candidate.get("status") == "RESEARCHER_OWNED_CANDIDATE_ONLY",
    )
    check(
        "R-525 authorization is absent",
        candidate_provenance.get("source_authorized_packet_present"),
        False,
        candidate_provenance.get("source_authorized_packet_present") is False,
    )
    check(
        "R-525 is non-bearing",
        [r525.get("claim_bearing"), r525.get("active_gate_change"), r525.get("physical_promotion")],
        [False, False, False],
        r525.get("claim_bearing") is False
        and r525.get("active_gate_change") is False
        and r525.get("physical_promotion") is False,
    )

    markers = owner_packet_markers()
    check("no current authorized packet marker", markers["authorized_paths"], [], not markers["authorized_paths"])
    check("no current complete owner status", markers["complete_paths"], [], not markers["complete_paths"])

    history = reachable_paths()
    check("reachable history inventory is sorted", history, sorted(history), history == sorted(history))
    check("inventory excludes dynamic fsck output", "fsck" not in json.dumps(history).lower(), True, "fsck" not in json.dumps(history).lower())

    required = intake.get("required_owner_payload", [])
    check("nine owner payload fields remain declared", len(required), 9, len(required) == 9)
    check(
        "candidate has unresolved owner fields",
        len(r525.get("missing_assumptions", [])),
        6,
        len(r525.get("missing_assumptions", [])) == 6,
    )

    return {
        "schema": "tect/pah-omc020-owner-inventory-stable/1.0",
        "audit_id": "PAH-OMC-020-OWNER-INVENTORY-STABLE-001",
        "result_id": "R-526",
        "task_id": "T-063",
        "status": "PASS_STABLE_OWNER_INVENTORY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "source_hashes": current,
        "reachable_history_path_count": len(history),
        "reachable_history_sha256": hashlib.sha256(
            ("\n".join(history) + "\n").encode("utf-8")
        ).hexdigest(),
        "current_inventory": markers,
        "finding": (
            "The deterministic bounded inventory finds no source-authorized "
            "PAH-OMC-020 owner packet. R-525 remains a researcher-owned "
            "non-coordinate local coupling candidate; the earlier replay "
            "failure is isolated to dynamic fsck output and is not used here."
        ),
        "scope_boundary": (
            "Current and reachable repository inventory only; absence is not a "
            "universal impossibility theorem and does not inspect external or "
            "future owner input."
        ),
        "next_single_question": (
            "Can a source owner authorize the exact R-525 maximal-prefix U_n "
            "and provide PAH-specific energy intertwining for N2b, N2c/N4 and "
            "N2d without changing PAH-001?"
        ),
        "reproduction": {
            "command": "python -X utf8 verification/scripts/pah_omc020_owner_packet_inventory_stable.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-inventory-stable/result.json",
            "check": "python -X utf8 verification/scripts/pah_omc020_owner_packet_inventory_stable.py --check",
        },
        "non_claims": [
            "No PAH-OMC-020 N2a/N2b/N2c/N4/N2d or semigroup convergence theorem.",
            "No universal comparison-map no-go; this is a bounded provenance inventory.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("stable owner inventory replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=args.output.name + ".", suffix=".tmp", dir=args.output.parent
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            temporary.write_bytes(encoded)
            temporary.replace(args.output)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(f"PAH-OMC-020 STABLE OWNER INVENTORY: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
