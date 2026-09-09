"""Audit the comparison-map status for the PAH-OMC-020 anchored-n route.

The audit distinguishes the declared fixed-n sampling map from the missing
anchored-n common-space or path-space map.  It is not a convergence proof.
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
    / "2026-09-08-pah-omc020-comparison-map-audit"
    / "map.json"
)

FILES = {
    "temporal": ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json",
    "target": ROOT / "strategy/pa-hyp/PAH-OMC-020-target-identification-contract-v1.json",
    "n2b": ROOT / "strategy/pa-hyp/PAH-OMC-020-N2B-common-space-audit-v1.1-contract.json",
    "omc001": ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def audit(recorded_at: str | None = None) -> dict:
    data = {name: load(path) for name, path in FILES.items()}
    temporal = data["temporal"]
    target = data["target"]
    n2b = data["n2b"]
    omc001 = data["omc001"]

    sampling = temporal["objects_and_comparison"]["S_nj"]
    n_comparison = temporal["objects_and_comparison"]["n_comparison"]
    target_status = target["admission_predicate"]["current_expected"]
    form_route = target["routes"]["form"]
    path_route = target["routes"]["path"]
    obstruction = omc001["refinement_contract"]["tested_nontrivial_candidate"]

    checks = {
        "fixed_n_sampling_map_declared": sampling.startswith("Direct same-observable evaluation"),
        "sampling_not_common_hilbert_claim": "not claimed an isometry" in sampling
        and "completed H" in sampling,
        "anchored_n_comparison_is_not_u_n": "No exterior conditional averaging" in n_comparison
        and "U_n" not in n_comparison,
        "form_route_requires_common_hilbert_map": "common_hilbert_map" in form_route["required_fields"],
        "form_route_incomplete": target_status["form_common_hilbert_map"] is False
        and target_status["form_liminf"] is False,
        "path_route_requires_common_space": "common_path_space" in path_route["required_fields"],
        "path_route_incomplete": target_status["path_common_space"] is False
        and target_status["path_correlation_transfer"] is False,
        "n2b_common_space_absent": n2b["current_status"]["common_space_U_n"] is False,
        "natural_restriction_has_exact_obstruction": obstruction["verdict"]
        == "EXACT_INTERTWINING_FAILS_FOR_THIS_NATURAL_REFINEMENT",
        "obstruction_is_route_local": "not a no-go for every possible block map" in obstruction["scope_boundary"],
    }
    assert all(checks.values()), checks

    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in FILES.values()}
    return {
        "schema": "tect/pah-omc020-comparison-map-audit/1.0",
        "status": "PASS_COMPARISON_MAP_GAP",
        "recorded_at": recorded_at
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "source_hashes": hashes,
        "finding": {
            "fixed_n_j_map": "S_nj direct same-observable sampling only",
            "anchored_n_common_hilbert_map": False,
            "anchored_n_common_path_map": False,
            "natural_free_vertex_restriction": "route-local exact intertwining failure",
            "full_comparison_map_admitted": False,
        },
        "remaining_fields": [
            "one source-authorized U_n into a fixed R-510/R-512 Hilbert space, or one source-authorized common path space",
            "cylinder recovery and norm compatibility",
            "N2b liminf/recovery and N2c/N4 boundary control",
            "N2d minimal-form identification and compact-time correlation transfer",
        ],
        "non_claims": [
            "This does not prove or refute PAH-OMC-020 ordered semigroup convergence.",
            "The natural restriction obstruction is not a no-go for every possible comparison map.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills, mass-gap or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    previous = None
    if args.output.exists():
        try:
            previous = json.loads(args.output.read_text(encoding="utf-8")).get("recorded_at")
        except (OSError, json.JSONDecodeError):
            previous = None
    result = audit(previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PAH-OMC-020 COMPARISON MAP: PASS fixed-n-S_nj; anchored-n-map=missing; natural-restriction=route-local-fail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
