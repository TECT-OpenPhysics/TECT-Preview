"""Audit source metadata for the hash-frozen HOLD-LC-001 products.

The audit reads only local cached bytes named by the existing byte-freeze
manifest.  It verifies raw SHA-256 and byte length, extracts compact gzip/FITS
header metadata, and writes a provenance report.  It does not estimate a
likelihood, covariance, nuisance law, candidate map, or score.
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
DEFAULT_CONTRACT = REPO / "strategy" / "hold-lc-001-estimator-contract-v0.1.json"
DEFAULT_OUTPUT = REPO / "strategy" / "hold-lc-001-product-metadata-audit-v0.1.json"
FITS_BLOCK_BYTES = 2880
FITS_CARD_BYTES = 80
GZIP_READ_BYTES = 8192
SELECTED_KEYS = {
    "BITPIX",
    "NAXIS",
    "NAXIS1",
    "NAXIS2",
    "NAXIS3",
    "PCOUNT",
    "GCOUNT",
    "XTENSION",
    "EXTNAME",
    "DATE-OBS",
    "DATE-END",
    "TIMESYS",
    "TIMEUNIT",
    "MJDREFI",
    "MJDREFF",
    "TSTART",
    "TSTOP",
    "TRIGTIME",
    "TELESCOP",
    "INSTRUME",
    "OBJECT",
    "RA_OBJ",
    "DEC_OBJ",
    "DETCHANS",
    "CHANTYPE",
    "CREATOR",
    "CAL_VER",
    "PROC_VER",
    "TSTARTI",
    "TSTOPI",
}
HEADER_VALUE_RE = re.compile(r"^([+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?)$")
TABLE_KEY_RE = re.compile(r"^(?:TTYPE|TFORM|TUNIT|TNULL|TSCAL|TZERO|TDISP|TDIM)\d+$")


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
    if HEADER_VALUE_RE.fullmatch(numeric):
        try:
            number = float(numeric) if any(ch in numeric for ch in ".Ee") else int(numeric)
            if isinstance(number, float) and math.isfinite(number):
                return number
            return number
        except ValueError:
            pass
    return value.strip()


def parse_fits_header_cards(block: bytes) -> tuple[dict[str, Any], bool]:
    fields: dict[str, Any] = {}
    ended = False
    for offset in range(0, len(block), FITS_CARD_BYTES):
        card = block[offset : offset + FITS_CARD_BYTES].decode("ascii", errors="replace")
        key = card[:8].strip()
        if key == "END":
            ended = True
            break
        if key and card[8:10] == "= ":
            raw = card[10:80].split("/", 1)[0]
            if key in SELECTED_KEYS or TABLE_KEY_RE.fullmatch(key):
                fields[key] = parse_scalar(raw)
    return fields, ended


def parse_fits(path: Path) -> list[dict[str, Any]]:
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
            _, ended = parse_fits_header_cards(block)
            if ended:
                break
        if not ended:
            raise ValueError(f"{path}: FITS END card missing")
        fields, _ = parse_fits_header_cards(bytes(cards))
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


def parse_gzip_preview(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rb") as handle:
        preview = handle.read(GZIP_READ_BYTES)
    text = preview.decode("utf-8", errors="replace")
    lines = text.splitlines()
    return {
        "preview_lines": lines[:4],
        "format": "text_preview",
        "header_fields": {
            "sample_rate_hz": int(match.group(1))
            if (match := re.search(r"has (\d+) samples per second", text))
            else None,
            "starting_gps": int(match.group(1))
            if (match := re.search(r"starting GPS (\d+)", text))
            else None,
            "duration_seconds": int(match.group(1))
            if (match := re.search(r"duration (\d+)", text))
            else None,
        },
    }


def product_path(cache_root: Path, local_cache_key: str) -> Path:
    relative = Path(local_cache_key.replace("/", os.sep))
    parts = relative.parts
    if len(parts) < 3:
        raise ValueError(f"malformed local_cache_key: {local_cache_key}")
    return cache_root / Path(*parts[2:])


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path)


def extract_product(manifest_product: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    path = product_path(cache_root, str(manifest_product["local_cache_key"]))
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_hash, actual_size = sha256_and_size(path)
    suffix = path.suffix.lower()
    metadata: dict[str, Any]
    if suffix == ".gz":
        metadata = {"gzip": parse_gzip_preview(path)}
    elif suffix in {".fit", ".rsp"}:
        metadata = {"fits_hdus": parse_fits(path)}
    else:
        metadata = {"binary_preview": path.read_bytes()[:256].decode("utf-8", errors="replace")}
    expected_hash = str(manifest_product["sha256"])
    expected_size = int(manifest_product["byte_length"])
    return {
        "id": manifest_product["id"],
        "role": manifest_product.get("role"),
        "detector": manifest_product.get("detector"),
        "local_cache_key": manifest_product["local_cache_key"],
        "recorded_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "recorded_byte_length": expected_size,
        "actual_byte_length": actual_size,
        "sha256_match": actual_hash == expected_hash,
        "byte_length_match": actual_size == expected_size,
        "metadata": metadata,
    }


def audit(manifest_path: Path, cache_root: Path, contract_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    manifest_hash, _ = sha256_and_size(manifest_path)
    contract_hash, _ = sha256_and_size(contract_path)
    contract_parent_hash = str(contract["exact_scope"]["input_manifest_sha256"])
    products = [extract_product(item, cache_root) for item in manifest["products"]]
    all_hashes_match = all(item["sha256_match"] for item in products)
    all_sizes_match = all(item["byte_length_match"] for item in products)
    fits_hdus = {
        item["id"]: item["metadata"].get("fits_hdus", [])
        for item in products
        if "fits_hdus" in item["metadata"]
    }
    timesys_values = sorted(
        {
            str(hdu["TIMESYS"])
            for hdus in fits_hdus.values()
            for hdu in hdus
            if "TIMESYS" in hdu
        }
    )
    available = {
        "raw_sha256_and_byte_length": all_hashes_match and all_sizes_match,
        "fits_time_keywords": bool(timesys_values),
        "fits_table_column_metadata": any(
            any(TABLE_KEY_RE.fullmatch(key) for key in hdu)
            for hdus in fits_hdus.values()
            for hdu in hdus
        ),
        "geocenter_correction": False,
        "joint_likelihood": False,
        "component_covariance": False,
        "intrinsic_emission_nuisance_law": False,
        "complete_f_reg": False,
        "complete_f_lim": False,
        "complete_f_eff": False,
        "complete_f_obs": False,
    }
    return {
        "schema": "tect/observation-metadata-audit/0.1",
        "id": "HOLD-LC-001-PRODUCT-METADATA-AUDIT-v0.1",
        "version": "0.1.0",
        "holdout_id": manifest["holdout_id"],
        "parent_manifest": display_path(manifest_path),
        "parent_manifest_sha256": manifest_hash,
        "contract": display_path(contract_path),
        "contract_sha256": contract_hash,
        "contract_parent_manifest_sha256": contract_parent_hash,
        "contract_parent_hash_match": manifest_hash == contract_parent_hash,
        "retrieved_from": display_path(cache_root),
        "status": "PARTIAL_SOURCE_METADATA_AVAILABLE_NO_STATISTICAL_ADMISSION",
        "claim_bearing": False,
        "methods_unchanged": True,
        "products": products,
        "available_metadata": available,
        "derived_source_observations": {
            "fits_timesys_values": timesys_values,
            "fits_table_extensions": {
                product_id: [
                    {
                        "extname": hdu.get("EXTNAME"),
                        "columns": {
                            key: value
                            for key, value in hdu.items()
                            if TABLE_KEY_RE.fullmatch(key)
                        },
                    }
                    for hdu in hdus
                    if "EXTNAME" in hdu
                    and any(TABLE_KEY_RE.fullmatch(key) for key in hdu)
                ]
                for product_id, hdus in fits_hdus.items()
            },
            "geocenter_and_shared_covariance": "NOT_PRESENT_IN_EXTRACTED_PRODUCT_HEADERS",
            "calibration_release_or_validity": "NOT_IDENTIFIED_BY_SELECTED_HEADER_KEYS",
            "window_and_selection_contract": "NOT_PRESENT_AS_A_FROZEN_ESTIMATOR",
            "likelihood_or_probability_law": "NOT_PRESENT",
        },
        "checks": {
            "product_count": len(products),
            "all_product_hashes_match_parent": all_hashes_match,
            "all_product_lengths_match_parent": all_sizes_match,
            "contract_parent_hash_match": manifest_hash == contract_parent_hash,
            "metadata_extraction_completed": True,
            "candidate_scoring": "STOPPED",
            "prospective_lock": "EMPTY",
        },
        "assumptions": [
            "The byte-freeze manifest remains the authority for product identity and expected hashes.",
            "Selected FITS header keywords are provenance metadata, not a complete calibration or timing likelihood.",
            "The local cache is ignored and can be reacquired from the parent manifest locators.",
        ],
        "missing_assumptions": [
            "Source-owned geocenter timing conversion and uncertainty.",
            "Fixed detector, energy, background and timing windows.",
            "Joint likelihood or covariance with shared calibration terms.",
            "Intrinsic-emission nuisance law or preregistered set-valued scoring rule.",
            "Complete source-owned F_reg/F_lim/F_eff/F_obs maps and immutable scorer.",
        ],
        "evidence_level": "T0 exact byte recheck plus compact source-header metadata extraction; no model test",
        "next_action": "Use the extracted metadata only to request or locate the missing source-owner calibration, conversion, window and statistical products; do not score candidates or alter T-054/T-059.",
        "non_claims": [
            "Header time keywords do not establish a geocenter correction, causal propagation law or microscopic dynamics.",
            "The audit does not construct a likelihood, covariance, nuisance probability law, candidate map, score or prospective prediction.",
            "No Pre-A, C6, A13, Sector-A, QFT, Yang-Mills, gravity, continuum, physical-vacuum, cosmic-origin, theory-of-everything or mass-gap claim follows.",
            "The existing T-054 forward method and T-059 inverse method are unchanged.",
        ],
        "recorded_by": "Codex",
    }


def self_test() -> int:
    cards = [
        "SIMPLE  =                    T",
        "BITPIX  =                    8",
        "NAXIS   =                    0",
        "END",
    ]
    header = b"".join(card.ljust(FITS_CARD_BYTES).encode("ascii") for card in cards)
    header += b" " * (FITS_BLOCK_BYTES - len(header))
    fields, ended = parse_fits_header_cards(header)
    assert ended is True
    assert fields["BITPIX"] == 8
    assert fields["NAXIS"] == 0
    assert parse_scalar("7.428703703703703E-04") > 0
    print("HOLD-LC-METADATA SELFTEST: PASS (FITS card parsing and scalar decoding)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=REPO / "internal" / "source-cache" / "HOLD-LC-001" / "2026-08-30",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    report = audit(args.manifest.resolve(), args.cache_root.resolve(), args.contract.resolve())
    atomic_json_write(args.output.resolve(), report)
    passed = all(
        item["sha256_match"] and item["byte_length_match"]
        for item in report["products"]
    ) and report["checks"]["contract_parent_hash_match"]
    print(
        "HOLD-LC-METADATA: "
        f"{'PASS' if passed else 'FAIL'} "
        f"products={report['checks']['product_count']} timesys={report['derived_source_observations']['fits_timesys_values']} "
        "likelihood=NOT_ADMITTED covariance=NOT_ADMITTED score=STOPPED"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
