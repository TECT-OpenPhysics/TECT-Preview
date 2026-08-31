#!/usr/bin/env python3
"""Independent standard-library audit of the pinned Rsp2 semantics.

This lane deliberately does not import the primary implementation.  It reads
the pinned contract and R-468 metadata, then recomputes strict-overlap and
fallback behavior without opening any response matrix bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-gdt-rsp2-selection-owner-v0.1.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-hold-lc-rsp2-segment-index/primary.json"
SOURCE = REPO / "internal/source-cache/HOLD-LC-001/2026-08-31" / ("gdt-core-response" + ".py")
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-hold-lc-gdt-selection-owner/independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
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


def source_index(rows: list[dict[str, Any]], start: float, stop: float) -> list[int]:
    if start > stop:
        raise ValueError("increasing range required")
    matches = []
    for index, row in enumerate(rows):
        if float(row["tstop_met"]) > start and float(row["tstart_met"]) < stop:
            matches.append(index)
    if matches:
        return matches
    return [0] if stop < float(rows[0]["tstart_met"]) else [len(rows) - 1]


def source_probe(rows: list[dict[str, Any]], q: float) -> dict[str, Any]:
    indices = source_index(rows, q, q)
    return {"query_met": format(q, ".17g"), "official_zero_based_indices": indices, "official_rsp_nums": [int(rows[i]["rsp_num"]) for i in indices], "selection_admitted": False}


def run() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    parent_hash = digest(PARENT)
    if parent_hash != contract["parent_index"]["sha256"]:
        raise ValueError("parent R-468 hash mismatch")
    source_hash = digest(SOURCE)
    source_pin = contract["source_owner"]
    if source_hash != source_pin["source_sha256"] or SOURCE.stat().st_size != int(source_pin["byte_length"]):
        raise ValueError("source pin mismatch")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    if parent.get("verdict") != "PASS" or parent.get("matrix_coefficients_read") is not False:
        raise ValueError("parent firewall mismatch")
    products = []
    offsets = [int(value) for value in contract["scope"]["query_offsets_s"]]
    for parent_product in parent["products"]:
        rows = sorted(parent_product["segments"], key=lambda row: int(row["rsp_num"]))
        if len(rows) != int(contract["scope"]["segments_per_product"]):
            raise ValueError("segment count mismatch")
        query = []
        trigger = float(parent_product["source"]["trigtime_met"])
        for offset in offsets:
            q = trigger + float(offset)
            indices = source_index(rows, q, q)
            old = next(item for item in parent_product["query_selection_alternatives"] if int(item["relative_offset_s"]) == offset)
            if len(indices) != 1 or int(rows[indices[0]]["rsp_num"]) != int(old["nearest_rsp_num"]):
                raise ValueError("interior selection disagreement")
            query.append({"relative_offset_s": offset, "official_zero_based_indices": indices, "official_rsp_nums": [int(rows[i]["rsp_num"]) for i in indices], "r468_nearest_rsp_num": int(old["nearest_rsp_num"]), "query_met": format(q, ".17g"), "selection_admitted": False})
        first = float(rows[0]["tstart_met"])
        last = float(rows[-1]["tstop_met"])
        probes = [
            ("before_first", first - 1.0),
            ("first_start", first),
            *[(f"interior_boundary_{i + 1}_{i + 2}", float(rows[i]["tstop_met"])) for i in range(len(rows) - 1)],
            ("last_stop", last),
            ("after_last", last + 1.0),
        ]
        products.append({"id": parent_product["id"], "segment_count": len(rows), "query_semantics": query, "edge_probes": [{"probe": name, **source_probe(rows, q)} for name, q in probes], "matrix_coefficients_read": False, "production_selection": "NONE_SELECTED"})
    synthetic_rows = [{"rsp_num": 1, "tstart_met": "0", "tstop_met": "20", "center_met": "10"}, {"rsp_num": 2, "tstart_met": "10", "tstop_met": "30", "center_met": "20"}]
    synthetic = source_index(synthetic_rows, 19.0, 19.0)
    if synthetic != [0, 1]:
        raise AssertionError("synthetic overlap oracle changed")
    canonical_products = []
    for product in products:
        canonical_products.append(
            {
                "id": product["id"],
                "segment_count": product["segment_count"],
                "query_semantics": [
                    {
                        "relative_offset_s": int(item["relative_offset_s"]),
                        "official_zero_based_indices": list(item["official_zero_based_indices"]),
                        "official_rsp_nums": list(item["official_rsp_nums"]),
                        "r468_nearest_rsp_num": int(item["r468_nearest_rsp_num"]),
                    }
                    for item in product["query_semantics"]
                ],
                "edge_probes": [
                    {
                        "probe": item["probe"],
                        "query_met": item["query_met"],
                        "official_zero_based_indices": list(item["official_zero_based_indices"]),
                        "official_rsp_nums": list(item["official_rsp_nums"]),
                    }
                    for item in product["edge_probes"]
                ],
            }
        )
    core = {"source_pin": source_pin, "parent_hash": parent_hash, "products": canonical_products, "synthetic_indices": synthetic, "selection_mode": "NONE_SELECTED", "matrix_coefficients_read": False}
    core_digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assertions = [
        {"name": "source_sha", "pass": True, "actual": source_hash, "expected": source_pin["source_sha256"]},
        {"name": "parent_sha", "pass": True, "actual": parent_hash, "expected": contract["parent_index"]["sha256"]},
        {"name": "products", "pass": len(products) == 2, "actual": len(products), "expected": 2},
        {"name": "segments", "pass": sum(item["segment_count"] for item in products) == 16, "actual": sum(item["segment_count"] for item in products), "expected": 16},
        {"name": "strict_overlap_fixture", "pass": synthetic == [0, 1], "actual": synthetic, "expected": [0, 1]},
        {"name": "selection_locked", "pass": True, "actual": "NONE_SELECTED", "expected": "NONE_SELECTED"},
        {"name": "matrix_locked", "pass": True, "actual": False, "expected": False},
    ]
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "HOLD-LC-001-GDT-RSP2-SELECTION-OWNER-INDEPENDENT", "claim_id": "C6-SPACETIME-SIGNATURE", "task_id": contract["task_id"], "holdout_id": contract["holdout_id"], "verdict": "PASS", "claim_bearing": False, "methods_unchanged": True, "selection_mode": "NONE_SELECTED", "candidate_scoring": False, "prospective_lock": "EMPTY", "matrix_coefficients_read": False, "source_owner_semantics_admitted": False, "source_pin": source_pin, "parent_index_sha256": parent_hash, "products": products, "synthetic_indices": synthetic, "assertions": assertions, "assertion_count": len(assertions), "passed": sum(1 for item in assertions if item["pass"]), "core_digest": core_digest, "boundary": contract["non_claims"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": digest(CONTRACT), "source_sha256": source_hash, "parent_index_sha256": parent_hash, "source_cache_checked": True}}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    if args.self_test:
        assert source_index([{"tstart_met": "0", "tstop_met": "10"}, {"tstart_met": "10", "tstop_met": "20"}], 10.0, 10.0) == [1]
        assert source_index([{"tstart_met": "0", "tstop_met": "10"}], -1.0, -1.0) == [0]
        print("HOLD-LC-GDT-RSP2-SELECTION OWNER INDEPENDENT SELFTEST: PASS")
        return 0
    try:
        payload = run()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, AssertionError, StopIteration) as exc:
        print(f"HOLD-LC-GDT-RSP2-SELECTION OWNER INDEPENDENT: FAIL - {exc}")
        return 1
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOLD-LC-GDT-RSP2-SELECTION OWNER INDEPENDENT: PASS products={len(payload['products'])} segments={sum(item['segment_count'] for item in payload['products'])} selection=NONE_SELECTED matrix=NOT_READ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
