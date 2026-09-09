#!/usr/bin/env python3
"""Check the PAH-OMC-020 N2a owner-packet intake contract.

This is an evidence-intake and provenance check only.  It deliberately does
not construct a comparison map, alter PAH-001, or claim a common-space or
semigroup theorem.  A future owner packet may be supplied with ``--packet``;
until then the deterministic result is HOLD_FOR_EVIDENCE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json"
RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-n2a-owner-packet-intake/result.json"
)

REQUIRED_SCOPE = {
    "functional_and_rates",
    "finite_spaces",
    "limit_hilbert_space",
    "comparison_maps",
    "time",
}
REQUIRED_ACCEPTANCE = {
    "owner_authority",
    "common_hilbert_realization",
    "local_cylinder_recovery",
    "n2b_liminf",
    "recovery_limsup",
    "n2c_n4_boundary_escape",
    "n2d_minimal_identification",
    "verification",
}
REQUIRED_PAYLOAD = [
    "packet_id, version, owner authority and SHA-256",
    "measurable/probability realization of every finite space and the common H",
    "explicit U_n (or equivalent) with domain, linearity and norm/inner-product control",
    "N1 local-cylinder stabilization and recovery quantifiers",
    "N2b arbitrary-sequence weak-liminf theorem with topology and bounded-energy quantifiers",
    "compatible limsup/recovery sequence for every target-form vector",
    "N2c/N4 compact-time boundary-escape estimate for the unchanged generator",
    "N2d identification with the R-512 minimal closed form",
    "primary, independent, hostile and Lean reproducibility manifests",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_text_file(path: Path) -> bool:
    raw = path.read_bytes()
    return b"\r" not in raw and raw.endswith(b"\n") and raw.decode("utf-8").encode("utf-8") == raw


def compute(packet_path: Path | None = None) -> dict:
    checks: list[dict] = []

    def check(name: str, condition: bool, actual: object, expected: object) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    check("contract text is UTF-8 LF", check_text_file(CONTRACT), True, True)
    check("contract identity", contract.get("contract_id") == "PAH-OMC-020-N2A-OWNER-INTAKE", contract.get("contract_id"), "PAH-OMC-020-N2A-OWNER-INTAKE")
    check("contract is intake-only", contract.get("status") == "INTAKE_CONTRACT_ONLY", contract.get("status"), "INTAKE_CONTRACT_ONLY")
    provenance = contract.get("provenance", {})
    check(
        "claim and promotion firewalls",
        provenance.get("claim_bearing") is False
        and provenance.get("active_gate_change") is False
        and provenance.get("physical_promotion") is False
        and provenance.get("source_authorized_packet_present") is False,
        provenance,
        "all false",
    )
    check("fixed scope is complete", set(contract.get("fixed_scope", {})) == REQUIRED_SCOPE, sorted(contract.get("fixed_scope", {})), sorted(REQUIRED_SCOPE))
    check("acceptance contract is complete", set(contract.get("acceptance_conditions", {})) == REQUIRED_ACCEPTANCE, sorted(contract.get("acceptance_conditions", {})), sorted(REQUIRED_ACCEPTANCE))
    check("required payload is ordered and complete", contract.get("required_owner_payload") == REQUIRED_PAYLOAD, contract.get("required_owner_payload"), REQUIRED_PAYLOAD)
    check("forbidden repair list is nonempty", bool(contract.get("forbidden_repairs")), len(contract.get("forbidden_repairs", [])), ">0")
    decision = contract.get("decision_rule", {})
    check("decision rule has HOLD branch", "HOLD_FOR_EVIDENCE" in decision and decision["HOLD_FOR_EVIDENCE"], sorted(decision), "HOLD_FOR_EVIDENCE present")
    check("single next question is explicit", isinstance(contract.get("single_next_question"), str) and bool(contract["single_next_question"].strip()), contract.get("single_next_question"), "nonempty")
    check("non-claims include physical boundary", any("physical Pre-A" in item for item in contract.get("non_claims", [])), contract.get("non_claims"), "physical boundary present")

    parent_hashes: dict[str, str] = {}
    for label, parent in contract.get("parents", {}).items():
        path = ROOT / parent["path"]
        check(f"parent present: {label}", path.is_file(), parent["path"], "file")
        actual = sha256(path)
        parent_hashes[parent["path"]] = actual
        check(f"parent hash: {label}", actual == parent["sha256"], actual, parent["sha256"])

    n2b_path = ROOT / contract["parents"]["PAH-OMC-020-N2B-AUDIT"]["path"]
    n2b = json.loads(n2b_path.read_text(encoding="utf-8"))
    check("N2b parent retains evidence hold", n2b.get("verdict") == "HOLD_FOR_EVIDENCE", n2b.get("verdict"), "HOLD_FOR_EVIDENCE")
    check("N2b parent is non-promotional", n2b.get("claim_bearing") is False and n2b.get("active_gate_change") is False and n2b.get("physical_promotion") is False, {key: n2b.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}, "all false")

    packet: dict | None = None
    packet_status = "ABSENT"
    if packet_path is not None:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet_status = "SUPPLIED"
        check("supplied packet is an object", isinstance(packet, dict), type(packet).__name__, "dict")
        check("supplied packet declares owner authority", bool(packet.get("owner_authority")), packet.get("owner_authority"), "nonempty")
        check("supplied packet declares all required fields", set(packet.get("fields", [])) == set(REQUIRED_PAYLOAD), packet.get("fields"), REQUIRED_PAYLOAD)
        check("supplied packet pins its own hash", bool(packet.get("sha256")), packet.get("sha256"), "nonempty SHA-256")
        check("supplied packet does not override fixed model", packet.get("model_change") is False, packet.get("model_change"), False)
    else:
        check("owner packet is not silently invented", contract["provenance"]["source_authorized_packet_present"] is False, packet_status, "ABSENT")

    return {
        "schema": "tect/pah-omc020-n2a-owner-packet-contract-check/1.0",
        "status": "PASS_SCOPED_INTAKE_AUDIT",
        "verdict": "HOLD_FOR_EVIDENCE" if packet is None else "PACKET_SUPPLIED_PENDING_PROOF",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "code_sha256": sha256(Path(__file__)),
        "contract_sha256": sha256(CONTRACT),
        "parent_hashes": parent_hashes,
        "packet_status": packet_status,
        "checks": checks,
        "finding": (
            "The intake contract is complete and all pinned parent hashes and "
            "firewalls pass, but no source-authorized U_n/common-space owner "
            "packet was supplied. N2a remains an evidence hold; this audit does "
            "not define a map or prove a theorem."
            if packet is None
            else "A packet was supplied for schema intake only; no N2a estimate is admitted by this checker."
        ),
        "next_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=None, help="optional future owner packet JSON")
    parser.add_argument("--output", type=Path, default=RUN)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packet = args.packet.resolve() if args.packet is not None else None
    payload = compute(packet)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if packet is not None:
            raise SystemExit("--check replays the absent-packet baseline; omit --packet")
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 N2a owner-packet intake replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(f"PAH-OMC-020 N2A OWNER-PACKET INTAKE: PASS {len(payload['checks'])}/{len(payload['checks'])}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
