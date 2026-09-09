#!/usr/bin/env python3
"""Primary audit for the PAH-OMC-020 target-process identification contract.

The script derives only the admission boundary for the missing D_n term.  It
does not construct a comparison map or process and never changes PAH-001.
"""

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
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-target-identification/primary.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        temp.write_bytes(data)
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()


def blob(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def compute() -> dict[str, Any]:
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    raw = CONTRACT.read_bytes()
    check("contract UTF-8 LF", b"\r" not in raw and raw.decode("utf-8").encode("utf-8") == raw, True, b"\r" not in raw)
    check("schema", contract.get("schema"), "tect/pah-omc020-target-identification-contract/1.0", contract.get("schema") == "tect/pah-omc020-target-identification-contract/1.0")
    check("version", contract.get("version"), "1.0.0", contract.get("version") == "1.0.0")
    check("task", contract.get("task_id"), "T-078", contract.get("task_id") == "T-078")
    check("classification", contract.get("classification"), "auxiliary_support", contract.get("classification") == "auxiliary_support")
    for field in ("conditional", "claim_bearing", "active_gate_change", "physical_promotion"):
        expected = field == "conditional"
        check(f"firewall {field}", contract.get(field), expected, contract.get(field) is expected)
    fixed = contract.get("fixed_scope", {})
    check("unchanged model", "Exactly immutable PAH-001" in fixed.get("model", ""), True, "Exactly immutable PAH-001" in fixed.get("model", ""))
    check("ordered limits", "j tends to infinity at fixed n first" in fixed.get("order", ""), True, "j tends to infinity at fixed n first" in fixed.get("order", ""))
    check("external time", "External stochastic Markov time" in fixed.get("time", ""), True, "External stochastic Markov time" in fixed.get("time", ""))

    pins = contract.get("source_pins", {})
    check("source pin count", len(pins), 8, isinstance(pins, dict) and len(pins) == 8)
    sources: dict[str, dict[str, Any]] = {}
    actual_hashes: dict[str, str] = {}
    for relative, expected_hash in sorted(pins.items()):
        path = ROOT / relative
        check(f"exists {relative}", path.is_file(), True, path.is_file())
        actual = digest(path)
        actual_hashes[relative] = actual
        check(f"hash {relative}", actual, expected_hash, actual == expected_hash)
        sources[relative] = load(path)

    pah = sources["strategy/pa-hyp/PAH-001-v1.json"]
    prereg = sources["strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"]
    r512 = sources["strategy/pa-hyp/PAH-OMC-019-result-v1.json"]
    r530 = sources["strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-result-v1.json"]
    r534 = sources["strategy/pa-hyp/PAH-OMC-020-sequential-gluing-result-v1.json"]
    r535 = sources["strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-result-v1.json"]
    r533 = sources["strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json"]
    r529 = sources["strategy/pa-hyp/PAH-OMC-020-energy-intertwining-result-v1.json"]

    check("PAH identity", pah.get("schema"), "tect/pre-a-researcher-hypothesis/1.0", pah.get("schema") == "tect/pre-a-researcher-hypothesis/1.0")
    prereg_target = prereg.get("objects_and_comparison", {}).get("target_semigroup", "")
    check("prereg retains target", "R-512" in blob(prereg_target) and "minimal" in blob(prereg_target), True, "R-512" in blob(prereg_target) and "minimal" in blob(prereg_target))
    target_form_closed = r512.get("result_id") == "R-512" and r512.get("verdict") == "PASS" and "minimal" in blob(r512).lower()
    check("R-512 fixed target form is present", target_form_closed, True, target_form_closed)

    missing_text = " ".join(str(item) for item in (r530.get("missing_assumptions") or []))
    missing_text += " " + " ".join(str(item) for item in (r534.get("missing_assumptions") or []))
    missing_text += " " + " ".join(str(item) for item in (r535.get("missing_assumptions") or []))
    owner_text = blob(r533.get("missing_assumptions")) + " " + blob(r533.get("remaining_gates"))
    form_common = not any(marker in missing_text for marker in ("U_n/common", "common U_n", "common-Hilbert"))
    form_liminf = not any(marker in missing_text for marker in ("N2b", "liminf", "liminf/recovery"))
    form_recovery = not any(marker in missing_text for marker in ("recovery", "N2b"))
    form_exact = target_form_closed and "minimal" in blob(r512).lower()
    form_transfer_text = missing_text + " " + blob(r512.get("remaining_gates")) + " " + blob(r534.get("remaining_gates"))
    form_transfer = not any(marker in form_transfer_text for marker in ("finite-semigroup", "finite-to-R-512", "semigroup convergence"))
    path_common = not any(marker in owner_text for marker in ("path-space", "path law", "filtration"))
    path_tightness = not any(marker in owner_text for marker in ("non-explosion", "tightness", "uniformity"))
    path_generator = not any(marker in owner_text for marker in ("R-512 process", "generator/form", "minimal-form identification", "identifying the resulting process/form"))
    path_unique = not any(marker in owner_text for marker in ("uniqueness", "non-explosion/uniqueness"))
    path_transfer = not any(marker in owner_text for marker in ("correlation", "semigroup"))
    flags = {
        "target_form_closed": target_form_closed,
        "form_common_hilbert_map": form_common,
        "form_liminf": form_liminf,
        "form_recovery": form_recovery,
        "target_form_exact": form_exact,
        "form_correlation_transfer": form_transfer,
        "path_common_space": path_common,
        "path_tightness": path_tightness,
        "path_generator_equality": path_generator,
        "path_uniqueness": path_unique,
        "path_correlation_transfer": path_transfer,
    }
    form_key_map = {
        "common_hilbert_map": "form_common_hilbert_map",
        "form_liminf": "form_liminf",
        "form_recovery": "form_recovery",
        "target_form_exact": "target_form_exact",
        "form_correlation_transfer": "form_correlation_transfer",
    }
    path_key_map = {
        "common_path_space": "path_common_space",
        "path_tightness": "path_tightness",
        "path_generator_equality": "path_generator_equality",
        "path_uniqueness": "path_uniqueness",
        "path_correlation_transfer": "path_correlation_transfer",
    }
    form_route = all(flags[form_key_map[key]] for key in contract["routes"]["form"]["required_fields"])
    path_route = all(flags[path_key_map[key]] for key in contract["routes"]["path"]["required_fields"])
    flags.update({"form_route_complete": form_route, "path_route_complete": path_route, "D_limit": form_route or path_route})
    expected = contract["admission_predicate"]["current_expected"]
    check("current field names", sorted(flags), sorted(expected), set(flags) == set(expected))
    check("current field partition", flags, expected, flags == expected)
    check("R-534 names D", "D_n" in blob(r534.get("missing_assumptions")), True, "D_n" in blob(r534.get("missing_assumptions")))
    check("R-535 marks D absent", "ABSENT_R512_PROCESS_LINK" in blob(r535.get("coverage")), True, "ABSENT_R512_PROCESS_LINK" in blob(r535.get("coverage")))
    check("R-533 has no owner path", "path-space" in owner_text and "source-authorized" in owner_text, True, "path-space" in owner_text and "source-authorized" in owner_text)
    static_warning = r529.get("result_id") == "R-529" and "does not imply" in blob(r529.get("conclusion")).lower()
    check("static coupling warning retained", static_warning, True, static_warning)
    check("form route not complete", form_route, False, form_route is False)
    check("path route not complete", path_route, False, path_route is False)
    check("D limit not admitted", flags["D_limit"], False, flags["D_limit"] is False)
    check("no physical promotion", contract.get("physical_promotion"), False, contract.get("physical_promotion") is False)

    route_status = {
        "form_route": {"complete": form_route, "fields": {key: flags[form_key_map[key]] for key in contract["routes"]["form"]["required_fields"]}},
        "path_route": {"complete": path_route, "fields": {key: flags[path_key_map[key]] for key in contract["routes"]["path"]["required_fields"]}},
    }
    payload = {
        "schema": "tect/pah-omc020-target-identification/1.0",
        "audit_id": "PAH-OMC-020-TARGET-IDENTIFICATION-PRIMARY-001",
        "task_id": "T-078",
        "status": "PASS_TARGET_IDENTIFICATION_BOUNDARY",
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
        "source_hashes": actual_hashes,
        "required_fields": flags,
        "route_status": route_status,
        "finding": "R-512/R-530 provide a closed target form, but the current pinned records provide neither a complete common-Hilbert form route nor a complete common-path route. D_n therefore remains uninstantiated.",
        "conditional_statement": contract["conditional_theorem"]["statement"],
        "missing_assumptions": contract["missing_assumptions"],
        "next_single_question": "Can one source-authorized packet complete either the five-field form route or the five-field path route with the declared anchored-n compact-time quantifiers?",
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
        "code_sha256": digest(Path(__file__)),
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    parser_output = payload
    return parser_output, encoded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    payload, encoded = compute()
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 target-identification primary replay mismatch")
    else:
        atomic_write(destination, encoded)
    print(f"PAH-OMC-020 TARGET IDENTIFICATION: PASS {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
