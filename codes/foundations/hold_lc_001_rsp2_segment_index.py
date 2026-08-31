#!/usr/bin/env python3
"""Primary binary-table structure and selection-ambiguity audit for HOLD-LC-001.

This is an additive T-061 owner-intake interface.  It verifies the two
hash-pinned rsp2 files, reads only scalar EBOUNDS/energy metadata and
variable-array descriptors, and reports covering/nearest/interpolation
alternatives without reading response coefficients or admitting a score.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-rsp2-segment-index-contract-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-hold-lc-rsp2-segment-index/primary.json"
DEFAULT_CACHE_ROOT = REPO / "internal/source-cache/HOLD-LC-001/2026-08-30"
sys.path.insert(0, str(REPO / "verification" / "scripts"))
from audit_hold_lc_owner_artifacts import parse_fits_headers, product_path, sha256_and_size, table_columns  # noqa: E402

FITS_BLOCK_BYTES = 2880
FITS_CARD_BYTES = 80


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def number(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"non-finite FITS scalar: {value!r}")
    return result


def compact(value: float) -> str:
    """Stable decimal presentation; the binary float remains an audit input."""
    # 17 significant digits round-trip an IEEE-754 binary64 value, so the
    # independent lane can recompute the same selection weights without
    # relying on a truncated intermediate timestamp.
    return format(value, ".17g")


def hdu_data(path: Path, header: dict[str, Any], raw: bytes) -> tuple[bytes, bytes, int, int]:
    header_start = int(header["_header_byte_offset"])
    header_length = int(header["_header_byte_length"])
    data_start = header_start + header_length
    row_length = int(header.get("NAXIS1", 0))
    row_count = int(header.get("NAXIS2", 0))
    table_length = row_length * row_count
    pcount = int(header.get("PCOUNT", 0))
    theap = int(header.get("THEAP", table_length))
    if theap < table_length:
        raise ValueError(f"{path}: THEAP precedes table end")
    heap_gap = theap - table_length
    heap_length = pcount - heap_gap
    if heap_length < 0:
        raise ValueError(f"{path}: PCOUNT smaller than THEAP gap")
    data_length = int(header.get("_data_byte_length", table_length + pcount))
    data_end = data_start + data_length
    if data_end > len(raw) or data_start + theap + heap_length > data_end:
        raise ValueError(f"{path}: table/heap outside FITS data")
    table = raw[data_start : data_start + table_length]
    heap = raw[data_start + theap : data_start + theap + heap_length]
    return table, heap, row_length, heap_length


def offsets(header: dict[str, Any]) -> dict[str, tuple[int, str]]:
    """Return byte offsets for the restricted formats used by this rsp2 set."""
    result: dict[str, tuple[int, str]] = {}
    offset = 0
    for column in table_columns(header):
        name = str(column["name"])
        form = str(column["format"] or "").upper().replace(" ", "")
        if form == "1E":
            width, kind = 4, "E"
        elif form == "1I":
            width, kind = 2, "I"
        elif form.startswith("PI(") and form.endswith(")"):
            width, kind = 8, form
        elif form.startswith("PE(") and form.endswith(")"):
            width, kind = 8, form
        else:
            raise ValueError(f"unsupported rsp2 TFORM {form!r} for {name}")
        result[name] = (offset, kind)
        offset += width
    if offset != int(header.get("NAXIS1", 0)):
        raise ValueError(f"row width mismatch: parsed={offset} declared={header.get('NAXIS1')}")
    return result


def scalar(row: bytes, position: tuple[int, str]) -> float | int:
    offset, kind = position
    if kind == "E":
        return struct.unpack_from(">f", row, offset)[0]
    if kind == "I":
        return struct.unpack_from(">h", row, offset)[0]
    raise ValueError(f"not a scalar field: {kind}")


def descriptor(row: bytes, position: tuple[int, str]) -> tuple[int, int, int]:
    offset, kind = position
    if not kind.startswith("P"):
        raise ValueError(f"not a variable descriptor: {kind}")
    count, start = struct.unpack_from(">ii", row, offset)
    match = kind[1:].split("(", 1)[0]
    element_width = {"I": 2, "E": 4}[match]
    return count, start, element_width


def validate_descriptor(count: int, start: int, width: int, maximum: int, heap_length: int) -> bool:
    if count < 0 or start < 0 or count > maximum:
        return False
    return start <= heap_length and count <= (heap_length - start) // width


def ebounds_audit(path: Path, header: dict[str, Any], raw: bytes, expected_rows: int) -> dict[str, Any]:
    table, _, row_length, _ = hdu_data(path, header, raw)
    positions = offsets(header)
    required = {"CHANNEL", "E_MIN", "E_MAX"}
    if set(positions) != required:
        raise ValueError(f"EBOUNDS columns mismatch: {sorted(positions)}")
    rows = int(header["NAXIS2"])
    if rows != expected_rows:
        raise ValueError(f"EBOUNDS row count {rows} != expected {expected_rows}")
    lows: list[float] = []
    highs: list[float] = []
    for index in range(rows):
        row = table[index * row_length : (index + 1) * row_length]
        channel = int(scalar(row, positions["CHANNEL"]))
        low = number(scalar(row, positions["E_MIN"]))
        high = number(scalar(row, positions["E_MAX"]))
        if channel != index or not low < high:
            raise ValueError(f"invalid EBOUNDS row {index}: channel={channel} interval={low},{high}")
        lows.append(low)
        highs.append(high)
    monotone = all(right >= left for left, right in zip(lows, lows[1:])) and all(
        right >= left for left, right in zip(highs, highs[1:])
    )
    if not monotone:
        raise ValueError("EBOUNDS energies are not monotone")
    return {
        "row_count": rows,
        "channel_first": 0,
        "channel_last": rows - 1,
        "energy_min_keV": compact(lows[0]),
        "energy_max_keV": compact(highs[-1]),
        "energy_bounds_monotone": True,
        "values_read": True,
    }


def matrix_audit(path: Path, header: dict[str, Any], raw: bytes, expected_rows: int) -> dict[str, Any]:
    table, heap, row_length, heap_length = hdu_data(path, header, raw)
    positions = offsets(header)
    required = {"ENERG_LO", "ENERG_HI", "N_GRP", "F_CHAN", "N_CHAN", "MATRIX"}
    if set(positions) != required:
        raise ValueError(f"matrix columns mismatch: {sorted(positions)}")
    rows = int(header["NAXIS2"])
    if rows != expected_rows:
        raise ValueError(f"matrix row count {rows} != expected {expected_rows}")
    energy_lows: list[float] = []
    energy_highs: list[float] = []
    descriptor_valid = 0
    descriptor_nonempty = 0
    descriptor_max_end = 0
    for index in range(rows):
        row = table[index * row_length : (index + 1) * row_length]
        low = number(scalar(row, positions["ENERG_LO"]))
        high = number(scalar(row, positions["ENERG_HI"]))
        groups = int(scalar(row, positions["N_GRP"]))
        if not low < high or groups < 0:
            raise ValueError(f"invalid matrix scalar row {index}")
        energy_lows.append(low)
        energy_highs.append(high)
        valid_row = True
        nonempty_row = False
        for name, maximum in (("F_CHAN", 1), ("N_CHAN", 1), ("MATRIX", 128)):
            count, start, width = descriptor(row, positions[name])
            valid = validate_descriptor(count, start, width, maximum, heap_length)
            valid_row = valid_row and valid
            nonempty_row = nonempty_row or count > 0
            descriptor_max_end = max(descriptor_max_end, start + count * width)
        if valid_row:
            descriptor_valid += 1
        if nonempty_row:
            descriptor_nonempty += 1
    monotone = all(right >= left for left, right in zip(energy_lows, energy_lows[1:])) and all(
        right >= left for left, right in zip(energy_highs, energy_highs[1:])
    )
    if not monotone:
        raise ValueError("matrix energy rows are not monotone")
    if descriptor_valid != rows or descriptor_nonempty != rows:
        raise ValueError("matrix variable-array descriptor validation failed")
    if descriptor_max_end > heap_length:
        raise ValueError("descriptor heap bound failed")
    return {
        "row_count": rows,
        "energy_min_keV": compact(energy_lows[0]),
        "energy_max_keV": compact(energy_highs[-1]),
        "energy_bins_monotone": True,
        "descriptor_rows_valid": descriptor_valid,
        "descriptor_rows_nonempty": descriptor_nonempty,
        "descriptor_heap_bytes": heap_length,
        "descriptor_max_end": descriptor_max_end,
        "descriptor_bounds_valid": True,
        "matrix_coefficients_read": False,
        "matrix_heap_interpreted": False,
    }


def segments_for(path: Path, headers: list[dict[str, Any]], expected_rows: int, expected_ebounds: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = path.read_bytes()
    ebounds_headers = [header for header in headers if header.get("EXTNAME") == "EBOUNDS"]
    matrices = [header for header in headers if header.get("EXTNAME") == "SPECRESP MATRIX"]
    if len(ebounds_headers) != 1:
        raise ValueError(f"expected one EBOUNDS table, got {len(ebounds_headers)}")
    ebounds = ebounds_audit(path, ebounds_headers[0], raw, expected_ebounds)
    segments: list[dict[str, Any]] = []
    for header in matrices:
        start = number(header["TSTART"])
        stop = number(header["TSTOP"])
        rsp_num = int(header["RSP_NUM"])
        if start > stop:
            raise ValueError(f"segment {rsp_num} reverses time")
        matrix = matrix_audit(path, header, raw, expected_rows)
        center = (start + stop) / 2.0
        segments.append(
            {
                "rsp_num": rsp_num,
                "hdu_index": int(headers.index(header)),
                "tstart_met": compact(start),
                "tstop_met": compact(stop),
                "center_met": compact(center),
                "duration_s": compact(stop - start),
                "row_count": matrix["row_count"],
                "energy_range_keV": [matrix["energy_min_keV"], matrix["energy_max_keV"]],
                "descriptor_rows_valid": matrix["descriptor_rows_valid"],
                "descriptor_rows_nonempty": matrix["descriptor_rows_nonempty"],
                "descriptor_heap_bytes": matrix["descriptor_heap_bytes"],
                "descriptor_max_end": matrix["descriptor_max_end"],
                "matrix_coefficients_read": False,
                "matrix_heap_interpreted": False,
            }
        )
    segments.sort(key=lambda item: item["rsp_num"])
    expected_numbers = list(range(1, len(segments) + 1))
    numbers = [item["rsp_num"] for item in segments]
    ordered = numbers == expected_numbers
    nonoverlap = all(float(current["tstart_met"]) >= float(previous["tstop_met"]) for previous, current in zip(segments, segments[1:]))
    if not ordered or not nonoverlap:
        raise ValueError(f"segment order/coverage invalid: numbers={numbers} nonoverlap={nonoverlap}")
    trigtime = next((number(header["TRIGTIME"]) for header in headers if "TRIGTIME" in header), None)
    if trigtime is None:
        raise ValueError("TRIGTIME missing")
    return (
        {
            "trigtime_met": compact(trigtime),
            "ebounds": ebounds,
            "response_segment_count": len(segments),
            "response_numbers": numbers,
            "segments_ordered_and_nonoverlapping": True,
        },
        segments,
    )


def select_segments(segments: list[dict[str, Any]], query: float) -> dict[str, Any]:
    starts = [float(item["tstart_met"]) for item in segments]
    stops = [float(item["tstop_met"]) for item in segments]
    centers = [float(item["center_met"]) for item in segments]
    numbers = [int(item["rsp_num"]) for item in segments]
    covering = [num for num, start, stop in zip(numbers, starts, stops) if start <= query <= stop]
    nearest_index = min(range(len(segments)), key=lambda index: (abs(query - centers[index]), numbers[index]))
    bracket: dict[str, Any] | None = None
    for index in range(len(segments) - 1):
        lower, upper = centers[index], centers[index + 1]
        if lower <= query <= upper and lower < upper:
            denominator = upper - lower
            bracket = {
                "lower_rsp_num": numbers[index],
                "upper_rsp_num": numbers[index + 1],
                "lower_center_met": compact(lower),
                "upper_center_met": compact(upper),
                "lower_weight": compact((upper - query) / denominator),
                "upper_weight": compact((query - lower) / denominator),
            }
            break
    return {
        "query_met": compact(query),
        "covering_rsp_nums": covering,
        "nearest_rsp_num": numbers[nearest_index],
        "interpolation_bracket": bracket,
    }


def product_audit(product: dict[str, Any], cache_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    path = product_path(cache_root, str(product["local_cache_key"]))
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_hash, actual_size = sha256_and_size(path)
    expected_hash = str(product["sha256"])
    expected_size = int(product["byte_length"])
    if actual_hash != expected_hash or actual_size != expected_size:
        raise ValueError(f"{product['id']}: byte identity mismatch")
    headers = parse_fits_headers(path)
    source, segments = segments_for(
        path,
        headers,
        int(contract["expected_source_structure"]["matrix_rows_per_segment"]),
        int(contract["expected_source_structure"]["ebounds_rows"]),
    )
    if source["response_segment_count"] != int(contract["expected_source_structure"]["response_segments_per_product"]):
        raise ValueError(f"{product['id']}: unexpected segment count")
    trigtime = float(source["trigtime_met"])
    queries = []
    for offset in contract["query_grid"]["relative_offsets_s"]:
        offset_value = float(offset)
        selected = select_segments(segments, trigtime + offset_value)
        selected["relative_offset_s"] = offset
        queries.append(selected)
    return {
        "id": product["id"],
        "detector": product.get("detector"),
        "local_cache_key": product["local_cache_key"],
        "recorded_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "recorded_byte_length": expected_size,
        "actual_byte_length": actual_size,
        "sha256_match": True,
        "byte_length_match": True,
        "source": source,
        "segments": segments,
        "query_selection_alternatives": queries,
    }


def validate_report(report: dict[str, Any], contract: dict[str, Any] | None = None) -> bool:
    """Strict scope and structural validator used by the hostile lane."""
    try:
        if report.get("verdict") != "PASS" or report.get("claim_bearing") is not False:
            return False
        if report.get("methods_unchanged") is not True:
            return False
        if report.get("selection_mode") != "NONE_SELECTED":
            return False
        if report.get("candidate_scoring") is not False or report.get("prospective_lock") != "EMPTY":
            return False
        if report.get("matrix_coefficients_read") is not False:
            return False
        admission = report["admission"]
        if any(admission[key] is not False for key in ("matrix_values_read", "calibration_validity_interpolation_admitted", "detector_to_geocenter_conversion_admitted", "timing_likelihood_admitted", "covariance_admitted", "nuisance_law_admitted", "f_reg_f_lim_f_eff_f_obs_defined", "candidate_scoring_allowed")):
            return False
        if admission.get("prospective_lock") != "EMPTY":
            return False
        if len(report.get("products", [])) != 2:
            return False
        if contract is not None:
            parent_path = REPO / contract["parent_response_history_manifest"]["path"]
            if digest(parent_path) != contract["parent_response_history_manifest"]["sha256"]:
                return False
            if report.get("provenance", {}).get("parent_response_history_manifest_sha256") != contract["parent_response_history_manifest"]["sha256"]:
                return False
            parent = json.loads(parent_path.read_text(encoding="utf-8"))
            parent_by_id = {str(item["id"]): item for item in parent.get("products", [])}
        else:
            parent_by_id = {}
        offsets_expected = list(contract["query_grid"]["relative_offsets_s"]) if contract is not None else [-30, -15, 0, 15, 30]
        expected_segments = int(contract["expected_source_structure"]["response_segments_per_product"]) if contract is not None else 8
        expected_ebounds = int(contract["expected_source_structure"]["ebounds_rows"]) if contract is not None else 128
        expected_matrix_rows = int(contract["expected_source_structure"]["matrix_rows_per_segment"]) if contract is not None else 140
        for item in report["products"]:
            source = item["source"]
            if not item["sha256_match"] or not item["byte_length_match"]:
                return False
            if contract is not None:
                parent_item = parent_by_id.get(str(item.get("id")))
                if parent_item is None or item.get("recorded_sha256") != parent_item.get("sha256") or item.get("actual_sha256") != parent_item.get("sha256") or item.get("recorded_byte_length") != parent_item.get("byte_length") or item.get("local_cache_key") != parent_item.get("local_cache_key"):
                    return False
            if source["response_segment_count"] != expected_segments or source["response_numbers"] != list(range(1, expected_segments + 1)):
                return False
            if not source["segments_ordered_and_nonoverlapping"]:
                return False
            if source["ebounds"]["row_count"] != expected_ebounds or not source["ebounds"]["energy_bounds_monotone"]:
                return False
            if len(item["segments"]) != expected_segments or len(item["query_selection_alternatives"]) != len(offsets_expected):
                return False
            if [row["relative_offset_s"] for row in item["query_selection_alternatives"]] != offsets_expected:
                return False
            if [segment["rsp_num"] for segment in item["segments"]] != list(range(1, expected_segments + 1)):
                return False
            starts = [float(segment["tstart_met"]) for segment in item["segments"]]
            stops = [float(segment["tstop_met"]) for segment in item["segments"]]
            centers = [float(segment["center_met"]) for segment in item["segments"]]
            if any(start > stop for start, stop in zip(starts, stops)) or any(current < previous for previous, current in zip(stops, starts[1:])):
                return False
            # Compact decimal fields are presentation values; allow their
            # bounded round-trip error while still rejecting a changed center.
            if any(not math.isclose(center, (start + stop) / 2.0, rel_tol=0, abs_tol=1e-3) for center, start, stop in zip(centers, starts, stops)):
                return False
            for segment in item["segments"]:
                if not segment["matrix_coefficients_read"] and not segment["matrix_heap_interpreted"]:
                    pass
                else:
                    return False
                if segment["row_count"] != expected_matrix_rows or segment["descriptor_rows_valid"] != expected_matrix_rows or segment["descriptor_rows_nonempty"] != expected_matrix_rows:
                    return False
            for row in item["query_selection_alternatives"]:
                if not row["covering_rsp_nums"] or not isinstance(row["nearest_rsp_num"], int):
                    return False
                bracket = row["interpolation_bracket"]
                if bracket is None:
                    return False
                weights = float(bracket["lower_weight"]), float(bracket["upper_weight"])
                if min(weights) < 0 or max(weights) > 1 or not math.isclose(sum(weights), 1.0, rel_tol=0, abs_tol=2e-10):
                    return False
                if bracket["lower_rsp_num"] >= bracket["upper_rsp_num"]:
                    return False
        if "core_digest" in report:
            core = {"products": report["products"], "admission": report["admission"], "selection_mode": report["selection_mode"], "candidate_scoring": report["candidate_scoring"], "prospective_lock": report["prospective_lock"], "matrix_coefficients_read": report["matrix_coefficients_read"]}
            expected_core = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            if report["core_digest"] != expected_core:
                return False
        return True
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def self_test() -> int:
    synthetic = [
        {"rsp_num": 1, "tstart_met": "0", "tstop_met": "10", "center_met": "5"},
        {"rsp_num": 2, "tstart_met": "10", "tstop_met": "20", "center_met": "15"},
    ]
    row = select_segments(synthetic, 12.5)
    assert row["covering_rsp_nums"] == [2]
    assert row["nearest_rsp_num"] == 2
    assert row["interpolation_bracket"]["lower_rsp_num"] == 1
    assert math.isclose(float(row["interpolation_bracket"]["lower_weight"]), 0.25)
    assert math.isclose(float(row["interpolation_bracket"]["upper_weight"]), 0.75)
    edge = select_segments(synthetic, 10.0)
    assert edge["covering_rsp_nums"] == [1, 2]
    assert edge["interpolation_bracket"]["lower_rsp_num"] == 1
    print("HOLD-LC-RSP2-INDEX SELFTEST: PASS (selection rules and boundary semantics)")
    return 0


def run(contract: dict[str, Any] | None = None, cache_root: Path = DEFAULT_CACHE_ROOT) -> dict[str, Any]:
    contract = contract or json.loads(CONTRACT.read_text(encoding="utf-8"))
    parent_path = REPO / contract["parent_response_history_manifest"]["path"]
    if digest(parent_path) != contract["parent_response_history_manifest"]["sha256"]:
        raise ValueError("parent response-history manifest hash mismatch")
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    by_id = {str(item["id"]): item for item in parent.get("products", [])}
    products = [product_audit(by_id[product_id], cache_root, contract) for product_id in contract["products"]]
    core = {
        "products": products,
        "admission": contract["admission"],
        "selection_mode": "NONE_SELECTED",
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "matrix_coefficients_read": False,
    }
    report = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "HOLD-LC-001-RSP2-SEGMENT-INDEX",
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
        "products": products,
        "admission": contract["admission"],
        "core_digest": hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "scope": {
            "query_grid_relative_offsets_s": contract["query_grid"]["relative_offsets_s"],
            "selection_alternatives": ["covering", "nearest", "interpolation_bracket"],
            "table_values_read": ["EBOUNDS scalar energy bounds", "matrix scalar energy bins", "P/N descriptors only"],
            "table_values_not_read": ["F_CHAN heap arrays", "N_CHAN heap arrays", "MATRIX response coefficients"],
        },
        "assumptions": contract["assumptions"],
        "missing_assumptions": contract["missing_assumptions"],
        "evidence_level": contract["evidence_level"],
        "boundary": contract["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "contract_sha256": digest(CONTRACT),
            "parent_response_history_manifest_sha256": digest(parent_path),
            "parser_dependencies": contract["parser_dependencies"],
        },
    }
    if not validate_report(report, contract):
        raise AssertionError("primary report failed its own validator")
    assertions: list[dict[str, Any]] = []
    def assertion(name: str, actual: Any, expected: Any, condition: bool = True) -> None:
        assertions.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(name)
    assertion("parent-manifest", report["provenance"]["parent_response_history_manifest_sha256"], contract["parent_response_history_manifest"]["sha256"])
    for product in products:
        assertion(f"{product['id']}-bytes", [product["sha256_match"], product["byte_length_match"]], [True, True])
        assertion(f"{product['id']}-segment-count", product["source"]["response_segment_count"], contract["expected_source_structure"]["response_segments_per_product"])
        assertion(f"{product['id']}-segment-order", product["source"]["response_numbers"], list(range(1, contract["expected_source_structure"]["response_segments_per_product"] + 1)))
        assertion(f"{product['id']}-ebounds", product["source"]["ebounds"]["row_count"], contract["expected_source_structure"]["ebounds_rows"])
        for segment in product["segments"]:
            assertion(f"{product['id']}-rsp{segment['rsp_num']}-descriptor", [segment["descriptor_rows_valid"], segment["descriptor_rows_nonempty"], segment["matrix_coefficients_read"]], [contract["expected_source_structure"]["matrix_rows_per_segment"], contract["expected_source_structure"]["matrix_rows_per_segment"], False])
        for query in product["query_selection_alternatives"]:
            assertion(f"{product['id']}-offset{query['relative_offset_s']}-alternatives", [bool(query["covering_rsp_nums"]), isinstance(query["nearest_rsp_num"], int), query["interpolation_bracket"] is not None], [True, True, True])
    report["assertions"] = assertions
    report["assertion_count"] = len(assertions)
    report["passed"] = report["assertion_count"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        report = run()
    except (OSError, KeyError, ValueError, AssertionError, json.JSONDecodeError) as exc:
        print(f"HOLD-LC-RSP2-INDEX: FAIL - {exc}")
        return 1
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, report)
    print(
        "HOLD-LC-RSP2-INDEX: PASS "
        f"products={len(report['products'])} segments={sum(item['source']['response_segment_count'] for item in report['products'])} "
        f"assertions={report['passed']} matrix_values=NOT_READ selection=NONE_SELECTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
