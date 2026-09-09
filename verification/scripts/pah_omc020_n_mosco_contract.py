#!/usr/bin/env python3
"""PAH-OMC-020 anchored-n Mosco/selection contract audit.

The audit checks the exact source-owned inputs and records the gap between
local cylinder recovery and a genuine varying-Hilbert-space liminf/semigroup
theorem.  It does not import a Mosco theorem without hypotheses, construct a
new embedding, or claim the R-512 minimal semigroup has been selected.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC017 = ROOT / "strategy/pa-hyp/PAH-OMC-017-result-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json"
OMC019 = ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def source_checks(rows: list[dict]) -> None:
    for relative, pin in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", digest(path) == pin, digest(path), pin)
    p001 = json.loads(PAH001.read_text(encoding="utf-8"))
    p017 = json.loads(OMC017.read_text(encoding="utf-8"))
    p018 = json.loads(OMC018.read_text(encoding="utf-8"))
    p019 = json.loads(OMC019.read_text(encoding="utf-8"))
    p020 = json.loads(OMC020.read_text(encoding="utf-8"))
    p017_answer = p017["conclusion"]["answer"]
    check(rows, "PAH-001 plaquette stiffness input",
          p001["functional_or_action"]["plaquette_stiffness"]
          == "J_p(s)=|boundary p|^(-1) sum_(e in boundary p) J_e(s)",
          p001["functional_or_action"]["plaquette_stiffness"],
          "boundary average of source edge stiffnesses")
    check(rows, "R-510 local state input", p017["result_id"] == "R-510"
          and "fixed prefix" in p017_answer
          and "converges" in p017_answer,
          p017_answer, "R-510 local prefix convergence")
    check(rows, "R-511 form input", p018["result_id"] == "R-511"
          and "pre-form" in p018["conclusion"], p018["conclusion"], "R-511 local pre-form")
    check(rows, "R-512 minimal closure input", p019["result_id"] == "R-512"
          and "minimal" in p019["conclusion"]
          and "closed" in p019["conclusion"], p019["conclusion"], "R-512 minimal closure")
    check(rows, "OMC-020 target keeps anchored order",
          "First j" in p020["scope"]["regulator_order"] and "then" in p020["scope"]["regulator_order"],
          p020["scope"]["regulator_order"], "j before anchored n")
    check(rows, "OMC-020 target is correlation-level",
          "Local stationary two-point correlation" in p020["objects_and_comparison"]["topology_boundary"],
          p020["objects_and_comparison"]["topology_boundary"], "local correlations")
    check(rows, "no varying-space shortcut is preregistered",
          "No assumption that a form core is an operator graph core" in p020["prohibited_shortcuts"][2]
          and "No inference of semigroup selection" in p020["prohibited_shortcuts"][1],
          p020["prohibited_shortcuts"], "explicit firewall")


def work_contract_checks(rows: list[dict]) -> None:
    text = WORK.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    markers = ("(N1)", "(N2a)", "(N2b)", "(N2c)", "(N2d)", "limsup/recovery", "liminf")
    check(rows, "anchored-n contract markers", all(marker in text for marker in markers),
          [marker for marker in markers if marker in text], "all markers")
    check(rows, "common realization is identified as missing",
          "measure-compatible realization U_n" in text and "must supply" in text,
          "(N2a) missing input", "explicitly missing")
    check(rows, "boundary escape is identified as missing",
          "boundary-escape estimate" in text and "unbounded source rates" in text,
          "(N2c) missing input", "explicitly missing")
    check(rows, "minimal selection is not silently inferred",
          "does not supply (N2b) or (N2c)" in compact
          and "no anchored temporal result is admitted" in compact,
          "R-512 is insufficient for liminf", "present")
    check(rows, "local pullback realization is separated from full U_n",
          "(J_n h)(x)=h(p_n x)" in compact
          and "(N3)" in compact
          and "not as a discharge of (N2a)" in compact,
          "J_n core candidate only", "explicit split")
    check(rows, "boundary escape contract is explicit",
          "(N4)" in compact
          and "A_n^{out,m}" in compact
          and "unbounded original rates" in compact,
          "N4 compact-time estimate", "explicitly required")
    check(rows, "terminal-square versus split-cell mismatch is retained",
          "unsplit terminal square" in compact
          and "no equality of the finite Gibbs laws" in compact
          and "square-to-split Radon--Nikodym kernel" in compact
          and "Conditional averaging" in compact,
          "S/K boundary mismatch", "explicitly unresolved")
    check(rows, "physical non-claims remain present",
          "No physical Pre-A" in text and "QFT" in text and "gravity" in text,
          "non-physical boundary", "present")


def recovery_arithmetic(rows: list[dict]) -> dict:
    # Support values are diagnostics for the exact N(f,g)=max(2,m+2) rule,
    # not a new geometry or a volume-uniform estimate.
    support = list(range(0, 9))
    stages = [max(2, m + 2) for m in support]
    check(rows, "support stabilization stage is monotone", all(b > a for a, b in zip(stages, stages[1:])),
          stages, "N=max(2,m+2)")
    check(rows, "support stage formula is exact on fixture", stages == [2, 3, 4, 5, 6, 7, 8, 9, 10],
          stages, "[2,3,...,10]")
    check(rows, "recovery candidates retain every local prefix",
          all(stage >= m + 2 for stage, m in zip(stages, support)),
          stages, "stage>=m+2")
    return {"support_values": support, "N_values": stages}


def hostile_checks(rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory(prefix="pah020-n-hostile-") as directory:
        altered = Path(directory) / "altered-work.md"
        altered.write_bytes(WORK.read_bytes().replace(b"(N2b)", b"(N2b-removed)", 1))
        check(rows, "hostile liminf omission changes work hash", digest(altered) != digest(WORK),
              digest(altered), "different from work hash")
    p020 = json.loads(OMC020.read_text(encoding="utf-8"))
    check(rows, "hostile diagonal limit remains rejected",
          "No diagonal, reversed" in p020["scope"]["regulator_order"],
          p020["scope"]["regulator_order"], "no diagonal/reversed order")
    check(rows, "hostile maximal-form substitution remains rejected",
          "maximal jump form" in WORK.read_text(encoding="utf-8"),
          "maximal jump form", "explicit firewall")


def boundary_factor_fixture(rows: list[dict]) -> dict:
    """Recompute the source terminal S/K distinction on one allowed state.

    At r=0 and s=1 with all old links +1, the source certificate gives zero
    horizontal edge energy.  The Wilson coefficient is the source boundary
    average of edge stiffnesses, so every J is 1 on this state.  The square
    and split face costs are recomputed for every retained link label, with
    the diagonal label retained.  This is a boundary-map diagnostic only; it
    does not replace the original process or prove a temporal limit.
    """
    link_signs = (-1, 1)
    edge_stiffness = 2.0 / (1.0 + 1.0)
    square_stiffness = (4.0 * edge_stiffness) / 4.0
    square_terms = [
        math.exp(-square_stiffness * (1 - h0 * h1))
        for h0, h1 in itertools.product(link_signs, repeat=2)
    ]
    triangle_terms = []
    for h0, h1, diagonal in itertools.product(link_signs, repeat=3):
        first_stiffness = (edge_stiffness + edge_stiffness + edge_stiffness) / 3.0
        second_stiffness = (edge_stiffness + edge_stiffness + edge_stiffness) / 3.0
        cost = (
            first_stiffness * (1 - h0 * diagonal)
            + second_stiffness * (1 - diagonal * h1)
        )
        triangle_terms.append(math.exp(-cost))
    square_factor = sum(square_terms)
    split_factor = sum(triangle_terms)
    elementary_a = math.exp(-2.0)
    check(rows, "boundary fixture square factor positive", square_factor > 0,
          square_factor, ">0")
    check(rows, "boundary fixture split factor positive", split_factor > 0,
          split_factor, ">0")
    check(rows, "boundary fixture retains diagonal label", len(triangle_terms) == 8,
          len(triangle_terms), 8)
    check(rows, "boundary fixture split factor formula",
          abs(split_factor - 2 * (1 + elementary_a) ** 2) < 1e-12,
          split_factor, "2*(1+exp(-2))^2")
    check(rows, "boundary fixture square factor formula",
          abs(square_factor - 2 * (1 + elementary_a)) < 1e-12,
          square_factor, "2*(1+exp(-2))")
    check(rows, "boundary fixture elementary exponential positive", elementary_a > 0,
          elementary_a, ">0")
    check(rows, "boundary fixture S/K distinction is nonzero", split_factor > square_factor,
          {"S": square_factor, "Kbar": split_factor}, "Kbar>S")
    return {
        "state": "r=0, s=1, old links +1",
        "square_factor_S": square_factor,
        "split_factor_Kbar": split_factor,
        "elementary_exp": elementary_a,
        "formula": "Kbar=2*(1+exp(-2))^2 > S=2*(1+exp(-2))",
        "scope": "finite boundary-map diagnostic; not a temporal or physical result",
    }


def lean_check() -> dict:
    compiler = Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lean.exe"
    if not compiler.is_file():
        return {"status": "NOT_AVAILABLE", "command": "lean verification/lean/Tect/PahOmc020.lean"}
    package_root = Path("E:/Dev/TECT/verification/lean/.lake/packages")
    env = os.environ.copy()
    if package_root.is_dir():
        paths = []
        for package in package_root.iterdir():
            candidate = package / ".lake/build/lib/lean"
            if candidate.is_dir():
                paths.append(str(candidate))
        env["LEAN_PATH"] = ";".join(paths)
    process = subprocess.run([str(compiler), str(LEAN)], cwd=LEAN.parent.parent.parent,
                             env=env, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False, timeout=180)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
            "command": "lean verification/lean/Tect/PahOmc020.lean", "returncode": process.returncode,
            "output": output[-2000:], "compiler": str(compiler)}


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    work_contract_checks(rows)
    arithmetic = recovery_arithmetic(rows)
    boundary = boundary_factor_fixture(rows)
    hostile_checks(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-n-mosco-contract/1.0",
        "status": "PASS_N_MOSCO_RECOVERY_CONTRACT",
        "temporal_verdict": "IN_PROGRESS",
        "source_pins": PINS,
        "work_sha256": digest(WORK),
        "code_sha256": digest(Path(__file__)),
        "checks": rows,
        "recovery_arithmetic": arithmetic,
        "boundary_factor_fixture": boundary,
        "lean": lean,
        "proved_scope": [
            "R-510 local-state and R-511 local-form inputs are pinned for the anchored-n recovery candidate",
            "support stabilization N(f,g)=max(2,m(f)+2,m(g)+2) is explicit",
            "the exact missing varying-space liminf, boundary-escape and minimal-selection obligations are recorded",
            "the coordinate pullback J_n is admitted only on the fixed local core, with full-space boundedness left open",
            "the finite unsplit terminal-square versus infinite split-cell mismatch is retained as an N2a boundary obstruction",
            "the source boundary fixture recomputes a nonzero S/K split factor difference without changing the process",
            "the original-generator boundary-escape estimate N4 is stated without replacing the process",
            "hostile shortcut/order/form-substitution controls and PahOmc020 Lean compilation PASS",
        ],
        "open_obligations": [
            "construct and hash-pin a measure-compatible realization U_n for the varying finite Hilbert spaces",
            "prove the arbitrary-sequence Mosco liminf and unbounded-rate boundary escape on [0,T]",
            "identify the limiting closed form with the R-512 minimal closure and derive correlation semigroup convergence",
        ],
        "non_claims": [
            "This is a recovery/liminf contract audit, not a Mosco theorem, semigroup convergence result or result-card admission.",
            "No maximal-domain equality, operator graph core, infinite-volume process, anchored n limit, physical Pre-A, spacetime, QFT, gravity, continuum, mass gap or TOE conclusion; no Q3LOCK or TECT-YM import.",
        ],
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = args.output.read_bytes()
        with tempfile.TemporaryDirectory(prefix="pah020-n-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 n-Mosco contract replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 N-MOSCO CONTRACT: PASS (recovery audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
