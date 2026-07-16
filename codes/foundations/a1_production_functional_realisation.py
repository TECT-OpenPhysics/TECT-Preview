#!/usr/bin/env python3
"""Audit the current full N-001 working branch for variational consistency.

This is deliberately an *audit*, not a replacement backend.  It independently
rebuilds the manifest's declared energy using Torch autodiff, then compares it
with the hash-pinned external backend's residual and Hessian under

    <u,v>_R = dV Re sum(conj(u) v).

Exit 0 means the independent energy control passed and the currently pinned
scalar and production mismatches were detected.  It never means closure
passed.  Use --assert-closure only after an authoritative repair: it exits 1
while the full-production mismatch remains.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    import torch
except ImportError as exc:  # pragma: no cover - explicit operator diagnosis
    raise SystemExit(f"Torch is required for the independent autodiff audit: {exc}")

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A1-PRODUCTION-FUNCTIONAL-REALISATION"
MANIFEST = REPO / "claims" / CLAIM / "production_functional_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-07-17-variational-audit" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_error(lhs: complex | float, rhs: complex | float) -> float:
    return float(abs(lhs - rhs) / max(1.0, abs(lhs), abs(rhs)))


def norm_rel(lhs: np.ndarray, rhs: np.ndarray) -> float:
    return float(np.linalg.norm((lhs - rhs).ravel()) / max(1.0, np.linalg.norm(lhs.ravel()), np.linalg.norm(rhs.ravel())))


def real_pairing(u: np.ndarray, v: np.ndarray, dvol: float) -> float:
    return float(dvol * np.real(np.vdot(u, v)))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_backend(path: Path):
    spec = importlib.util.spec_from_file_location("a1_pinned_backend", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import backend at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def torch_params(params: dict[str, Any]) -> dict[str, Any]:
    """Force an auditable CPU/complex128 execution path without changing physics."""
    out = dict(params)
    out.update({"use_cuda": False, "use_xpu": False, "device": "cpu", "torch_complex_dtype": "complex128"})
    return out


def tfield(x: np.ndarray) -> torch.Tensor:
    return torch.tensor(x, dtype=torch.complex128, device="cpu")


def kmesh(shape: tuple[int, int, int], params: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    nx, ny, nz = shape
    axes = [
        2.0 * math.pi * torch.fft.fftfreq(n, d=float(length) / n, dtype=torch.float64)
        for n, length in zip(shape, (params["Lx"], params["Ly"], params["Lz"]))
    ]
    kx, ky, kz = torch.meshgrid(*axes, indexing="ij")
    return kx, ky, kz, torch.sqrt(kx * kx + ky * ky + kz * kz)


def fft_grad(psi: torch.Tensor, params: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    kx, ky, kz, _ = kmesh(tuple(psi.shape[1:]), params)
    psik = torch.fft.fftn(psi, dim=(1, 2, 3))
    grads = torch.stack([torch.fft.ifftn(1j * k.unsqueeze(0) * psik, dim=(1, 2, 3)) for k in (kx, ky, kz)], dim=0)
    lap = torch.fft.ifftn(-(kx * kx + ky * ky + kz * kz).unsqueeze(0) * psik, dim=(1, 2, 3))
    return grads, lap


def generators() -> list[torch.Tensor]:
    return [
        torch.tensor([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=torch.complex128),
        torch.tensor([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=torch.complex128),
        torch.tensor([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=torch.complex128),
    ]


def declared_energy(psi: torch.Tensor, params: dict[str, Any]) -> torch.Tensor:
    """Independent reconstruction of shell_free_energy's declared formula.

    It intentionally does not import the backend's energy method, so autodiff
    remains an independent check of its discrete formula and conventions.
    """
    nx, ny, nz = (int(n) for n in psi.shape[1:])
    dvol = (float(params["Lx"]) / nx) * (float(params["Ly"]) / ny) * (float(params["Lz"]) / nz)
    rho = torch.sum(torch.abs(psi) ** 2, dim=0)
    grad, lap = fft_grad(psi, params)
    result = 0.5 * float(params["r"]) * torch.sum(rho)
    result = result + 0.5 * float(params["Z"]) * torch.sum(torch.abs(grad) ** 2)
    result = result + 0.5 * float(params["Y"]) * torch.sum(torch.abs(lap) ** 2)

    family = torch.diag(torch.tensor(params["family_masses"], dtype=torch.complex128))
    fam_psi = torch.einsum("ab,bxyz->axyz", family, psi)
    result = result + 0.5 * torch.sum(torch.real(torch.sum(torch.conj(psi) * fam_psi, dim=0)))

    z0 = torch.tensor(params["z0"], dtype=torch.complex128)
    p0 = torch.outer(z0, torch.conj(z0)) / torch.real(torch.vdot(z0, z0))
    lock_psi = float(params["k_lock"]) * torch.einsum("ab,bxyz->axyz", torch.eye(3, dtype=torch.complex128) - p0, psi)
    if abs(float(params["k_lock"])) > 0.0:
        result = result + 0.5 / float(params["k_lock"]) * torch.sum(torch.real(torch.sum(torch.conj(lock_psi) * lock_psi, dim=0)))

    result = result + 0.5 * float(params["lambda"]) * torch.sum(rho ** 2)
    result = result + (float(params["gamma"]) / 3.0) * torch.sum(rho ** 3)

    eta = float(params["eta_shell"])
    if abs(eta) > 0.0:
        _, _, _, kmag = kmesh((nx, ny, nz), params)
        psik = torch.fft.fftn(psi, dim=(1, 2, 3))
        result = result + (0.5 * eta * torch.sum(torch.abs((kmag - float(params["q0"])).unsqueeze(0) * psik) ** 2) / (nx * ny * nz)) / dvol

    alpha, beta, mass = (float(params[key]) for key in ("alpha_X", "beta_X", "M_X"))
    pref_jj = float(params["cJJ"]) * alpha * alpha / (mass * mass + 1e-12)
    pref_kk = float(params["cKK"]) * beta * beta / (mass * mass + 1e-12)
    rho_safe = rho + 1e-12
    grad_rho = 2.0 * torch.real(torch.sum(torch.conj(psi).unsqueeze(0) * grad, dim=1))
    for gen in generators():
        tpsi = torch.einsum("ab,bxyz->axyz", gen, psi)
        moment = torch.sum(torch.conj(psi) * tpsi, dim=0)
        grad_moment = torch.sum(torch.conj(grad) * tpsi.unsqueeze(0), dim=1) + torch.sum(
            torch.conj(psi).unsqueeze(0) * torch.einsum("ab,ibxyz->iaxyz", gen, grad), dim=1
        )
        reduced = grad_moment - (moment / rho_safe).unsqueeze(0) * grad_rho
        result = result + 0.5 * pref_jj * torch.sum(torch.abs(grad_moment) ** 2)
        result = result + 0.5 * pref_kk * torch.sum(torch.abs(reduced) ** 2)
    return torch.real(result * dvol)


def reference_energy(psi: torch.Tensor, params: dict[str, Any]) -> torch.Tensor:
    """Proposed full variational functional under the manifest real pairing.

    This is a reference candidate, not a claim about the hash-pinned working
    branch.  It corrects the scalar real-gradient normalisation and retains all
    three Class-II couplings through the symmetric quadratic form in (J, K).
    Its residual is derived below by autodiff; its Hessian uses a centred
    derivative of that gradient rather than copied external-source code.
    """
    nx, ny, nz = (int(n) for n in psi.shape[1:])
    dvol = (float(params["Lx"]) / nx) * (float(params["Ly"]) / ny) * (float(params["Lz"]) / nz)
    # Write every squared complex norm polynomially.  torch.abs(z)**2 has a
    # non-smooth complex-autodiff path at z=0, whereas Re(conj(z) z) preserves
    # the same value and gives a defined zero-field derivative/Hessian.
    norm_sq = lambda value: torch.real(torch.conj(value) * value)
    rho = torch.sum(norm_sq(psi), dim=0)
    grad, lap = fft_grad(psi, params)
    result = 0.5 * float(params["r"]) * torch.sum(rho)
    result = result + 0.5 * float(params["Z"]) * torch.sum(norm_sq(grad))
    result = result + 0.5 * float(params["Y"]) * torch.sum(norm_sq(lap))

    family = torch.diag(torch.tensor(params["family_masses"], dtype=torch.complex128))
    fam_psi = torch.einsum("ab,bxyz->axyz", family, psi)
    result = result + 0.5 * torch.sum(torch.real(torch.sum(torch.conj(psi) * fam_psi, dim=0)))
    z0 = torch.tensor(params["z0"], dtype=torch.complex128)
    p0 = torch.outer(z0, torch.conj(z0)) / torch.real(torch.vdot(z0, z0))
    lock = torch.einsum("ab,bxyz->axyz", torch.eye(3, dtype=torch.complex128) - p0, psi)
    result = result + 0.5 * float(params["k_lock"]) * torch.sum(norm_sq(lock))

    # Under <.,.>_R, these coefficients give lambda*rho*Psi and gamma*rho^2*Psi.
    result = result + 0.25 * float(params["lambda"]) * torch.sum(rho ** 2)
    result = result + (float(params["gamma"]) / 6.0) * torch.sum(rho ** 3)
    eta = float(params["eta_shell"])
    if abs(eta) > 0.0:
        _, _, _, kmag = kmesh((nx, ny, nz), params)
        psik = torch.fft.fftn(psi, dim=(1, 2, 3))
        result = result + (0.5 * eta * torch.sum(norm_sq((kmag - float(params["q0"])).unsqueeze(0) * psik)) / (nx * ny * nz)) / dvol

    alpha, beta, mass = (float(params[key]) for key in ("alpha_X", "beta_X", "M_X"))
    denominator = mass * mass + 1e-12
    pref_jj = float(params["cJJ"]) * alpha * alpha / denominator
    pref_jk = float(params["cJK"]) * alpha * beta / denominator
    pref_kk = float(params["cKK"]) * beta * beta / denominator
    rho_safe = rho + 1e-12
    grad_rho = 2.0 * torch.real(torch.sum(torch.conj(psi).unsqueeze(0) * grad, dim=1))
    for gen in generators():
        tpsi = torch.einsum("ab,bxyz->axyz", gen, psi)
        moment = torch.sum(torch.conj(psi) * tpsi, dim=0)
        current = torch.sum(torch.conj(grad) * tpsi.unsqueeze(0), dim=1) + torch.sum(
            torch.conj(psi).unsqueeze(0) * torch.einsum("ab,ibxyz->iaxyz", gen, grad), dim=1
        )
        covariant = current - (moment / rho_safe).unsqueeze(0) * grad_rho
        result = result + 0.5 * pref_jj * torch.sum(norm_sq(current))
        result = result + pref_jk * torch.sum(torch.real(torch.conj(current) * covariant))
        result = result + 0.5 * pref_kk * torch.sum(norm_sq(covariant))
    return torch.real(result * dvol)


def _real_coordinates(psi: np.ndarray, *, requires_grad: bool = False) -> torch.Tensor:
    return torch.stack((torch.tensor(psi.real, dtype=torch.float64), torch.tensor(psi.imag, dtype=torch.float64))).requires_grad_(requires_grad)


def _reference_energy_real(x: torch.Tensor, params: dict[str, Any]) -> torch.Tensor:
    return reference_energy(torch.complex(x[0], x[1]), params)


def reference_residual(psi: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    """Real gradient of reference_energy, converted to the manifest pairing."""
    x = _real_coordinates(psi, requires_grad=True)
    energy = _reference_energy_real(x, params)
    gradient = torch.autograd.grad(energy, x)[0]
    nx, ny, nz = (int(n) for n in psi.shape[1:])
    dvol = (float(params["Lx"]) / nx) * (float(params["Ly"]) / ny) * (float(params["Lz"]) / nz)
    return ((gradient[0].detach().cpu().numpy() + 1j * gradient[1].detach().cpu().numpy()) / dvol).astype(np.complex128)


def reference_hessian_vec(psi: np.ndarray, direction: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    """Centred derivative of the autodiff real gradient.

    Torch's complex-FFT second-derivative path is unavailable on the current
    CPU runtime.  The residual remains an autodiff gradient; this H uses a
    manifest-labelled centred derivative, while the outer audit uses three
    independent steps to test DR=H and Hessian symmetry.
    """
    step = float(params.get("reference_hessian_step", 3e-5))
    return (reference_residual(psi + step * direction, params) - reference_residual(psi - step * direction, params)) / (2.0 * step)


def autodiff_directional(psi: np.ndarray, direction: np.ndarray, params: dict[str, Any]) -> float:
    x = torch.stack((torch.tensor(psi.real, dtype=torch.float64), torch.tensor(psi.imag, dtype=torch.float64))).requires_grad_(True)
    complex_psi = torch.complex(x[0], x[1])
    energy = declared_energy(complex_psi, params)
    gradient = torch.autograd.grad(energy, x)[0]
    vx = torch.stack((torch.tensor(direction.real, dtype=torch.float64), torch.tensor(direction.imag, dtype=torch.float64)))
    return float(torch.sum(gradient * vx).detach().cpu().item())


def finite_difference_energy(psi: np.ndarray, direction: np.ndarray, params: dict[str, Any], step: float) -> float:
    plus = float(declared_energy(tfield(psi + step * direction), params).detach().cpu().item())
    minus = float(declared_energy(tfield(psi - step * direction), params).detach().cpu().item())
    return (plus - minus) / (2.0 * step)


def finite_difference_reference_energy(psi: np.ndarray, direction: np.ndarray, params: dict[str, Any], step: float) -> float:
    plus = float(reference_energy(tfield(psi + step * direction), params).detach().cpu().item())
    minus = float(reference_energy(tfield(psi - step * direction), params).detach().cpu().item())
    return (plus - minus) / (2.0 * step)


def make_fields(n: int, params: dict[str, Any]) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(20260717)
    grid = np.arange(n, dtype=float)
    x, y, z = np.meshgrid(grid, grid, grid, indexing="ij")
    base = np.asarray([0.55 + 0.15j, 0.35 - 0.20j, 0.25 + 0.10j], dtype=np.complex128)[:, None, None, None]
    homogeneous = np.broadcast_to(base, (3, n, n, n)).copy()
    random = homogeneous + 0.05 * (rng.normal(size=(3, n, n, n)) + 1j * rng.normal(size=(3, n, n, n)))
    phase = np.exp(2j * math.pi * (x + y + z) / n)
    q0_shell = homogeneous + np.asarray([0.11, -0.07j, 0.05], dtype=np.complex128)[:, None, None, None] * phase
    classii = homogeneous.copy()
    classii[0] += 0.10 * phase
    classii[1] += 0.08j * np.conj(phase)
    classii[2] += 0.04 * np.exp(2j * math.pi * (x - y) / n)
    return {"zero": np.zeros((3, n, n, n), dtype=np.complex128), "homogeneous": homogeneous, "random": random, "q0-shell": q0_shell, "classII-active": classii}


def unit_complex(rng: np.random.Generator, shape: tuple[int, ...], dvol: float) -> np.ndarray:
    raw = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    return raw / math.sqrt(real_pairing(raw, raw, dvol))


@dataclass(frozen=True)
class AuditConfig:
    name: str
    params: dict[str, Any]


def variants(base: dict[str, Any]) -> list[AuditConfig]:
    scalar = dict(base)
    scalar.update({"family_masses": [0.0, 0.0, 0.0], "k_lock": 0.0, "eta_shell": 0.0, "alpha_X": 0.0, "beta_X": 0.0, "cJJ": 0.0, "cJK": 0.0, "cKK": 0.0})
    active = dict(base)
    active["eta_shell"] = 0.07  # manifest-declared audit activation, not physical retuning
    return [AuditConfig("scalar-core-control", scalar), AuditConfig("pinned-production", dict(base)), AuditConfig("all-terms-activation", active)]


def run_case(backend: Any, config: AuditConfig, name: str, psi: np.ndarray, direction: np.ndarray, other: np.ndarray, steps: list[float]) -> dict[str, Any]:
    p = torch_params(config.params)
    shape = tuple(int(v) for v in psi.shape[1:])
    dvol = (p["Lx"] / shape[0]) * (p["Ly"] / shape[1]) * (p["Lz"] / shape[2])
    r = backend.residual(psi, p)
    hv = backend.hessian_vec(psi, direction, p)
    hu = backend.hessian_vec(psi, other, p)
    ad = autodiff_directional(psi, direction, p)
    records = []
    for step in steps:
        fd_e = finite_difference_energy(psi, direction, p, step)
        dr_fd = (backend.residual(psi + step * direction, p) - backend.residual(psi - step * direction, p)) / (2.0 * step)
        records.append({
            "step": step,
            "energy_fd": fd_e,
            "autodiff_rel_error": rel_error(ad, fd_e),
            "residual_rel_error": rel_error(real_pairing(r, direction, dvol), fd_e),
            "dr_hessian_rel_error": norm_rel(dr_fd, hv),
        })
    symmetry = rel_error(real_pairing(other, hv, dvol), real_pairing(hu, direction, dvol))
    return {"variant": config.name, "field": name, "autodiff_directional": ad, "residual_directional": real_pairing(r, direction, dvol), "symmetry_rel_error": symmetry, "steps": records}


def reference_variants(base: dict[str, Any]) -> list[AuditConfig]:
    activation = dict(base)
    activation["eta_shell"] = 0.07  # manifest-declared audit activation, not physical retuning
    return [AuditConfig("reference-pinned-production", dict(base)), AuditConfig("reference-all-terms-activation", activation)]


def run_reference_case(config: AuditConfig, name: str, psi: np.ndarray, direction: np.ndarray, other: np.ndarray, steps: list[float]) -> dict[str, Any]:
    p = torch_params(config.params)
    shape = tuple(int(v) for v in psi.shape[1:])
    dvol = (p["Lx"] / shape[0]) * (p["Ly"] / shape[1]) * (p["Lz"] / shape[2])
    residual = reference_residual(psi, p)
    hv = reference_hessian_vec(psi, direction, p)
    hu = reference_hessian_vec(psi, other, p)
    records = []
    for step in steps:
        fd_e = finite_difference_reference_energy(psi, direction, p, step)
        dr_fd = (reference_residual(psi + step * direction, p) - reference_residual(psi - step * direction, p)) / (2.0 * step)
        records.append({
            "step": step,
            "energy_fd": fd_e,
            "variational_rel_error": rel_error(real_pairing(residual, direction, dvol), fd_e),
            "dr_hessian_rel_error": norm_rel(dr_fd, hv),
        })
    symmetry = rel_error(real_pairing(other, hv, dvol), real_pairing(hu, direction, dvol))
    return {"variant": config.name, "field": name, "residual_directional": real_pairing(residual, direction, dvol), "symmetry_rel_error": symmetry, "steps": records}


def max_metric(rows: list[dict[str, Any]], metric: str) -> float:
    values: list[float] = []
    for row in rows:
        if metric == "symmetry_rel_error":
            values.append(float(row[metric]))
        else:
            values.extend(float(s[metric]) for s in row["steps"])
    return max(values, default=0.0)


def run_reference_closure(manifest: dict[str, Any], grid: int, output_path: Path) -> dict[str, Any]:
    """Run the proposed functional through all three identities and persist it."""
    pinned = manifest["parameters"]
    steps = [float(x) for x in manifest["test_matrix"]["finite_difference_steps"]]
    fields = make_fields(grid, pinned)
    dvol = (pinned["Lx"] / grid) * (pinned["Ly"] / grid) * (pinned["Lz"] / grid)
    rng = np.random.default_rng(20260717 + 2)
    rows: list[dict[str, Any]] = []
    for config in reference_variants(pinned):
        for name, psi in fields.items():
            rows.append(run_reference_case(config, name, psi, unit_complex(rng, psi.shape, dvol), unit_complex(rng, psi.shape, dvol), steps))
    thresholds = {"variational": 2e-7, "hessian": 2e-5, "symmetry": 1e-9}
    checks = {
        "all_scalar_terms_present": float(pinned["lambda"]) != 0.0 and float(pinned["gamma"]) != 0.0,
        "all_classII_terms_present": all(float(pinned[key]) != 0.0 for key in ("cJJ", "cJK", "cKK", "alpha_X", "beta_X", "M_X")),
        "variational_identity": max_metric(rows, "variational_rel_error") < thresholds["variational"],
        "hessian_identity": max_metric(rows, "dr_hessian_rel_error") < thresholds["hessian"],
        "real_hessian_symmetry": max_metric(rows, "symmetry_rel_error") < thresholds["symmetry"],
    }
    result = {
        "schema": "tect/a1-production-reference-functional-closure/1.0",
        "date": "2026-07-17",
        "claim_id": CLAIM,
        "verdict": "REFERENCE-CLOSURE-PASS" if all(checks.values()) else "REFERENCE-CLOSURE-FAIL",
        "scope": "proposed reference functional only; not the external working-branch backend",
        "checks": checks,
        "thresholds": thresholds,
        "maxima": {metric: max_metric(rows, metric) for metric in ("variational_rel_error", "dr_hessian_rel_error", "symmetry_rel_error")},
        "rows": rows,
        "functional": manifest["proposed_reference_functional"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--reference-closure", action="store_true", help="also verify the proposed full reference functional")
    ap.add_argument("--reference-output", type=Path, default=REPO / "claims" / CLAIM / "runs" / "2026-07-17-reference-functional-closure" / "result.json")
    ap.add_argument("--grid", type=int, default=4, help="diagnostic N; manifest currently certifies N=4")
    ap.add_argument("--assert-closure", action="store_true", help="return nonzero unless the full production identities close")
    args = ap.parse_args()
    if args.grid != 4:
        raise SystemExit("This v1.0 manifest pins N=4; extend the manifest before changing --grid.")

    manifest = load_json(MANIFEST)
    backend_info, config_info = manifest["authority"]["backend"], manifest["authority"]["config"]
    backend_path, config_path = Path(backend_info["path"]), Path(config_info["path"])
    checks: dict[str, bool] = {
        "manifest_schema": manifest["schema"] == "tect/a1-production-functional-realisation/1.0",
        "backend_exists": backend_path.is_file(),
        "config_exists": config_path.is_file(),
    }
    if checks["backend_exists"]:
        checks["backend_sha256"] = sha256(backend_path) == backend_info["sha256"]
    else:
        checks["backend_sha256"] = False
    if checks["config_exists"]:
        checks["config_sha256"] = sha256(config_path) == config_info["sha256"]
    else:
        checks["config_sha256"] = False
    if not all(checks.values()):
        raise SystemExit(f"P1 audit refused: source-manifest check failed: {checks}")

    external_config = load_json(config_path)
    pinned = manifest["parameters"]
    checks["pinned_parameters_match_source"] = all(external_config.get(k) == v for k, v in pinned.items() if k in external_config)
    if not checks["pinned_parameters_match_source"]:
        raise SystemExit("P1 audit refused: manifest parameter values drift from the pinned config source")
    checks["classii_coefficients_distinct"] = float(pinned["cJK"]) != float(pinned["cKK"])
    q_commensurate = math.sqrt(3.0) * 2.0 * math.pi / float(pinned["Lx"])
    checks["q0_shell_commensurate"] = abs(q_commensurate - float(pinned["q0"])) < 1e-9

    backend = load_backend(backend_path)
    steps = [float(x) for x in manifest["test_matrix"]["finite_difference_steps"]]
    fields = make_fields(args.grid, pinned)
    dvol = (pinned["Lx"] / args.grid) * (pinned["Ly"] / args.grid) * (pinned["Lz"] / args.grid)
    rng = np.random.default_rng(20260717 + 1)
    rows: list[dict[str, Any]] = []
    for config in variants(pinned):
        for name, psi in fields.items():
            rows.append(run_case(backend, config, name, psi, unit_complex(rng, psi.shape, dvol), unit_complex(rng, psi.shape, dvol), steps))

    controls = [row for row in rows if row["variant"] == "scalar-core-control"]
    full = [row for row in rows if row["variant"] == "pinned-production"]
    active = [row for row in rows if row["variant"] == "all-terms-activation"]
    # Tooling thresholds, not physics inputs.  They diagnose the N=4/complex128 audit.
    thresholds = {"autodiff": 2e-7, "residual": 2e-6, "hessian": 2e-5, "mismatch": 1e-4}
    checks["independent_autodiff_control"] = max_metric(controls, "autodiff_rel_error") < thresholds["autodiff"]
    checks["scalar_nonlinear_mismatch_detected"] = max_metric(controls, "residual_rel_error") > thresholds["mismatch"]
    checks["scalar_hessian_control"] = max_metric(controls, "dr_hessian_rel_error") < thresholds["hessian"]
    checks["scalar_hessian_symmetry"] = max_metric(controls, "symmetry_rel_error") < thresholds["hessian"]
    checks["full_mismatch_detected"] = max_metric(full, "residual_rel_error") > thresholds["mismatch"]
    checks["activation_mismatch_detected"] = max_metric(active, "residual_rel_error") > thresholds["mismatch"]
    checks["full_symmetry_failure_detected"] = max_metric(full, "symmetry_rel_error") > 1e-5  # tooling detection threshold
    audit_pass = all(checks.values())
    closure_pass = (max_metric(full, "residual_rel_error") < thresholds["residual"] and max_metric(full, "symmetry_rel_error") < thresholds["hessian"])

    output = {
        "schema": "tect/a1-production-functional-realisation-audit/1.0",
        "date": "2026-07-17",
        "claim_id": CLAIM,
        "verdict": "AUDIT-PASS-MISMATCH-DETECTED" if audit_pass else "AUDIT-FAIL",
        "full_production_closure": closure_pass,
        "checks": checks,
        "thresholds": thresholds,
        "maxima": {
            "control": {m: max_metric(controls, m) for m in ("autodiff_rel_error", "residual_rel_error", "dr_hessian_rel_error", "symmetry_rel_error")},
            "pinned_production": {m: max_metric(full, m) for m in ("autodiff_rel_error", "residual_rel_error", "dr_hessian_rel_error", "symmetry_rel_error")},
            "all_terms_activation": {m: max_metric(active, m) for m in ("autodiff_rel_error", "residual_rel_error", "dr_hessian_rel_error", "symmetry_rel_error")},
        },
        "rows": rows,
        "source_hashes": {"backend": sha256(backend_path), "config": sha256(config_path)},
        "known_obstruction": manifest["known_obstruction"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"P1 audit result: {output['verdict']}")
    print(f"  scalar control max residual error: {output['maxima']['control']['residual_rel_error']:.3e}")
    print(f"  pinned production max residual error: {output['maxima']['pinned_production']['residual_rel_error']:.3e}")
    print(f"  pinned production max symmetry error: {output['maxima']['pinned_production']['symmetry_rel_error']:.3e}")
    print(f"  evidence: {args.output}")
    reference_pass = True
    if args.reference_closure:
        reference = run_reference_closure(manifest, args.grid, args.reference_output)
        reference_pass = reference["verdict"] == "REFERENCE-CLOSURE-PASS"
        print(f"P1 reference result: {reference['verdict']}")
        print(f"  reference max variational error: {reference['maxima']['variational_rel_error']:.3e}")
        print(f"  reference max Hessian error: {reference['maxima']['dr_hessian_rel_error']:.3e}")
        print(f"  reference max symmetry error: {reference['maxima']['symmetry_rel_error']:.3e}")
        print(f"  reference evidence: {args.reference_output}")
    if args.assert_closure:
        return 0 if closure_pass else 1
    return 0 if audit_pass and reference_pass else 1


if __name__ == "__main__":
    sys.exit(main())
