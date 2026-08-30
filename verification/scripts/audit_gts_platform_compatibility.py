#!/usr/bin/env python3
"""Audit the supported-platform boundary for the pinned public GTS runtime.

This is an environment/provenance audit only.  It does not read event bytes,
response matrices, or score an observation.  The public GDT dependency
contract is fetched from PyPI and the conda-forge package index is queried for
the exact healpy requirement.  A complete event-level runtime is admitted
only when the exact dependency contract has a supported platform build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/hold-lc-001-gts-code-owner-candidate-v0.1.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-gts-platform-compatibility/platform.json"
)
PYPI_HEALPY = "https://pypi.org/pypi/healpy/1.18.0/json"
PYPI_ASTRO_GDT = "https://pypi.org/pypi/astro-gdt/json"
CONDA_HEALPY = "https://api.anaconda.org/package/conda-forge/healpy"


def canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def fetch_json(url: str) -> tuple[dict[str, Any], str]:
    request = Request(url, headers={"User-Agent": "TECT-GTS-platform-audit/0.1"})
    with urlopen(request, timeout=30) as response:
        raw = response.read()
    payload = json.loads(raw.decode("utf-8"))
    return payload, canonical_sha(payload)


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload, canonical_sha(payload)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def source_revision(source_root: Path) -> str | None:
    if not source_root.exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_root = REPO / args.source_root
    sources: dict[str, dict[str, Any]] = {}
    for key, url, path in (
        ("pypi_healpy", PYPI_HEALPY, args.pypi_healpy),
        ("pypi_astro_gdt", PYPI_ASTRO_GDT, args.pypi_astro_gdt),
        ("conda_healpy", CONDA_HEALPY, args.conda_healpy),
    ):
        if path:
            payload, digest = read_json(REPO / path)
            source = {"url": url, "input": path, "canonical_sha256": digest}
        else:
            payload, digest = fetch_json(url)
            source = {"url": url, "canonical_sha256": digest}
        sources[key] = source | {"payload": payload}

    healpy = sources["pypi_healpy"]["payload"]
    astro_gdt = sources["pypi_astro_gdt"]["payload"]
    conda = sources["conda_healpy"]["payload"]
    pypi_files = healpy.get("urls", [])
    pypi_filenames = [str(item.get("filename", "")) for item in pypi_files]
    windows_wheels = [
        name for name in pypi_filenames if name.endswith(".whl") and any(tag in name for tag in ("win_amd64", "win32", "win_arm64"))
    ]
    wheels = [name for name in pypi_filenames if name.endswith(".whl")]
    source_archives = [name for name in pypi_filenames if name.endswith(".tar.gz")]
    required_specs = [str(item) for item in (astro_gdt.get("info", {}).get("requires_dist") or [])]
    healpy_specs = [item for item in required_specs if item.lower().startswith("healpy")]
    conda_files = conda.get("files", [])
    win_118 = [
        str(item.get("basename", ""))
        for item in conda_files
        if str(item.get("basename", "")).startswith("win-64/") and str(item.get("version", "")) == "1.18.0"
    ]
    win_versions = sorted(
        {
            str(item.get("version", ""))
            for item in conda_files
            if str(item.get("basename", "")).startswith("win-64/")
        }
    )

    checks = [
        {
            "id": "pypi-release",
            "status": "PASS" if healpy.get("info", {}).get("version") == "1.18.0" else "FAIL",
            "detail": "PyPI metadata is the requested healpy 1.18.0 release.",
            "actual": healpy.get("info", {}).get("version"),
            "expected": "1.18.0",
        },
        {
            "id": "pypi-windows-wheel",
            "status": "PASS" if not windows_wheels else "FAIL",
            "detail": "No Windows wheel is published for healpy 1.18.0.",
            "actual": windows_wheels,
            "expected": [],
        },
        {
            "id": "pypi-wheel-coverage",
            "status": "PASS" if wheels else "FAIL",
            "detail": "The release has non-Windows wheels or source metadata for comparison.",
            "actual": len(wheels),
            "expected": ">=1",
        },
        {
            "id": "astro-gdt-healpy-contract",
            "status": "PASS" if "healpy~=1.18.0" in healpy_specs else "FAIL",
            "detail": "Current astro-gdt metadata requires the healpy 1.18 minor line.",
            "actual": healpy_specs,
            "expected": "healpy~=1.18.0",
        },
        {
            "id": "conda-win-118",
            "status": "PASS" if not win_118 else "FAIL",
            "detail": "Conda-forge has no win-64 healpy 1.18.0 artifact in the queried index.",
            "actual": win_118,
            "expected": [],
        },
    ]
    if any(row["status"] == "FAIL" for row in checks):
        raise AssertionError(checks)

    return {
        "schema": "tect/gts-platform-compatibility-audit/0.1",
        "id": "GTS-PLATFORM-COMPATIBILITY-001",
        "claim_bearing": False,
        "tier": "T0",
        "status": "EXACT_HEALPY_118_WINDOWS_BUILD_UNAVAILABLE",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_candidate": {
            "path": "strategy/hold-lc-001-gts-code-owner-candidate-v0.1.json",
            "sha256": file_sha(MANIFEST),
            "commit": manifest.get("official_code_source", {}).get("commit"),
        },
        "source_revision_observed": source_revision(source_root),
        "sources": {
            key: {field: value for field, value in entry.items() if field != "payload"}
            for key, entry in sources.items()
        },
        "checks": checks,
        "derived": {
            "pypi_healpy_118_file_count": len(pypi_files),
            "pypi_healpy_118_wheel_count": len(wheels),
            "pypi_healpy_118_windows_wheel_count": len(windows_wheels),
            "pypi_healpy_118_source_archive_count": len(source_archives),
            "conda_win_118_count": len(win_118),
            "conda_win_versions_observed": win_versions,
            "required_healpy_specs": healpy_specs,
        },
        "runtime_admission": {
            "full_gts_event_execution": False,
            "reason": "The exact astro-gdt healpy~=1.18.0 dependency has no queried Windows wheel or conda win-64 1.18.0 artifact; a source build or different platform is required.",
            "event_bytes_read": False,
            "response_values_read": False,
        },
        "method_status": {
            "existing_t054_forward_unchanged": True,
            "existing_t059_inverse_unchanged": True,
            "owner_order_unchanged": True,
            "promotion_firewalls_unchanged": True,
        },
        "non_claims": [
            "This is a package/platform availability boundary, not a scientific no-go.",
            "No event likelihood, response calibration, timing covariance, candidate score, prospective prediction or physical identity is admitted.",
            "No Pre-A, C6, Sector-A, QFT, Yang--Mills, continuum, physical-vacuum, mass-gap or theory-of-everything conclusion follows.",
            "The established T-054 forward and T-059 observation-first inverse methods are unchanged.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", default="internal/tmp/gts-public")
    parser.add_argument("--pypi-healpy")
    parser.add_argument("--pypi-astro-gdt")
    parser.add_argument("--conda-healpy")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args)
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(
        "PASS_PLATFORM_BOUNDARY "
        f"healpy_pypi_windows={payload['derived']['pypi_healpy_118_windows_wheel_count']} "
        f"healpy_conda_win118={payload['derived']['conda_win_118_count']} "
        f"required={payload['derived']['required_healpy_specs']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
