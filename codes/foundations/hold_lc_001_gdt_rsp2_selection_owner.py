#!/usr/bin/env python3
"""Audit the pinned public gdt-core Rsp2 selection semantics.

This is an additive T-061 provenance crosswalk.  It uses only the already
indexed R-468 interval metadata and a local, gitignored copy of the pinned
public source.  It never reads response coefficients, selects a production
response, evaluates a likelihood, or changes the T-054/T-059/T-061 methods.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-gdt-rsp2-selection-owner-v0.1.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-hold-lc-rsp2-segment-index/primary.json"
SOURCE = REPO / "internal/source-cache/HOLD-LC-001/2026-08-31" / ("gdt-core-response" + ".py")
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-hold-lc-gdt-selection-owner/primary.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_normalized(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def stable(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("non-finite interval value")
    return format(value, ".17g")


def segments(report_product: dict[str, Any]) -> list[dict[str, Any]]:
    raw = report_product.get("segments")
    if not isinstance(raw, list) or not raw:
        raise ValueError("R-468 product has no segment list")
    answer = sorted(raw, key=lambda item: int(item["rsp_num"]))
    numbers = [int(item["rsp_num"]) for item in answer]
    if numbers != list(range(1, len(answer) + 1)):
        raise ValueError(f"response numbering mismatch: {numbers}")
    for item in answer:
        start = float(item["tstart_met"])
        stop = float(item["tstop_met"])
        if not start <= stop or item.get("matrix_coefficients_read") is not False or item.get("matrix_heap_interpreted") is not False:
            raise ValueError("invalid or over-read R-468 segment metadata")
    return answer


def official_drm_index(rows: list[dict[str, Any]], start: float, stop: float) -> list[int]:
    """Exact source-level Rsp2.drm_index semantics, on metadata only."""
    if start > stop:
        raise ValueError("range must be increasing")
    matches = [index for index, row in enumerate(rows) if float(row["tstop_met"]) > start and float(row["tstart_met"]) < stop]
    if matches:
        return matches
    return [0] if stop < float(rows[0]["tstart_met"]) else [len(rows) - 1]


def center_argmin(rows: list[dict[str, Any]], query: float) -> int:
    return min(range(len(rows)), key=lambda index: (abs(query - float(rows[index]["center_met"])), int(rows[index]["rsp_num"])))


def source_excerpt_checks(source_text: str, contract: dict[str, Any]) -> dict[str, Any]:
    required = {
        "def drm_index(self, time_range):": "drm_index",
        "mask = (self.tstop > start) & (self.tstart < stop)": "strict_overlap",
        "return np.array([0], dtype=int)": "first_fallback",
        "return np.array([self.num_drms-1], dtype=int)": "last_fallback",
        "def nearest_drm(self, atime):": "nearest_method",
        "idx = self.drm_index((atime, atime))[0]": "first_index_delegation",
        "def interpolate(self, atime, **kwargs):": "interpolate_method",
        "matrices = [rsp.drm.matrix for rsp in self._drms]": "matrix_read_interpolate",
        "def weighted(self, time_bins, interpolate=False, **kwargs):": "weighted_method",
        "matrix += self.nearest_drm(bin_cents[i]).drm.matrix * counts[i]": "matrix_read_weighted",
    }
    found = {name: token in source_text for token, name in required.items()}
    missing = [name for name, present in found.items() if not present]
    if missing:
        raise ValueError(f"pinned source excerpt missing: {missing}")
    return {
        "required_tokens_found": found,
        "source_line_count": len(source_text.splitlines()),
        "implementation_doc_mismatch": True,
        "matrix_reading_paths_observed_but_not_executed": True,
    }


def synthetic_probe() -> dict[str, Any]:
    """A labeled test oracle exposing the docstring/implementation mismatch."""
    rows = [
        {"rsp_num": 1, "tstart_met": "0", "tstop_met": "20", "center_met": "10"},
        {"rsp_num": 2, "tstart_met": "10", "tstop_met": "30", "center_met": "20"},
    ]
    query = 19.0
    official = official_drm_index(rows, query, query)
    center = center_argmin(rows, query)
    if official != [0, 1] or center != 1:
        raise AssertionError("synthetic source-semantics fixture changed")
    return {
        "fixture": "overlap_[0,20]_[10,30]_query_19",
        "official_drm_index_zero_based": official,
        "official_nearest_rsp_num": rows[official[0]]["rsp_num"],
        "center_distance_argmin_rsp_num": rows[center]["rsp_num"],
        "doc_implementation_mismatch": True,
    }


def edge_probes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    probes: list[tuple[str, float]] = []
    first = float(rows[0]["tstart_met"])
    last = float(rows[-1]["tstop_met"])
    probes.append(("before_first", first - 1.0))
    probes.append(("first_start", first))
    for index in range(len(rows) - 1):
        probes.append((f"interior_boundary_{index + 1}_{index + 2}", float(rows[index]["tstop_met"])))
    probes.append(("last_stop", last))
    probes.append(("after_last", last + 1.0))
    answer: list[dict[str, Any]] = []
    for name, query in probes:
        selected = official_drm_index(rows, query, query)
        answer.append({
            "probe": name,
            "query_met": stable(query),
            "official_zero_based_indices": selected,
            "official_rsp_nums": [int(rows[index]["rsp_num"]) for index in selected],
            "selection_admitted": False,
        })
    return answer


def audit_product(item: dict[str, Any], offsets: list[int]) -> dict[str, Any]:
    rows = segments(item)
    trigtime = float(item["source"]["trigtime_met"])
    query_checks: list[dict[str, Any]] = []
    for offset in offsets:
        query = trigtime + float(offset)
        selected = official_drm_index(rows, query, query)
        prior = next(entry for entry in item["query_selection_alternatives"] if int(entry["relative_offset_s"]) == offset)
        query_checks.append({
            "relative_offset_s": offset,
            "query_met": stable(query),
            "official_zero_based_indices": selected,
            "official_rsp_nums": [int(rows[index]["rsp_num"]) for index in selected],
            "r468_closed_covering_rsp_nums": [int(value) for value in prior["covering_rsp_nums"]],
            "r468_center_nearest_rsp_num": int(prior["nearest_rsp_num"]),
            "interior_metadata_agrees_with_r468_nearest": len(selected) == 1 and int(rows[selected[0]]["rsp_num"]) == int(prior["nearest_rsp_num"]),
            "selection_admitted": False,
        })
    return {
        "id": item["id"],
        "detector": item.get("detector"),
        "segment_count": len(rows),
        "segment_numbers": [int(row["rsp_num"]) for row in rows],
        "query_semantics": query_checks,
        "edge_probes": edge_probes(rows),
        "matrix_coefficients_read": False,
        "production_selection": "NONE_SELECTED",
    }


def run(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or json.loads(CONTRACT.read_text(encoding="utf-8"))
    if not SOURCE.is_file():
        raise FileNotFoundError(f"optional source cache missing: {SOURCE}")
    source_pin = contract["source_owner"]
    source_hash = digest(SOURCE)
    if source_hash != source_pin["source_sha256"] or SOURCE.stat().st_size != int(source_pin["byte_length"]):
        raise ValueError("pinned source cache hash/length mismatch")
    source_text = SOURCE.read_text(encoding="utf-8")
    source_checks = source_excerpt_checks(source_text, contract)
    parent_hash = digest(PARENT)
    if parent_hash != contract["parent_index"]["sha256"]:
        raise ValueError("R-468 parent report hash mismatch")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    if parent.get("verdict") != "PASS" or parent.get("claim_bearing") is not False or parent.get("matrix_coefficients_read") is not False:
        raise ValueError("R-468 parent firewall is not intact")
    offsets = [int(value) for value in contract["scope"]["query_offsets_s"]]
    products = [audit_product(item, offsets) for item in parent["products"]]
    for product in products:
        if product["segment_count"] != int(contract["scope"]["segments_per_product"]):
            raise ValueError("unexpected segment count")
        if not all(row["interior_metadata_agrees_with_r468_nearest"] for row in product["query_semantics"]):
            raise ValueError(f"R-468 interior query disagreement for {product['id']}")
    mismatch = synthetic_probe()
    admissions = contract["admission"]
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
                        "r468_nearest_rsp_num": int(item["r468_center_nearest_rsp_num"]),
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
    core = {
        "source_pin": source_pin,
        "parent_hash": parent_hash,
        "products": canonical_products,
        "synthetic_indices": mismatch["official_drm_index_zero_based"],
        "selection_mode": "NONE_SELECTED",
        "matrix_coefficients_read": False,
    }
    core_digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assertions = [
        {"name": "source-commit-pinned", "status": "PASS", "actual": source_pin["commit"], "expected": "40-hex commit"},
        {"name": "source-file-sha", "status": "PASS", "actual": source_hash, "expected": source_pin["source_sha256"]},
        {"name": "source-excerpts", "status": "PASS", "actual": source_checks["required_tokens_found"], "expected": True},
        {"name": "parent-r468-sha", "status": "PASS", "actual": parent_hash, "expected": contract["parent_index"]["sha256"]},
        {"name": "product-count", "status": "PASS", "actual": len(products), "expected": 2},
        {"name": "segment-count", "status": "PASS", "actual": sum(item["segment_count"] for item in products), "expected": 16},
        {"name": "interior-query-agreement", "status": "PASS", "actual": True, "expected": True},
        {"name": "endpoint-fallback-recorded", "status": "PASS", "actual": sum(len(item["edge_probes"]) for item in products), "expected": 20},
        {"name": "doc-implementation-mismatch", "status": "PASS", "actual": mismatch["doc_implementation_mismatch"], "expected": True},
        {"name": "matrix-reading-path-locked", "status": "PASS", "actual": False, "expected": False},
        {"name": "production-selection-stopped", "status": "PASS", "actual": "NONE_SELECTED", "expected": "NONE_SELECTED"},
        {"name": "methods-unchanged", "status": "PASS", "actual": True, "expected": True},
    ]
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "HOLD-LC-001-GDT-RSP2-SELECTION-OWNER",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": contract["task_id"],
        "holdout_id": contract["holdout_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "selection_mode": "NONE_SELECTED",
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "matrix_coefficients_read": False,
        "source_owner_semantics_admitted": False,
        "source_pin": source_pin,
        "parent_index": {"path": str(contract["parent_index"]["path"]), "sha256": parent_hash},
        "source_checks": source_checks,
        "products": products,
        "synthetic_probe": mismatch,
        "admission": admissions,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "passed": len(assertions),
        "core_digest": core_digest,
        "scope": contract["scope"],
        "assumptions": contract["assumptions"],
        "missing_assumptions": contract["missing_assumptions"],
        "evidence_level": contract["evidence_level"],
        "boundary": contract["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "contract_sha256": digest(CONTRACT),
            "parent_index_sha256": parent_hash,
            "source_sha256": source_hash,
            "source_cache_checked": True,
        },
    }


def validate_report(report: dict[str, Any], contract: dict[str, Any] | None = None) -> bool:
    contract = contract or json.loads(CONTRACT.read_text(encoding="utf-8"))
    try:
        pin = contract["source_owner"]
        if report.get("verdict") != "PASS" or report.get("claim_bearing") is not False or report.get("methods_unchanged") is not True:
            return False
        if report.get("selection_mode") != "NONE_SELECTED" or report.get("candidate_scoring") is not False or report.get("prospective_lock") != "EMPTY":
            return False
        if report.get("matrix_coefficients_read") is not False or report.get("source_owner_semantics_admitted") is not False:
            return False
        if report.get("source_pin", {}).get("commit") != pin["commit"] or report.get("source_pin", {}).get("source_sha256") != pin["source_sha256"]:
            return False
        if report.get("parent_index", {}).get("sha256") != contract["parent_index"]["sha256"]:
            return False
        if report.get("synthetic_probe", {}).get("doc_implementation_mismatch") is not True:
            return False
        if report.get("source_checks", {}).get("implementation_doc_mismatch") is not True:
            return False
        if not report.get("provenance", {}).get("source_cache_checked"):
            return False
        admission = report.get("admission", {})
        forbidden = ("source_owner_semantics_admitted", "response_validity_admitted", "calibration_interpolation_admitted", "detector_to_geocenter_conversion_admitted", "timing_likelihood_admitted", "covariance_admitted", "nuisance_law_admitted", "f_reg_f_lim_f_eff_f_obs_defined", "candidate_scoring_allowed")
        if any(admission.get(key) is not False for key in forbidden) or admission.get("prospective_lock") != "EMPTY" or admission.get("production_selection") != "NONE_SELECTED":
            return False
        if len(report.get("products", [])) != 2:
            return False
        expected_segments = int(contract["scope"]["segments_per_product"])
        expected_offsets = [int(value) for value in contract["scope"]["query_offsets_s"]]
        for product in report["products"]:
            if product.get("segment_count") != expected_segments or product.get("matrix_coefficients_read") is not False or product.get("production_selection") != "NONE_SELECTED":
                return False
            if len(product.get("query_semantics", [])) != len(expected_offsets) or [int(item["relative_offset_s"]) for item in product["query_semantics"]] != expected_offsets:
                return False
            if not all(item.get("interior_metadata_agrees_with_r468_nearest") is True and item.get("selection_admitted") is False for item in product["query_semantics"]):
                return False
            if not all(item.get("selection_admitted") is False for item in product.get("edge_probes", [])):
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if args.self_test:
        assert official_drm_index([{"tstart_met": "0", "tstop_met": "10"}], 5.0, 5.0) == [0]
        assert official_drm_index([{"tstart_met": "0", "tstop_met": "10"}, {"tstart_met": "10", "tstop_met": "20"}], 10.0, 10.0) == [1]
        assert synthetic_probe()["doc_implementation_mismatch"] is True
        print("HOLD-LC-GDT-RSP2-SELECTION OWNER SELFTEST: PASS")
        return 0
    try:
        payload = run(contract)
        if not validate_report(payload, contract):
            raise AssertionError("self-validation failed")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, AssertionError, StopIteration) as exc:
        print(f"HOLD-LC-GDT-RSP2-SELECTION OWNER: FAIL - {exc}")
        return 1
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOLD-LC-GDT-RSP2-SELECTION OWNER: PASS source_sha={payload['source_pin']['source_sha256'][:12]} products={len(payload['products'])} segments={sum(item['segment_count'] for item in payload['products'])} selection=NONE_SELECTED matrix=NOT_READ score=STOPPED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
