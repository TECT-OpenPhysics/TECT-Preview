#!/usr/bin/env python3
"""Non-importing stdlib verifier for the R-167 v2.9 route split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-selector-yarotsky-maximal-continuous-kms-envelope-route-split"
PRIMARY = REPO / f"codes/foundations/pre_a_cp1_st8_q3lock_selector_yarotsky_maximal_continuous_kms_envelope_route_split.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def derive_selector() -> dict[str, Any]:
    z = 2 * 3
    dimension = z // 2
    coupling = Fraction(8)
    high_gap = Fraction(100)
    selector = Fraction(1)
    labels = {
        "+": (Fraction(0), Fraction(1), Fraction(0)),
        "-": (Fraction(0), Fraction(-1), Fraction(1)),
        "h": (high_gap, Fraction(0), Fraction(0)),
    }

    def edge(a: str, b: str) -> Fraction:
        ka, sa, pa = labels[a]
        kb, sb, pb = labels[b]
        return (ka + kb) / z + coupling * (1 - sa * sb) + selector * (pa + pb) / z

    values: list[Fraction] = []
    for configuration in product(labels, repeat=dimension + 1):
        values.append(sum((edge(configuration[0], configuration[i]) for i in range(1, dimension + 1)), Fraction(0)))
    positives = sorted(value for value in values if value > 0)
    alpha = Fraction(1, 100)
    beta = Fraction(1, 1000)
    return {
        "z": z,
        "dimension": dimension,
        "J": coupling,
        "Gamma": high_gap,
        "u": selector,
        "edge_plus_plus": edge("+", "+"),
        "edge_minus_minus": edge("-", "-"),
        "edge_plus_minus": edge("+", "-"),
        "edge_plus_high": edge("+", "h"),
        "star_kernel_dimension": sum(value == 0 for value in values),
        "star_gap": positives[0],
        "alpha": alpha,
        "beta": beta,
        "normalized_beta": dimension * beta / selector,
        "selector_removal_ratio": selector / selector,
    }


def derive_radius() -> dict[str, Any]:
    n = 2
    defect = Fraction(1, n**3)
    radius = Fraction(1, n**4)
    ratio = defect / radius
    assert all(Fraction(1, k**3) / Fraction(1, k**4) == k for k in range(2, 10))
    return {"sample_N": n, "defect": defect, "radius": radius, "eventual_entry": ratio < 1}


def matmul(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def adjoint(a: list[list[complex]]) -> list[list[complex]]:
    return [[a[j][i].conjugate() for j in range(2)] for i in range(2)]


def trace(a: list[list[complex]]) -> complex:
    return a[0][0] + a[1][1]


def derive_categorical() -> dict[str, Any]:
    sigma_x = [[0j, 1 + 0j], [1 + 0j, 0j]]
    unitary = [[1 + 0j, 0j], [0j, 1j]]
    evolved = matmul(matmul(unitary, sigma_x), adjoint(unitary))
    delta = [[sigma_x[i][j] - evolved[i][j] for j in range(2)] for i in range(2)]
    gram = matmul(adjoint(delta), delta)
    assert gram[0][1] == gram[1][0] == 0 and gram[0][0] == gram[1][1]
    distance_squared = Fraction(int(gram[0][0].real))
    ground_weight = Fraction(1)
    excited_weight = Fraction(1, 2)
    odd_partition = ground_weight + excited_weight
    odd_density = [
        [ground_weight / odd_partition, Fraction(0)],
        [Fraction(0), excited_weight / odd_partition],
    ]
    even_partition = ground_weight + ground_weight
    even_density = [
        [ground_weight / even_partition, Fraction(0)],
        [Fraction(0), ground_weight / even_partition],
    ]
    e22 = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    e12 = [[Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]]
    e21 = [[Fraction(0), Fraction(0)], [Fraction(1), Fraction(0)]]
    alpha_ibeta_e21 = [[Fraction(0), Fraction(0)], [excited_weight, Fraction(0)]]
    even_gibbs = trace(matmul(even_density, e22))
    odd_gibbs = trace(matmul(odd_density, e22))
    left = trace(matmul(odd_density, matmul(e12, alpha_ibeta_e21)))
    right = trace(matmul(odd_density, matmul(e21, e12)))
    return {
        "evolved_distance_squared": distance_squared,
        "even_gibbs": even_gibbs,
        "odd_gibbs": odd_gibbs,
        "odd_kms_left": left,
        "odd_kms_right": right,
        "all_shape_cauchy": distance_squared == 0,
        "unique_kms_cluster": even_gibbs == odd_gibbs,
    }

def stringify(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, str)):
        return value
    return str(value)


def independence_firewall() -> dict[str, Any]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {"__future__", "argparse", "ast", "hashlib", "json", "os", "tempfile", "fractions", "itertools", "pathlib", "typing"}
    imported: list[str] = []
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec", "compile"}:
                dynamic.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "exec_module", "load_module"}:
                dynamic.append(node.func.attr)
    import_roots = sorted(set(imported))
    return {
        "imports": import_roots,
        "unapproved": sorted(set(import_roots) - allowed),
        "dynamic": dynamic,
        "primary_imported": any(name.startswith("pre_a_cp1") for name in import_roots),
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    selector = derive_selector()
    radius = derive_radius()
    categorical = derive_categorical()
    firewall = independence_firewall()
    audit = Audit()

    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["exploration_id"] == "EXP-000833", (manifest["package_id"], manifest["exploration_id"]), (SLUG, "EXP-000833"), "identity")
    audit.check("closed and negative cardinalities", (len(manifest["closed_gate_ids"]), len(manifest["negative_ids"])) == (4, 3), (len(manifest["closed_gate_ids"]), len(manifest["negative_ids"])), (4, 3), "identity")
    audit.check("five parent firewall", len(manifest["open_parent_gate_ids"]) == 5, manifest["open_parent_gate_ids"], "five", "identity")

    selector_oracle = manifest["exact_fixture"]["selector"]
    for key in ("edge_plus_plus", "edge_minus_minus", "edge_plus_minus", "edge_plus_high", "star_gap", "alpha", "beta", "normalized_beta", "selector_removal_ratio"):
        audit.check(f"selector {key}", str(selector[key]) == selector_oracle[key], selector[key], selector_oracle[key], "selector")
    audit.check("selector enumeration", selector["star_kernel_dimension"] == selector_oracle["star_kernel_dimension"] == 1, selector["star_kernel_dimension"], 1, "selector")

    radius_oracle = manifest["exact_fixture"]["radius"]
    audit.check("radius fixture", str(radius["defect"]) == radius_oracle["defect"] and str(radius["radius"]) == radius_oracle["radius"] and radius["eventual_entry"] is False, radius, radius_oracle, "radius")

    categorical_oracle = manifest["exact_fixture"]["categorical"]
    for key in ("evolved_distance_squared", "even_gibbs", "odd_gibbs", "odd_kms_left", "odd_kms_right"):
        audit.check(f"categorical {key}", str(categorical[key]) == categorical_oracle[key], categorical[key], categorical_oracle[key], "categorical")
    audit.check("categorical failure flags", categorical["all_shape_cauchy"] is False and categorical["unique_kms_cluster"] is False, categorical, "false/false", "categorical")

    audit.check("stdlib independence firewall", not firewall["unapproved"] and not firewall["dynamic"] and not firewall["primary_imported"], firewall, "stdlib only", "independence")
    audit.check("independent source distinct", normalized_sha256(SCRIPT) != normalized_sha256(PRIMARY), normalized_sha256(SCRIPT), "different from primary", "independence")

    required = ("exact star gap", "quadratic-form", "categorical", "all-shape Cauchy", "GNS parent stays OPEN", "No v2.9 PDF")
    audit.check("certificate boundary coverage", all(token in certificate for token in required), [token for token in required if token not in certificate], [], "authority")
    audit.check("manifest proof-first", manifest["checkpoint_synthesis"]["pdf_issued"] is False, manifest["checkpoint_synthesis"], "no PDF", "authority")

    formal_tokens = ["EXP-000833", "R-167 v2.9", *manifest["closed_gate_ids"], *manifest["negative_ids"]]
    formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
    if not staged:
        audit.check("formal authority landed", all(token in formal_text for token in formal_tokens), [token for token in formal_tokens if token not in formal_text], [], "formal")

    payload = {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": {"selector": stringify(selector), "radius": stringify(radius), "categorical": stringify(categorical), "firewall": firewall},
        "source_hashes": {str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path) for path in (SCRIPT, MANIFEST, CERTIFICATE)},
    }
    return payload


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
    print(f"R-167 v2.9 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
