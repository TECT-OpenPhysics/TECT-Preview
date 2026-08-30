#!/usr/bin/env python3
"""Audit hash-frozen event-day Fermi owner-artifact candidates.

The audit is deliberately additive.  It verifies exact bytes and reads FITS
headers/table declarations for the event-day position/attitude and spectral
history products.  It never reads table rows, constructs a detector-to-
geocenter conversion, estimates uncertainty, or admits a timing likelihood.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "strategy" / "hold-lc-001-owner-artifact-byte-freeze-v0.1.json"
DEFAULT_OUTPUT = REPO / "strategy" / "hold-lc-001-owner-artifact-audit-v0.1.json"
DEFAULT_CACHE_ROOT = REPO / "internal" / "source-cache" / "HOLD-LC-001" / "2026-08-30"
FITS_BLOCK_BYTES = 2880
FITS_CARD_BYTES = 80
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?$")

POSITION_ROLE = "position_attitude_history_owner_candidate"
SPECTRAL_ROLE = "spectral_gain_resolution_history_owner_candidate"

POSITION_COLUMNS = (
    "SCLK_UTC",
    "QSJ_1",
    "QSJ_2",
    "QSJ_3",
    "QSJ_4",
    "WSJ_1",
    "WSJ_2",
    "WSJ_3",
    "POS_X",
    "POS_Y",
)
SPECTRAL_COLUMNS = (
    "LINECENT",
    "LINE_WID",
    "LINE_AMP",
    "ERR_CENT",
    "ERR_WID",
    "ERR_AMP",
    "EN_RES",
    "START",
    "STOP",
    "NUM_REC",
)
COVERAGE_KEYS = ("DATE-OBS", "DATE-END", "TSTART", "TSTOP", "TIMESYS", "TIMEUNIT")


def atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    fd, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256_and_size(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


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
            return number if not isinstance(number, float) or math.isfinite(number) else number
        except ValueError:
            pass
    return value


def parse_header_cards(block: bytes) -> tuple[dict[str, Any], bool]:
    fields: dict[str, Any] = {}
    ended = False
    if len(block) % FITS_CARD_BYTES:
        raise ValueError("FITS header block is not a multiple of 80 bytes")
    for offset in range(0, len(block), FITS_CARD_BYTES):
        card = block[offset : offset + FITS_CARD_BYTES].decode("ascii", errors="replace")
        key = card[:8].strip()
        if key == "END":
            ended = True
            break
        if key and card[8:10] == "= ":
            raw = card[10:80]
            in_quote = False
            value_end = len(raw)
            for index, character in enumerate(raw):
                if character == "'":
                    in_quote = not in_quote
                elif character == "/" and not in_quote:
                    value_end = index
                    break
            fields[key] = parse_scalar(raw[:value_end])
    return fields, ended


def parse_fits_headers(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if len(data) % FITS_BLOCK_BYTES:
        raise ValueError(f"{path}: FITS byte length is not block aligned")
    offset = 0
    headers: list[dict[str, Any]] = []
    while offset < len(data):
        start = offset
        cards = bytearray()
        ended = False
        while offset < len(data):
            block = data[offset : offset + FITS_BLOCK_BYTES]
            if len(block) != FITS_BLOCK_BYTES:
                raise ValueError(f"{path}: truncated FITS header at byte {offset}")
            cards.extend(block)
            offset += FITS_BLOCK_BYTES
            _, ended = parse_header_cards(block)
            if ended:
                break
        if not ended:
            raise ValueError(f"{path}: FITS END card missing")
        fields, _ = parse_header_cards(bytes(cards))
        bitpix = int(fields.get("BITPIX", 8))
        naxis = int(fields.get("NAXIS", 0))
        axes = [int(fields.get(f"NAXIS{index}", 0)) for index in range(1, naxis + 1)]
        elements = math.prod(axes) if naxis else 0
        pcount = int(fields.get("PCOUNT", 0))
        gcount = int(fields.get("GCOUNT", 1))
        data_bytes = (abs(bitpix) // 8) * elements * gcount + pcount
        padded = ((data_bytes + FITS_BLOCK_BYTES - 1) // FITS_BLOCK_BYTES) * FITS_BLOCK_BYTES
        if offset + padded > len(data):
            raise ValueError(f"{path}: FITS data exceeds file at byte {offset}")
        offset += padded
        fields["_header_byte_offset"] = start
        fields["_header_byte_length"] = len(cards)
        fields["_data_byte_length"] = data_bytes
        headers.append(fields)
    return headers


def product_path(cache_root: Path, local_cache_key: str) -> Path:
    relative = Path(local_cache_key.replace("/", os.sep))
    parts = relative.parts
    if len(parts) < 3:
        raise ValueError(f"malformed local_cache_key: {local_cache_key}")
    return cache_root / Path(*parts[2:])


def load_product(manifest: dict[str, Any], product_id: str) -> dict[str, Any]:
    for product in manifest.get("products", []):
        if product.get("id") == product_id:
            return product
    raise KeyError(f"product not found: {product_id}")


def table_columns(header: dict[str, Any]) -> list[dict[str, Any]]:
    count = int(header.get("TFIELDS", 0))
    columns: list[dict[str, Any]] = []
    for index in range(1, count + 1):
        columns.append(
            {
                "index": index,
                "name": header.get(f"TTYPE{index}"),
                "format": header.get(f"TFORM{index}"),
                "unit": header.get(f"TUNIT{index}"),
            }
        )
    return columns


def hdu_summary(index: int, header: dict[str, Any]) -> dict[str, Any]:
    selected_keys = (
        "XTENSION",
        "EXTNAME",
        "BITPIX",
        "NAXIS",
        "NAXIS1",
        "NAXIS2",
        "PCOUNT",
        "GCOUNT",
        "TFIELDS",
        "DATE-OBS",
        "DATE-END",
        "MJDREFI",
        "MJDREFF",
        "TSTART",
        "TSTOP",
        "TIMESYS",
        "TIMEUNIT",
        "DETNAM",
        "CREATOR",
        "FILENAME",
    )
    return {
        "hdu_index": index,
        "header_byte_offset": header["_header_byte_offset"],
        "header_byte_length": header["_header_byte_length"],
        "data_byte_length": header["_data_byte_length"],
        "fields": {key: header[key] for key in selected_keys if key in header},
        "table_columns": table_columns(header),
    }


def first_value(headers: list[dict[str, Any]], key: str) -> Any:
    for header in headers:
        if key in header:
            return header[key]
    return None


def audit_schema(role: str, summaries: list[dict[str, Any]]) -> dict[str, Any]:
    expected_extension = "GLAST POS HIST" if role == POSITION_ROLE else "GBM SPEC HIST"
    expected_columns = POSITION_COLUMNS if role == POSITION_ROLE else SPECTRAL_COLUMNS
    table_hdus = [item for item in summaries if item["fields"].get("XTENSION") == "BINTABLE"]
    matching = [item for item in table_hdus if item["fields"].get("EXTNAME") == expected_extension]
    names = {column["name"] for item in matching for column in item["table_columns"]}
    coverage = {key: first_value([item["fields"] for item in summaries], key) for key in COVERAGE_KEYS}
    coverage_present = all(value is not None for value in coverage.values())
    row_count_present = any(int(item["fields"].get("NAXIS2", 0)) > 0 for item in matching)
    missing_columns = [column for column in expected_columns if column not in names]
    schema_match = bool(matching) and not missing_columns and coverage_present and row_count_present
    return {
        "expected_extension": expected_extension,
        "matching_table_hdu_indices": [item["hdu_index"] for item in matching],
        "declared_columns": sorted(names),
        "required_columns": list(expected_columns),
        "missing_required_columns": missing_columns,
        "coverage": coverage,
        "coverage_metadata_present": coverage_present,
        "nonempty_table_rows_declared": row_count_present,
        "schema_match": schema_match,
    }


def audit_product(product: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    path = product_path(cache_root, str(product["local_cache_key"]))
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_hash, actual_size = sha256_and_size(path)
    expected_hash = str(product["sha256"])
    expected_size = int(product["byte_length"])
    record: dict[str, Any] = {
        "id": product["id"],
        "role": product["role"],
        "dataset_family": product.get("dataset_family"),
        "detector": product.get("detector"),
        "local_cache_key": product["local_cache_key"],
        "recorded_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "recorded_byte_length": expected_size,
        "actual_byte_length": actual_size,
        "sha256_match": actual_hash == expected_hash,
        "byte_length_match": actual_size == expected_size,
        "header_audit_performed": False,
        "hdu_count": 0,
        "hdus": [],
        "schema": None,
    }
    if record["sha256_match"] and record["byte_length_match"]:
        headers = parse_fits_headers(path)
        summaries = [hdu_summary(index, header) for index, header in enumerate(headers)]
        record["header_audit_performed"] = True
        record["hdu_count"] = len(summaries)
        record["hdus"] = summaries
        record["schema"] = audit_schema(str(product["role"]), summaries)
    return record


def audit(manifest_path: Path, cache_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_hash, manifest_size = sha256_and_size(manifest_path)
    try:
        manifest_display = str(manifest_path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        manifest_display = str(manifest_path)
    products = [audit_product(product, cache_root) for product in manifest.get("products", [])]
    all_hashes = all(item["sha256_match"] and item["byte_length_match"] for item in products)
    all_schema = all(item["schema"] and item["schema"]["schema_match"] for item in products)
    position_items = [item for item in products if item["role"] == POSITION_ROLE]
    spectral_items = [item for item in products if item["role"] == SPECTRAL_ROLE]
    coverage_items = [item for item in products if item["schema"] and item["schema"]["coverage_metadata_present"]]
    return {
        "schema": "tect/observation-owner-artifact-audit/0.1",
        "id": "HOLD-LC-001-OWNER-ARTIFACT-AUDIT-v0.1",
        "version": "0.1.0",
        "task_id": "T-061",
        "holdout_id": "HOLD-LC-001",
        "claim_bearing": False,
        "status": "OWNER_BYTES_AND_SCHEMA_PRESENT_STATISTICAL_OWNER_UNADMITTED",
        "parent_owner_manifest": manifest_display,
        "parent_owner_manifest_sha256": manifest_hash,
        "parent_owner_manifest_byte_length": manifest_size,
        "scope": {
            "products": [item["id"] for item in products],
            "roles": {
                "position_attitude": [item["id"] for item in position_items],
                "spectral_gain_resolution": [item["id"] for item in spectral_items],
            },
            "extraction": "Exact SHA-256/byte-length verification plus FITS scalar headers and table declarations; no table rows, event values, attitude values, calibration values, timing fit or score.",
            "data_role": "CALIBRATION",
            "finite_scope": "Finite owner-provenance/schema intake only; no continuum, physical identity or prospective validation claim.",
        },
        "products": products,
        "available_metadata": {
            "owner_product_sha256_and_byte_length": all_hashes,
            "position_attitude_schema": bool(position_items) and all(
                item["schema"] and item["schema"]["schema_match"] for item in position_items
            ),
            "spectral_gain_resolution_schema": bool(spectral_items) and all(
                item["schema"] and item["schema"]["schema_match"] for item in spectral_items
            ),
            "event_day_coverage_metadata": len(coverage_items) == len(products),
            "time_standard_fields_present": bool(coverage_items) and all(
                item["schema"]["coverage"].get("TIMESYS") == "TT"
                and item["schema"]["coverage"].get("TIMEUNIT") == "s"
                for item in coverage_items
            ),
            "detector_to_geocenter_conversion": False,
            "calibration_validity_interpolation": False,
            "source_owned_timing_likelihood": False,
            "component_or_shared_covariance": False,
            "intrinsic_emission_nuisance_law": False,
            "complete_f_reg_f_lim_f_eff_f_obs": False,
        },
        "interpretation": {
            "position_attitude": "The event-day GLAST POS HIST table declares spacecraft position/attitude history columns and coverage metadata. Header presence does not itself provide the detector-to-geocenter conversion, interpolation rule or timing uncertainty.",
            "spectral_history": "The event-day GBM SPEC HIST tables declare line, energy-resolution and interval fields for N0 and B0. Header presence does not itself establish calibration validity, response linkage or a shared uncertainty model.",
            "admission": "These bytes refine the physical-owner request only. Candidate scoring and the four estimator-map stages remain stopped until the conversion, uncertainty, likelihood and nuisance owners are frozen.",
        },
        "checks": {
            "all_selected_product_hashes_match": all_hashes,
            "all_role_schemas_match": all_schema,
            "header_only_no_table_rows_read": True,
            "candidate_scoring": "STOPPED",
            "prospective_lock": "EMPTY",
        },
        "assumptions": [
            "The owner-artifact byte-freeze manifest remains authoritative for product identity, roles, hashes and locators.",
            "FITS scalar headers and table declarations are descriptive provenance; no table value is interpreted by this audit.",
            "The event-day position/attitude and spectral-history products are owner candidates, not a complete timing or calibration implementation.",
            "The existing T-054 forward method, T-059 inverse method, owner order and promotion firewalls remain controlling.",
        ],
        "missing_assumptions": [
            "Source-owned detector-to-geocenter timing conversion and uncertainty for each instrument and time window.",
            "Calibration release validity intervals, interpolation rules and an explicit link from spectral history to the selected response products.",
            "Frozen detector, energy, background and temporal windows with selection semantics.",
            "A source-owned joint timing likelihood or component/shared covariance including calibration and intrinsic-emission nuisance terms.",
            "A complete candidate-neutral F_reg/F_lim/F_eff/F_obs map and immutable scorer.",
            "A prospective holdout not used for source selection, calibration choice or estimator design.",
        ],
        "evidence_level": "T0 exact public-product byte freeze and FITS header/schema intake; no model test",
        "next_action": "Use the frozen owner-candidate metadata to request the matching validity, conversion and uncertainty artefacts. Independently reproduce F_reg only after the required physical-owner and proof-owner fields are frozen; keep scoring stopped.",
        "non_claims": [
            "This audit does not admit a detector-to-geocenter conversion, timing likelihood, covariance, calibration validity law, nuisance law, candidate, map, score or prediction.",
            "Position/attitude and spectral-history headers do not by themselves identify microscopic dynamics or a causal propagation law.",
            "No Pre-A, C6, A13, Sector-A, QFT, Yang-Mills, gravity, continuum, physical-vacuum, cosmic-origin, theory-of-everything or mass-gap claim follows.",
            "The established T-054 forward and T-059 inverse methods are unchanged; this is additive owner-artifact intake only.",
        ],
    }


def make_card(keyword: str, value: str | None = None) -> bytes:
    if keyword == "END":
        line = "END"
    elif value is None:
        line = keyword
    else:
        line = f"{keyword:<8}= {value}"
    return line.ljust(FITS_CARD_BYTES)[:FITS_CARD_BYTES].encode("ascii")


def self_test() -> int:
    primary = bytearray(FITS_BLOCK_BYTES)
    for index, card in enumerate(
        [
            make_card("SIMPLE", "                    T / standard"),
            make_card("BITPIX", "                    8 / bits"),
            make_card("NAXIS", "                    0 / no axes"),
            make_card("CREATOR", "'a/b' / slash inside string"),
            make_card("END"),
        ]
    ):
        primary[index * FITS_CARD_BYTES : (index + 1) * FITS_CARD_BYTES] = card
    extension = bytearray(FITS_BLOCK_BYTES)
    extension_cards = [
        make_card("XTENSION", "'BINTABLE' / table"),
        make_card("BITPIX", "                    8"),
        make_card("NAXIS", "                    2"),
        make_card("NAXIS1", "                    1"),
        make_card("NAXIS2", "                    1"),
        make_card("PCOUNT", "                    0"),
        make_card("GCOUNT", "                    1"),
        make_card("TFIELDS", "                    2"),
        make_card("EXTNAME", "'GLAST POS HIST'"),
        make_card("TTYPE1", "'SCLK_UTC'"),
        make_card("TTYPE2", "'POS_X'"),
        make_card("DATE-OBS", "'2017-08-16T23:59:00'"),
        make_card("DATE-END", "'2017-08-18T00:00:59'"),
        make_card("TSTART", "                    1.0"),
        make_card("TSTOP", "                    2.0"),
        make_card("TIMESYS", "'TT'"),
        make_card("TIMEUNIT", "'s'"),
        make_card("END"),
    ]
    for index, card in enumerate(extension_cards):
        extension[index * FITS_CARD_BYTES : (index + 1) * FITS_CARD_BYTES] = card
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "synthetic.fit"
        path.write_bytes(bytes(primary) + bytes(extension) + bytes(FITS_BLOCK_BYTES))
        headers = parse_fits_headers(path)
    assert len(headers) == 2
    assert headers[0]["_data_byte_length"] == 0
    assert headers[0]["CREATOR"] == "a/b"
    summary = hdu_summary(1, headers[1])
    result = audit_schema(POSITION_ROLE, [hdu_summary(0, headers[0]), summary])
    assert result["matching_table_hdu_indices"] == [1]
    assert result["coverage_metadata_present"]
    assert not result["schema_match"]
    print("HOLD-LC-OWNER SELFTEST: PASS (zero-axis FITS and quote-aware header rules)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        report = audit(args.manifest, args.cache_root)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"HOLD-LC-OWNER: FAIL - {exc}")
        return 1
    if not report["checks"]["all_selected_product_hashes_match"]:
        mismatches = [item["id"] for item in report["products"] if not item["sha256_match"] or not item["byte_length_match"]]
        print(f"HOLD-LC-OWNER: FAIL - hash/length mismatch: {','.join(mismatches)}")
        return 1
    if not report["checks"]["all_role_schemas_match"]:
        failures = [item["id"] for item in report["products"] if not item["schema"] or not item["schema"]["schema_match"]]
        print(f"HOLD-LC-OWNER: FAIL - schema mismatch: {','.join(failures)}")
        return 1
    atomic_json_write(args.output, report)
    print(
        "HOLD-LC-OWNER: PASS "
        f"products={len(report['products'])} "
        f"position={len([item for item in report['products'] if item['role'] == POSITION_ROLE])} "
        f"spectral={len([item for item in report['products'] if item['role'] == SPECTRAL_ROLE])} "
        f"time_standard={report['available_metadata']['time_standard_fields_present']} "
        "likelihood=NOT_ADMITTED covariance=NOT_ADMITTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())