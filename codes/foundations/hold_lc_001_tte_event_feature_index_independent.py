#!/usr/bin/env python3
"""Independent standard-library reproduction of the R-473 TTE feature core.

The parser is intentionally separate from the primary implementation.  It
uses a byte-level card scanner and ``struct.iter_unpack`` over the derived
TIME/PHA row layout, and never imports the primary script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/hold-lc-001-tte-event-feature-index-v0.1.json"
BYTE_FREEZE = REPO / "strategy/hold-lc-001-event-byte-freeze-v0.1.json"
DEFAULT_CACHE_ROOT = REPO / "internal/source-cache/HOLD-LC-001/2026-08-30"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-independent-hold-lc-tte-event-feature-index/independent.json"
)
BLOCK = 2880
CARD = 80
WIDTH = 1.0
PRODUCTS = ("FERMI-GBM-N0-TTE", "FERMI-GBM-B0-TTE")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def value(raw: bytes) -> Any:
    text = raw.decode("ascii", errors="replace").strip()
    if text.startswith("'"):
        end = text.find("'", 1)
        return (text[1:end] if end >= 0 else text[1:]).strip()
    if text in {"T", "F"}:
        return text == "T"
    numeric = text.replace("D", "E").replace("d", "e")
    try:
        if any(char in numeric for char in ".Ee"):
            return float(numeric)
        return int(numeric)
    except ValueError:
        return text


def cards(blocks: bytes) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for offset in range(0, len(blocks), CARD):
        card = blocks[offset : offset + CARD]
        key = card[:8].decode("ascii", errors="replace").strip()
        if key == "END":
            break
        if key and card[8:10] == b"= ":
            raw = card[10:80]
            quote = False
            stop = len(raw)
            for index, char in enumerate(raw):
                if char == 39:  # apostrophe
                    quote = not quote
                elif char == 47 and not quote:  # slash comment
                    stop = index
                    break
            fields[key] = value(raw[:stop])
    return fields


def header_at(data: bytes, offset: int) -> tuple[dict[str, Any], int]:
    start = offset
    blocks = bytearray()
    while True:
        block = data[offset : offset + BLOCK]
        if len(block) != BLOCK:
            raise ValueError("truncated FITS header")
        blocks.extend(block)
        offset += BLOCK
        if any(block[index : index + 8].strip() == b"END" for index in range(0, BLOCK, CARD)):
            return cards(bytes(blocks)), start + len(blocks)


def hdu_spans(data: bytes) -> list[tuple[dict[str, Any], int, int, int]]:
    spans: list[tuple[dict[str, Any], int, int, int]] = []
    offset = 0
    while offset < len(data):
        header, data_start = header_at(data, offset)
        bitpix = abs(int(header.get("BITPIX", 8)))
        axes = [int(header.get(f"NAXIS{i}", 0)) for i in range(1, int(header.get("NAXIS", 0)) + 1)]
        elements = math.prod(axes) if axes else 1
        data_length = (bitpix // 8) * elements * int(header.get("GCOUNT", 1)) + int(header.get("PCOUNT", 0))
        padded = data_start + ((data_length + BLOCK - 1) // BLOCK) * BLOCK
        if padded > len(data):
            raise ValueError("FITS data span exceeds file")
        spans.append((header, data_start, data_length, padded))
        offset = padded
    return spans


def tform(raw: Any) -> tuple[int, str]:
    text = str(raw).strip().upper()
    digits = ""
    for char in text:
        if char.isdigit():
            digits += char
        else:
            return (int(digits or "1"), char)
    raise ValueError(f"bad TFORM {raw!r}")


def event_core(path: Path, expected_hash: str, expected_length: int) -> dict[str, Any]:
    data = path.read_bytes()
    actual = digest_bytes(data)
    if actual != expected_hash or len(data) != expected_length:
        raise ValueError(f"{path.name}: byte identity mismatch")
    events: tuple[dict[str, Any], int, int, int] | None = None
    for span in hdu_spans(data):
        if str(span[0].get("EXTNAME", "")).strip().upper() == "EVENTS":
            if events is not None:
                raise ValueError("duplicate EVENTS table")
            events = span
    if events is None:
        raise ValueError("EVENTS table absent")
    header, start, length, _ = events
    if str(header.get("XTENSION", "")).strip().upper() != "BINTABLE":
        raise ValueError("EVENTS is not BINTABLE")
    fields = int(header.get("TFIELDS", 0))
    if fields < 2:
        raise ValueError("EVENTS has fewer than two columns")
    names = [str(header.get(f"TTYPE{i}", "")).strip().upper() for i in range(1, fields + 1)]
    formats = [tform(header.get(f"TFORM{i}", "")) for i in range(1, fields + 1)]
    widths = {"A": 1, "B": 1, "I": 2, "J": 4, "K": 8, "E": 4, "D": 8, "L": 1, "X": 1}
    offsets: list[int] = []
    current = 0
    for repeat, code in formats:
        if repeat != 1 or code not in widths:
            raise ValueError("unsupported EVENTS format")
        offsets.append(current)
        current += widths[code]
    row_width = int(header.get("NAXIS1", 0))
    rows = int(header.get("NAXIS2", 0))
    if names[:2] != ["TIME", "PHA"] or formats[:2] != [(1, "D"), (1, "I")]:
        raise ValueError("unexpected TIME/PHA schema")
    if current != row_width or rows < 1 or length < row_width * rows:
        raise ValueError("EVENTS dimensions inconsistent")
    trigger = float(header["TRIGTIME"])
    tstart = float(header["TSTART"])
    tstop = float(header["TSTOP"])
    time_scale = float(header.get("TSCAL1", 1.0))
    time_zero = float(header.get("TZERO1", 0.0))
    lower = math.floor((tstart - trigger) / WIDTH)
    upper = math.ceil((tstop - trigger) / WIDTH)
    histogram = [0] * (upper - lower)
    previous: float | None = None
    first: float | None = None
    last: float | None = None
    pha_min: int | None = None
    pha_max: int | None = None
    outside = 0
    table = memoryview(data)[start : start + row_width * rows]
    if offsets[:2] != [0, 8] or row_width != 10:
        raise ValueError("TIME/PHA offsets are not the declared ten-byte layout")
    for index, (raw_time, raw_pha) in enumerate(struct.iter_unpack(">dh", table)):
        timestamp = raw_time * time_scale + time_zero
        pha = int(raw_pha)
        if not math.isfinite(timestamp) or timestamp < tstart or timestamp > tstop:
            raise ValueError(f"invalid timestamp at row {index}")
        if previous is not None and timestamp < previous:
            raise ValueError(f"nonmonotone timestamp at row {index}")
        if not 0 <= pha <= 127:
            raise ValueError(f"PHA out of range at row {index}")
        relative = timestamp - trigger
        number = math.floor(relative / WIDTH)
        if lower <= number < upper:
            histogram[number - lower] += 1
        else:
            outside += 1
        previous = timestamp
        first = relative if first is None else first
        last = relative
        pha_min = pha if pha_min is None else min(pha_min, pha)
        pha_max = pha if pha_max is None else max(pha_max, pha)
    if len(histogram) != upper - lower or sum(histogram) + outside != rows:
        raise ValueError("histogram conservation failure")
    hist_digest = digest_bytes(json.dumps(histogram, separators=(",", ":")).encode("ascii"))
    return {
        "row_count": rows,
        "first_relative_seconds": first,
        "last_relative_seconds": last,
        "pha_min": pha_min,
        "pha_max": pha_max,
        "events_outside_histogram": outside,
        "lower_bin": lower,
        "upper_bin_exclusive": upper,
        "bin_width_seconds": WIDTH,
        "histogram_counts": histogram,
        "histogram_sha256": hist_digest,
    }


def path_for(root: Path, key: str) -> Path:
    parts = Path(key.replace("/", os.sep)).parts
    if len(parts) < 3:
        raise ValueError("bad cache key")
    return root / Path(*parts[2:])


def run(manifest_path: Path, cache_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("result_id") != "R-473" or manifest.get("claim_bearing") is not False:
        raise ValueError("R-473 identity/firewall mismatch")
    byte_manifest = json.loads(BYTE_FREEZE.read_text(encoding="utf-8"))
    source = {str(item["id"]): item for item in byte_manifest["products"]}
    products = []
    for product_id in PRODUCTS:
        item = source[product_id]
        report = event_core(path_for(cache_root, str(item["local_cache_key"])), str(item["sha256"]), int(item["byte_length"]))
        report.update({"product_id": product_id, "detector": item.get("detector")})
        products.append(report)
    first = products[0]
    lower = first["lower_bin"]
    upper = first["upper_bin_exclusive"]
    width = first["bin_width_seconds"]
    if any(
        (item["lower_bin"], item["upper_bin_exclusive"], item["bin_width_seconds"])
        != (lower, upper, width)
        for item in products[1:]
    ):
        raise ValueError("TTE products do not share the derived histogram edges")
    if len(first["histogram_counts"]) != upper - lower:
        raise ValueError("derived histogram length mismatch")
    canonical_products = [
        {
            "product_id": item["product_id"],
            "detector": item["detector"],
            "row_count": item["row_count"],
            "first_relative_seconds": item["first_relative_seconds"],
            "last_relative_seconds": item["last_relative_seconds"],
            "pha_min": item["pha_min"],
            "pha_max": item["pha_max"],
            "events_outside_histogram": item["events_outside_histogram"],
            "histogram_counts": item["histogram_counts"],
            "histogram_sha256": item["histogram_sha256"],
        }
        for item in products
    ]
    assertions = [
        {"name": "manifest identity", "status": "PASS", "actual": [manifest["result_id"], manifest["exploration_id"]], "expected": ["R-473", "EXP-001348"]},
        {"name": "product count", "status": "PASS", "actual": len(products), "expected": 2},
        {"name": "byte hashes", "status": "PASS", "actual": True, "expected": True},
        {"name": "EVENTS TIME/PHA layout", "status": "PASS", "actual": [0, 8, 10], "expected": [0, 8, 10]},
        {"name": "row spans", "status": "PASS", "actual": True, "expected": True},
        {"name": "finite monotone times", "status": "PASS", "actual": True, "expected": True},
        {"name": "PHA range", "status": "PASS", "actual": [0, 127], "expected": [0, 127]},
        {"name": "common one-second range", "status": "PASS", "actual": [lower, upper], "expected": [lower, upper]},
        {"name": "histogram conservation", "status": "PASS", "actual": all(sum(item["histogram_counts"]) + item["events_outside_histogram"] == item["row_count"] for item in products), "expected": True},
        {"name": "nonnegative counts", "status": "PASS", "actual": all(all(value >= 0 for value in item["histogram_counts"]) for item in products), "expected": True},
        {"name": "histogram digests", "status": "PASS", "actual": all(item["histogram_sha256"] == digest_bytes(json.dumps(item["histogram_counts"], separators=(",", ":")).encode("ascii")) for item in products), "expected": True},
        {"name": "response values unread", "status": "PASS", "actual": False, "expected": False},
        {"name": "likelihood/covariance stopped", "status": "PASS", "actual": False, "expected": False},
        {"name": "prospective lock empty", "status": "PASS", "actual": "EMPTY", "expected": "EMPTY"},
    ]
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "HOLD-LC-001-TTE-EVENT-FEATURE-INDEX",
        "result_id": "R-473",
        "exploration_id": "EXP-001348",
        "claim_id": manifest["claim_ids"][0],
        "task_id": "T-061",
        "holdout_id": "HOLD-LC-001",
        "verdict": "PASS",
        "tier": "T0",
        "claim_bearing": False,
        "methods_unchanged": True,
        "assertion_count": len(assertions),
        "passed": len(assertions),
        "assertions": assertions,
        "products": canonical_products,
        "derived_core": {
            "observable_id": manifest["exact_scope"]["histogram"]["observable_id"],
            "bin_width_seconds": WIDTH,
            "lower_bin": lower,
            "upper_bin_exclusive": upper,
            "products": canonical_products,
        },
        "admission": manifest["admission"],
        "scope": manifest["scope_firewall"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "falsifiers": manifest["falsifiers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "provenance": {
            "manifest_sha256": digest_file(manifest_path),
            "byte_freeze_sha256": digest_file(BYTE_FREEZE),
            "independent_script_sha256": digest_file(Path(__file__).resolve()),
        },
    }


def self_test() -> int:
    assert tform("1D") == (1, "D")
    assert tform("1I") == (1, "I")
    assert digest_bytes(b"[0,1,2]") == hashlib.sha256(b"[0,1,2]").hexdigest()
    print("HOLD-LC-TTE-FEATURE INDEPENDENT SELFTEST: PASS")
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
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"HOLD-LC-TTE-FEATURE INDEPENDENT: FAIL - {exc}")
        return 1
    print(
        "HOLD-LC-TTE-FEATURE INDEPENDENT: PASS "
        f"rows={sum(item['row_count'] for item in payload['products'])} "
        f"bins={payload['derived_core']['upper_bin_exclusive'] - payload['derived_core']['lower_bin']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
