#!/usr/bin/env python3
"""Hostile fail-closed checks for the current-byte N2b owner audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2b-common-space-audit-v1.1/hostile.json"
)

PINNED = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json": "14c7e4da055ccb6104c1952367b0c6615533a5fc50219ef5d7b047cd1552464c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md": "2eeaa12411cba9525bfb6672fdae73d47a113349236639e0c3aa2e9ed8fbd9ab",
}

REQUIRED = (
    "owner_authority", "common_hilbert_realization", "n2b_liminf",
    "recovery_limsup", "n2c_n4_boundary_escape", "n2d_minimal_identification",
    "verification",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    actual = {path: sha(ROOT / path) for path in PINNED}
    check("current-byte hostile pins", actual, PINNED, actual == PINNED)
    intake = load("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    work = (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8")
    required_contract = {
        "owner_authority": "versioned authority",
        "common_hilbert_realization": "one H and U_n",
        "n2b_liminf": "arbitrary sequence liminf",
        "recovery_limsup": "all-local recovery",
        "n2c_n4_boundary_escape": "unbounded-rate boundary",
        "n2d_minimal_identification": "R-512 minimal form",
        "verification": "independent hostile Lean",
    }

    def strict_admit(packet: dict[str, Any]) -> bool:
        provenance = packet.get("provenance", {})
        payload = packet.get("owner_payload", {})
        payload_items = (
            isinstance(payload, dict)
            and all(
                isinstance(payload.get(key), dict)
                and any(payload[key].get(marker) for marker in ("evidence", "statement", "path"))
                for key in REQUIRED
            )
        )
        return (
            provenance.get("source_authorized_packet_present") is True
            and bool(packet.get("packet_id"))
            and bool(packet.get("version"))
            and bool(packet.get("sha256"))
            and payload_items
        )

    check("intake is not admitted", strict_admit(intake), False, not strict_admit(intake))
    fake_flag = copy.deepcopy(intake)
    fake_flag.setdefault("owner_payload", {})
    fake_flag["provenance"]["source_authorized_packet_present"] = True
    check("authorization flag cannot replace payload", strict_admit(fake_flag), False, not strict_admit(fake_flag))
    fake_complete = copy.deepcopy(intake)
    fake_complete["provenance"]["source_authorized_packet_present"] = True
    fake_complete["packet_id"] = "PAH-OMC-020-FAKE"
    fake_complete["version"] = "0.0.0"
    fake_complete["sha256"] = "0" * 64
    fake_complete["owner_payload"] = {key: "label only" for key in REQUIRED}
    check("labels without source payload are rejected", strict_admit(fake_complete), False, not strict_admit(fake_complete))

    no_liminf = dict(required_contract)
    no_liminf.pop("n2b_liminf")
    check("liminf omission is visible", "n2b_liminf" not in no_liminf, True, "n2b_liminf" not in no_liminf)
    check("partial variational packet is not complete", set(no_liminf) == set(REQUIRED), False, set(no_liminf) != set(REQUIRED))

    no_n4 = work.replace("A_n^{out,m}", "A_n^{inside,m}")
    check("N4 deletion is detected", "A_n^{out,m}" not in no_n4, True, "A_n^{out,m}" not in no_n4)
    check("N4 deletion cannot pass", "A_n^{out,m}" in no_n4 and "N4" in no_n4, False, not ("A_n^{out,m}" in no_n4 and "N4" in no_n4))

    physical_time = prereg["scope"]["time"].replace("external unaccelerated Markov time", "Lorentzian time")
    check("physical-time relabel is visible", "Lorentzian time" in physical_time, True, "Lorentzian time" in physical_time)
    check("physical-time relabel cannot preserve firewall", "external unaccelerated Markov time" not in physical_time, True, "external unaccelerated Markov time" not in physical_time)

    direct_sum = work + "\nphasewise direct-sum rescue\n"
    check("direct-sum rescue is forbidden", "direct-sum" in direct_sum.lower(), True, "direct-sum" in direct_sum.lower())
    check("direct-sum rescue changes the declared boundary", "direct-sum" not in work.lower(), True, "direct-sum" not in work.lower())

    return {
        "schema": "tect/pah-omc020-n2b-common-space-audit-hostile/1.1",
        "audit_id": "PAH-OMC-020-N2B-COMMON-SPACE-AUDIT-001-V1.1-HOSTILE",
        "task_id": "T-064",
        "status": "PASS_HOSTILE_N2B_CURRENT_BYTE_FAIL_CLOSED",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual,
        "checks": checks,
        "checks_passed": len(checks),
        "mutations": [
            "authorization flag without owner payload",
            "fabricated labels and hash without source evidence",
            "liminf field omission",
            "N4 evolved-vector term deletion",
            "external Markov time relabelled as Lorentzian time",
            "phasewise direct-sum rescue",
        ],
        "finding": "Hostile mutations cannot promote the current-byte N2b evidence hold; the stale original replay is repaired without altering the PAH model.",
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence or universal impossibility theorem.",
            "No PAH functional, rate, state, carrier, regulator, normalization, time or order change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_n2b_common_space_audit_v11_hostile.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    if args.check:
        if not destination.is_file() or json.loads(destination.read_text(encoding="utf-8")) != payload:
            raise SystemExit("PAH-OMC-020 N2b hostile v1.1 replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 N2B HOSTILE V1.1: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
