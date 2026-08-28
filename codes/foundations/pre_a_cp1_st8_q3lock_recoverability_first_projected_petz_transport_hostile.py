#!/usr/bin/env python3
"""Hostile omitted-displacement-budget mutation for R-396."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-recoverability-first-projected-petz-transport-manifest.json"
PARENT_PATH = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer.py"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "hostile.json"


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location("r391_hostile_parent", PARENT_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load R-391")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


PARENT = load_parent()


def td(left: np.ndarray, right: np.ndarray) -> float:
    return PARENT.trace_distance(left, right)


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); cfg = manifest["finite_fixture"]
    tolerance = float(cfg["numerical_tolerance"]); threshold = float(cfg["hostile_threshold"]); positivity = float(cfg["positivity_tolerance"])
    best: dict[str, Any] | None = None
    for volume, dimension in ((4, 3),):
        values, vectors = np.linalg.eigh(PARENT.build_system(dimension, volume, cfg)); state = PARENT.gibbs_from_spectrum(values, vectors, 1.0)
        for part in PARENT.tripartitions(volume, [2], [1, 2]):
            dims = (dimension**len(part["core"]), dimension**len(part["buffer"]), dimension**len(part["environment"])); abc_sites = part["core"] + part["buffer"] + part["environment"]
            rho_abc = PARENT.partial_trace_sites(state, dimension, volume, abc_sites); rho_ab = PARENT.partial_trace_groups(rho_abc, list(dims), [0, 1])
            local_values, local_vectors = np.linalg.eigh(PARENT.build_system(dimension, 2, cfg)); shifted = local_values - local_values.min()
            for raw_energy in cfg["energy_windows"]:
                energy = float(Fraction(raw_energy)); mask = shifted <= energy + positivity; P = PARENT.hermitian(local_vectors[:, mask] @ local_vectors[:, mask].conj().T)
                lifted = np.kron(P, np.eye(dims[1] * dims[2], dtype=complex)); raw_sigma = PARENT.hermitian(lifted @ rho_abc @ lifted); mass = float(np.trace(raw_sigma).real); sigma = PARENT.hermitian(raw_sigma / mass)
                sigma_ab = PARENT.partial_trace_groups(sigma, list(dims), [0, 1]); sigma_b = PARENT.partial_trace_groups(sigma, list(dims), [1]); sigma_bc = PARENT.partial_trace_groups(sigma, list(dims), [1, 2])
                rec_sigma = PARENT.petz_recovery(sigma_ab, sigma_bc, sigma_b, dims, positivity); rec_rho = PARENT.petz_recovery(rho_ab, sigma_bc, sigma_b, dims, positivity)
                dabc = td(rho_abc, sigma); dab = td(rho_ab, sigma_ab); projected = td(sigma, rec_sigma); transported = td(rho_abc, rec_rho); genuine = projected + dabc + dab; mutated = projected; gap = transported - mutated
                candidate = {"volume": volume, "dimension": dimension, "beta": 1.0, "core": part["core"], "buffer": part["buffer"], "environment": part["environment"], "orientation": part["orientation"], "energy_window": energy, "projection_mass": mass, "delta_abc": dabc, "delta_ab": dab, "projected_error": projected, "transported_error": transported, "genuine_budget": genuine, "mutated_budget_without_displacements": mutated, "mutation_gap": gap}
                if best is None or gap > best["mutation_gap"]: best = candidate
    if best is None: raise AssertionError("no hostile candidate")
    checks = [
        {"name": "transport visible", "status": "PASS" if best["transported_error"] > threshold else "FAIL", "actual": best["transported_error"], "expected": f">{threshold}"},
        {"name": "genuine triangle budget", "status": "PASS" if best["transported_error"] <= best["genuine_budget"] + tolerance else "FAIL", "actual": [best["transported_error"], best["genuine_budget"]], "expected": "transported <= genuine budget"},
        {"name": "omitted displacement terms caught", "status": "PASS" if best["mutation_gap"] > threshold else "FAIL", "actual": [best["transported_error"], best["mutated_budget_without_displacements"], best["mutation_gap"]], "expected": "transported > projected error alone"}
    ]
    if any(item["status"] != "PASS" for item in checks): raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r396-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-396", "exploration_id": "EXP-001239", "verdict": "PASS", "checks": checks, "derived": best}
    save(path, payload)
    print(f"R-396 HOSTILE PASS 3/3 transported={best['transported_error']:.6g} mutated_gap={best['mutation_gap']:.6g} OMITTED-DISPLACEMENT-MUTATION-CAUGHT")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); run(parser.parse_args().output)


if __name__ == "__main__": main()
