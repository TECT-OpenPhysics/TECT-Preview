"""Audit the missing dynamic input for the PAH-OMC-020 form route."""

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
    / "2026-09-08-pah-omc020-form-route-input-audit"
    / "form-route.json"
)

FILES = {
    "candidate": ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json",
    "factorization": ROOT / "strategy/pa-hyp/PAH-OMC-020-generator-factorization-result-v1.json",
    "energy": ROOT / "strategy/pa-hyp/PAH-OMC-020-energy-intertwining-result-v1.json",
    "mosco": ROOT / "strategy/pa-hyp/PAH-OMC-020-mosco-resolvent-result-v1.json",
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
    candidate = data["candidate"]
    factorization = data["factorization"]
    energy = data["energy"]
    mosco = data["mosco"]

    candidate_missing = [item.lower() for item in candidate["missing_assumptions"]]
    energy_missing = [item.lower() for item in energy["missing_assumptions"]]
    mosco_missing = [item.lower() for item in mosco["missing_assumptions"]]
    factor_missing = [item.lower() for item in factorization["missing_assumptions"]]
    checks = {
        "candidate_is_researcher_only": candidate["candidate"]["status"]
        == "RESEARCHER_OWNED_CANDIDATE_ONLY",
        "candidate_authorization_absent": "source-owner sign-off is still absent"
        in candidate["candidate"]["authorization"].lower(),
        "candidate_energy_missing": any("energy-form intertwining" in item for item in candidate_missing),
        "factorization_requires_root_transfer": "c_n" in factorization["exact_scope"]["comparison"].lower()
        and "unprovided source-owner" in factorization["exact_scope"]["comparison"].lower(),
        "factorization_has_two_defects": "gradient defect" in factorization["conclusion"]["finding"].lower()
        and "divergence defect" in factorization["conclusion"]["finding"].lower(),
        "factorization_terminal_square_missing": any("terminal-square" in item for item in factor_missing),
        "energy_dynamic_root_missing": any("dynamic coupling" in item for item in energy_missing),
        "energy_uniform_control_missing": any("uniform" in item and "defect" in item for item in energy_missing),
        "mosco_common_space_missing": any("common hilbert" in item and "u_n" in item for item in mosco_missing),
        "mosco_semigroup_bridge_missing": any(
            "semigroup bridge" in item.lower() or "compact-time-correlation bridge" in item.lower()
            for item in mosco_missing + mosco["remaining_gates"]
        ),
    }
    assert all(checks.values()), checks

    return {
        "schema": "tect/pah-omc020-form-route-input-audit/1.0",
        "status": "PASS_FORM_ROUTE_INPUT_GAP",
        "recorded_at": recorded_at
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in FILES.values()},
        "finding": {
            "r525_static_candidate": True,
            "source_authorized_u_n": False,
            "root_transfer_c_n": False,
            "gradient_defect_bound": False,
            "divergence_defect_bound": False,
            "terminal_square_correspondence": False,
            "form_route_admissible": False,
        },
        "required_owner_payload": [
            "source authorization and hash-pinned R-525 U_n",
            "root-space transfer C_n with multiplicity and partial-domain conventions",
            "gradient defect G_n and divergence defect D_n estimates",
            "uniform anchored-n conductance/defect control on the declared form domain",
            "terminal-square correspondence and Mosco liminf/recovery inputs",
        ],
        "non_claims": [
            "This does not prove or refute PAH-OMC-020 ordered semigroup convergence.",
            "The static L2 coupling candidate is not an energy or generator intertwining theorem.",
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
    print("PAH-OMC-020 FORM ROUTE: PASS static-U_n; C_n=missing; gradient/divergence=missing; semigroup-bridge=missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
