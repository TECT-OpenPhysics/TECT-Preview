"""Reconcile the PAH-OMC-020 composite source chain with the R-552 scope.

This is a provenance/scope audit only.  It does not alter PAH-001, add a
comparison map, or claim temporal convergence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT
    / "claims"
    / "C6-SPACETIME-SIGNATURE"
    / "runs"
    / "2026-09-08-pah-omc020-source-chain-scope-audit"
    / "scope.json"
)

FILES = {
    "temporal_prereg": ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json",
    "omc018_prereg": ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-prereg-v1.json",
    "omc001": ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json",
    "r552": ROOT / "strategy/pa-hyp/PAH-OMC-020-semigroup-wellposedness-result-v1.json",
    "r557": ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-packet-sufficiency-result-v1.json",
    "r566": ROOT / "strategy/pa-hyp/PAH-OMC-026-cut-set-packet-crosswalk-result-v1.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_scope(recorded_at: str | None = None) -> dict:
    payloads = {name: load_json(path) for name, path in FILES.items()}
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in FILES.values()}

    temporal_sources = payloads["temporal_prereg"]["sources"]
    omc018_sources = payloads["omc018_prereg"]["sources"]
    omc001 = payloads["omc001"]
    r552 = payloads["r552"]
    r557 = payloads["r557"]
    r566 = payloads["r566"]

    checks = {
        "temporal_uses_omc018_result": temporal_sources.get(
            "strategy/pa-hyp/PAH-OMC-018-result-v1.json"
        )
        == sha256(FILES["omc018_prereg"].with_name("PAH-OMC-018-result-v1.json")),
        "temporal_uses_omc018_prereg": temporal_sources.get(
            "strategy/pa-hyp/PAH-OMC-018-generator-prereg-v1.json"
        )
        == sha256(FILES["omc018_prereg"]),
        "omc018_uses_omc001": omc018_sources.get(
            "strategy/pa-hyp/PAH-OMC-001-v1.json"
        )
        == sha256(FILES["omc001"]),
        "omc001_parent_is_pah001": omc001["parent"]["packet_id"] == "PAH-001",
        "omc001_is_successor_contract": omc001["provenance"]["class"]
        == "RESEARCHER_HYPOTHESIS_SUCCESSOR_CONTRACT",
        "omc001_marks_nonretroactive": "not retroactive evidence"
        in omc001["parent"]["composition_rule"],
        "omc001_retains_k2_channels": "two distinct channels"
        in omc001["invalid_and_duplicate_conventions"]["K_equals_2"],
        "r552_is_parent_scope": set(r552["source_files"]) == {
            "strategy/pa-hyp/PAH-001-v1.json",
            "strategy/pa-hyp/PAH-OMC-004-v1.json",
            "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json",
            "strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json",
        },
        "r557_requires_source_owner_fields": any(
            "source-authorized" in item.lower() and "root" in item.lower()
            for item in r557["missing_assumptions"]
        ),
        "r557_requires_common_realization": any(
            "common realization" in item.lower() for item in r557["missing_assumptions"]
        ),
        "r566_still_missing_packet": any(
            "source-authorized packet" in item.lower() for item in r566["missing_assumptions"]
        ),
        "r566_still_open_jd": any(
            "full-domain" in item.lower() and "anchored" in item.lower()
            for item in r566["missing_assumptions"]
        ),
    }
    assert all(checks.values()), checks

    return {
        "schema": "tect/pah-omc020-source-chain-scope-audit/1.0",
        "status": "PASS_SCOPE_RECONCILIATION",
        "recorded_at": recorded_at
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "source_hashes": hashes,
        "finding": {
            "composite_model_root_semantics": True,
            "composite_model_authority": "researcher-owned OMC-001/OMC-018 successor contract",
            "r552_parent_only_scope": True,
            "r552_alone_refutes_omc020": False,
            "owner_packet_admitted": False,
            "anchored_n_comparison_open": True,
        },
        "remaining_fields": [
            "source-authorized common realization U_n/H",
            "N1 local recovery",
            "arbitrary-sequence N2b liminf and recovery",
            "N2c/N4 boundary escape",
            "N2d R-512 minimal-form identification",
            "full-domain J_(n,j) and anchored D_n estimates",
        ],
        "non_claims": [
            "This does not prove or refute PAH-OMC-020 ordered semigroup convergence.",
            "The researcher-owned OMC-001/OMC-018 successor is not a source-authorized owner packet.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills, mass-gap or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    prior_timestamp = None
    if args.output.exists():
        try:
            prior_timestamp = json.loads(args.output.read_text(encoding="utf-8")).get("recorded_at")
        except (OSError, json.JSONDecodeError):
            prior_timestamp = None
    result = check_scope(prior_timestamp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PAH-OMC-020 SOURCE-CHAIN SCOPE: PASS root-convention-composite; owner-packet=missing; anchored-n=open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
