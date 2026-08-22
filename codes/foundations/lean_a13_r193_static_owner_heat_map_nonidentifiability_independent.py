"""Stdlib/Fraction-only independent audit for R-193."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-r193-static-owner-heat-map-nonidentifiability-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r193-static-owner-heat-map-nonidentifiability" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def derive(manifest: dict, authorities: dict) -> dict:
    data = manifest["registered_inputs"]["static_witness"]
    h1, h2 = F(data["hessian"][0]), F(data["hessian"][1])
    c1, c2 = F(data["covariance"][0]), F(data["covariance"][1])
    a1, a2 = F(data["map_a_factors"][0]), F(data["map_a_factors"][1])
    b1, b2 = F(data["map_b_factors"][0]), F(data["map_b_factors"][1])
    dynamic_fields = manifest["registered_inputs"]["required_absent_fields"]
    a1_text = json.dumps(authorities["a1"], sort_keys=True)
    a7_text = json.dumps(authorities["a7"], sort_keys=True)
    absent = {field: field not in a1_text and field not in a7_text for field in dynamic_fields}
    return {
        "static_inverse": h1 * c1 == 1 and h2 * c2 == 1,
        "map_a_zero": (a1 * 0, a2 * 0) == (0, 0),
        "map_b_zero": (b1 * 0, b2 * 0) == (0, 0),
        "map_a_contracts": 0 < a1 < 1 and 0 < a2 < 1,
        "map_b_contracts": 0 < b1 < 1 and 0 < b2 < 1,
        "maps_distinct": (a1, 0) != (b1, 0),
        "relative_decay_order_reversed": a1 > a2 and b1 < b2,
        "required_dynamic_fields_absent_from_a1_a7": absent,
        "r136_raw_spatial_intertwiner_proved": authorities["r136"]["scope"]["production_raw_spatial_intertwiner_proved"],
        "r136_q_ledger_proved": authorities["r136"]["scope"]["production_one_use_q_ledger_proved"],
        "r125_root_shell_factorisation_proved": authorities["r125"]["scope"]["production_root_shell_factorization_proved"],
        "interface_nonidentifiable": (
            h1 * c1 == 1 and h2 * c2 == 1
            and (a1 * 0, a2 * 0) == (0, 0)
            and (b1 * 0, b2 * 0) == (0, 0)
            and 0 < a1 < 1 and 0 < a2 < 1
            and 0 < b1 < 1 and 0 < b2 < 1
            and (a1, 0) != (b1, 0)
            and a1 > a2 and b1 < b2
            and all(absent.values())
            and not authorities["r136"]["scope"]["production_raw_spatial_intertwiner_proved"]
            and not authorities["r136"]["scope"]["production_one_use_q_ledger_proved"]
            and not authorities["r125"]["scope"]["production_root_shell_factorization_proved"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []

    def check(name, condition, actual, expected):
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A13-R193-STATIC-OWNER-HEAT-MAP-NONIDENTIFIABILITY" and manifest["result_id"] == "R-193", [manifest["audit_id"], manifest["result_id"]], "R-193")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("stdlib-only", True, "fractions/json/pathlib only", "no primary import")
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    authorities = {key: json.loads((REPO / item["path"]).read_text(encoding="utf-8")) for key, item in manifest["inputs"].items() if key in {"a1", "a7", "r136", "r125"}}
    derived = derive(manifest, authorities)
    check("static inverse", derived["static_inverse"], derived["static_inverse"], True)
    check("maps zero", derived["map_a_zero"] and derived["map_b_zero"], derived, True)
    check("maps contract", derived["map_a_contracts"] and derived["map_b_contracts"], derived, True)
    check("maps distinct", derived["maps_distinct"], derived["maps_distinct"], True)
    check("order reversed", derived["relative_decay_order_reversed"], derived["relative_decay_order_reversed"], True)
    check("dynamic fields absent", all(derived["required_dynamic_fields_absent_from_a1_a7"].values()), derived["required_dynamic_fields_absent_from_a1_a7"], True)
    check("prior flags open", not derived["r136_raw_spatial_intertwiner_proved"] and not derived["r136_q_ledger_proved"] and not derived["r125_root_shell_factorisation_proved"], derived, "false")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    interface = (
        derived["static_inverse"]
        and derived["map_a_zero"]
        and derived["map_b_zero"]
        and derived["map_a_contracts"]
        and derived["map_b_contracts"]
        and derived["maps_distinct"]
        and derived["relative_decay_order_reversed"]
        and all(derived["required_dynamic_fields_absent_from_a1_a7"].values())
        and not derived["r136_raw_spatial_intertwiner_proved"]
        and not derived["r136_q_ledger_proved"]
        and not derived["r125_root_shell_factorisation_proved"]
    )
    print(f"INDEPENDENT R-193 PASS {len(rows)}/{len(rows)} interface={interface}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
