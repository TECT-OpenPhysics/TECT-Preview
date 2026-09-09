"""Fail-closed owner audit for the PAH-OMC-020 N2c/N4 process contract.

The audit does not invent a process, Lyapunov function, rate, carrier, or
physical time.  It freezes PAH-001 and R-522, inventories the current
researcher-owned records, and checks whether a source-authorized path-space
or non-explosion packet contains the fields needed to turn the static C2(A)
bound into the evolved-vector boundary estimate N4.  Repository absence is
reported as HOLD_FOR_EVIDENCE, not as a universal no-go theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2c-owner-audit-v1.1/primary.json"
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

REQUIRED_FIELDS = {
    "owner_authority": "versioned owner, signer/authority, provenance and packet SHA-256",
    "path_space_law": "path-space or martingale-problem law with filtration and cylinder generator",
    "non_explosion": "compact-time existence, non-explosion and uniqueness for the unchanged rates",
    "lyapunov_compensator": "source-derived Lyapunov drift or cumulative jump-intensity estimate using C2",
    "n2c_n4_boundary": "unconditional N2c/N4 estimate for A_n^(out,m) Q_n(s) g under the original rates",
    "minimal_form_link": "identification of the resulting process/form with the R-512 minimal closure",
    "verification_manifest": "primary, non-importing independent, hostile and Lean manifests for the packet",
}

MARKERS = {
    "path-space": re.compile(r"path[ -]?space", re.IGNORECASE),
    "martingale": re.compile(r"martingale", re.IGNORECASE),
    "non-explosion": re.compile(r"non[ -]?explosion", re.IGNORECASE),
    "lyapunov": re.compile(r"lyapunov", re.IGNORECASE),
    "N2c": re.compile(r"N2c", re.IGNORECASE),
    "N4": re.compile(r"N4", re.IGNORECASE),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def load(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def scan_source_records() -> list[dict]:
    """Inventory source records without treating marker text as authority."""
    hits: list[dict] = []
    source_root = ROOT / "strategy/pa-hyp"
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md"}:
            continue
        if "n2c-owner-audit" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        found = sorted(name for name, pattern in MARKERS.items() if pattern.search(text))
        if found:
            relative = path.relative_to(ROOT).as_posix()
            hits.append({
                "path": relative,
                "markers": found,
                "pah_omc020": path.name.lower().startswith("pah-omc-020"),
            })
    return hits


def source_authorized_packet_candidates(hits: list[dict]) -> list[str]:
    """Apply a deliberately strict admission predicate to JSON candidates."""
    candidates: list[str] = []
    for item in hits:
        if not item["pah_omc020"] or not item["path"].lower().endswith(".json"):
            continue
        payload = load(item["path"])
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        authorized = bool(re.search(
            r"(?:source[_ -]?authorized|owner[_ -]?authorized|authority[_ -]?scope)"
            r"[^\n]{0,80}(?:true|SOURCE_AUTHORIZED)",
            encoded,
            re.IGNORECASE,
        ))
        field_text = encoded.lower()
        complete = all(token.lower() in field_text for token in (
            "path", "martingale", "non", "lyapunov", "n2c", "n4", "minimal", "lean"
        ))
        if authorized and complete:
            candidates.append(item["path"])
    return candidates


def compute() -> dict:
    rows: list[dict] = []
    source_hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    pah = load("strategy/pa-hyp/PAH-001-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r522 = load("strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json")
    r520 = load("strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json")
    intake = load("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.1.json")
    r512 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    temporal_work = (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(
        encoding="utf-8"
    )

    check(rows, "PAH packet identity", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check(rows, "PAH definitions remain immutable", pah["immutability"].startswith("This accepted source file is immutable"), True,
          pah["immutability"].startswith("This accepted source file is immutable"))
    check(rows, "temporal contract identity", prereg["contract_id"], "PAH-OMC-020",
          prereg["contract_id"] == "PAH-OMC-020")
    check(rows, "j-before-n order", "first j" in prereg["scope"]["regulator_order"].lower()
          and "anchored n" in prereg["scope"]["regulator_order"].lower(), True,
          "first j" in prereg["scope"]["regulator_order"].lower()
          and "anchored n" in prereg["scope"]["regulator_order"].lower())
    check(rows, "external Markov time only", "external unaccelerated Markov time" in prereg["scope"]["time"], True,
          "external unaccelerated Markov time" in prereg["scope"]["time"])
    check(rows, "R-522 is local C2", "C2(A)" in r522["conclusion"]["local_bound"], True,
          "C2(A)" in r522["conclusion"]["local_bound"])
    check(rows, "R-522 leaves process open", any("path-space" in item.lower() or "non-explosion" in item.lower()
                                                  for item in r522["missing_assumptions"]), True,
          r522["missing_assumptions"])
    check(rows, "R-520 target process absent", "not supplied" in r520["conclusion"]["target_status"].lower(), True,
          r520["conclusion"]["target_status"])
    intake_authorized = intake["provenance"]["source_authorized_packet_present"]
    check(rows, "N2a intake is not an owner packet", intake_authorized, False,
          intake_authorized is False)
    check(rows, "N4 evolved-vector target is explicit",
          "A_n^{out,m}" in temporal_work and "Q_n(s)" in temporal_work and "N4" in temporal_work,
          True, "A_n^{out,m}" in temporal_work and "Q_n(s)" in temporal_work and "N4" in temporal_work)
    check(rows, "R-512 is a form target, not a process proof",
          any("No finite-semigroup convergence" in item for item in r512["non_claims"]), True,
          r512["non_claims"])

    hits = scan_source_records()
    candidates = source_authorized_packet_candidates(hits)
    pah020_hits = [item for item in hits if item["pah_omc020"]]
    check(rows, "strict owner packet admission is empty", candidates, [], not candidates)
    check(rows, "pah-omc-020 records are inventoried", len(pah020_hits) > 0, True, len(pah020_hits) > 0)

    c2_text = " ".join(r522["non_claims"] + r522["missing_assumptions"])
    check(rows, "C2 is not a pathwise compensator", "does not construct" in c2_text.lower()
          or "process" in c2_text.lower(), True,
          "does not construct a process" in c2_text.lower() or "process" in c2_text.lower())
    check(rows, "C2 is not N2c/N4", any("N2c" in item or "N4" in item for item in r522["missing_assumptions"]), True,
          r522["missing_assumptions"])

    field_status = {
        field: {
            "status": "MISSING",
            "required": description,
            "source_authorized_evidence": False,
        }
        for field, description in REQUIRED_FIELDS.items()
    }
    required_pathwise_contract = {
        "filtration_and_law": "A source-owned path law or martingale problem for the unchanged PAH cylinder generator.",
        "compensator": "For every compact T, a source-bound predictable jump compensator or Lyapunov drift estimate uniform in n and R.",
        "non_explosion": "lim_{K->infinity} sup_n P(sup_{s<=T} V_m(X_s)>=K)=0, with existence and uniqueness on the same domain.",
        "boundary_escape": "sup_{n>=N(f,g)} integral_0^T ||A_n^(out,m) Q_n(s)g||_2 ds -> 0 as m->infinity.",
        "form_identification": "The constructed process/form is proved equal to the R-512 minimal closed form, not merely another extension.",
    }
    finding = (
        "R-522 supplies a static Gibbs-weighted local second-rate-moment bound, "
        "but the pinned PAH-OMC-020 records contain no source-authorized path law, "
        "predictable compensator/Lyapunov estimate, non-explosion/uniqueness proof, "
        "or unconditional N2c/N4 evolved-vector bound.  Therefore the C2-to-process "
        "step is HOLD_FOR_EVIDENCE.  The empty inventory is not a universal no-go."
    )

    return {
        "schema": "tect/pah-omc020-n2c-owner-audit-primary/1.0",
        "status": "HOLD_FOR_EVIDENCE_N2C_OWNER_PACKET",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "checks": rows,
        "checks_passed": len(rows),
        "exact_scope": {
            "functional": "Exact immutable PAH-001 F_rho and original PH/LK/AP/TR rates and partial domains.",
            "input": "R-522 source-owned C2(A)<=60|A| local Gibbs-weighted second-rate-moment estimate.",
            "target": "Path-space existence/non-explosion and N2c/N4 boundary escape for the original process.",
            "state": "Original labelled Gibbs state and the registered j-before-anchored-n order.",
            "time": "External stochastic Markov time only; no quantum, proper or Lorentzian time.",
            "volume_and_regulator": "Finite OMC-004 strips with OMC-010 path; no infinite-volume conclusion is asserted.",
        },
        "owner_packet_contract": {
            "admission_predicate": "source-authorized, versioned and hash-pinned packet with every required field present before estimates are evaluated",
            "field_status": field_status,
            "required_pathwise_contract": required_pathwise_contract,
            "candidate_paths_with_strict_admission": candidates,
            "inventory": pah020_hits,
        },
        "c2_role": {
            "closed": "static local Gibbs L2 second-rate moment and a local ||L f||_2 estimate",
            "not_closed": "pathwise compensator, non-explosion, uniqueness, or the evolved-vector N4 estimate",
            "reason": "C2 is a stationary local sum; N4 acts on Q_n(s)g through roots outside a fixed prefix.",
        },
        "finding": finding,
        "assumptions": [
            "All pinned source files retain their exact bytes.",
            "R-522 C2(A)<=60|A| is used only as a static domination input.",
            "A source owner may later provide a packet satisfying the strict admission predicate.",
        ],
        "missing_assumptions": [
            "A source-authorized path-space or martingale-problem law with filtration and cylinder generator.",
            "A source-derived predictable compensator or Lyapunov drift estimate for compact-time non-explosion and uniqueness.",
            "An unconditional N2c/N4 boundary-escape estimate for A_n^(out,m)Q_n(s)g under the unchanged rates.",
            "A proof identifying the process/form with the R-512 minimal closed form.",
        ],
        "adversarial_review": [
            {
                "objection": "R-522 C2(A) already proves non-explosion.",
                "disposition": "UPHELD AGAINST PROMOTION: C2 is a stationary local L2 estimate and supplies no pathwise compensator or evolved-vector bound.",
            },
            {
                "objection": "R-520's conditional bridge can be treated as an owner packet.",
                "disposition": "REJECTED: R-520 explicitly marks process construction, non-explosion and minimal-form identification as not supplied.",
            },
            {
                "objection": "The absence scan proves universal non-existence.",
                "disposition": "REJECTED: the result is repository-scoped evidence hold and allows external or future owner input.",
            },
            {
                "objection": "A finite path-word tail can replace N4.",
                "disposition": "UPHELD AGAINST PROMOTION: finite word controls do not bound Q_n(s)g for all n without a source coupling/compensator theorem.",
            },
            {
                "objection": "The process variable is physical time or a spacetime construction.",
                "disposition": "REJECTED: only external stochastic Markov time is retained.",
            },
        ],
        "non_claims": [
            "No PAH-OMC-020 non-explosion, path-space, N2c/N4, N2b, N2d or anchored-n semigroup theorem.",
            "No universal impossibility claim follows from the repository-scoped empty owner-packet inventory.",
            "No new functional, rate, state, carrier, counterterm, projection, regulator or limit order.",
            "No physical Pre-A, spacetime, event horizon, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "formal_refs": {"results": ["R-512", "R-520", "R-522"], "negatives": [], "events": []},
        "next_single_question": (
            "Can a source owner provide one versioned path-space/Lyapunov packet whose "
            "compensator proves compact-time non-explosion and whose N2c/N4 estimate "
            "controls A_n^(out,m)Q_n(s)g under the unchanged PAH rates?"
        ),
        "revisit_condition": (
            "Reopen only when a packet with every required field is hash-pinned, or "
            "when an exact PAH-specific contradiction to one required estimate is found; "
            "do not repeat finite carrier or physical-empty calculations."
        ),
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_n2c_owner_audit.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    atomic_json(args.output, payload)
    if args.check:
        replay = json.loads(args.output.read_text(encoding="utf-8"))
        if replay != payload:
            raise SystemExit("PAH-OMC-020 N2c owner audit replay mismatch")
    print(
        f"PAH-OMC-020 N2C OWNER AUDIT: PASS {payload['checks_passed']} checks "
        "(owner packet absent; HOLD_FOR_EVIDENCE)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
