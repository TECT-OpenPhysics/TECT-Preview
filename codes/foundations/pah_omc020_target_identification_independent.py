#!/usr/bin/env python3
"""Non-importing reconstruction of the PAH-OMC-020 D_n route boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-target-identification-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-target-identification/independent.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    tmp = Path(name)
    try:
        tmp.write_bytes(data)
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dest = args.output if args.output.is_absolute() else ROOT / args.output
    contract = read(CONTRACT)
    checks: list[dict[str, Any]] = []

    def ok(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    ok("schema", contract.get("schema"), "tect/pah-omc020-target-identification-contract/1.0", contract.get("schema") == "tect/pah-omc020-target-identification-contract/1.0")
    ok("task", contract.get("task_id"), "T-078", contract.get("task_id") == "T-078")
    ok("auxiliary firewall", contract.get("classification"), "auxiliary_support", contract.get("classification") == "auxiliary_support")
    ok("claim firewall", contract.get("claim_bearing"), False, contract.get("claim_bearing") is False)
    ok("gate firewall", contract.get("active_gate_change"), False, contract.get("active_gate_change") is False)
    ok("physical firewall", contract.get("physical_promotion"), False, contract.get("physical_promotion") is False)
    ok("order firewall", "j tends to infinity at fixed n first" in contract.get("fixed_scope", {}).get("order", ""), True, "j tends to infinity at fixed n first" in contract.get("fixed_scope", {}).get("order", ""))
    ok("time firewall", "External stochastic Markov time" in contract.get("fixed_scope", {}).get("time", ""), True, "External stochastic Markov time" in contract.get("fixed_scope", {}).get("time", ""))

    pins = contract.get("source_pins", {})
    ok("eight source pins", len(pins), 8, isinstance(pins, dict) and len(pins) == 8)
    sources: dict[str, dict[str, Any]] = {}
    hashes: dict[str, str] = {}
    for rel, expected in sorted(pins.items()):
        path = ROOT / rel
        ok(f"exists {rel}", path.is_file(), True, path.is_file())
        actual = sha(path)
        hashes[rel] = actual
        ok(f"hash {rel}", actual, expected, actual == expected)
        sources[rel] = read(path)

    r512 = sources["strategy/pa-hyp/PAH-OMC-019-result-v1.json"]
    r530 = sources["strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json"]
    r534 = sources["strategy/pa-hyp/PAH-OMC-020-sequential-gluing-result-v1.json"]
    r535 = sources["strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-result-v1.json"]
    r533 = sources["strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json"]
    r529 = sources["strategy/pa-hyp/PAH-OMC-020-energy-intertwining-result-v1.json"]
    closed = r512.get("result_id") == "R-512" and r512.get("verdict") == "PASS"
    ok("R-512 target exists", closed, True, closed)
    missing = " ".join(str(x) for x in (r530.get("missing_assumptions") or [])) + " " + " ".join(str(x) for x in (r534.get("missing_assumptions") or [])) + " " + " ".join(str(x) for x in (r535.get("missing_assumptions") or []))
    owner = json.dumps(r533, ensure_ascii=True, sort_keys=True)
    fields = {
        "target_form_closed": closed,
        "form_common_hilbert_map": "common-Hilbert" not in missing and "U_n" not in missing,
        "form_liminf": "N2b" not in missing and "liminf" not in missing,
        "form_recovery": "recovery" not in missing and "N2b" not in missing,
        "target_form_exact": closed and "minimal" in json.dumps(r512, ensure_ascii=True).lower(),
        "form_correlation_transfer": all(marker not in (missing + " " + json.dumps(r512.get("remaining_gates")) + " " + json.dumps(r534.get("remaining_gates"))) for marker in ("finite-semigroup", "finite-to-R-512", "semigroup convergence")),
        "path_common_space": all(marker not in owner for marker in ("path-space", "filtration", "path law")),
        "path_tightness": all(marker not in owner for marker in ("tightness", "non-explosion")),
        "path_generator_equality": all(marker not in owner for marker in ("R-512 process", "minimal-form identification", "identifying the resulting process/form")),
        "path_uniqueness": "uniqueness" not in owner,
        "path_correlation_transfer": "correlation" not in owner and "semigroup" not in owner,
    }
    route_values = {
        "common_hilbert_map": fields["form_common_hilbert_map"],
        "form_liminf": fields["form_liminf"],
        "form_recovery": fields["form_recovery"],
        "target_form_exact": fields["target_form_exact"],
        "form_correlation_transfer": fields["form_correlation_transfer"],
        "common_path_space": fields["path_common_space"],
        "path_tightness": fields["path_tightness"],
        "path_generator_equality": fields["path_generator_equality"],
        "path_uniqueness": fields["path_uniqueness"],
        "path_correlation_transfer": fields["path_correlation_transfer"],
    }
    fields["form_route_complete"] = all(route_values[name] for name in contract["routes"]["form"]["required_fields"])
    fields["path_route_complete"] = all(route_values[name] for name in contract["routes"]["path"]["required_fields"])
    fields["D_limit"] = fields["form_route_complete"] or fields["path_route_complete"]
    ok("R-534 keeps D open", "D_n" in json.dumps(r534), True, "D_n" in json.dumps(r534))
    ok("R-535 keeps target link absent", "ABSENT_R512_PROCESS_LINK" in json.dumps(r535), True, "ABSENT_R512_PROCESS_LINK" in json.dumps(r535))
    ok("R-533 owner audit is empty", "source-authorized" in owner and "path-space" in owner, True, "source-authorized" in owner and "path-space" in owner)
    static_warning = "does not imply" in json.dumps(r529).lower()
    ok("R-529 warns static insufficiency", static_warning, True, static_warning)
    ok("field partition matches contract", fields, contract["admission_predicate"]["current_expected"], fields == contract["admission_predicate"]["current_expected"])
    ok("no route is complete", fields["form_route_complete"] or fields["path_route_complete"], False, not (fields["form_route_complete"] or fields["path_route_complete"]))
    ok("D remains absent", fields["D_limit"], False, fields["D_limit"] is False)

    payload = {
        "schema": "tect/pah-omc020-target-identification-independent/1.0",
        "audit_id": "PAH-OMC-020-TARGET-IDENTIFICATION-INDEPENDENT-001",
        "task_id": "T-078",
        "status": "PASS_INDEPENDENT_TARGET_BOUNDARY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "source_hashes": hashes,
        "required_fields": fields,
        "finding": "Independent parsing agrees that the fixed R-512 target form is not a finite-to-target process identification route.",
        "next_single_question": "Can one source-authorized packet complete either the form or path route without changing PAH-001?",
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
        "implementation": "Fresh source-hash and field derivation; no primary-script import.",
        "code_sha256": sha(Path(__file__)),
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not dest.is_file() or dest.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 target-identification independent replay mismatch")
    else:
        write(dest, encoded)
    print(f"PAH-OMC-020 TARGET IDENTIFICATION INDEPENDENT: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
