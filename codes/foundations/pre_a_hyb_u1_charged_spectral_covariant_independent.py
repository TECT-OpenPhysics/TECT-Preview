#!/usr/bin/env python3
"""Independent verifier for the finite charged U(1) same-parent candidate.

This file intentionally reimplements the transport, spectral convolution, and
finite scalar action with a different site ordering; it does not import the
primary verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-hyb-u1-charged-spectral-covariant-manifest.json"
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R192 = REPO / "strategy" / "pre-a13-t058-bounded-complete-production-cylinder-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-hyb-u1-charged-spectral-covariant" / "independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".charged-independent-", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    tmp = Path(name)
    try:
        tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def idx(c: tuple[int, int, int], side: int) -> int:
    # Independent order: x is the fastest coordinate (primary uses x outermost).
    x, y, z = c
    return z * side * side + y * side + x


def sites(side: int) -> list[tuple[int, int, int]]:
    return [(x, y, z) for z in range(side) for y in range(side) for x in range(side)]


def fwd(c: tuple[int, int, int], axis: int, side: int) -> tuple[int, int, int]:
    out = list(c)
    out[axis] = (out[axis] + 1) % side
    return tuple(out)


def transporter(links: np.ndarray, side: int) -> np.ndarray:
    out = np.ones((side**3, side**3), dtype=np.complex128)
    for target in sites(side):
        it = idx(target, side)
        for source in sites(side):
            cur = list(source)
            phase = 1.0 + 0.0j
            for axis in (0, 1, 2):
                for _ in range((target[axis] - cur[axis]) % side):
                    phase *= np.conj(links[axis, idx(tuple(cur), side)])
                    cur[axis] = (cur[axis] + 1) % side
            if tuple(cur) != target:
                raise AssertionError("transport endpoint mismatch")
            out[it, idx(source, side)] = phase
    return out


def d_matrices(links: np.ndarray, side: int, lengths: tuple[float, float, float]) -> list[np.ndarray]:
    W = transporter(links, side)
    result: list[np.ndarray] = []
    for axis, length in enumerate(lengths):
        k = 2.0 * math.pi * np.fft.fftfreq(side, d=length / side)
        kernel = np.fft.ifft(1j * k)
        D = np.zeros((side**3, side**3), dtype=np.complex128)
        for target in sites(side):
            it = idx(target, side)
            for source in sites(side):
                if all(target[j] == source[j] for j in range(3) if j != axis):
                    delta = (target[axis] - source[axis]) % side
                    D[it, idx(source, side)] = kernel[delta] * W[it, idx(source, side)]
        result.append(D)
    return result


def transformed(links: np.ndarray, gauge: np.ndarray, side: int) -> np.ndarray:
    out = np.empty_like(links)
    for axis in range(3):
        for c in sites(side):
            i = idx(c, side)
            out[axis, i] = gauge[i] * links[axis, i] * np.conj(gauge[idx(fwd(c, axis, side), side)])
    return out


def as_grid(v: np.ndarray, side: int) -> np.ndarray:
    # Site index is x-fastest, matching Fortran flattening of an x,y,z grid.
    return v.reshape((side, side, side), order="F")


def as_vec(a: np.ndarray) -> np.ndarray:
    return np.asarray(a).reshape(-1, order="F")


def fft_derivative(v: np.ndarray, side: int, length: float, axis: int) -> np.ndarray:
    arr = as_grid(v, side)
    k = 2.0 * math.pi * np.fft.fftfreq(side, d=length / side)
    wave = np.fft.fftn(arr, axes=(0, 1, 2))
    shape = [1, 1, 1]
    shape[axis] = side
    mult = k.reshape(shape)
    return as_vec(np.fft.ifftn(1j * mult * wave, axes=(0, 1, 2)))


def core_energy(psi: np.ndarray, Ds: list[np.ndarray], params: dict[str, Any], side: int) -> float:
    L = sum((D.conj().T @ D for D in Ds), np.zeros_like(Ds[0]))
    rho = np.sum(np.abs(psi) ** 2, axis=0)
    value = 0.5 * float(params["r"]) * np.sum(rho)
    value += 0.5 * float(params["Z"]) * sum(np.sum(np.abs(D @ psi[a]) ** 2) for D in Ds for a in range(3))
    value += 0.5 * float(params["Y"]) * np.sum(np.abs(np.stack([L @ psi[a] for a in range(3)])) ** 2)
    masses = np.asarray(params["family_masses"], dtype=float)
    value += 0.5 * sum(masses[a] * np.sum(np.abs(psi[a]) ** 2) for a in range(3))
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    P = np.outer(z0, np.conj(z0)) / float(np.vdot(z0, z0).real)
    locked = (np.eye(3, dtype=np.complex128) - P) @ psi
    value += 0.5 * float(params["k_lock"]) * np.sum(np.abs(locked) ** 2)
    value += 0.25 * float(params["lambda"]) * np.sum(rho**2) + float(params["gamma"]) / 6.0 * np.sum(rho**3)
    return float(np.real(value))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--no-store", action="store_true")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads(A1.read_text(encoding="utf-8"))
    r192 = json.loads(R192.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual)})
        if not ok:
            raise AssertionError(f"{name}: {actual}")

    check("manifest candidate", manifest["candidate_id"] == "HYB-TECT-U1-CHARGED-SPECTRAL-0002", manifest.get("candidate_id"))
    check("comparison-only tier", manifest["tier"] == "T0" and manifest["claim_bearing"] is False, manifest.get("tier"))
    for key, item in manifest["source_authorities"].items():
        p = REPO / item["path"]
        check(f"authority hash {key}", p.is_file() and digest(p) == item["sha256"], digest(p) if p.is_file() else None)

    for rel, expected in manifest.get("artifact_hashes", {}).items():
        p = REPO / rel
        check(f"artifact {rel}", p.is_file() and digest(p) == expected, digest(p) if p.is_file() else None)
    params = a1["parameters"]
    side = int(manifest["finite_regulator"]["side"])
    lengths = tuple(float(params[k]) for k in ("Lx", "Ly", "Lz"))
    rng = np.random.default_rng(int(manifest["finite_regulator"]["test_seed"]) + 17)
    n = side**3
    psi = rng.normal(size=(3, n)) + 1j * rng.normal(size=(3, n))
    links = np.exp(1j * rng.normal(size=(3, n)))
    gauge = np.exp(1j * rng.normal(size=n))
    D = d_matrices(links, side, lengths)
    Dg = d_matrices(transformed(links, gauge, side), side, lengths)
    H = np.diag(gauge)
    d_err = [float(np.max(np.abs(x - H @ y @ H.conj().T))) for x, y in zip(Dg, D)]
    check("independent endpoint covariance", max(d_err) < 7e-12, d_err)
    L = sum((x.conj().T @ x for x in D), np.zeros_like(D[0]))
    Lg = sum((x.conj().T @ x for x in Dg), np.zeros_like(D[0]))
    l_err = float(np.max(np.abs(Lg - H @ L @ H.conj().T)))
    check("independent Laplacian covariance", l_err < 7e-12, l_err)
    off = np.ones_like(links)
    Do = d_matrices(off, side, lengths)
    fft_err = max(float(np.max(np.abs(Do[axis] @ psi[0] - fft_derivative(psi[0], side, lengths[axis], axis)))) for axis in range(3))
    check("independent gauge-off spectral derivative", fft_err < 7e-12, fft_err)
    e = core_energy(psi, D, params, side)
    eg = core_energy(gauge[None, :] * psi, Dg, params, side)
    check("independent scalar action orbit invariance", abs(e - eg) < 5e-10, {"before": e, "after": eg})
    eo = core_energy(psi, Do, params, side)
    # The independent gauge-off action is compared to an independently assembled FFT core.
    rho = np.sum(np.abs(psi) ** 2, axis=0)
    grad = [np.stack([fft_derivative(psi[a], side, lengths[axis], axis) for a in range(3)]) for axis in range(3)]
    lap = sum((Do[axis].conj().T @ Do[axis] for axis in range(3)), np.zeros_like(Do[0]))
    e_fft = 0.5 * float(params["r"]) * np.sum(rho)
    e_fft += 0.5 * float(params["Z"]) * sum(np.sum(np.abs(g) ** 2) for g in grad)
    e_fft += 0.5 * float(params["Y"]) * np.sum(np.abs(np.stack([lap @ psi[a] for a in range(3)])) ** 2)
    masses = np.asarray(params["family_masses"], dtype=float)
    e_fft += 0.5 * sum(masses[a] * np.sum(np.abs(psi[a]) ** 2) for a in range(3))
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    locked = (np.eye(3, dtype=np.complex128) - np.outer(z0, np.conj(z0)) / np.vdot(z0, z0).real) @ psi
    e_fft += 0.5 * float(params["k_lock"]) * np.sum(np.abs(locked) ** 2)
    e_fft += 0.25 * float(params["lambda"]) * np.sum(rho**2) + float(params["gamma"]) / 6.0 * np.sum(rho**3)
    check("independent gauge-off action recovery", abs(eo - float(np.real(e_fft))) < 5e-10, {"matrix": eo, "fft": e_fft})
    mu = Fraction(str(params["r"])) - Fraction(str(params["Z"])) ** 2 / (4 * Fraction(str(params["Y"])))
    check("independent quadratic coercivity", mu > 0, mu)
    aa = Fraction(str(params["cJJ"])) * Fraction(str(params["alpha_X"])) ** 2 / (Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"])) )
    bb = Fraction(str(params["cJK"])) * Fraction(str(params["alpha_X"])) * Fraction(str(params["beta_X"])) / (Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"])) )
    cc = Fraction(str(params["cKK"])) * Fraction(str(params["beta_X"])) ** 2 / (Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"])) )
    check("independent Class-II determinant", aa * cc - bb**2 > 0, aa * cc - bb**2)
    check("independent Gibbs fixture", ((Fraction(11, 5) - Fraction(7, 2) * Fraction(2, 7) ** 2) + Fraction(1, 1) / Fraction(7, 2) * (-Fraction(7, 2) * Fraction(11, 5) + Fraction(7, 2) ** 2 * Fraction(2, 7) ** 2)) == 0, "exact")
    cross = manifest["r192_crosswalk"]
    check("independent R-192 boundary", cross["first_missing_slot"] == r192["registered_inputs"]["first_failure_slot"] == "heat_root_incidence", cross["first_missing_slot"])
    check("independent owner nonclaim", cross["production_owner"] is False and not any(cross[k] for k in ("heat_root_incidence", "root_filtration", "conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger")), cross)
    verdict = "HYB-TECT-U1-CHARGED-SPECTRAL-INDEPENDENT-PASS" if len(checks) == sum(int(x["pass"]) for x in checks) else "HYB-TECT-U1-CHARGED-SPECTRAL-INDEPENDENT-FAIL"
    payload = {"schema": "tect/pre-a-hyb-u1-charged-spectral-covariant-independent/1.0", "candidate_id": manifest["candidate_id"], "verdict": verdict, "assertion_count": len(checks), "assertions": checks, "derived": {"D_covariance_max_error": max(d_err), "L_covariance_max_error": l_err, "spectral_derivative_max_error": fft_err, "r192_first_missing_slot": cross["first_missing_slot"], "production_owner": cross["production_owner"]}, "boundary": manifest["boundary"]}
    if not args.no_store:
        store_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"{sum(int(x['pass']) for x in checks)}/{len(checks)} PASS")
    print(verdict)
    print("R-192 first missing:", cross["first_missing_slot"])
    return 0 if verdict.endswith("-PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
