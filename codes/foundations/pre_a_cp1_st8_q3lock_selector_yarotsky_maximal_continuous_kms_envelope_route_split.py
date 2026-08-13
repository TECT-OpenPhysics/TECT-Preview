#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v2.9 selector/continuous-core split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-selector-yarotsky-maximal-continuous-kms-envelope-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
GATES = REPO / "claims/GATES.md"
RESULTS = REPO / "RESULTS-LEDGER.md"
NEGATIVES = REPO / "negative-results/registry.md"
EXPLORATIONS = REPO / "explorations/log.jsonl"


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


def selector_fixture() -> dict[str, Any]:
    # Test inputs. Every reported value below is derived from them.
    z = 6
    dimension = 3
    coupling = sp.Integer(8)
    high_gap = sp.Integer(100)
    selector = sp.Integer(1)
    data = {
        "+": (sp.Integer(0), sp.Integer(1), sp.Integer(0)),
        "-": (sp.Integer(0), sp.Integer(-1), sp.Integer(1)),
        "h": (high_gap, sp.Integer(0), sp.Integer(0)),
    }

    def edge(a: str, b: str) -> sp.Expr:
        ka, sa, pa = data[a]
        kb, sb, pb = data[b]
        return sp.factor((ka + kb) / z + coupling * (1 - sa * sb) + selector * (pa + pb) / z)

    spectrum: list[sp.Expr] = []
    for labels in product(data, repeat=int(dimension + 1)):
        spectrum.append(sp.factor(sum(edge(labels[0], labels[i]) for i in range(1, int(dimension + 1)))))
    positive = sorted(v for v in spectrum if v > 0)
    alpha = sp.Rational(1, 100)
    beta = sp.Rational(1, 1000)
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
        "star_kernel_dimension": sum(v == 0 for v in spectrum),
        "star_gap": positive[0],
        "alpha": alpha,
        "beta": beta,
        "normalized_beta": dimension * beta / selector,
        "selector_removal_ratio": sp.simplify(selector / selector),
    }


def radius_fixture() -> dict[str, Any]:
    sample_n = 2
    defect = sp.Rational(1, sample_n**3)
    radius = sp.Rational(1, sample_n**4)
    ratio = sp.simplify(defect / radius)
    general_n = sp.Symbol("N", integer=True, positive=True)
    assert sp.simplify(general_n ** -3 / general_n ** -4) == general_n
    return {"sample_N": sample_n, "defect": defect, "radius": radius, "eventual_entry": bool(ratio < 1)}


