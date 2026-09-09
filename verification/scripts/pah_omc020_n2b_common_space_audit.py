#!/usr/bin/env python3
"""Scoped audit of the PAH-OMC-020 N2b common-space obligation.

This audit separates the already registered R-512 fixed-limit Hilbert-space
form closure from the still-required varying-space realization and Mosco
liminf statement in PAH-OMC-020.  It does not invent an embedding, alter a
rate or state, or treat a source absence as a universal mathematical no-go.
The expected outcome is a reproducible evidence hold until an owner-authorized
common-space packet is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
OMC017 = ROOT / "strategy/pa-hyp/PAH-OMC-017-result-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json"
OMC019 = ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json"
OMC019_CERT = ROOT / "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
OWNER_AUDIT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-owner-inventory-stable/result.json"
)
MOSCO_RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json"
)
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-n2b-common-space-audit/result.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json":
        "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md":
        "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-inventory-stable/result.json":
        "e4ed74bed72b1b30a13ea059e51fab87af540ce85bc45515da6384b0e2a2ecf2",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json":
        "f70a3ad6b6f476377dfc355506f82124507ffbed1a5e4848d92cec1116729869",
    "verification/lean/Tect/PahOmc020.lean":
        "f269428a0732204cf37cdec2dd9e87ea094329a7150fdfba6b08ffb762ad9b3c",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def compute() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    current = {relative: sha256(ROOT / relative) for relative in PINS}
    check("all source pins", current == PINS, current, PINS)

    pah = load_json(PAH)
    omc013 = load_json(OMC013)
    omc017 = load_json(OMC017)
    omc018 = load_json(OMC018)
    omc019 = load_json(OMC019)
    omc020 = load_json(OMC020)
    owner = load_json(OWNER_AUDIT)
    mosco = load_json(MOSCO_RUN)
    work_text = WORK.read_text(encoding="utf-8")
    lean_text = LEAN.read_text(encoding="utf-8")

    check("PAH identity", pah.get("packet_id") == "PAH-001", pah.get("packet_id"), "PAH-001")
    check("OMC-013 finite identity", omc013.get("contract_id") == "PAH-OMC-013" and omc013.get("status", {}).get("stage2_status") == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP", omc013.get("status"), "finite result with stage2 hold")
    check("R-510/R-511/R-512 chain", omc017.get("result_id") == "R-510" and omc018.get("result_id") == "R-511" and omc019.get("result_id") == "R-512", [omc017.get("result_id"), omc018.get("result_id"), omc019.get("result_id")], ["R-510", "R-511", "R-512"])
    check("R-512 fixed-H closure", "Hilbert completion" in omc019.get("exact_scope", {}).get("state", "") and "minimal closed" in omc019.get("conclusion", ""), omc019.get("conclusion"), "fixed state-H minimal closure")
    check("R-512 does not provide varying-space map", "U_n" not in omc019.get("conclusion", "") and "varying" not in omc019.get("exact_scope", {}).get("domain", "").lower(), omc019.get("exact_scope", {}).get("domain"), "no U_n claim")

    snj = omc020["objects_and_comparison"]["S_nj"]
    check("OMC-020 keeps direct finite evaluation", "Direct same-observable evaluation" in snj, snj, "source S_nj definition")
    check("S_nj completion boundedness is not assumed", "not claimed" in snj and "bounded map" in snj, snj, "no completed-H boundedness shortcut")
    check("N2a is explicit", "(N2a)" in work_text and "measure-compatible realization U_n" in work_text, "(N2a) U_n", "required")
    check("N2b is explicit", "(N2b)" in work_text and "liminf" in work_text and "weakly converging" in work_text, "(N2b) weak liminf", "required")
    check("N2d is separate", "(N2d)" in work_text and "minimal" in work_text and "boundary extension" in work_text, "(N2d) minimal selection", "separate obligation")
    check("N1 is not arbitrary-sequence liminf", "(N1) says nothing about arbitrary sequences" in work_text, "N1/local recovery only", "explicit separation")
    check("R-512 is not silently promoted", "R-512 closability/minimality does not supply (N2b) or (N2c)" in " ".join(work_text.split()), "R-512 limitation", "present")
    check("local pullback is not full U_n", "(J_n h)(x)=h(p_n x)" in work_text and "not" in work_text[work_text.find("(J_n h)(x)=h(p_n x)"):work_text.find("(J_n h)(x)=h(p_n x)") + 1500] and "full" in work_text[work_text.find("(J_n h)(x)=h(p_n x)"):work_text.find("(J_n h)(x)=h(p_n x)") + 1800], "J_n local candidate", "full map not admitted")
    check("owner audit remains evidence hold", owner.get("verdict") == "HOLD_FOR_EVIDENCE" and "no source-authorized" in owner.get("finding", "").lower(), owner.get("finding"), "owner packet absent in bounded inventory")
    check("Mosco contract remains open", mosco.get("temporal_verdict") == "IN_PROGRESS" and len(mosco.get("open_obligations", [])) >= 1, mosco.get("open_obligations"), "N2b/N2c/N2d open")

    required_fields = [
        "one common Hilbert space H and its measurable/probability realization",
        "explicit U_n or equivalent maps with local norm and inner-product convergence",
        "weak topology and bounded-energy quantifiers for every sequence U_n u_n",
        "PAH-specific liminf proof E_infty(u,u) <= liminf E_n(u_n,u_n)",
        "recovery/limsup construction compatible with the same maps",
        "N4 unbounded-rate boundary escape and compact-time control",
        "identification of the selected closed form with the R-512 minimal closure",
        "independent, hostile and Lean verification of the model-specific estimates",
    ]
    check("missing-input contract is nonempty", len(required_fields) == 8, required_fields, "eight explicit N2b inputs")

    # The registered Lean file is intentionally limited to finite/algebraic
    # facts.  This check prevents a source comment or filename from being
    # mistaken for an N2b theorem.
    n2b_markers = ("mosco_liminf", "recovery_sequence", "common_space_embedding", "liminf_form")
    check("Lean N2b theorem is not registered", not any(marker in lean_text for marker in n2b_markers), n2b_markers, "none in PahOmc020.lean")
    check("Lean file states finite scope", "does not formalize the PAH measure" in lean_text and "either ordered limit" in lean_text, "finite algebraic Lean scope", "explicit")

    # Hostile controls: accepting any of these shortcuts would turn an
    # evidence hold into an unsupported theorem, so the audit requires their
    # rejection to remain visible in the frozen preregistration/certificate.
    prohibited = omc020.get("prohibited_shortcuts", [])
    check("hostile cross-Q rescue rejected", any("direct-sum rescue" in item for item in prohibited), prohibited, "cross-Q/direct-sum shortcut rejected")
    check("hostile form-core substitution rejected", any("form core" in item and "operator graph core" in item for item in prohibited), prohibited, "form/operator core distinction")
    check("R-512 keeps temporal construction separate", any("No finite-semigroup convergence" in item for item in omc019.get("non_claims", [])), omc019.get("non_claims"), "temporal convergence remains separate")

    return {
        "schema": "tect/pah-omc020-n2b-common-space-audit/1.0",
        "audit_id": "PAH-OMC-020-N2B-COMMON-SPACE-AUDIT-001",
        "task_id": "T-064",
        "status": "PASS_SCOPED_N2B_AUDIT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "code_sha256": sha256(Path(__file__)),
        "source_hashes": current,
        "fixed_form_scope": "R-512 closes the R-511 form on the anchored R-510 limit Hilbert space under inherited fixed-space hypotheses.",
        "n2b_scope": "PAH-OMC-020 requires a varying finite-space realization, arbitrary-sequence weak liminf, recovery compatibility, boundary escape and minimal-form identification in the fixed j-before-n order.",
        "finding": "The fixed-space R-512 closure and finite OMC-013 intertwining are internally pinned, but the current source does not supply the varying-space U_n/common-Hilbert realization or the PAH-specific arbitrary-sequence N2b liminf estimate. The existing coordinate pullback is explicitly only a local-core candidate, and the bounded owner-history inventory contains no source-authorized non-coordinate packet.",
        "missing_assumptions": required_fields,
        "reproduction": {
            "command": "python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json",
            "check": "python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit.py --check",
        },
        "next_question": "Can one source-authorized U_n packet satisfy the eight listed common-space, weak-liminf, recovery, boundary and verification fields without changing PAH-001?",
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence, Mosco theorem, N2a/N2b/N2c/N2d/N4 completion or R-512 selection theorem.",
            "No claim that every abstract common-space realization is impossible; external or future owner input is not inspected.",
            "No physical Pre-A, spacetime, QFT, gravity, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE conclusion.",
        ],
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 N2b common-space audit replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 N2B COMMON-SPACE AUDIT: PASS {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
