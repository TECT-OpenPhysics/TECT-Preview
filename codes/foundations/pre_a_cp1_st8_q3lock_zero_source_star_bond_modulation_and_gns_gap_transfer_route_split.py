#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.0 route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-zero-source-star-bond-modulation-and-gns-gap-transfer-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Labelled fixture inputs only. All reported quantities are derived below.
STAR_INPUTS = {"dimension": 3, "z": 6, "J": 8, "Gamma": 96, "alpha_den": 100, "beta_den": 1000}
RADIUS_INPUTS = {"C_alpha": 16, "C_beta": 8, "a_2": 1, "b_2": 1, "g_0": 1, "N_1": 10}
BOND_INPUTS = {"phase": -1}
SHELL_INPUTS = {"radius": 4, "geometric_base_den": 2}
GNS_INPUTS = {"Delta": 3, "coefficient_num": 2, "coefficient_den": 5, "hbar": 1}
NEGATIVE_INPUTS = {"sample_n": 7, "uniform_lower_gap": 1, "hbar": 1}


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def operator_norm(matrix: sp.Matrix) -> sp.Expr:
    gram = sp.simplify(matrix.H * matrix)
    eigenvalues = [sp.simplify(value) for value in gram.eigenvals()]
    return sp.sqrt(max(eigenvalues))


def star_fixture() -> dict[str, Any]:
    dimension = sp.Integer(STAR_INPUTS["dimension"])
    z = sp.Integer(STAR_INPUTS["z"])
    coupling = sp.Integer(STAR_INPUTS["J"])
    high_gap = sp.Integer(STAR_INPUTS["Gamma"])
    labels = {
        "+": (sp.Integer(0), sp.Integer(1)),
        "-": (sp.Integer(0), sp.Integer(-1)),
        "h": (high_gap, sp.Integer(0)),
    }

    def edge(a: str, b: str) -> sp.Expr:
        ka, sa = labels[a]
        kb, sb = labels[b]
        return sp.factor((ka + kb) / z + coupling * (1 - sa * sb))

    energies: dict[tuple[str, ...], sp.Expr] = {}
    for configuration in product(labels, repeat=int(dimension + 1)):
        energies[configuration] = sp.factor(
            sum(edge(configuration[0], configuration[index]) for index in range(1, int(dimension + 1)))
        )
    positives = sorted(value for value in energies.values() if value > 0)
    alpha = sp.Rational(1, STAR_INPUTS["alpha_den"])
    beta = sp.Rational(1, STAR_INPUTS["beta_den"])
    gap = positives[0]
    low_disagreement = energies[("+", "-", "+", "+")]
    high_neighbour = energies[("+", "h", "+", "+")]
    high_centre = energies[("h", "+", "+", "+")]
    formula_gap = sp.Min(2 * coupling, high_gap / z + coupling)
    return {
        "z": int(z),
        "dimension": int(dimension),
        "J": coupling,
        "Gamma": high_gap,
        "kernel_dimension": sum(value == 0 for value in energies.values()),
        "low_disagreement": low_disagreement,
        "high_neighbour": high_neighbour,
        "high_centre": high_centre,
        "gap": gap,
        "formula_gap": formula_gap,
        "alpha": alpha,
        "beta": beta,
        "normalized_beta": sp.factor(dimension * beta / gap),
    }


def radius_fixture() -> dict[str, Any]:
    c_alpha = sp.Integer(RADIUS_INPUTS["C_alpha"])
    c_beta = sp.Integer(RADIUS_INPUTS["C_beta"])
    a_2 = sp.Integer(RADIUS_INPUTS["a_2"])
    b_2 = sp.Integer(RADIUS_INPUTS["b_2"])
    g_0 = sp.Integer(RADIUS_INPUTS["g_0"])
    n_1 = sp.Integer(RADIUS_INPUTS["N_1"])
    square_threshold = sp.sqrt(c_alpha / a_2)
    cube_threshold = sp.real_root(3 * c_beta / (g_0 * b_2), 3)
    n_star = 1 + max(int(n_1), int(sp.floor(square_threshold)), int(sp.floor(cube_threshold)))
    alpha_at = sp.factor(c_alpha / n_star**2)
    beta_at = sp.factor(3 * c_beta / (g_0 * n_star**3))
    return {
        "C_alpha": c_alpha,
        "C_beta": c_beta,
        "a_2": a_2,
        "b_2": b_2,
        "g_0": g_0,
        "N_1": int(n_1),
        "N_star": n_star,
        "strict_alpha_at_N_star": bool(alpha_at < a_2),
        "strict_beta_at_N_star": bool(beta_at < b_2),
        "alpha_at_N_star": alpha_at,
        "beta_prime_at_N_star": beta_at,
    }


