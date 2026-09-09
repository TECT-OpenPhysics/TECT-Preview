"""Non-importing replay of the PAH-OMC-020 N2c owner audit.

This lane reconstructs the source inventory and the fail-closed admission
decision independently of verification/scripts/pah_omc020_n2c_owner_audit.py.
It treats the existing C2 estimate as static input only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


BASE = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = BASE / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2c-owner-audit-v1.1/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json":
        "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json":
        "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-certificate.md":
        "61284627c3a74df7d30e346365df983bba2781138639877196f4fbf90229887c",
    "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json":
        "12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json":
        "14c7e4da055ccb6104c1952367b0c6615533a5fc50219ef5d7b047cd1552464c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "2eeaa12411cba9525bfb6672fdae73d47a113349236639e0c3aa2e9ed8fbd9ab",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
}

MARKERS = (
    ("path-space", re.compile(r"path[ -]?space", re.I)),
    ("martingale", re.compile(r"martingale", re.I)),
    ("non-explosion", re.compile(r"non[ -]?explosion", re.I)),
    ("lyapunov", re.compile(r"lyapunov", re.I)),
    ("N2c", re.compile(r"N2c", re.I)),
    ("N4", re.compile(r"N4", re.I)),
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


def record(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def json_at(relative: str) -> dict:
    return json.loads((BASE / relative).read_text(encoding="utf-8"))


def source_inventory() -> list[dict]:
    rows: list[dict] = []
    for path in sorted((BASE / "strategy/pa-hyp").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md"}:
            continue
        if "n2c-owner-audit" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        found = [name for name, pattern in MARKERS if pattern.search(text)]
        if found:
            rows.append({
                "path": path.relative_to(BASE).as_posix(),
                "markers": sorted(found),
                "pah_omc020": path.name.lower().startswith("pah-omc-020"),
            })
    return rows


def strict_owner_candidates(inventory: list[dict]) -> list[str]:
    required_tokens = ("path", "martingale", "non", "lyapunov", "n2c", "n4", "minimal", "lean")
    accepted: list[str] = []
    for item in inventory:
        if not item["pah_omc020"] or not item["path"].endswith(".json"):
            continue
        text = (BASE / item["path"]).read_text(encoding="utf-8")
        authorized = re.search(
            r"(?:source[_ -]?authorized|owner[_ -]?authorized|authority[_ -]?scope)"
            r"[^\n]{0,80}(?:true|SOURCE_AUTHORIZED)", text, re.I
        )
        if authorized and all(token in text.lower() for token in required_tokens):
            accepted.append(item["path"])
    return accepted


def compute() -> dict:
    checks: list[dict] = []
    actual_pins = {}
    for relative, expected in PINS.items():
        actual = sha(BASE / relative)
        actual_pins[relative] = actual
        record(checks, f"independent source hash {relative}", actual, expected, actual == expected)

    pah = json_at("strategy/pa-hyp/PAH-001-v1.json")
    prereg = json_at("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r522 = json_at("strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json")
    r520 = json_at("strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json")
    intake = json_at("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json")
    r512 = json_at("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    work = (BASE / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8")

    record(checks, "immutable PAH source", pah["immutability"].startswith("This accepted source file is immutable"), True,
           pah["immutability"].startswith("This accepted source file is immutable"))
    record(checks, "temporal preregistration", prereg["contract_id"], "PAH-OMC-020",
           prereg["contract_id"] == "PAH-OMC-020")
    record(checks, "external time text", "external unaccelerated Markov time" in prereg["scope"]["time"], True,
           "external unaccelerated Markov time" in prereg["scope"]["time"])
    record(checks, "R-522 C2 text", "C2(A)" in r522["conclusion"]["local_bound"], True,
           "C2(A)" in r522["conclusion"]["local_bound"])
    record(checks, "R-522 process gap", any("process" in item.lower() or "non-explosion" in item.lower()
                                             for item in r522["missing_assumptions"]), True,
           r522["missing_assumptions"])
    record(checks, "R-520 process gap", "not supplied" in r520["conclusion"]["target_status"].lower(), True,
           r520["conclusion"]["target_status"])
    record(checks, "intake provenance remains false", intake["provenance"]["source_authorized_packet_present"], False,
           intake["provenance"]["source_authorized_packet_present"] is False)
    record(checks, "N4 expression retained", all(token in work for token in ("A_n^{out,m}", "Q_n(s)", "N4")), True,
           all(token in work for token in ("A_n^{out,m}", "Q_n(s)", "N4")))
    record(checks, "R-512 is not temporal proof",
           any("No finite-semigroup convergence" in item for item in r512["non_claims"]), True,
           r512["non_claims"])

    inventory = source_inventory()
    accepted = strict_owner_candidates(inventory)
    record(checks, "strict owner admission remains empty", accepted, [], not accepted)
    record(checks, "inventory contains PAH records", sum(1 for item in inventory if item["pah_omc020"]) > 0, True,
           sum(1 for item in inventory if item["pah_omc020"]) > 0)
    record(checks, "static C2 is not N4", any("N2c" in item or "N4" in item for item in r522["missing_assumptions"]), True,
           r522["missing_assumptions"])

    return {
        "schema": "tect/pah-omc020-n2c-owner-audit-independent/1.0",
        "status": "PASS_INDEPENDENT_N2C_OWNER_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual_pins,
        "checks": checks,
        "checks_passed": len(checks),
        "inventory": inventory,
        "strict_owner_candidates": accepted,
        "finding": (
            "Independent reconstruction agrees that R-522 is a static local C2 input "
            "and that no source-authorized path-space, compensator/Lyapunov, "
            "non-explosion or unconditional N2c/N4 packet is present."
        ),
        "missing_assumptions": [
            "Source-authorized path-space or martingale-problem law with filtration and cylinder generator.",
            "Predictable compensator or Lyapunov drift estimate for compact-time non-explosion and uniqueness.",
            "Unconditional N2c/N4 boundary escape for A_n^(out,m)Q_n(s)g under unchanged rates.",
            "Identification of the process/form with the R-512 minimal closed form.",
        ],
        "non_claims": [
            "No PAH-OMC-020 temporal convergence theorem or universal no-go theorem.",
            "No new PAH functional, rate, state, carrier, regulator, limit order or physical time.",
            "No physical Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_n2c_owner_audit_independent.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != payload:
        raise SystemExit("independent N2c owner replay mismatch")
    print(f"PAH-OMC-020 N2C INDEPENDENT: PASS {payload['checks_passed']} checks (HOLD_FOR_EVIDENCE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
