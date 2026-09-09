#!/usr/bin/env python3
"""Current-byte successor replay for the PAH-OMC-020 N2b audit.

The original T-064 audit remains immutable.  This successor updates only the
two stale parent pins identified by replay (temporal-work and the N-Mosco
diagnostic), then reuses the same fail-closed N2b admission predicate.  It does
not define a comparison map or promote the temporal claim.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "verification/scripts/pah_omc020_n2b_common_space_audit.py"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2b-common-space-audit-v1.1/result.json"
)

UPDATED_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json": "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md": "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md": "2eeaa12411cba9525bfb6672fdae73d47a113349236639e0c3aa2e9ed8fbd9ab",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-inventory-stable/result.json": "e4ed74bed72b1b30a13ea059e51fab87af540ce85bc45515da6384b0e2a2ecf2",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json": "5864d7e10312a3a220d4fd7766f7bbd1d260287eb3441bc844e172a26026c96a",
    "verification/lean/Tect/PahOmc020.lean": "f269428a0732204cf37cdec2dd9e87ea094329a7150fdfba6b08ffb762ad9b3c",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def load_legacy():
    spec = importlib.util.spec_from_file_location("pah_omc020_n2b_legacy", LEGACY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {LEGACY}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compute() -> dict[str, Any]:
    module = load_legacy()
    module.PINS = dict(UPDATED_PINS)
    payload = module.compute()
    payload["schema"] = "tect/pah-omc020-n2b-common-space-audit/1.1"
    payload["audit_id"] = "PAH-OMC-020-N2B-COMMON-SPACE-AUDIT-001-V1.1"
    payload["code_sha256"] = digest(Path(__file__))
    payload["successor"] = {
        "supersedes": "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json",
        "reason": "The original T-064 replay pinned stale temporal-work and n-mosco bytes; this current-byte successor preserves its predicate and updates only those parent hashes.",
    }
    payload["finding"] = (
        "Current-byte replay confirms that the fixed-space R-512 closure and finite OMC-013 intertwining are internally pinned, "
        "but no source-authorized varying-space U_n/common-Hilbert realization or PAH-specific arbitrary-sequence N2b liminf estimate is present. "
        "The coordinate pullback remains only a local-core candidate and the bounded owner inventory contains no source-authorized non-coordinate packet."
    )
    payload["reproduction"] = {
        "command": "python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v11.py",
        "check": "python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v11.py --check",
    }
    payload["non_claims"] = [
        "No PAH-OMC-020 semigroup convergence, Mosco theorem, N2a/N2b/N2c/N2d/N4 completion or R-512 selection theorem.",
        "No claim that every abstract common-space realization is impossible; external or future owner input is not inspected.",
        "No physical Pre-A, spacetime, QFT, gravity, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE conclusion.",
    ]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 N2b v1.1 replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 N2B COMMON-SPACE AUDIT V1.1: PASS {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
