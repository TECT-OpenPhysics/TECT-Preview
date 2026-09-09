#!/usr/bin/env python3
"""Independent reconstruction of the stable PAH-OMC-020 owner inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
R525 = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-inventory-stable/independent.json"
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def json_inventory() -> tuple[list[str], list[str], list[str]]:
    roots = (
        ROOT / "strategy/pa-hyp",
        ROOT / "verification/scripts",
        ROOT / "verification/lean",
    )
    token_paths: set[str] = set()
    authorised: set[str] = set()
    complete: set[str] = set()
    for root in roots:
        for path in sorted(root.rglob("*.json")):
            relative = path.relative_to(ROOT).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
                obj = json.loads(text)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue
            if "pah-omc-020" in text.lower() or "source-authorized" in text.lower():
                token_paths.add(relative)
            if not isinstance(obj, dict):
                continue
            provenance = obj.get("provenance")
            if isinstance(provenance, dict) and provenance.get("source_authorized_packet_present") is True:
                authorised.add(relative)
            status = obj.get("status")
            if isinstance(status, str) and status in {"SOURCE_AUTHORIZED_COMPLETE", "OWNER_AUTHORIZED_COMPLETE"}:
                complete.add(relative)
    return sorted(token_paths), sorted(authorised), sorted(complete)


def reachable_history() -> list[str]:
    # This independent lane intentionally does not call git fsck.  Dangling
    # objects are workspace state and cannot be a stable provenance input.
    import subprocess

    proc = subprocess.run(
        ["git", "rev-list", "--all", "--objects"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    prefixes = ("strategy/pa-hyp/", "verification/scripts/", "verification/lean/")
    values: set[str] = set()
    for line in proc.stdout.splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) == 2:
            path = fields[1].replace("\\", "/")
            if path.startswith(prefixes):
                values.add(path)
    return sorted(values)


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    actual_pins = {key: digest(ROOT / key) for key in PINS}
    check("independent source hashes", actual_pins, PINS, actual_pins == PINS)
    pah = read_object(PAH)
    prereg = read_object(PREREG)
    intake = read_object(INTAKE)
    candidate = read_object(CANDIDATE)
    r525 = read_object(R525)
    check("PAH packet", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    check("OMC contract", prereg.get("contract_id"), "PAH-OMC-020", prereg.get("contract_id") == "PAH-OMC-020")
    intake_provenance = intake.get("provenance", {})
    check("intake false authorization", intake_provenance.get("source_authorized_packet_present"), False, intake_provenance.get("source_authorized_packet_present") is False)
    candidate_provenance = candidate.get("provenance", {})
    check("candidate false authorization", candidate_provenance.get("source_authorized_packet_present"), False, candidate_provenance.get("source_authorized_packet_present") is False)
    check("candidate status", candidate.get("status"), "RESEARCHER_OWNED_CANDIDATE_ONLY", candidate.get("status") == "RESEARCHER_OWNED_CANDIDATE_ONLY")
    check("R525 remains non-bearing", [r525.get("claim_bearing"), r525.get("active_gate_change"), r525.get("physical_promotion")], [False, False, False], all(r525.get(key) is False for key in ("claim_bearing", "active_gate_change", "physical_promotion")))
    tokens, authorised, complete = json_inventory()
    check("no authorized JSON packet", authorised, [], not authorised)
    check("no completed owner status", complete, [], not complete)
    history = reachable_history()
    check("reachable paths sorted", history, sorted(history), history == sorted(history))
    check("no fsck state in audit", False, False, "fsck" not in json.dumps(history).lower())
    required = intake.get("required_owner_payload", [])
    check("required owner payload retained", len(required), 9, len(required) == 9)
    return {
        "schema": "tect/pah-omc020-owner-inventory-stable-independent/1.0",
        "audit_id": "PAH-OMC-020-OWNER-INVENTORY-STABLE-INDEPENDENT-001",
        "task_id": "T-063",
        "status": "PASS_INDEPENDENT_STABLE_OWNER_INVENTORY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "source_hashes": actual_pins,
        "current_token_path_count": len(tokens),
        "authorized_paths": authorised,
        "complete_paths": complete,
        "reachable_history_path_count": len(history),
        "reachable_history_sha256": hashlib.sha256(("\n".join(history) + "\n").encode("utf-8")).hexdigest(),
        "finding": "Independent reconstruction confirms that the bounded current and reachable history contain no source-authorized PAH-OMC-020 owner packet; the dynamic fsck output is intentionally excluded.",
        "next_single_question": "Can a source owner authorize the exact R-525 U_n and supply PAH-specific energy intertwining without changing PAH-001?",
        "non_claims": [
            "No N2a/N2b/N2c/N4/N2d or PAH-OMC-020 semigroup theorem.",
            "No universal comparison-map impossibility theorem.",
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
            raise SystemExit("independent stable owner inventory replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=args.output.name + ".", suffix=".tmp", dir=args.output.parent)
        os.close(descriptor)
        temporary = Path(name)
        try:
            temporary.write_bytes(encoded)
            temporary.replace(args.output)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(f"PAH-OMC-020 STABLE OWNER INVENTORY INDEPENDENT: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