def bond_fixture() -> dict[str, Any]:
    phase = sp.Integer(BOND_INPUTS["phase"])
    modulation = sp.diag(1, phase)
    offdiagonal = sp.Matrix([[0, 1], [1, 0]])
    diagonal = sp.diag(2, -1)
    off_distance = sp.simplify(operator_norm(modulation.H * offdiagonal * modulation - offdiagonal))
    diagonal_distance = sp.simplify(operator_norm(modulation.H * diagonal * modulation - diagonal))
    return {
        "offdiagonal_modulation_distance": off_distance,
        "diagonal_modulation_distance": diagonal_distance,
        "nonzero_time_supremum": off_distance,
    }


def shell_fixture() -> dict[str, Any]:
    radius = SHELL_INPUTS["radius"]
    denominator = SHELL_INPUTS["geometric_base_den"]
    base = sp.Rational(1, denominator)
    tail = sp.simplify(base ** (radius + 1) / (1 - base))
    return {"radius": radius, "tail": tail, "cauchy_bound": tail}


def gns_fixture() -> dict[str, Any]:
    delta_gap = sp.Integer(GNS_INPUTS["Delta"])
    coefficient = sp.Rational(GNS_INPUTS["coefficient_num"], GNS_INPUTS["coefficient_den"])
    hbar = sp.Integer(GNS_INPUTS["hbar"])
    hamiltonian = sp.diag(0, delta_gap)
    observable = sp.Matrix([[0, 0], [coefficient, 0]])
    density = sp.diag(1, 0)
    derivation = sp.I * (hamiltonian * observable - observable * hamiltonian) / hbar
    mean = sp.trace(density * observable)
    variance = sp.simplify(sp.trace(density * observable.H * observable) - sp.conjugate(mean) * mean)
    energy = sp.simplify(-sp.I * hbar * sp.trace(density * observable.H * derivation))
    return {
        "Delta": delta_gap,
        "coefficient": coefficient,
        "variance": variance,
        "energy": energy,
        "gap_ratio": sp.simplify(energy / variance),
    }


def negative_fixture() -> dict[str, Any]:
    n = sp.Integer(NEGATIVE_INPUTS["sample_n"])
    lower = sp.Integer(NEGATIVE_INPUTS["uniform_lower_gap"])
    hbar = sp.Integer(NEGATIVE_INPUTS["hbar"])
    observable = sp.Matrix([[0, 0], [1, 0]])
    density = sp.diag(1, 0)
    limiting_density = sp.diag(1, 0)
    hamiltonian = sp.diag(0, n)
    eigenvalues = sorted(sp.simplify(value) for value in hamiltonian.eigenvals())
    finite_gap = sp.simplify(eigenvalues[1] - eigenvalues[0])

    def derivation(index: sp.Integer) -> sp.Matrix:
        finite_hamiltonian = sp.diag(0, index)
        return sp.I * (finite_hamiltonian * observable - observable * finite_hamiltonian) / hbar

    delta_n = derivation(n)
    delta_next = derivation(n + 1)
    return {
        "sample_n": int(n),
        "finite_gap": finite_gap,
        "uniform_lower_gap": lower,
        "state_distance": sp.simplify(operator_norm(density - limiting_density)),
        "generator_norm": sp.simplify(operator_norm(delta_n)),
        "next_generator_distance": sp.simplify(operator_norm(delta_next - delta_n)),
        "variance": sp.trace(density * observable.H * observable),
        "energy": sp.simplify(-sp.I * hbar * sp.trace(density * observable.H * delta_n)),
    }


