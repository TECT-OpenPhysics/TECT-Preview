#!/usr/bin/env python3
"""Device- and precision-variable independent implementation for P3 audits.

This module reproduces the P1 reference functional without importing its
backend.  It is audit code, not a replacement production solver.  Parameters,
device, and complex dtype are explicit inputs.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import torch

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"


def real_dtype(complex_dtype: torch.dtype) -> torch.dtype:
    if complex_dtype == torch.complex128:
        return torch.float64
    if complex_dtype == torch.complex64:
        return torch.float32
    raise ValueError(f"unsupported complex dtype: {complex_dtype}")


def kmesh(shape: tuple[int, int, int], params: dict[str, Any], device: torch.device, dtype: torch.dtype) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    axes = [2.0 * math.pi * torch.fft.fftfreq(n, d=float(params[key]) / n, dtype=dtype, device=device) for key, n in zip(("Lx", "Ly", "Lz"), shape)]
    kx, ky, kz = torch.meshgrid(*axes, indexing="ij")
    k2 = kx * kx + ky * ky + kz * kz
    return kx, ky, kz, torch.sqrt(k2)


def grad_lap(psi: torch.Tensor, params: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    shape = tuple(int(n) for n in psi.shape[1:])
    kx, ky, kz, _ = kmesh(shape, params, psi.device, psi.real.dtype)
    psi_k = torch.fft.fftn(psi, dim=(1, 2, 3))
    grad = torch.stack([torch.fft.ifftn(1j * wave.unsqueeze(0) * psi_k, dim=(1, 2, 3)) for wave in (kx, ky, kz)], dim=0)
    k2 = kx * kx + ky * ky + kz * kz
    lap = torch.fft.ifftn(-k2.unsqueeze(0) * psi_k, dim=(1, 2, 3))
    return grad, lap


def generators(device: torch.device, dtype: torch.dtype) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    return (
        torch.tensor([[0, 1, 0], [1, 0, 0], [0, 0, 0]], device=device, dtype=dtype),
        torch.tensor([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], device=device, dtype=dtype),
        torch.tensor([[1, 0, 0], [0, -1, 0], [0, 0, 0]], device=device, dtype=dtype),
    )


def energy_tensor(psi: torch.Tensor, params: dict[str, Any]) -> torch.Tensor:
    if psi.ndim != 4 or int(psi.shape[0]) != 3:
        raise ValueError("Psi must have shape (3,Nx,Ny,Nz)")
    shape = tuple(int(n) for n in psi.shape[1:])
    device, complex_dtype = psi.device, psi.dtype
    dtype = psi.real.dtype
    dvol = math.prod(float(params[key]) / n for key, n in zip(("Lx", "Ly", "Lz"), shape))
    norm_sq = lambda value: torch.real(torch.conj(value) * value)
    rho = torch.sum(norm_sq(psi), dim=0)
    grad, lap = grad_lap(psi, params)

    result = 0.5 * float(params["r"]) * torch.sum(rho)
    result = result + 0.5 * float(params["Z"]) * torch.sum(norm_sq(grad))
    result = result + 0.5 * float(params["Y"]) * torch.sum(norm_sq(lap))
    family = torch.diag(torch.tensor(params["family_masses"], device=device, dtype=complex_dtype))
    family_psi = torch.einsum("ab,bxyz->axyz", family, psi)
    result = result + 0.5 * torch.sum(torch.real(torch.sum(torch.conj(psi) * family_psi, dim=0)))
    z0 = torch.tensor(params["z0"], device=device, dtype=complex_dtype)
    projector = torch.outer(z0, torch.conj(z0)) / torch.real(torch.vdot(z0, z0))
    identity = torch.eye(3, device=device, dtype=complex_dtype)
    locked = torch.einsum("ab,bxyz->axyz", identity - projector, psi)
    result = result + 0.5 * float(params["k_lock"]) * torch.sum(norm_sq(locked))
    result = result + 0.25 * float(params["lambda"]) * torch.sum(rho ** 2)
    result = result + (float(params["gamma"]) / 6.0) * torch.sum(rho ** 3)

    eta = float(params["eta_shell"])
    if eta != 0.0:
        _, _, _, kmag = kmesh(shape, params, device, dtype)
        psi_k = torch.fft.fftn(psi, dim=(1, 2, 3))
        penalty = (kmag - float(params["q0"])).unsqueeze(0) * psi_k
        result = result + (0.5 * eta * torch.sum(norm_sq(penalty)) / math.prod(shape)) / dvol

    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_jj = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_jk = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_kk = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    rho_safe = rho + torch.tensor(float(params["rho_regularizer"]), device=device, dtype=dtype)
    grad_rho = 2.0 * torch.real(torch.sum(torch.conj(psi).unsqueeze(0) * grad, dim=1))
    for generator in generators(device, complex_dtype):
        transformed = torch.einsum("ab,bxyz->axyz", generator, psi)
        moment = torch.sum(torch.conj(psi) * transformed, dim=0)
        current = torch.sum(torch.conj(grad) * transformed.unsqueeze(0), dim=1) + torch.sum(
            torch.conj(psi).unsqueeze(0) * torch.einsum("ab,ibxyz->iaxyz", generator, grad), dim=1
        )
        covariant = current - (moment / rho_safe).unsqueeze(0) * grad_rho
        result = result + 0.5 * a_jj * torch.sum(norm_sq(current))
        result = result + b_jk * torch.sum(torch.real(torch.conj(current) * covariant))
        result = result + 0.5 * c_kk * torch.sum(norm_sq(covariant))
    return torch.real(result * dvol)


def energy_residual(array: np.ndarray, params: dict[str, Any], device_name: str, complex_dtype: torch.dtype) -> tuple[float, np.ndarray]:
    device = torch.device(device_name)
    dtype = real_dtype(complex_dtype)
    real = torch.tensor(np.asarray(array).real, device=device, dtype=dtype)
    imag = torch.tensor(np.asarray(array).imag, device=device, dtype=dtype)
    coordinates = torch.stack((real, imag)).requires_grad_(True)
    psi = torch.complex(coordinates[0], coordinates[1])
    energy = energy_tensor(psi, params)
    gradient = torch.autograd.grad(energy, coordinates)[0]
    shape = tuple(int(n) for n in psi.shape[1:])
    dvol = math.prod(float(params[key]) / n for key, n in zip(("Lx", "Ly", "Lz"), shape))
    residual = (gradient[0] + 1j * gradient[1]) / dvol
    return float(energy.detach().cpu().item()), residual.detach().cpu().numpy().astype(np.complex128)
