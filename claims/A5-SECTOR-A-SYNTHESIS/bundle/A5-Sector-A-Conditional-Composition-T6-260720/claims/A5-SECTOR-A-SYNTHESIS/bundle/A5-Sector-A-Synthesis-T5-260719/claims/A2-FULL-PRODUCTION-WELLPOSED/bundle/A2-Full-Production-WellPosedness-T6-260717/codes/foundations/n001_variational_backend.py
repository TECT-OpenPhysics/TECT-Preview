#!/usr/bin/env python3
"""Standalone three-component variational backend for P1.

The sole authority is the explicit functional recorded by
``A1-PRODUCTION-FUNCTIONAL-REALISATION``.  This module does not import the
historical working-branch backend or the P1 verifier.  It exposes energy,
real-gradient residual, and a centred derivative of that gradient.

Convention
----------
``Psi`` has shape ``(3,Nx,Ny,Nz)`` and

    <u,v>_R = dV Re sum(conj(u) v).

The Class-II quadratic form contains all ``cJJ``, ``cJK``, and ``cKK`` terms.
Every physical coefficient and regularisation scale is supplied by ``params``;
there are no embedded production parameter values in this source.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import torch

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"


def _validate(psi: np.ndarray | torch.Tensor, params: dict[str, Any]) -> tuple[int, int, int]:
    if psi.ndim != 4 or int(psi.shape[0]) != 3:
        raise ValueError("Psi must have shape (3,Nx,Ny,Nz)")
    required = {
        "Lx", "Ly", "Lz", "q0", "r", "Z", "Y", "lambda", "gamma",
        "family_masses", "z0", "k_lock", "eta_shell", "alpha_X", "beta_X",
        "M_X", "cJJ", "cJK", "cKK", "rho_regularizer",
        "classii_mass_regularizer", "reference_hessian_step",
    }
    missing = sorted(required - set(params))
    if missing:
        raise KeyError(f"missing variational-backend parameters: {missing}")
    if len(params["family_masses"]) != 3 or len(params["z0"]) != 3:
        raise ValueError("family_masses and z0 must be length 3")
    if float(params["Y"]) <= 0.0 or float(params["M_X"]) <= 0.0:
        raise ValueError("Y and M_X must be positive")
    if float(params["rho_regularizer"]) <= 0.0 or float(params["classii_mass_regularizer"]) <= 0.0:
        raise ValueError("regularisers must be positive")
    return tuple(int(n) for n in psi.shape[1:])


def _dvol(shape: tuple[int, int, int], params: dict[str, Any]) -> float:
    return math.prod(float(params[key]) / n for key, n in zip(("Lx", "Ly", "Lz"), shape))


def _real_coordinates(psi: np.ndarray, requires_grad: bool = False) -> torch.Tensor:
    x = torch.stack((torch.tensor(psi.real, dtype=torch.float64), torch.tensor(psi.imag, dtype=torch.float64)))
    return x.requires_grad_(requires_grad)


def _complex(x: torch.Tensor) -> torch.Tensor:
    return torch.complex(x[0], x[1])


def _kmesh(shape: tuple[int, int, int], params: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    axes = [
        2.0 * math.pi * torch.fft.fftfreq(n, d=float(params[key]) / n, dtype=torch.float64)
        for key, n in zip(("Lx", "Ly", "Lz"), shape)
    ]
    kx, ky, kz = torch.meshgrid(*axes, indexing="ij")
    k2 = kx * kx + ky * ky + kz * kz
    return kx, ky, kz, torch.sqrt(k2)


def _grad_lap(psi: torch.Tensor, params: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    shape = tuple(int(n) for n in psi.shape[1:])
    kx, ky, kz, _ = _kmesh(shape, params)
    psi_k = torch.fft.fftn(psi, dim=(1, 2, 3))
    grad = torch.stack(
        [torch.fft.ifftn(1j * k.unsqueeze(0) * psi_k, dim=(1, 2, 3)) for k in (kx, ky, kz)],
        dim=0,
    )
    k2 = kx * kx + ky * ky + kz * kz
    lap = torch.fft.ifftn(-k2.unsqueeze(0) * psi_k, dim=(1, 2, 3))
    return grad, lap


def _generators() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    return (
        torch.tensor([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=torch.complex128),
        torch.tensor([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=torch.complex128),
        torch.tensor([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=torch.complex128),
    )


def energy_tensor(psi: torch.Tensor, params: dict[str, Any]) -> torch.Tensor:
    """Return the real discrete reference functional as a Torch scalar."""
    shape = _validate(psi, params)
    dvol = _dvol(shape, params)
    norm_sq = lambda value: torch.real(torch.conj(value) * value)
    rho = torch.sum(norm_sq(psi), dim=0)
    grad, lap = _grad_lap(psi, params)

    result = 0.5 * float(params["r"]) * torch.sum(rho)
    result = result + 0.5 * float(params["Z"]) * torch.sum(norm_sq(grad))
    result = result + 0.5 * float(params["Y"]) * torch.sum(norm_sq(lap))

    family = torch.diag(torch.tensor(params["family_masses"], dtype=torch.complex128))
    family_psi = torch.einsum("ab,bxyz->axyz", family, psi)
    result = result + 0.5 * torch.sum(torch.real(torch.sum(torch.conj(psi) * family_psi, dim=0)))
    z0 = torch.tensor(params["z0"], dtype=torch.complex128)
    projector = torch.outer(z0, torch.conj(z0)) / torch.real(torch.vdot(z0, z0))
    locked = torch.einsum("ab,bxyz->axyz", torch.eye(3, dtype=torch.complex128) - projector, psi)
    result = result + 0.5 * float(params["k_lock"]) * torch.sum(norm_sq(locked))

    result = result + 0.25 * float(params["lambda"]) * torch.sum(rho ** 2)
    result = result + (float(params["gamma"]) / 6.0) * torch.sum(rho ** 3)
    eta = float(params["eta_shell"])
    if eta != 0.0:
        _, _, _, kmag = _kmesh(shape, params)
        psi_k = torch.fft.fftn(psi, dim=(1, 2, 3))
        penalty = (kmag - float(params["q0"])).unsqueeze(0) * psi_k
        result = result + (0.5 * eta * torch.sum(norm_sq(penalty)) / math.prod(shape)) / dvol

    alpha = float(params["alpha_X"])
    beta = float(params["beta_X"])
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_jj = float(params["cJJ"]) * alpha * alpha / denominator
    b_jk = float(params["cJK"]) * alpha * beta / denominator
    c_kk = float(params["cKK"]) * beta * beta / denominator
    rho_safe = rho + float(params["rho_regularizer"])
    grad_rho = 2.0 * torch.real(torch.sum(torch.conj(psi).unsqueeze(0) * grad, dim=1))
    for generator in _generators():
        transformed = torch.einsum("ab,bxyz->axyz", generator, psi)
        moment = torch.sum(torch.conj(psi) * transformed, dim=0)
        current = torch.sum(torch.conj(grad) * transformed.unsqueeze(0), dim=1) + torch.sum(
            torch.conj(psi).unsqueeze(0) * torch.einsum("ab,ibxyz->iaxyz", generator, grad),
            dim=1,
        )
        covariant = current - (moment / rho_safe).unsqueeze(0) * grad_rho
        result = result + 0.5 * a_jj * torch.sum(norm_sq(current))
        result = result + b_jk * torch.sum(torch.real(torch.conj(current) * covariant))
        result = result + 0.5 * c_kk * torch.sum(norm_sq(covariant))
    return torch.real(result * dvol)


def energy(psi: np.ndarray, params: dict[str, Any]) -> float:
    array = np.asarray(psi, dtype=np.complex128)
    return float(energy_tensor(torch.tensor(array, dtype=torch.complex128), params).detach().cpu().item())


def residual(psi: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    """Return the real gradient with respect to the stated torus pairing."""
    array = np.asarray(psi, dtype=np.complex128)
    shape = _validate(array, params)
    x = _real_coordinates(array, requires_grad=True)
    gradient = torch.autograd.grad(energy_tensor(_complex(x), params), x)[0]
    value = (gradient[0].detach().cpu().numpy() + 1j * gradient[1].detach().cpu().numpy()) / _dvol(shape, params)
    return value.astype(np.complex128, copy=False)


def hessian_vec(psi: np.ndarray, direction: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    """Return the centred derivative of the real-gradient residual."""
    array = np.asarray(psi, dtype=np.complex128)
    vector = np.asarray(direction, dtype=np.complex128)
    _validate(array, params)
    if vector.shape != array.shape:
        raise ValueError("direction must have the same shape as Psi")
    step = float(params["reference_hessian_step"])
    if step <= 0.0:
        raise ValueError("reference_hessian_step must be positive")
    return (residual(array + step * vector, params) - residual(array - step * vector, params)) / (2.0 * step)
