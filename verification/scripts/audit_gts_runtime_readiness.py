#!/usr/bin/env python3
"""Audit the pre-event GTS runtime and byte inventory without reading science values.

The audit is deliberately limited to source/manifest hashes, byte lengths and
Python module availability.  It does not parse FITS tables, read response
matrix values, execute the external GTS repository, or evaluate an event score.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST_PATHS = (
    REPO / "strategy" / "hold-lc-001-event-byte-freeze-v0.1.json",
    REPO / "strategy" / "hold-lc-001-owner-artifact-byte-freeze-v0.1.json",
    REPO / "strategy" / "hold-lc-001-response-history-byte-freeze-v0.1.json",
)
CANDIDATE_PATH = REPO / "strategy" / "hold-lc-001-gts-code-owner-candidate-v0.1.json"
REQUIRED_MODULES = (
    "numpy",
    "scipy",
    "astropy",
    "healpy",
    "gdt.core",
    "gdt.missions.fermi.gbm",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _module_probe(module: str) -> dict[str, Any]:
    try:
        spec = importlib.util.find_spec(module)
    except (ImportError, AttributeError, ValueError) as exc:
        return {"module": module, "available": False, "error": type(exc).__name__}
    available = spec is not None
    package_name = module.split(".", 1)[0]
    version: str | None = None
    if available:
        try:
            version = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            version = None
    return {"module": module, "available": available, "distribution_version": version}


def _load_products() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    products: list[dict[str, Any]] = []
    manifest_meta: list[dict[str, Any]] = []
    for manifest_path in MANIFEST_PATHS:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_meta.append(
            {
                "path": manifest_path.relative_to(REPO).as_posix(),
                "id": data.get("id"),
                "status": data.get("status"),
            }
        )
        for product in data.get("products", []):
            item = dict(product)
            item["manifest_path"] = manifest_path.relative_to(REPO).as_posix()
            products.append(item)
    return products, manifest_meta


def _audit_bytes(products: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
    records: list[dict[str, Any]] = []
    all_match = True
    seen: set[str] = set()
    for product in products:
        key = str(product["local_cache_key"])
        if key in seen:
            raise AssertionError(f"duplicate local cache key: {key}")
        seen.add(key)
        local_path = REPO / "internal" / "source-cache" / Path(*key.split("/"))
        exists = local_path.is_file()
        actual_length = local_path.stat().st_size if exists else None
        actual_sha256 = _sha256(local_path) if exists else None
        length_match = actual_length == int(product["byte_length"])
        hash_match = actual_sha256 == str(product["sha256"])
        match = exists and length_match and hash_match
        all_match = all_match and match
        records.append(
            {
                "id": product.get("id"),
                "role": product.get("role"),
                "manifest_path": product["manifest_path"],
                "local_cache_key": key,
                # Keep the public artefact free of internal workspace paths;
                # the manifest cache key is the durable locator.
                "cache_locator": key,
                "exists": exists,
                "recorded_byte_length": int(product["byte_length"]),
                "actual_byte_length": actual_length,
                "recorded_sha256": str(product["sha256"]),
                "actual_sha256": actual_sha256,
                "byte_length_match": length_match,
                "sha256_match": hash_match,
                "matrix_values_read": False,
            }
        )
    return records, all_match


def run() -> dict[str, Any]:
    products, manifest_meta = _load_products()
    byte_records, bytes_match = _audit_bytes(products)
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    source = candidate["official_code_source"]
    probes = [_module_probe(module) for module in REQUIRED_MODULES]
    dependencies_ready = all(item["available"] for item in probes)
    status = "READY_FOR_EXTERNAL_EXECUTION" if bytes_match and dependencies_ready else "INPUTS_HASH_PINNED_RUNTIME_NOT_READY"
    checks = [
        {
            "id": "manifest-byte-inventory",
            "finding": "PASS" if bytes_match else "FAIL",
            "detail": f"{sum(1 for item in byte_records if item['sha256_match'] and item['byte_length_match'])}/{len(byte_records)} manifest products exist with matching byte length and SHA-256; no matrix values were read.",
        },
        {
            "id": "source-commit-pin",
            "finding": "PASS" if source.get("commit") == "1bc1e913f97fd7195a7e297f8d6032a5c7758894" else "FAIL",
            "detail": f"GTS source commit recorded as {source.get('commit')}.",
        },
        {
            "id": "runtime-dependency-probe",
            "finding": "PASS" if dependencies_ready else "PARTIAL-PASS-RUNTIME-GAP",
            "detail": f"{sum(1 for item in probes if item['available'])}/{len(probes)} required import modules are available in the audit interpreter; missing modules remain explicit.",
        },
        {
            "id": "event-execution-firewall",
            "finding": "PASS",
            "detail": "The audit hashes bytes and probes imports only; it does not parse science values, execute GTS, select response segments, or score an event.",
        },
    ]
    if not bytes_match:
        raise AssertionError("one or more hash-pinned local input products do not match")
    if source.get("commit") != "1bc1e913f97fd7195a7e297f8d6032a5c7758894":
        raise AssertionError("GTS source commit drifted from the parent candidate card")
    return {
        "schema": "tect/gts-runtime-readiness/0.1",
        "id": "GTS-RUNTIME-READINESS-001",
        "recorded_on": "2026-08-30",
        "claim_bearing": False,
        "tier": "T0",
        "status": status,
        "source_repository": source["url"],
        "source_commit": source["commit"],
        "interpreter": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "required_modules": probes,
        "manifest_sources": manifest_meta,
        "byte_inventory": byte_records,
        "checks": checks,
        "run_command": "python verification/scripts/audit_gts_runtime_readiness.py --out claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-runtime-readiness/readiness.json",
        "interpretation": "The hash-pinned local event/owner byte inventory is ready for a later event-freeze packet, while the current interpreter is not an external GTS execution environment when required modules are missing. This is a readiness boundary, not a statistical or physical result.",
        "next_action": "Provide a separately hash-pinned environment containing every required GTS module and exact package version, then rerun this audit before any event-level execution. Keep response values, segment selection, timing likelihood, covariance, nuisance law, scorer and prospective credit locked.",
        "non_claims": [
            "No FITS table or response-matrix science value was read or validated.",
            "No external GTS repository execution, event-level GBM likelihood, response value, calibration validity or detector-to-geocenter correction is established.",
            "The synthetic GTS audit and this runtime inventory do not provide a Stachie joint Lambda, continuous Delta_t_det likelihood, covariance, intrinsic-lag law, candidate score or prospective prediction.",
            "No microscopic dynamics, QFT/Yang--Mills/gravity identity, Pre-A, C6, Sector-A, continuum, physical-vacuum, cosmic-origin, theory-of-everything or mass-gap claim follows.",
            "The established T-054 forward and T-059 inverse methods, owner order and stopped-loop rules are unchanged.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-runtime-readiness/readiness.json"),
    )
    args = parser.parse_args()
    payload = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": args.out.as_posix(), "status": payload["status"], "checks": payload["checks"]}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
