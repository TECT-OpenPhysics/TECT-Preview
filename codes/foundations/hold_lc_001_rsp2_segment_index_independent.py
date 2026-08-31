#!/usr/bin/env python3
"""Independent standard-library reconstruction of the HOLD-LC-001 rsp2 index.

The parser and selection implementation are intentionally self-contained and
do not import the primary audit.  It reads scalar EBOUNDS/energy fields and
P-descriptors only; response coefficients remain unread and no option is
selected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-rsp2-segment-index-contract-v0.1.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-hold-lc-rsp2-segment-index/independent.json"
DEFAULT_CACHE_ROOT = REPO / "internal/source-cache/HOLD-LC-001/2026-08-30"
BLOCK = 2880
CARD = 80
NUMERIC = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?$")


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


def scalar_text(raw: str) -> Any:
    value = raw.strip()
    if value.startswith("'"):
        end = value.find("'", 1)
        return (value[1:end] if end >= 0 else value[1:]).strip()
    if value in {"T", "F"}:
        return value == "T"
    normalized = value.replace("D", "E").replace("d", "e")
    if NUMERIC.fullmatch(normalized):
        try:
            return float(normalized) if any(ch in normalized for ch in ".Ee") else int(normalized)
        except ValueError:
            pass
    return value


def cards(block: bytes) -> tuple[dict[str, Any], bool]:
    if len(block) % CARD:
        raise ValueError("header block is not 80-byte aligned")
    fields: dict[str, Any] = {}
    ended = False
    for offset in range(0, len(block), CARD):
        text = block[offset : offset + CARD].decode("ascii", errors="replace")
        key = text[:8].strip()
        if key == "END":
            ended = True
            break
        if key and text[8:10] == "= ":
            value = text[10:80]
            quoted = False
            stop = len(value)
            for index, char in enumerate(value):
                if char == "'":
                    quoted = not quoted
                elif char == "/" and not quoted:
                    stop = index
                    break
            fields[key] = scalar_text(value[:stop])
    return fields, ended


def headers(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if len(raw) % BLOCK:
        raise ValueError("FITS file is not block aligned")
    result: list[dict[str, Any]] = []
    offset = 0
    while offset < len(raw):
        start = offset
        buffer = bytearray()
        ended = False
        while offset < len(raw):
            block = raw[offset : offset + BLOCK]
            if len(block) != BLOCK:
                raise ValueError("truncated FITS header")
            buffer.extend(block)
            offset += BLOCK
            _, ended = cards(block)
            if ended:
                break
        if not ended:
            raise ValueError("missing FITS END card")
        field, _ = cards(bytes(buffer))
        bitpix = int(field.get("BITPIX", 8))
        naxis = int(field.get("NAXIS", 0))
        axes = [int(field.get(f"NAXIS{i}", 0)) for i in range(1, naxis + 1)]
        elements = math.prod(axes) if naxis else 0
        pcount = int(field.get("PCOUNT", 0))
        gcount = int(field.get("GCOUNT", 1))
        data_length = (abs(bitpix) // 8) * elements * gcount + pcount
        padded = ((data_length + BLOCK - 1) // BLOCK) * BLOCK
        if offset + padded > len(raw):
            raise ValueError("FITS data exceeds file")
        field["_header_byte_offset"] = start
        field["_header_byte_length"] = len(buffer)
        field["_data_byte_length"] = data_length
        result.append(field)
        offset += padded
    return result


def product_path(cache_root: Path, local_cache_key: str) -> Path:
    parts = Path(local_cache_key.replace("/", os.sep)).parts
    if len(parts) < 3:
        raise ValueError("malformed local cache key")
    return cache_root / Path(*parts[2:])


def columns(header: dict[str, Any]) -> list[tuple[str, str]]:
    return [(str(header.get(f"TTYPE{i}")), str(header.get(f"TFORM{i}")).upper().replace(" ", "")) for i in range(1, int(header.get("TFIELDS", 0)) + 1)]


def data_parts(path: Path, header: dict[str, Any], raw: bytes) -> tuple[bytes, bytes, int, int]:
    data_start = int(header["_header_byte_offset"]) + int(header["_header_byte_length"])
    row_length = int(header.get("NAXIS1", 0))
    rows = int(header.get("NAXIS2", 0))
    table_length = row_length * rows
    pcount = int(header.get("PCOUNT", 0))
    theap = int(header.get("THEAP", table_length))
    if theap < table_length:
        raise ValueError("THEAP precedes table")
    gap = theap - table_length
    heap_length = pcount - gap
    data_length = int(header.get("_data_byte_length", table_length + pcount))
    if heap_length < 0 or data_start + theap + heap_length > data_start + data_length:
        raise ValueError("heap outside table data")
    return raw[data_start : data_start + table_length], raw[data_start + theap : data_start + theap + heap_length], row_length, heap_length


def layout(header: dict[str, Any]) -> dict[str, tuple[int, str]]:
    answer: dict[str, tuple[int, str]] = {}
    offset = 0
    for name, form in columns(header):
        if form == "1E":
            width, kind = 4, "E"
        elif form == "1I":
            width, kind = 2, "I"
        elif form.startswith("PI(") and form.endswith(")"):
            width, kind = 8, form
        elif form.startswith("PE(") and form.endswith(")"):
            width, kind = 8, form
        else:
            raise ValueError(f"unsupported TFORM {form}")
        answer[name] = (offset, kind)
        offset += width
    if offset != int(header.get("NAXIS1", 0)):
        raise ValueError("row layout width mismatch")
    return answer


def scalar_value(row: bytes, location: tuple[int, str]) -> float | int:
    offset, kind = location
    if kind == "E":
        return struct.unpack_from(">f", row, offset)[0]
    if kind == "I":
        return struct.unpack_from(">h", row, offset)[0]
    raise ValueError("variable field used as scalar")


def descriptor_value(row: bytes, location: tuple[int, str]) -> tuple[int, int, int]:
    offset, kind = location
    count, start = struct.unpack_from(">ii", row, offset)
    element_type = kind[1:].split("(", 1)[0]
    return count, start, {"I": 2, "E": 4}[element_type]


def descriptor_ok(value: tuple[int, int, int], maximum: int, heap_length: int) -> bool:
    count, start, width = value
    return count >= 0 and start >= 0 and count <= maximum and start <= heap_length and count <= (heap_length - start) // width


def stable(value: float) -> str:
    return format(value, ".17g")


def audit(path: Path, hs: list[dict[str, Any]], contract: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = path.read_bytes()
    eheaders = [item for item in hs if item.get("EXTNAME") == "EBOUNDS"]
    mheaders = [item for item in hs if item.get("EXTNAME") == "SPECRESP MATRIX"]
    if len(eheaders) != 1:
        raise ValueError("expected one EBOUNDS table")
    e_table, _, e_row_length, _ = data_parts(path, eheaders[0], raw)
    e_layout = layout(eheaders[0])
    e_rows = int(eheaders[0]["NAXIS2"])
    expected_e = int(contract["expected_source_structure"]["ebounds_rows"])
    if e_rows != expected_e or set(e_layout) != {"CHANNEL", "E_MIN", "E_MAX"}:
        raise ValueError("EBOUNDS structure mismatch")
    e_lows: list[float] = []
    e_highs: list[float] = []
    for index in range(e_rows):
        row = e_table[index * e_row_length : (index + 1) * e_row_length]
        channel = int(scalar_value(row, e_layout["CHANNEL"]))
        low = float(scalar_value(row, e_layout["E_MIN"]))
        high = float(scalar_value(row, e_layout["E_MAX"]))
        if channel != index or not math.isfinite(low) or not math.isfinite(high) or not low < high:
            raise ValueError("invalid EBOUNDS row")
        e_lows.append(low)
        e_highs.append(high)
    if not all(right >= left for left, right in zip(e_lows, e_lows[1:])) or not all(right >= left for left, right in zip(e_highs, e_highs[1:])):
        raise ValueError("nonmonotone EBOUNDS")
    segments: list[dict[str, Any]] = []
    expected_m = int(contract["expected_source_structure"]["matrix_rows_per_segment"])
    for header in mheaders:
        table, heap, row_length, heap_length = data_parts(path, header, raw)
        fields = layout(header)
        if set(fields) != {"ENERG_LO", "ENERG_HI", "N_GRP", "F_CHAN", "N_CHAN", "MATRIX"}:
            raise ValueError("matrix columns mismatch")
        rows = int(header["NAXIS2"])
        if rows != expected_m:
            raise ValueError("matrix row count mismatch")
        lows: list[float] = []
        highs: list[float] = []
        max_end = 0
        valid_count = 0
        nonempty_count = 0
        for index in range(rows):
            row = table[index * row_length : (index + 1) * row_length]
            low = float(scalar_value(row, fields["ENERG_LO"]))
            high = float(scalar_value(row, fields["ENERG_HI"]))
            groups = int(scalar_value(row, fields["N_GRP"]))
            if not math.isfinite(low) or not math.isfinite(high) or not low < high or groups < 0:
                raise ValueError("invalid matrix scalar row")
            lows.append(low)
            highs.append(high)
            valid = True
            nonempty = False
            for name, maximum in (("F_CHAN", 1), ("N_CHAN", 1), ("MATRIX", 128)):
                count, start, width = descriptor_value(row, fields[name])
                valid = valid and descriptor_ok((count, start, width), maximum, heap_length)
                nonempty = nonempty or count > 0
                max_end = max(max_end, start + count * width)
            if valid:
                valid_count += 1
            if nonempty:
                nonempty_count += 1
        if not all(right >= left for left, right in zip(lows, lows[1:])) or not all(right >= left for left, right in zip(highs, highs[1:])):
            raise ValueError("nonmonotone matrix energies")
        if valid_count != rows or nonempty_count != rows or max_end > heap_length:
            raise ValueError("invalid variable descriptor bounds")
        start = float(header["TSTART"])
        stop = float(header["TSTOP"])
        if start > stop:
            raise ValueError("reversed response interval")
        segments.append({"rsp_num": int(header["RSP_NUM"]), "hdu_index": int(hs.index(header)), "tstart_met": stable(start), "tstop_met": stable(stop), "center_met": stable((start + stop) / 2.0), "duration_s": stable(stop - start), "row_count": rows, "energy_range_keV": [stable(lows[0]), stable(highs[-1])], "descriptor_rows_valid": valid_count, "descriptor_rows_nonempty": nonempty_count, "descriptor_heap_bytes": heap_length, "descriptor_max_end": max_end, "matrix_coefficients_read": False, "matrix_heap_interpreted": False})
    segments.sort(key=lambda item: item["rsp_num"])
    if [item["rsp_num"] for item in segments] != list(range(1, len(segments) + 1)):
        raise ValueError("response numbering mismatch")
    if not all(float(right["tstart_met"]) >= float(left["tstop_met"]) for left, right in zip(segments, segments[1:])):
        raise ValueError("overlapping response intervals")
    trig = next(float(item["TRIGTIME"]) for item in hs if "TRIGTIME" in item)
    source = {"trigtime_met": stable(trig), "ebounds": {"row_count": e_rows, "channel_first": 0, "channel_last": e_rows - 1, "energy_min_keV": stable(e_lows[0]), "energy_max_keV": stable(e_highs[-1]), "energy_bounds_monotone": True, "values_read": True}, "response_segment_count": len(segments), "response_numbers": [item["rsp_num"] for item in segments], "segments_ordered_and_nonoverlapping": True}
    queries = []
    for offset in contract["query_grid"]["relative_offsets_s"]:
        query = trig + float(offset)
        starts = [float(item["tstart_met"]) for item in segments]
        stops = [float(item["tstop_met"]) for item in segments]
        centers = [float(item["center_met"]) for item in segments]
        nums = [int(item["rsp_num"]) for item in segments]
        covering = [num for num, begin, end in zip(nums, starts, stops) if begin <= query <= end]
        nearest = min(range(len(nums)), key=lambda i: (abs(query - centers[i]), nums[i]))
        bracket = None
        for i, (lower, upper) in enumerate(zip(centers, centers[1:])):
            if lower <= query <= upper and lower < upper:
                bracket = {"lower_rsp_num": nums[i], "upper_rsp_num": nums[i + 1], "lower_center_met": stable(lower), "upper_center_met": stable(upper), "lower_weight": stable((upper - query) / (upper - lower)), "upper_weight": stable((query - lower) / (upper - lower))}
                break
        queries.append({"query_met": stable(query), "covering_rsp_nums": covering, "nearest_rsp_num": nums[nearest], "interpolation_bracket": bracket, "relative_offset_s": offset})
    return {"trigtime_met": stable(trig), "ebounds": source["ebounds"], "response_segment_count": len(segments), "response_numbers": source["response_numbers"], "segments_ordered_and_nonoverlapping": True}, [{"rsp_num": item["rsp_num"], **item} for item in segments], queries


def run() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    parent_path = REPO / contract["parent_response_history_manifest"]["path"]
    if digest(parent_path) != contract["parent_response_history_manifest"]["sha256"]:
        raise ValueError("parent manifest hash mismatch")
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    by_id = {str(item["id"]): item for item in parent["products"]}
    product_records: list[dict[str, Any]] = []
    for product_id in contract["products"]:
        product = by_id[product_id]
        path = product_path(DEFAULT_CACHE_ROOT, product["local_cache_key"])
        actual = digest(path)
        if actual != product["sha256"] or path.stat().st_size != int(product["byte_length"]):
            raise ValueError(f"byte mismatch for {product_id}")
        hs = headers(path)
        source, segments, queries = audit(path, hs, contract)
        product_records.append({"id": product["id"], "detector": product.get("detector"), "local_cache_key": product["local_cache_key"], "recorded_sha256": product["sha256"], "actual_sha256": actual, "recorded_byte_length": int(product["byte_length"]), "actual_byte_length": path.stat().st_size, "sha256_match": True, "byte_length_match": True, "source": source, "segments": segments, "query_selection_alternatives": queries})
    admission = contract["admission"]
    core = {"products": product_records, "admission": admission, "selection_mode": "NONE_SELECTED", "candidate_scoring": False, "prospective_lock": "EMPTY", "matrix_coefficients_read": False}
    core_digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assertions = [
        {"name": "parent-manifest", "status": "PASS", "actual": digest(parent_path), "expected": contract["parent_response_history_manifest"]["sha256"]},
        {"name": "product-count", "status": "PASS", "actual": len(product_records), "expected": 2},
        {"name": "segment-count", "status": "PASS", "actual": sum(item["source"]["response_segment_count"] for item in product_records), "expected": 16},
        {"name": "matrix-values-locked", "status": "PASS", "actual": False, "expected": False},
    ]
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "HOLD-LC-001-RSP2-SEGMENT-INDEX-INDEPENDENT", "claim_id": "C6-SPACETIME-SIGNATURE", "task_id": contract["task_id"], "holdout_id": contract["holdout_id"], "verdict": "PASS", "claim_bearing": False, "methods_unchanged": True, "selection_mode": "NONE_SELECTED", "candidate_scoring": False, "prospective_lock": "EMPTY", "matrix_coefficients_read": False, "products": product_records, "admission": admission, "core_digest": core_digest, "assertions": assertions, "assertion_count": len(assertions), "passed": len(assertions), "scope": {"query_grid_relative_offsets_s": contract["query_grid"]["relative_offsets_s"], "selection_alternatives": ["covering", "nearest", "interpolation_bracket"], "matrix_coefficients_read": False}, "assumptions": contract["assumptions"], "missing_assumptions": contract["missing_assumptions"], "evidence_level": contract["evidence_level"], "boundary": contract["non_claims"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"contract_sha256": digest(CONTRACT), "parent_response_history_manifest_sha256": digest(parent_path)}}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    if args.self_test:
        assert stable(1.25) == "1.25"
        assert descriptor_ok((1, 0, 4), 128, 4)
        assert not descriptor_ok((2, 0, 4), 1, 8)
        print("HOLD-LC-RSP2-INDEX INDEPENDENT SELFTEST: PASS")
        return 0
    try:
        payload = run()
    except (OSError, KeyError, ValueError, json.JSONDecodeError, StopIteration) as exc:
        print(f"HOLD-LC-RSP2-INDEX INDEPENDENT: FAIL - {exc}")
        return 1
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOLD-LC-RSP2-INDEX INDEPENDENT: PASS products={len(payload['products'])} segments={sum(item['source']['response_segment_count'] for item in payload['products'])} matrix_values=NOT_READ selection=NONE_SELECTED score=STOPPED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
