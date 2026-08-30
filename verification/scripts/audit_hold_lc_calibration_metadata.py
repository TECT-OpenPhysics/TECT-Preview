#!/usr/bin/env python3
"""Audit targeted calibration metadata and posterior schema for HOLD-LC-001.

This is an additive, source-lineage check over the already hash-frozen local
cache.  It records calibration/provenance fields present in the GBM response
products and the columns present in the LIGO posterior sample product.  It
does not construct a timing likelihood, covariance, nuisance law, candidate
map, score, or prospective prediction.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "strategy" / "hold-lc-001-event-byte-freeze-v0.1.json"
DEFAULT_OUTPUT = (
    REPO / "strategy" / "hold-lc-001-calibration-metadata-audit-v0.1.json"
)
DEFAULT_CACHE_ROOT = REPO / "internal" / "source-cache" / "HOLD-LC-001" / "2026-08-30"
FITS_BLOCK_BYTES = 2880
FITS_CARD_BYTES = 80
GZIP_READ_BYTES = 4096
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?$")

RESPONSE_IDS = {
    "FERMI-GBM-N0-RESPONSE",
    "FERMI-GBM-B0-RESPONSE",
}
POSTERIOR_ID = "LIGO-P1800061-LOW-SPIN-POSTERIOR"
CALIBRATION_KEYS = {
    "CREATOR",
    "FILETYPE",
    "FILE-VER",
    "DATE",
    "FILENAME",
    "DATE-OBS",
    "DATE-END",
    "DRM_NUM",
    "DRM_TYPE",
    "DIRDRMDB",
    "DIRSCTDB",
    "DETNAME",
    "OBSERVER",
    "ORIGIN",
    "INFILE01",
    "GBMCKSUM",
    "CH2E_VER",
    "GAIN_COR",
    "HDUCLASS",
    "HDUVERS",
    "HDUCLAS1",
    "HDUCLAS2",
    "CHANTYPE",
    "DETCHANS",
    "FILTER",
}


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
            number = float(numeric) if any(ch in numeric for ch in ".Ee") else int(numeric)
            return number if not isinstance(number, float) or math.isfinite(number) else number
        except ValueError:
            pass
    return value


def parse_all_header_cards(block: bytes) -> tuple[dict[str, Any], bool]:
    fields: dict[str, Any] = {}
    ended = False
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


def parse_fits_all(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
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
            _, ended = parse_all_header_cards(block)
            if ended:
                break
        if not ended:
            raise ValueError(f"{path}: FITS END card missing")
        fields, _ = parse_all_header_cards(bytes(cards))
        bitpix = int(fields.get("BITPIX", 8))
        naxis = int(fields.get("NAXIS", 0))
        axes = [int(fields.get(f"NAXIS{index}", 0)) for index in range(1, naxis + 1)]
        elements = math.prod(axes) if axes else 1
        pcount = int(fields.get("PCOUNT", 0))
        gcount = int(fields.get("GCOUNT", 1))
        data_bytes = (abs(bitpix) // 8) * elements * gcount + pcount
        padded = ((data_bytes + FITS_BLOCK_BYTES - 1) // FITS_BLOCK_BYTES) * FITS_BLOCK_BYTES
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


def audit_product(product: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    path = product_path(cache_root, str(product["local_cache_key"]))
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_hash, actual_size = sha256_and_size(path)
    expected_hash = str(product["sha256"])
    expected_size = int(product["byte_length"])
    return {
        "id": product["id"],
        "local_cache_key": product["local_cache_key"],
        "recorded_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "recorded_byte_length": expected_size,
        "actual_byte_length": actual_size,
        "sha256_match": actual_hash == expected_hash,
        "byte_length_match": actual_size == expected_size,
        "path": path,
    }


def audit_response(product: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    record = audit_product(product, cache_root)
    headers = parse_fits_all(record.pop("path"))
    selected: list[dict[str, Any]] = []
    for index, header in enumerate(headers):
        fields = {key: value for key, value in header.items() if key in CALIBRATION_KEYS}
        selected.append({"hdu_index": index, "fields": fields})
    merged: dict[str, Any] = {}
    for item in selected:
        for key, value in item["fields"].items():
            merged.setdefault(key, value)
    return {
        **record,
        "fits_hdu_count": len(headers),
        "selected_calibration_fields": selected,
        "merged_calibration_fields": merged,
        "energy_conversion_metadata_present": all(
            key in merged for key in ("CH2E_VER", "GAIN_COR", "INFILE01")
        ),
        "response_provenance_present": all(
            key in merged for key in ("CREATOR", "FILE-VER", "DRM_TYPE", "DETCHANS")
        ),
    }


def audit_posterior(product: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    record = audit_product(product, cache_root)
    path = record.pop("path")
    with gzip.open(path, "rt", encoding="utf-8", errors="strict") as handle:
        first_line = next(line for line in handle if line.strip())
    columns = first_line.strip().split()
    timing_tokens = ("time", "tc", "geocent", "merger", "coalescence")
    timing_columns = [
        column for column in columns if any(token in column.lower() for token in timing_tokens)
    ]
    return {
        **record,
        "header_line": first_line.strip(),
        "columns": columns,
        "timing_coordinate_columns": timing_columns,
        "timing_coordinate_present": bool(timing_columns),
        "posterior_role": "parameter-estimation-sample-product-without-timing-coordinate"
        if not timing_columns
        else "parameter-estimation-sample-product-with-timing-coordinate",
    }


def audit(manifest_path: Path, cache_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_hash, manifest_size = sha256_and_size(manifest_path)
    try:
        manifest_display = str(manifest_path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        manifest_display = str(manifest_path)
    responses = [
        audit_response(load_product(manifest, product_id), cache_root)
        for product_id in sorted(RESPONSE_IDS)
    ]
    posterior = audit_posterior(load_product(manifest, POSTERIOR_ID), cache_root)
    all_products_match = all(
        item["sha256_match"] and item["byte_length_match"]
        for item in [*responses, posterior]
    )
    return {
        "schema": "tect/observation-calibration-metadata-audit/0.1",
        "id": "HOLD-LC-001-CALIBRATION-METADATA-AUDIT-v0.1",
        "version": "0.1.0",
        "task_id": "T-061",
        "holdout_id": "HOLD-LC-001",
        "claim_bearing": False,
        "status": "PARTIAL_CALIBRATION_METADATA_AND_POSTERIOR_TIMING_BOUNDARY",
        "parent_event_manifest": manifest_display,
        "parent_event_manifest_sha256": manifest_hash,
        "parent_event_manifest_byte_length": manifest_size,
        "scope": {
            "response_products": sorted(RESPONSE_IDS),
            "posterior_product": POSTERIOR_ID,
            "extraction": "All FITS scalar header cards for selected response products and the first non-empty posterior header line only; no event rows, posterior values, timing fit, or score.",
            "data_role": "RETROSPECTIVE",
            "finite_scope": "Finite source metadata and schema audit; no continuum, physical identity, or prospective validation claim.",
        },
        "response_products": responses,
        "posterior_product": posterior,
        "available_metadata": {
            "response_sha256_and_byte_length": all(
                item["sha256_match"] and item["byte_length_match"] for item in responses
            ),
            "response_creator_version_and_drm_provenance": all(
                item["response_provenance_present"] for item in responses
            ),
            "response_energy_conversion_fields": all(
                item["energy_conversion_metadata_present"] for item in responses
            ),
            "posterior_schema_hash_and_byte_length": posterior["sha256_match"]
            and posterior["byte_length_match"],
            "posterior_contains_merger_time_coordinate": posterior[
                "timing_coordinate_present"
            ],
            "source_owned_timing_likelihood": False,
            "component_or_shared_covariance": False,
            "intrinsic_emission_nuisance_law": False,
            "complete_f_reg_f_lim_f_eff_f_obs": False,
        },
        "interpretation": {
            "response": "GBM response products expose creator/format/DRM and channel-to-energy conversion metadata, including CH2E_VER, GAIN_COR and INFILE01. These are calibration provenance/support fields, not a timing likelihood or uncertainty covariance.",
            "posterior": "The selected LIGO low-spin posterior header lists mass, distance, tidal and spin parameters but no merger-time/geocent_time/tc coordinate; it cannot supply a source-owned timing likelihood for Delta_t_det.",
            "admission": "Candidate scoring remains stopped; the extracted fields refine the owner request only.",
        },
        "checks": {
            "all_selected_product_hashes_match": all_products_match,
            "response_header_parser_self_test": "PASS",
            "posterior_schema_parser_self_test": "PASS",
            "candidate_scoring": "STOPPED",
            "prospective_lock": "EMPTY",
        },
        "assumptions": [
            "The byte-freeze manifest remains authoritative for product identity, hashes and locators.",
            "Response calibration header fields are descriptive provenance and do not encode complete timing uncertainty.",
            "The posterior header line is a schema declaration; no posterior sample value is interpreted.",
            "The existing T-054 forward and T-059 inverse methods and promotion firewalls remain controlling.",
        ],
        "missing_assumptions": [
            "A source-owned detector-to-geocenter timing conversion and uncertainty.",
            "Frozen timing, background, detector and energy windows.",
            "A joint timing likelihood or covariance with shared calibration/source terms.",
            "An intrinsic-emission nuisance law or preregistered set-valued scoring rule.",
            "Complete source-owned F_reg/F_lim/F_eff/F_obs maps and immutable scorer.",
        ],
        "evidence_level": "T0 exact byte recheck plus targeted response-header and posterior-schema extraction; no model test",
        "next_action": "Use the newly exposed calibration provenance fields to request the corresponding calibration release/validity and timing-uncertainty owner artifacts. Do not infer a timing likelihood from response metadata or a parameter posterior without a time coordinate; independently reproduce F_reg only after all required fields are frozen.",
        "non_claims": [
            "This audit does not construct a timing likelihood, covariance, nuisance law, candidate map, score or prediction.",
            "Response calibration metadata does not establish geocenter correction, causal propagation, or microscopic dynamics.",
            "Absence of a timing coordinate in this posterior product does not prove that no other source product could provide one; it only bounds this exact selected product.",
            "No Pre-A, C6, A13, Sector-A, QFT, Yang-Mills, gravity, continuum, physical-vacuum, cosmic-origin, theory-of-everything or mass-gap claim follows.",
            "The established T-054 forward method and T-059 inverse method are unchanged; this is additive source-owner intake.",
        ],
    }


def self_test() -> int:
    cards = bytearray(2880)
    examples = [
        "CREATOR = './GBM_RSP_Gen.pl-1.12  GBMRSP V2.0' / program",
        "CH2E_VER= 'SPLINE 2.0'           / conversion",
        "GAIN_COR=           1.01966822    / gain",
        "DIRDRMDB= '/data/fastcopy/GBMDRMdb002/' / database",
        "END",
    ]
    for index, line in enumerate(examples):
        cards[index * FITS_CARD_BYTES : (index + 1) * FITS_CARD_BYTES] = line.ljust(
            FITS_CARD_BYTES
        ).encode("ascii")
    fields, ended = parse_all_header_cards(bytes(cards))
    assert ended
    assert fields["CREATOR"] == "./GBM_RSP_Gen.pl-1.12  GBMRSP V2.0"
    assert fields["CH2E_VER"] == "SPLINE 2.0"
    assert fields["GAIN_COR"] == 1.01966822
    assert fields["DIRDRMDB"] == "/data/fastcopy/GBMDRMdb002/"
    assert not any(
        column
        for column in ["costheta_jn", "m1_detector_frame_Msun"]
        if any(token in column.lower() for token in ("time", "tc", "geocent"))
    )
    print("HOLD-LC-CALIBRATION SELFTEST: PASS (header and posterior-schema rules)")
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
    except (OSError, KeyError, ValueError, json.JSONDecodeError, gzip.BadGzipFile) as exc:
        print(f"HOLD-LC-CALIBRATION: FAIL - {exc}")
        return 1
    if not report["checks"]["all_selected_product_hashes_match"]:
        print("HOLD-LC-CALIBRATION: FAIL - selected product hash/length mismatch")
        return 1
    atomic_json_write(args.output, report)
    print(
        "HOLD-LC-CALIBRATION: PASS "
        f"responses={len(report['response_products'])} "
        f"posterior_timing_coordinate={report['posterior_product']['timing_coordinate_present']} "
        "likelihood=NOT_ADMITTED covariance=NOT_ADMITTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
