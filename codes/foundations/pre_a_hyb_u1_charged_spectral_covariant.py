#!/usr/bin/env python3
"""Primary finite same-parent charged U(1) spectral covariantization audit.

This is a T0 candidate screen.  It keeps the A1 F_ref family/lock and
spectral coefficients, replaces only the spatial derivative by an endpoint
parallel-transported spectral convolution, and checks the declared finite
gauge-off reduction.  It does not claim an R-192 production owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-hyb-u1-charged-spectral-covariant-manifest.json"
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R192 = REPO / "strategy" / "pre-a13-t058-bounded-complete-production-cylinder-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "HYB0002.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-hyb-u1-charged-spectral-covariant" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".charged-hyb-", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, default=str) + "\n", encoding="utf-8")
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def site_index(c: tuple[int, int, int], side: int) -> int:
    return c[0] * side * side + c[1] * side + c[2]


def all_sites(side: int) -> list[tuple[int, int, int]]:
    return [(x, y, z) for x in range(side) for y in range(side) for z in range(side)]


def forward(c: tuple[int, int, int], axis: int, side: int) -> tuple[int, int, int]:
    out = list(c)
    out[axis] = (out[axis] + 1) % side
    return tuple(out)


def path_transport(links: np.ndarray, side: int) -> np.ndarray:
    sites = all_sites(side)
    n = len(sites)
    transport = np.ones((n, n), dtype=np.complex128)
    for x in sites:
        ix = site_index(x, side)
        for y in sites:
            iy = site_index(y, side)
            cur = list(y)
            phase = 1.0 + 0.0j
            for axis in range(3):
                steps = (x[axis] - cur[axis]) % side
                for _ in range(steps):
                    cc = tuple(cur)
                    phase *= np.conj(links[axis, site_index(cc, side)])
                    cur[axis] = (cur[axis] + 1) % side
            if tuple(cur) != x:
                raise AssertionError("canonical path failed to reach endpoint")
            transport[ix, iy] = phase
    return transport


def derivative_matrices(links: np.ndarray, side: int, lengths: tuple[float, float, float]) -> list[np.ndarray]:
    sites = all_sites(side)
    n = len(sites)
    transport = path_transport(links, side)
    matrices: list[np.ndarray] = []
    for axis, length in enumerate(lengths):
        frequencies = 2.0 * math.pi * np.fft.fftfreq(side, d=length / side)
        kernel = np.fft.ifft(1j * frequencies)
        matrix = np.zeros((n, n), dtype=np.complex128)
        for x in sites:
            ix = site_index(x, side)
            for y in sites:
                iy = site_index(y, side)
                if all(x[j] == y[j] for j in range(3) if j != axis):
                    delta = (x[axis] - y[axis]) % side
                    matrix[ix, iy] = kernel[delta] * transport[ix, iy]
        matrices.append(matrix)
    return matrices


def transformed_links(links: np.ndarray, gauge: np.ndarray, side: int) -> np.ndarray:
    out = np.empty_like(links)
    for axis, c in ((a, c) for a in range(3) for c in all_sites(side)):
        i = site_index(c, side)
        out[axis, i] = gauge[i] * links[axis, i] * np.conj(gauge[site_index(forward(c, axis, side), side)])
    return out


def generators() -> np.ndarray:
    return np.array(
        [
            [[0, 1, 0], [1, 0, 0], [0, 0, 0]],
            [[0, -1j, 0], [1j, 0, 0], [0, 0, 0]],
            [[1, 0, 0], [0, -1, 0], [0, 0, 0]],
        ],
        dtype=np.complex128,
    )


def energy_from_fields(
    psi: np.ndarray,
    grad: np.ndarray,
    lap: np.ndarray,
    shell_penalty: np.ndarray | None,
    params: dict[str, Any],
) -> float:
    shape = tuple(int(v) for v in psi.shape[1:])
    dvol = math.prod(float(params[key]) / n for key, n in zip(("Lx", "Ly", "Lz"), shape))
    sites = math.prod(shape)
    rho = np.sum(np.abs(psi) ** 2, axis=0)
    result = 0.5 * float(params["r"]) * np.sum(rho)
    result += 0.5 * float(params["Z"]) * np.sum(np.abs(grad) ** 2)
    result += 0.5 * float(params["Y"]) * np.sum(np.abs(lap) ** 2)
    masses = np.asarray(params["family_masses"], dtype=float).reshape((3,) + (1,) * 3)
    result += 0.5 * np.sum(masses * np.abs(psi) ** 2)
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    projector = np.outer(z0, np.conj(z0)) / float(np.vdot(z0, z0).real)
    locked = np.einsum("ab,bxyz->axyz", np.eye(3, dtype=np.complex128) - projector, psi)
    result += 0.5 * float(params["k_lock"]) * np.sum(np.abs(locked) ** 2)
    result += 0.25 * float(params["lambda"]) * np.sum(rho**2)
    result += float(params["gamma"]) / 6.0 * np.sum(rho**3)
    eta = float(params["eta_shell"])
    if eta != 0.0:
        if shell_penalty is None:
            raise ValueError("active shell term requires a penalty")
        result += (0.5 * eta * np.sum(np.abs(shell_penalty) ** 2) / sites) / dvol

    alpha = float(params["alpha_X"])
    beta = float(params["beta_X"])
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_jj = float(params["cJJ"]) * alpha * alpha / denominator
    b_jk = float(params["cJK"]) * alpha * beta / denominator
    c_kk = float(params["cKK"]) * beta * beta / denominator
    rho_safe = rho + float(params["rho_regularizer"])
    gset = generators()
    for g in gset:
        transformed = np.einsum("ab,bxyz->axyz", g, psi)
        moment = np.sum(np.conj(psi) * transformed, axis=0)
        for axis in range(3):
            dpsi = grad[axis]
            gdpsi = np.einsum("ab,bxyz->axyz", g, dpsi)
            current = np.sum(np.conj(dpsi) * transformed + np.conj(psi) * gdpsi, axis=0)
            grad_rho = 2.0 * np.real(np.sum(np.conj(psi) * dpsi, axis=0))
            covariant = current - (moment / rho_safe) * grad_rho
            result += 0.5 * a_jj * np.sum(np.abs(current) ** 2)
            result += b_jk * np.sum(np.real(np.conj(current) * covariant))
            result += 0.5 * c_kk * np.sum(np.abs(covariant) ** 2)
    return float(np.real(result * dvol))


def energy_spectral(psi_flat: np.ndarray, side: int, lengths: tuple[float, float, float], params: dict[str, Any]) -> float:
    psi = psi_flat.reshape((3, side, side, side))
    axes = [
        2.0 * math.pi * np.fft.fftfreq(side, d=length / side)
        for length in lengths
    ]
    kx, ky, kz = np.meshgrid(*axes, indexing="ij")
    wave = np.fft.fftn(psi, axes=(1, 2, 3))
    grad = np.stack([np.fft.ifftn(1j * k * wave, axes=(1, 2, 3)) for k in (kx, ky, kz)], axis=0)
    lap = np.fft.ifftn(-(kx * kx + ky * ky + kz * kz) * wave, axes=(1, 2, 3))
    shell = None
    if float(params["eta_shell"]) != 0.0:
        shell = (np.sqrt(kx * kx + ky * ky + kz * kz) - float(params["q0"])) * wave
    return energy_from_fields(psi, grad, lap, shell, params)


def energy_covariant(
    links: np.ndarray,
    psi_flat: np.ndarray,
    side: int,
    lengths: tuple[float, float, float],
    params: dict[str, Any],
) -> tuple[float, list[np.ndarray], np.ndarray]:
    matrices = derivative_matrices(links, side, lengths)
    laplacian = sum((matrix.conj().T @ matrix for matrix in matrices), np.zeros_like(matrices[0]))
    dpsi = np.stack([np.stack([matrix @ psi_flat[a] for a in range(3)], axis=0) for matrix in matrices], axis=0)
    lpsi = np.stack([laplacian @ psi_flat[a] for a in range(3)], axis=0)
    shell = None
    if float(params["eta_shell"]) != 0.0:
        values, vectors = np.linalg.eigh(laplacian)
        root = vectors @ np.diag(np.sqrt(np.maximum(values, 0.0))) @ vectors.conj().T
        shell = ((root - float(params["q0"]) * np.eye(len(psi_flat[0]))) @ psi_flat).reshape((3, side, side, side))
    energy = energy_from_fields(
        psi_flat.reshape((3, side, side, side)),
        dpsi.reshape((3, 3, side, side, side)),
        lpsi.reshape((3, side, side, side)),
        shell,
        params,
    )
    return energy, matrices, laplacian


def find_lake() -> Path | None:
    found = shutil.which("lake")
    if found:
        return Path(found)
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    return candidate if candidate.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads(A1.read_text(encoding="utf-8"))
    r192 = json.loads(R192.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    check("manifest identity", manifest["audit_id"] == "PRE-A-HYB-U1-CHARGED-SPECTRAL-COVARIANT", manifest["audit_id"])
    check("claim nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", manifest["claim_bearing"])
    check("finite parent explicit", manifest["finite_regulator"]["side"] == 4 and manifest["finite_regulator"]["gauge_group"] == "U(1)", manifest["finite_regulator"])
    for key, item in manifest["source_authorities"].items():
        path = REPO / item["path"]
        check(f"authority {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None)
    check("A1 F_ref and F_decl remain explicit", "F_ref" in A1.read_text(encoding="utf-8") and "F_decl" in A1.read_text(encoding="utf-8"), True)
    for rel, expected in manifest.get("artifact_hashes", {}).items():
        path = REPO / rel
        check(f"artifact {rel}", path.is_file() and sha256(path) == expected, sha256(path) if path.is_file() else None)
    params = a1["parameters"]
    side = int(manifest["finite_regulator"]["side"])
    lengths = tuple(float(params[key]) for key in ("Lx", "Ly", "Lz"))
    n = side**3
    rng = np.random.default_rng(int(manifest["finite_regulator"]["test_seed"]))
    psi = rng.normal(size=(3, n)) + 1j * rng.normal(size=(3, n))
    angles = rng.normal(size=(3, n))
    links = np.exp(1j * angles)
    gauge = np.exp(1j * rng.normal(size=n))
    links_h = transformed_links(links, gauge, side)
    energy, matrices, laplacian = energy_covariant(links, psi, side, lengths, params)
    energy_h, matrices_h, laplacian_h = energy_covariant(links_h, gauge[None, :] * psi, side, lengths, params)
    H = np.diag(gauge)
    D_errors = [float(np.max(np.abs(dh - H @ d @ H.conj().T))) for d, dh in zip(matrices, matrices_h)]
    L_error = float(np.max(np.abs(laplacian_h - H @ laplacian @ H.conj().T)))
    check("D endpoint covariance", max(D_errors) < 5e-12, D_errors)
    check("L endpoint covariance", L_error < 5e-12, L_error)
    check("full finite action orbit invariance", abs(energy_h - energy) < 2e-10, {"before": energy, "after": energy_h})
    off_links = np.ones_like(links)
    covariant_off, _, _ = energy_covariant(off_links, psi, side, lengths, params)
    spectral_off = energy_spectral(psi, side, lengths, params)
    check("exact gauge-off F_ref recovery", abs(covariant_off - spectral_off) < 2e-10, {"covariant": covariant_off, "spectral": spectral_off})
    check("quadratic core coercivity", Fraction(str(params["Y"])) > 0 and Fraction(str(params["r"])) - Fraction(str(params["Z"])) ** 2 / (4 * Fraction(str(params["Y"]))) > 0, "mu_eff>0")
    aa = Fraction(str(params["cJJ"])) * Fraction(str(params["alpha_X"])) ** 2 / (Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"])))
    bb = Fraction(str(params["cJK"])) * Fraction(str(params["alpha_X"])) * Fraction(str(params["beta_X"])) / (Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"])))
    cc = Fraction(str(params["cKK"])) * Fraction(str(params["beta_X"])) ** 2 / (Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"])))
    check("Class-II PSD", aa > 0 and cc > 0 and aa * cc - bb * bb > 0, {"a": str(aa), "b": str(bb), "c": str(cc)})
    lam = Fraction(str(params["lambda"]))
    gam = Fraction(str(params["gamma"]))
    check("sextic finite lower bound", lam < 0 and gam > 0 and lam**3 / (12 * gam**2) < 0, {"lambda": str(lam), "gamma": str(gam)})
    beta = Fraction(7, 2)
    fp = Fraction(2, 7)
    fpp = Fraction(11, 5)
    dyn_residual = (fpp - beta * fp**2) + (Fraction(1, 1) / beta) * (-beta * fpp + beta**2 * fp**2)
    check("formal identity-mobility Gibbs residual", dyn_residual == 0, str(dyn_residual))
    cross = manifest["r192_crosswalk"]
    check("R-192 first failure preserved", cross["first_missing_slot"] == r192["registered_inputs"]["first_failure_slot"] == "heat_root_incidence", cross)
    check("R-192 owner fields absent", not any(cross[name] for name in ("heat_root_incidence", "root_filtration", "conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger")), cross)
    check("candidate remains comparison-only", cross["production_owner"] is False and manifest["selection"]["admission"] == "comparison_candidate_only", manifest["selection"])

    lake = find_lake()
    lean_run = subprocess.run([str(lake), "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, capture_output=True, check=False) if lake else None
    check("Lean compile", lean_run is not None and lean_run.returncode == 0, lean_run.returncode if lean_run else None)
    check("Lean no forbidden escape", lean_run is not None and not any(tok in LEAN_ENTRYPOINT.read_text(encoding="utf-8").split() for tok in ("sorry", "admit", "axiom", "unsafe")), "clean")

    passed = sum(row["pass"] for row in rows)
    verdict = "HYB-TECT-U1-CHARGED-SPECTRAL-PRIMARY-PASS" if passed == len(rows) else "HYB-TECT-U1-CHARGED-SPECTRAL-PRIMARY-FAIL"
    payload = {
        "schema": "tect/pre-a-hyb-u1-charged-spectral-covariant-primary/1.0",
        "script_version": __version__,
        "audit_id": manifest["audit_id"],
        "candidate_id": manifest["candidate_id"],
        "verdict": verdict,
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "D_covariance_max_error": max(D_errors),
            "L_covariance_max_error": L_error,
            "gauge_off_energy_abs_error": abs(covariant_off - spectral_off),
            "mu_eff": str(Fraction(str(params["r"])) - Fraction(str(params["Z"])) ** 2 / (4 * Fraction(str(params["Y"])))),
            "classii_determinant": str(aa * cc - bb * bb),
            "r192_first_missing_slot": cross["first_missing_slot"],
            "production_owner": cross["production_owner"]
        },
        "boundary": manifest["boundary"]
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"{passed}/{len(rows)} PASS")
    print(verdict)
    print("R-192 first missing:", cross["first_missing_slot"])
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
