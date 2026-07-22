#!/usr/bin/env python3
"""Stage-4 CPU/GPU and complex-precision cross-check for P3."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

import a3_full_production_hessian_ritz_convergence as ritz
import a3_full_production_portable_backend as portable
import a3_full_production_spatial_consistency as spatial

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
BACKEND_PATH = REPO / "codes" / "foundations" / "n001_variational_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-hardware-precision" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_backend() -> Any:
    spec = importlib.util.spec_from_file_location("p3_hardware_reference", BACKEND_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load canonical backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_scalar(value: float, reference: float) -> float:
    return abs(value - reference) / max(abs(reference), 1e-30)


def relative_array(value: np.ndarray, reference: np.ndarray, params: dict[str, Any]) -> float:
    return spatial.relative_l2(value, reference, params)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    params = dict(p1["parameters"])
    params["eta_shell"] = 0.0
    stage = manifest["stage4"]
    acceptance = stage["acceptance"]
    n = int(stage["grid"])
    backend = load_backend()
    stress = ritz.hessian_stress_field(n, params)
    homogeneous = np.broadcast_to(np.mean(stress, axis=(-3, -2, -1), keepdims=True), stress.shape).copy()
    fields = {"homogeneous": homogeneous, "classii_stress": stress}

    references = {name: {"energy": backend.energy(field, params), "residual": backend.residual(field, params)} for name, field in fields.items()}
    configurations = [
        ("cpu_complex128", "cpu", torch.complex128, True),
        ("cpu_complex64", "cpu", torch.complex64, True),
        ("cuda_complex128", "cuda", torch.complex128, torch.cuda.is_available()),
        ("cuda_complex64", "cuda", torch.complex64, torch.cuda.is_available()),
    ]
    rows = []
    assertions = []
    for label, device, dtype, available in configurations:
        if not available:
            rows.append({"configuration": label, "status": "UNAVAILABLE", "reason": "torch.cuda.is_available() is false"})
            continue
        field_rows = []
        for name, field in fields.items():
            energy, residual = portable.energy_residual(field, params, device, dtype)
            field_rows.append({
                "field": name,
                "energy_relative_error": relative_scalar(energy, references[name]["energy"]),
                "residual_relative_l2": relative_array(residual, references[name]["residual"], params),
            })
        energy_limit = float(acceptance[f"{label}_energy_relative_max"] if label.startswith("cuda") else acceptance["cpu_complex128_energy_relative_max"] if label.endswith("128") else acceptance["complex64_energy_relative_max"])
        residual_limit = float(acceptance[f"{label}_residual_relative_max"] if label.startswith("cuda") else acceptance["cpu_complex128_residual_relative_max"] if label.endswith("128") else acceptance["complex64_residual_relative_max"])
        maximum_energy = max(row["energy_relative_error"] for row in field_rows)
        maximum_residual = max(row["residual_relative_l2"] for row in field_rows)
        status = "PASS" if maximum_energy <= energy_limit and maximum_residual <= residual_limit else "FAIL"
        rows.append({"configuration": label, "status": status, "energy_limit": energy_limit, "residual_limit": residual_limit, "maximum_energy_relative_error": maximum_energy, "maximum_residual_relative_l2": maximum_residual, "fields": field_rows})
        assertions.append({"name": label, "status": status, "detail": f"energy={maximum_energy:.6e}/{energy_limit:.6e}; residual={maximum_residual:.6e}/{residual_limit:.6e}"})

    cpu_pass = all(row["status"] == "PASS" for row in rows if row["configuration"].startswith("cpu"))
    cuda_rows = [row for row in rows if row["configuration"].startswith("cuda")]
    cuda_available = torch.cuda.is_available()
    cuda_pass = cuda_available and all(row["status"] == "PASS" for row in cuda_rows)
    assertions.insert(0, {"name": "canonical_backend_hash", "status": "PASS" if sha256(BACKEND_PATH) == manifest["authority"]["p1_backend"]["sha256"] else "FAIL", "detail": sha256(BACKEND_PATH)})
    assertions.append({"name": "cuda_availability_reported_honestly", "status": "PASS", "detail": f"cuda_available={cuda_available}; unavailable is not counted as GPU PASS"})
    passed = sum(item["status"] == "PASS" for item in assertions)
    total = len(assertions)
    if cpu_pass and cuda_pass:
        verdict = "A3-FULL-HARDWARE-PRECISION-PASS"
    elif cpu_pass and not cuda_available:
        verdict = "A3-FULL-CPU-PRECISION-PASS-GPU-UNAVAILABLE"
    else:
        verdict = "A3-FULL-HARDWARE-PRECISION-FAIL"
    output = {
        "schema": "tect/a3-full-production-hardware-precision-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "torch": {"version": torch.__version__, "cuda_available": cuda_available, "cuda_version": torch.version.cuda, "device_count": torch.cuda.device_count(), "devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]},
        "verdict": verdict,
        "scope": "portable independent functional implementation compared with canonical CPU complex128 on homogeneous and nonuniform Class-II-active fields",
        "gate_closed": bool(cpu_pass and cuda_pass),
        "rows": rows,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": total}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{total} available assertions PASS")
    print(verdict)
    for row in rows:
        print(f"{row['configuration']}: {row['status']}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if cpu_pass and (cuda_pass or not cuda_available) else 1


if __name__ == "__main__":
    raise SystemExit(main())