def categorical_fixture() -> dict[str, Any]:
    sigma_x = sp.Matrix([[0, 1], [1, 0]])
    d = sp.diag(0, 1)
    time = sp.pi / 2
    unitary = sp.diag(1, sp.exp(sp.I * time))
    evolved = sp.simplify(unitary * sigma_x * unitary.H)
    delta = sigma_x - evolved
    distance_squared = max(sp.simplify(v) for v in (delta.H * delta).eigenvals())
    beta = sp.log(2)
    even_density = sp.eye(2) / 2
    odd_density = sp.diag(1, sp.exp(-beta)) / (1 + sp.exp(-beta))
    e22 = sp.diag(0, 1)
    e12 = sp.Matrix([[0, 1], [0, 0]])
    e21 = e12.T
    alpha_ibeta_e21 = sp.exp(-beta * d) * e21 * sp.exp(beta * d)
    left = sp.simplify(sp.trace(odd_density * e12 * alpha_ibeta_e21))
    right = sp.simplify(sp.trace(odd_density * e21 * e12))
    even_gibbs = sp.simplify(sp.trace(even_density * e22))
    odd_gibbs = sp.simplify(sp.trace(odd_density * e22))
    return {
        "evolved_distance_squared": sp.simplify(distance_squared),
        "even_gibbs": even_gibbs,
        "odd_gibbs": odd_gibbs,
        "odd_kms_left": left,
        "odd_kms_right": right,
        "all_shape_cauchy": bool(distance_squared == 0),
        "unique_kms_cluster": bool(even_gibbs == odd_gibbs),
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


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    selector = selector_fixture()
    radius = radius_fixture()
    categorical = categorical_fixture()
    audit = Audit()

    audit.check("manifest schema", manifest["schema"] == "tect/pre-a-q3lock-selector-continuous-envelope/1.0", manifest["schema"], "exact", "identity")
    audit.check("version and exploration", manifest["version"] == "R-167 v2.9" and manifest["exploration_id"] == "EXP-000833", (manifest["version"], manifest["exploration_id"]), ("R-167 v2.9", "EXP-000833"), "identity")
    audit.check("four closed children", len(manifest["closed_gate_ids"]) == 4 and len(set(manifest["closed_gate_ids"])) == 4, manifest["closed_gate_ids"], "four unique", "identity")
    audit.check("three scoped negatives", len(manifest["negative_ids"]) == 3 and len(set(manifest["negative_ids"])) == 3, manifest["negative_ids"], "three unique", "identity")

    oracle = manifest["exact_fixture"]["selector"]
    for key in ("edge_plus_plus", "edge_minus_minus", "edge_plus_minus", "edge_plus_high", "star_gap", "alpha", "beta", "normalized_beta", "selector_removal_ratio"):
        audit.check(f"selector {key}", str(selector[key]) == oracle[key], selector[key], oracle[key], "selector")
    audit.check("selector star unique kernel", selector["star_kernel_dimension"] == oracle["star_kernel_dimension"] == 1, selector["star_kernel_dimension"], 1, "selector")
    audit.check("selector global allocation factor", selector["z"] == 2 * selector["dimension"], selector["z"], 2 * selector["dimension"], "selector")

    r_oracle = manifest["exact_fixture"]["radius"]
    audit.check("N-dependent radius arithmetic", str(radius["defect"]) == r_oracle["defect"] and str(radius["radius"]) == r_oracle["radius"], radius, r_oracle, "radius")
    audit.check("vanishing defect need not enter", radius["eventual_entry"] is r_oracle["eventual_entry"] is False and radius["defect"] > radius["radius"], radius, "defect exceeds radius", "radius")

    c_oracle = manifest["exact_fixture"]["categorical"]
    for key in ("evolved_distance_squared", "even_gibbs", "odd_gibbs", "odd_kms_left", "odd_kms_right"):
        audit.check(f"categorical {key}", str(categorical[key]) == c_oracle[key], categorical[key], c_oracle[key], "categorical")
    audit.check("categorical negative flags", categorical["all_shape_cauchy"] is False and categorical["unique_kms_cluster"] is False, categorical, "both false", "categorical")

    required = (
        "possibly infinite-dimensional onsite Hilbert spaces",
        "3beta_N/u",
        "maximal invariant unital C-star",
        "weak-star dense maximal invariant norm-C0",
        "All five active parent gates remain OPEN",
        "No v2.9 PDF is issued",
    )
    audit.check("certificate theorem tokens", all(token in certificate for token in required), [token for token in required if token not in certificate], [], "authority")
    audit.check("manifest parent firewall", len(manifest["open_parent_gate_ids"]) == 5 and "remain OPEN" in manifest["no_overclaim"], manifest["open_parent_gate_ids"], "five OPEN", "authority")
    audit.check("checkpoint deferred", manifest["checkpoint_synthesis"]["pdf_issued"] is False and "DEFERRED" in manifest["checkpoint_synthesis"]["status"], manifest["checkpoint_synthesis"], "deferred", "authority")

    formal_tokens = ["EXP-000833", "R-167 v2.9", *manifest["closed_gate_ids"], *manifest["negative_ids"]]
    formal_text = "\n".join(path.read_text(encoding="utf-8") for path in (GATES, RESULTS, NEGATIVES, EXPLORATIONS))
    formal_ok = all(token in formal_text for token in formal_tokens)
    if not staged:
        audit.check("formal authority landed", formal_ok, [token for token in formal_tokens if token not in formal_text], [], "formal")

    derived = {"selector": stringify(selector), "radius": stringify(radius), "categorical": stringify(categorical)}
    payload = {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
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
    print(f"R-167 v2.9 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
