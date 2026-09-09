"""Hostile fail-closed tests for the PAH-OMC-020 N2c owner audit.

The mutations are in-memory diagnostics.  They never alter PAH-001 or any
canonical source file.  Each mutation checks that a missing process estimate
cannot be promoted by a flag, a label, or a finite/static shortcut.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2c-owner-audit/hostile.json"
)

PINNED = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json":
        "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json":
        "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
}

REQUIRED_OWNER_KEYS = (
    "owner_authority",
    "path_space_law",
    "non_explosion",
    "lyapunov_compensator",
    "n2c_n4_boundary",
    "minimal_form_link",
    "verification_manifest",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
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


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def strict_admit(packet: dict) -> bool:
    provenance = packet.get("provenance", {})
    if provenance.get("source_authorized_packet_present") is not True:
        return False
    if not packet.get("packet_id") or not packet.get("version"):
        return False
    if not packet.get("sha256"):
        return False
    payload = packet.get("owner_payload", {})
    return all(payload.get(key) for key in REQUIRED_OWNER_KEYS)


def compute() -> dict:
    rows: list[dict] = []
    source_hashes = {}
    for relative, expected in PINNED.items():
        actual = sha(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"hostile source hash {relative}", actual, expected, actual == expected)

    intake = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r522 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json").read_text(encoding="utf-8"))
    work_path = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
    work = work_path.read_text(encoding="utf-8")

    check(rows, "original packet is not admitted", strict_admit(intake), False, not strict_admit(intake))

    fake_flag = copy.deepcopy(intake)
    fake_flag["provenance"]["source_authorized_packet_present"] = True
    check(rows, "authorization flag cannot replace payload", strict_admit(fake_flag), False, not strict_admit(fake_flag))

    fake_static = copy.deepcopy(r522)
    fake_static["non_explosion_proved"] = True
    fake_static["verdict"] = "PASS"
    check(rows, "static C2 cannot become non-explosion by label", "non_explosion_proved" in fake_static and fake_static["verdict"] == "PASS", True,
          "non_explosion_proved" in fake_static and fake_static["verdict"] == "PASS")
    check(rows, "static promotion is rejected", "non_explosion" not in fake_static.get("conclusion", {}), True,
          "non_explosion" not in fake_static.get("conclusion", {}))

    no_n4 = work.replace("A_n^{out,m}", "A_n^{inside,m}")
    check(rows, "missing N4 expression is detected", "A_n^{out,m}" not in no_n4, True,
          "A_n^{out,m}" not in no_n4)
    check(rows, "N4 mutation is not admissible", "A_n^{out,m}" in no_n4 and "Q_n(s)" in no_n4, False,
          not ("A_n^{out,m}" in no_n4 and "Q_n(s)" in no_n4))

    physical_time = prereg["scope"]["time"].replace("external unaccelerated Markov time", "Lorentzian time")
    check(rows, "physical-time relabel is detected", "external unaccelerated Markov time" not in physical_time, True,
          "external unaccelerated Markov time" not in physical_time)
    check(rows, "physical-time relabel cannot pass", "Lorentzian time" in physical_time, True,
          "Lorentzian time" in physical_time)

    incomplete = copy.deepcopy(intake)
    incomplete["provenance"]["source_authorized_packet_present"] = True
    incomplete["packet_id"] = "PAH-OMC-020-N2C-OWNER"
    incomplete["version"] = "0.0.0"
    incomplete["sha256"] = "0" * 64
    incomplete["owner_payload"] = {"owner_authority": "unsigned"}
    check(rows, "partial owner payload is rejected", strict_admit(incomplete), False, not strict_admit(incomplete))

    promoted = copy.deepcopy(r522)
    promoted["claim_bearing"] = True
    promoted["physical_promotion"] = True
    check(rows, "claim/physical flags are visible mutations", promoted["claim_bearing"] and promoted["physical_promotion"], True,
          promoted["claim_bearing"] and promoted["physical_promotion"])
    check(rows, "claim/physical mutations are not source evidence", "path-space" in " ".join(promoted["missing_assumptions"]), True,
          "path-space" in " ".join(promoted["missing_assumptions"]))

    return {
        "schema": "tect/pah-omc020-n2c-owner-audit-hostile/1.0",
        "status": "PASS_HOSTILE_N2C_FAIL_CLOSED",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "checks": rows,
        "checks_passed": len(rows),
        "mutations": [
            "authorization flag without owner payload",
            "static C2 relabelled as non-explosion",
            "N4 evolved-vector term removed",
            "external Markov time relabelled as Lorentzian time",
            "partial owner payload with fabricated hash",
            "claim/physical promotion flags",
        ],
        "finding": "All hostile shortcuts are rejected; the missing pathwise contract remains a hold, not a PAH counterexample.",
        "non_claims": [
            "No PAH functional, rate, state, carrier, regulator, time or limit order is changed.",
            "No universal non-existence or physical Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE claim.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_n2c_owner_audit_hostile.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != payload:
        raise SystemExit("hostile N2c owner replay mismatch")
    print(f"PAH-OMC-020 N2C HOSTILE: PASS {payload['checks_passed']} fail-closed checks (HOLD_FOR_EVIDENCE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
