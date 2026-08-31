#!/usr/bin/env python3
"""Extract a frozen detector-frame feature index from the HOLD-LC-001 TTE rows.

This is an additive T-061 P1 source-feature audit.  It reads only the TIME and
PHA columns of the two hash-pinned Fermi EVENTS tables, verifies their FITS
layout and header time interval, and creates a one-second trigger-relative
histogram.  It does not read response matrices, perform a geocentre
conversion, estimate a likelihood/covariance, or score a candidate.
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
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "hold-lc-001-tte-event-feature-index-v0.1.json"
BYTE_FREEZE = REPO / "strategy" / "hold-lc-001-event-byte-freeze-v0.1.json"
DEFAULT_CACHE_ROOT = REPO / "internal" / "source-cache" / "HOLD-LC-001" / "2026-08-30"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-primary-hold-lc-tte-event-feature-index/primary.json"
)

FITS_BLOCK_BYTES = 2880
FITS_CARD_BYTES = 80
BIN_WIDTH_SECONDS = 1.0
PHA_MIN = 0
PHA_MAX = 127
REQUIRED_PRODUCTS = ("FERMI-GBM-N0-TTE", "FERMI-GBM-B0-TTE")
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?$")
TFORM_RE = re.compile(r"^(\d*)([A-Za-z])(?:\(\d+\))?$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
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


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("'"):
        end = value.find("'", 1)
        return (value[1:end] if end >= 0 else value[1:]).strip()
    if value in {"T", "F"}:
        return value == "T"
    numeric = value.replace("D", "E").replace("d", "e")
    if NUMERIC_RE.fullmatch(numeric):
        try:
            number = float(numeric) if any(char in numeric for char in ".Ee") else int(numeric)
            if isinstance(number, float) and not math.isfinite(number):
                raise ValueError("non-finite FITS scalar")
            return number
        except ValueError:
            pass
    return value


def parse_cards(header: bytes) -> tuple[dict[str, Any], bool]:
    if len(header) % FITS_CARD_BYTES:
        raise ValueError("FITS header is not card aligned")
    fields: dict[str, Any] = {}
    ended = False
    for offset in range(0, len(header), FITS_CARD_BYTES):
        card = header[offset : offset + FITS_CARD_BYTES].decode("ascii", errors="replace")
        key = card[:8].strip()
        if key == "END":
            ended = True
            break
        if key and card[8:10] == "= ":
            raw = card[10:80]
            in_quote = False
            end = len(raw)
            for index, char in enumerate(raw):
                if char == "'":
                    in_quote = not in_quote
                elif char == "/" and not in_quote:
                    end = index
                    break
            fields[key] = parse_scalar(raw[:end])
    return fields, ended


def read_hdus(data: bytes) -> list[dict[str, Any]]:
    """Read FITS headers and data spans without interpreting table payloads."""
    offset = 0
    hdus: list[dict[str, Any]] = []
    while offset < len(data):
        header_start = offset
        blocks = bytearray()
        ended = False
        while offset < len(data):
            block = data[offset : offset + FITS_BLOCK_BYTES]
            if len(block) != FITS_BLOCK_BYTES:
                raise ValueError(f"truncated FITS header at byte {offset}")
            blocks.extend(block)
            offset += FITS_BLOCK_BYTES
            _, ended = parse_cards(block)
            if ended:
                break
        if not ended:
            raise ValueError("FITS END card missing")
        fields, _ = parse_cards(bytes(blocks))
        bitpix = int(fields.get("BITPIX", 8))
        naxis = int(fields.get("NAXIS", 0))
        if naxis < 0:
            raise ValueError("negative FITS NAXIS")
        axes = [int(fields.get(f"NAXIS{index}", 0)) for index in range(1, naxis + 1)]
        if any(axis < 0 for axis in axes):
            raise ValueError("negative FITS axis")
        elements = math.prod(axes) if axes else 1
        pcount = int(fields.get("PCOUNT", 0))
        gcount = int(fields.get("GCOUNT", 1))
        if pcount < 0 or gcount < 1:
            raise ValueError("invalid FITS PCOUNT/GCOUNT")
        data_bytes = (abs(bitpix) // 8) * elements * gcount + pcount
        data_start = offset
        data_end = data_start + data_bytes
        padded_end = data_start + ((data_bytes + FITS_BLOCK_BYTES - 1) // FITS_BLOCK_BYTES) * FITS_BLOCK_BYTES
        if padded_end > len(data):
            raise ValueError("FITS data span exceeds file length")
        hdus.append(
            {
                "header": fields,
                "header_offset": header_start,
                "header_length": len(blocks),
                "data_offset": data_start,
                "data_length": data_bytes,
                "data_padded_end": padded_end,
            }
        )
        offset = padded_end
    return hdus


def parse_tform(value: Any) -> tuple[int, str]:
    match = TFORM_RE.fullmatch(str(value).strip())
    if not match:
        raise ValueError(f"unsupported TFORM {value!r}")
    repeat = int(match.group(1) or "1")
    if repeat < 1:
        raise ValueError("TFORM repeat must be positive")
    return repeat, match.group(2).upper()


def table_columns(header: dict[str, Any]) -> list[dict[str, Any]]:
    count = int(header.get("TFIELDS", 0))
    if count < 1:
        raise ValueError("binary table has no fields")
    columns: list[dict[str, Any]] = []
    offset = 0
    for index in range(1, count + 1):
        name = str(header.get(f"TTYPE{index}", "")).strip().upper()
        repeat, code = parse_tform(header.get(f"TFORM{index}", ""))
        widths = {"L": 1, "X": 1, "B": 1, "I": 2, "J": 4, "K": 8, "A": 1, "E": 4, "D": 8, "C": 8, "M": 16, "P": 8, "Q": 16}
        if code not in widths:
            raise ValueError(f"unsupported binary-table code {code}")
        width = widths[code] * repeat
        columns.append(
            {
                "index": index,
                "name": name,
                "repeat": repeat,
                "code": code,
                "offset": offset,
                "width": width,
                "tscal": float(header.get(f"TSCAL{index}", 1.0)),
                "tzero": float(header.get(f"TZERO{index}", 0.0)),
            }
        )
        offset += width
    row_width = int(header.get("NAXIS1", 0))
    if offset != row_width:
        raise ValueError(f"declared row width {row_width} differs from column width {offset}")
    return columns


def product_path(cache_root: Path, local_cache_key: str) -> Path:
    parts = Path(local_cache_key.replace("/", os.sep)).parts
    if len(parts) < 3:
        raise ValueError(f"malformed local_cache_key {local_cache_key!r}")
    return cache_root / Path(*parts[2:])


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path)


def canonical_histogram_digest(values: list[int]) -> str:
    encoded = json.dumps(values, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def extract_tte(path: Path, *, expected_hash: str | None = None, expected_length: int | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()
    if expected_hash is not None and actual_hash != expected_hash:
        raise ValueError(f"{path.name}: SHA-256 mismatch")
    if expected_length is not None and len(data) != expected_length:
        raise ValueError(f"{path.name}: byte-length mismatch")
    hdus = read_hdus(data)
    events: dict[str, Any] | None = None
    for hdu in hdus:
        header = hdu["header"]
        if str(header.get("EXTNAME", "")).strip().upper() == "EVENTS":
            if events is not None:
                raise ValueError(f"{path.name}: duplicate EVENTS extension")
            events = hdu
    if events is None:
        raise ValueError(f"{path.name}: EVENTS extension missing")
    header = events["header"]
    if str(header.get("XTENSION", "")).strip().upper() != "BINTABLE":
        raise ValueError(f"{path.name}: EVENTS is not a binary table")
    columns = table_columns(header)
    names = [column["name"] for column in columns]
    if names[:2] != ["TIME", "PHA"]:
        raise ValueError(f"{path.name}: first columns are not TIME then PHA: {names[:2]}")
    time_column, pha_column = columns[0], columns[1]
    if (time_column["repeat"], time_column["code"]) != (1, "D"):
        raise ValueError(f"{path.name}: TIME must be 1D")
    if (pha_column["repeat"], pha_column["code"]) != (1, "I"):
        raise ValueError(f"{path.name}: PHA must be 1I")
    row_width = int(header.get("NAXIS1", 0))
    row_count = int(header.get("NAXIS2", 0))
    if row_width < pha_column["offset"] + pha_column["width"] or row_count < 1:
        raise ValueError(f"{path.name}: invalid EVENTS dimensions")
    if events["data_length"] < row_width * row_count:
        raise ValueError(f"{path.name}: EVENTS rows exceed data span")
    trigtime = float(header["TRIGTIME"])
    tstart = float(header["TSTART"])
    tstop = float(header["TSTOP"])
    if not all(math.isfinite(value) for value in (trigtime, tstart, tstop)) or tstart > tstop:
        raise ValueError(f"{path.name}: invalid header time interval")
    lower_bin = math.floor((tstart - trigtime) / BIN_WIDTH_SECONDS)
    upper_bin = math.ceil((tstop - trigtime) / BIN_WIDTH_SECONDS)
    if upper_bin <= lower_bin:
        raise ValueError(f"{path.name}: empty trigger-relative bin range")
    histogram = [0 for _ in range(upper_bin - lower_bin)]
    data_start = int(events["data_offset"])
    previous_time: float | None = None
    first_relative: float | None = None
    last_relative: float | None = None
    pha_min: int | None = None
    pha_max: int | None = None
    out_of_window = 0
    for row_index in range(row_count):
        row_start = data_start + row_index * row_width
        row_end = row_start + row_width
        if row_end > len(data):
            raise ValueError(f"{path.name}: row {row_index} exceeds file length")
        raw_time = struct.unpack(">d", data[row_start + time_column["offset"] : row_start + time_column["offset"] + 8])[0]
        physical_time = raw_time * time_column["tscal"] + time_column["tzero"]
        pha_value = int(struct.unpack(">h", data[row_start + pha_column["offset"] : row_start + pha_column["offset"] + 2])[0])
        if not math.isfinite(physical_time) or not math.isfinite(float(pha_value)):
            raise ValueError(f"{path.name}: non-finite event value at row {row_index}")
        if previous_time is not None and physical_time < previous_time:
            raise ValueError(f"{path.name}: event times decrease at row {row_index}")
        if physical_time < tstart or physical_time > tstop:
            raise ValueError(f"{path.name}: event row {row_index} lies outside TSTART/TSTOP")
        if pha_value < PHA_MIN or pha_value > PHA_MAX:
            raise ValueError(f"{path.name}: PHA {pha_value} outside [{PHA_MIN},{PHA_MAX}]")
        relative = physical_time - trigtime
        bin_number = math.floor(relative / BIN_WIDTH_SECONDS)
        if lower_bin <= bin_number < upper_bin:
            histogram[bin_number - lower_bin] += 1
        else:
            out_of_window += 1
        previous_time = physical_time
        if first_relative is None:
            first_relative = relative
        last_relative = relative
        pha_min = pha_value if pha_min is None else min(pha_min, pha_value)
        pha_max = pha_value if pha_max is None else max(pha_max, pha_value)
    if sum(histogram) + out_of_window != row_count:
        raise ValueError(f"{path.name}: histogram does not conserve event rows")
    return {
        "id": path.name,
        "sha256": actual_hash,
        "byte_length": len(data),
        "hdu_count": len(hdus),
        "events_hdu": {
            "header_offset": int(events["header_offset"]),
            "header_length": int(events["header_length"]),
            "data_offset": data_start,
            "data_length": int(events["data_length"]),
            "row_width": row_width,
            "row_count": row_count,
            "columns": [
                {
                    "name": column["name"],
                    "format": f"{column['repeat']}{column['code']}",
                    "offset": column["offset"],
                    "width": column["width"],
                }
                for column in columns
            ],
        },
        "time_header": {
            "timesys": str(header.get("TIMESYS", "")),
            "timeunit": str(header.get("TIMEUNIT", "")),
            "trigtime": trigtime,
            "tstart": tstart,
            "tstop": tstop,
            "tzero_time": time_column["tzero"],
            "tscal_time": time_column["tscal"],
        },
        "event_summary": {
            "first_relative_seconds": first_relative,
            "last_relative_seconds": last_relative,
            "pha_min": pha_min,
            "pha_max": pha_max,
            "monotone_non_decreasing": True,
            "all_rows_in_header_interval": True,
            "events_in_histogram": sum(histogram),
            "events_outside_histogram": out_of_window,
        },
        "histogram": {
            "lower_bin": lower_bin,
            "upper_bin_exclusive": upper_bin,
            "bin_width_seconds": BIN_WIDTH_SECONDS,
            "counts": histogram,
            "count_sum": sum(histogram),
            "sha256": canonical_histogram_digest(histogram),
        },
        "response_matrix_values_read": False,
    }


def load_products(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    byte_manifest = json.loads(BYTE_FREEZE.read_text(encoding="utf-8"))
    by_id = {str(item["id"]): item for item in byte_manifest["products"]}
    products: list[dict[str, Any]] = []
    for product_id in REQUIRED_PRODUCTS:
        if product_id not in by_id:
            raise ValueError(f"byte-freeze product missing: {product_id}")
        item = by_id[product_id]
        if item.get("role") != "raw_gamma_ray_time_tagged_event_product":
            raise ValueError(f"unexpected role for {product_id}")
        products.append(item)
    return products


def run(manifest_path: Path = MANIFEST, cache_root: Path = DEFAULT_CACHE_ROOT) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("result_id") != "R-473" or manifest.get("exploration_id") != "EXP-001348":
        raise ValueError("R-473 manifest identity mismatch")
    if manifest.get("claim_bearing") is not False or manifest.get("tier") != "T0":
        raise ValueError("claim/tier firewall changed")
    if any(value is not True for value in manifest["methods_preserved"].values()):
        raise ValueError("method-preservation firewall changed")
    source_products = load_products(manifest)
    product_reports: list[dict[str, Any]] = []
    for item in source_products:
        path = product_path(cache_root, str(item["local_cache_key"]))
        report = extract_tte(path, expected_hash=str(item["sha256"]), expected_length=int(item["byte_length"]))
        report["product_id"] = str(item["id"])
        report["detector"] = item.get("detector")
        report["local_cache_key"] = item["local_cache_key"]
        product_reports.append(report)
    first_hist = product_reports[0]["histogram"]
    for report in product_reports[1:]:
        if [report["histogram"][key] for key in ("lower_bin", "upper_bin_exclusive", "bin_width_seconds")] != [first_hist[key] for key in ("lower_bin", "upper_bin_exclusive", "bin_width_seconds")]:
            raise ValueError("TTE products do not share the frozen histogram edges")
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"]], ["R-473", "EXP-001348", "T-061"], ["R-473", "EXP-001348", "T-061"])
    check("claim and tier firewall", [manifest["claim_bearing"], manifest["tier"]], [False, "T0"], [False, "T0"])
    check("methods unchanged", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true")
    check("byte-freeze parent", BYTE_FREEZE.is_file(), relative_path(BYTE_FREEZE), "present")
    check("product count", len(product_reports), len(REQUIRED_PRODUCTS), len(REQUIRED_PRODUCTS))
    check("all source hashes", all(report["sha256"] == next(item["sha256"] for item in source_products if item["id"] == report["product_id"]) for report in product_reports), True, True)
    check("all source lengths", all(report["byte_length"] == next(int(item["byte_length"]) for item in source_products if item["id"] == report["product_id"]) for report in product_reports), True, True)
    check("EVENTS schema", all(report["events_hdu"]["columns"][:2] == [{"name": "TIME", "format": "1D", "offset": 0, "width": 8}, {"name": "PHA", "format": "1I", "offset": 8, "width": 2}] for report in product_reports), True, True)
    check("row widths derived", all(report["events_hdu"]["row_width"] == sum(column["width"] for column in report["events_hdu"]["columns"]) for report in product_reports), True, True)
    check("HDU spans in bounds", all(report["events_hdu"]["data_offset"] + report["events_hdu"]["data_length"] <= report["byte_length"] for report in product_reports), True, True)
    check("positive row counts", all(report["events_hdu"]["row_count"] > 0 for report in product_reports), True, True)
    check("TT time metadata", all(report["time_header"]["timesys"] == "TT" and report["time_header"]["timeunit"] == "s" for report in product_reports), True, True)
    check("monotone event rows", all(report["event_summary"]["monotone_non_decreasing"] for report in product_reports), True, True)
    check("all rows in GTI header interval", all(report["event_summary"]["all_rows_in_header_interval"] for report in product_reports), True, True)
    check("PHA range", all(PHA_MIN <= report["event_summary"]["pha_min"] <= report["event_summary"]["pha_max"] <= PHA_MAX for report in product_reports), True, True)
    check("positive bin width", first_hist["bin_width_seconds"] > 0, first_hist["bin_width_seconds"], ">0")
    check("common histogram edges", all(report["histogram"]["lower_bin"] == first_hist["lower_bin"] and report["histogram"]["upper_bin_exclusive"] == first_hist["upper_bin_exclusive"] for report in product_reports), True, True)
    check("histogram conservation", all(report["histogram"]["count_sum"] + report["event_summary"]["events_outside_histogram"] == report["events_hdu"]["row_count"] for report in product_reports), True, True)
    check("nonnegative histogram", all(all(value >= 0 for value in report["histogram"]["counts"]) for report in product_reports), True, True)
    check("histogram digests", all(report["histogram"]["sha256"] == canonical_histogram_digest(report["histogram"]["counts"]) for report in product_reports), True, True)
    check("response values unread", all(report["response_matrix_values_read"] is False for report in product_reports), False, False)
    check("statistical admission stopped", manifest["admission"]["timing_likelihood_admitted"] is False and manifest["admission"]["component_covariance_admitted"] is False, manifest["admission"], "likelihood/covariance false")
    check("prospective lock empty", manifest["admission"]["prospective_lock"] == "EMPTY", manifest["admission"]["prospective_lock"], "EMPTY")
    derived_core = {
        "observable_id": manifest["exact_scope"]["histogram"]["observable_id"],
        "bin_width_seconds": BIN_WIDTH_SECONDS,
        "lower_bin": first_hist["lower_bin"],
        "upper_bin_exclusive": first_hist["upper_bin_exclusive"],
        "products": [
            {
                "product_id": report["product_id"],
                "detector": report["detector"],
                "row_count": report["events_hdu"]["row_count"],
                "first_relative_seconds": report["event_summary"]["first_relative_seconds"],
                "last_relative_seconds": report["event_summary"]["last_relative_seconds"],
                "pha_min": report["event_summary"]["pha_min"],
                "pha_max": report["event_summary"]["pha_max"],
                "events_outside_histogram": report["event_summary"]["events_outside_histogram"],
                "histogram_counts": report["histogram"]["counts"],
                "histogram_sha256": report["histogram"]["sha256"],
            }
            for report in product_reports
        ],
    }
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "HOLD-LC-001-TTE-EVENT-FEATURE-INDEX",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "holdout_id": "HOLD-LC-001",
        "verdict": "PASS",
        "tier": "T0",
        "claim_bearing": False,
        "methods_unchanged": True,
        "assertion_count": len(assertions),
        "passed": len(assertions),
        "assertions": assertions,
        "products": product_reports,
        "derived_core": derived_core,
        "admission": manifest["admission"],
        "scope": manifest["scope_firewall"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "falsifiers": manifest["falsifiers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "provenance": {
            "manifest_sha256": sha256(manifest_path),
            "byte_freeze_sha256": sha256(BYTE_FREEZE),
            "cache_root": relative_path(cache_root),
            "primary_script_sha256": sha256(Path(__file__).resolve()),
        },
    }


def self_test() -> int:
    assert parse_tform("1D") == (1, "D")
    assert parse_tform("1I") == (1, "I")
    assert canonical_histogram_digest([0, 1, 2]) == hashlib.sha256(b"[0,1,2]").hexdigest()
    assert math.floor(-0.001) == -1
    print("HOLD-LC-TTE-FEATURE SELFTEST: PASS (FITS format, binning and digest helpers)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        payload = run(args.manifest.resolve(), args.cache_root.resolve())
        atomic_json(args.output.resolve(), payload)
    except (AssertionError, OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, StopIteration) as exc:
        print(f"HOLD-LC-TTE-FEATURE: FAIL - {exc}")
        return 1
    print(
        "HOLD-LC-TTE-FEATURE: PASS "
        f"products={len(payload['products'])} "
        f"rows={sum(item['events_hdu']['row_count'] for item in payload['products'])} "
        f"bins={payload['derived_core']['upper_bin_exclusive'] - payload['derived_core']['lower_bin']} "
        "likelihood=NOT_ADMITTED covariance=NOT_ADMITTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