def stringify(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    return str(value)


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    star = star_fixture()
    radius = radius_fixture()
    bond = bond_fixture()
    shell = shell_fixture()
    gns = gns_fixture()
    negative = negative_fixture()
    audit = Audit()

    audit.check("manifest identity", manifest["version"] == "R-167 v3.0" and manifest["exploration_id"] == "EXP-000834", (manifest["version"], manifest["exploration_id"]), ("R-167 v3.0", "EXP-000834"), "identity")
    audit.check("three scoped children", len(manifest["closed_gate_ids"]) == len(set(manifest["closed_gate_ids"])) == 3, manifest["closed_gate_ids"], "three unique", "identity")
    audit.check("one scoped negative", len(manifest["negative_ids"]) == len(set(manifest["negative_ids"])) == 1, manifest["negative_ids"], "one unique", "identity")

    fixture_map = {"star": star, "radius": radius, "bond": bond, "shell": shell, "gns": gns, "negative": negative}
    for group, derived in fixture_map.items():
        oracle = manifest["exact_fixture"][group]
        for key, expected in oracle.items():
            audit.check(f"{group} {key}", key in derived and stringify(derived[key]) == expected, derived.get(key), expected, group)
    audit.check("star formula attained", star["gap"] == star["formula_gap"], star["gap"], star["formula_gap"], "star")
    audit.check("star allocation", star["z"] == 2 * star["dimension"], star["z"], 2 * star["dimension"], "star")
    audit.check("GNS equality", gns["energy"] == gns["Delta"] * gns["variance"], gns["energy"], gns["Delta"] * gns["variance"], "gns")
    audit.check("negative Poincare", negative["energy"] == negative["finite_gap"] * negative["variance"], negative["energy"], negative["finite_gap"] * negative["variance"], "negative")
    audit.check("negative uniform finite gap", negative["finite_gap"] >= negative["uniform_lower_gap"], negative["finite_gap"], negative["uniform_lower_gap"], "negative")

    normalized_certificate = " ".join(certificate.split())
    required_tokens = (
        "Pirogov--Sinai theory",
        "k_NP_N=P_Nk_N=0",
        "g^0_{\\star,N}",
        "applies directly to the exact infinite-dimensional",
        "lower semicontinuous",
        "every finite intermediate background",
        "form core for `H^(1/2)`",
        "All five active parent gates remain OPEN",
        "No v3.0 PDF is issued",
    )
    manifest_star_setup = manifest["zero_source_forward_star"]["setup"]
    audit.check("certificate theorem and scope tokens", all(token in normalized_certificate for token in required_tokens) and "k_N P_N=P_N k_N=0" in manifest_star_setup, {"certificate_missing": [token for token in required_tokens if token not in normalized_certificate], "manifest_kernel_premise": "k_N P_N=P_N k_N=0" in manifest_star_setup}, {"certificate_missing": [], "manifest_kernel_premise": True}, "authority")
    audit.check("five OPEN parent firewall", len(manifest["open_parent_gate_ids"]) == 5 and "All five active parent gates remain OPEN" in manifest["no_overclaim"] and "cutoff-stable passage theorem" in manifest["no_overclaim"], manifest["open_parent_gate_ids"], "five OPEN and cutoff-passage firewall", "authority")
    audit.check("proof-first no PDF", manifest["checkpoint_synthesis"]["pdf_issued"] is False, manifest["checkpoint_synthesis"], "no PDF", "authority")

    if not staged:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        formal_tokens = ["EXP-000834", "R-167 v3.0", *manifest["closed_gate_ids"], *manifest["negative_ids"]]
        audit.check("formal authority landed", all(token in formal_text for token in formal_tokens), [token for token in formal_tokens if token not in formal_text], [], "formal")

    derived = {key: stringify(value) for key, value in fixture_map.items()}
    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.0 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
