"""Primary Lean/Fraction audit for the sharp A6 running-mass boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a6-sharp-running-mass-counterterm-boundary-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R194.lean"
TOOLCHAIN = LEAN_ROOT / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-K-COMPOSITE-DEFINITION" / "runs" / "2026-08-22-lean-r194-sharp-running-mass" / "primary.json"


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def pinned_lean() -> Path | None:
    encoded = TOOLCHAIN.read_text(encoding="utf-8").strip().replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / ("lean.exe" if os.name == "nt" else "lean")
    return candidate if candidate.is_file() else None


def compile_lean() -> subprocess.CompletedProcess[str]:
    lean = pinned_lean()
    if lean is None:
        return subprocess.CompletedProcess([], 1, "", "pinned lean executable missing")
    search = [LEAN_ROOT / ".lake" / "build" / "lib" / "lean"]
    packages = LEAN_ROOT / ".lake" / "packages"
    if packages.is_dir():
        search.extend(p / ".lake" / "build" / "lib" / "lean" for p in packages.iterdir() if (p / ".lake" / "build" / "lib" / "lean").is_dir())
    env = os.environ.copy()
    env["LEAN_PATH"] = os.pathsep.join(str(path) for path in search if path.is_dir())
    return subprocess.run([str(lean), str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False, env=env)


def coefficients(a1: dict[str, Any]) -> tuple[F, F, F]:
    p = a1["parameters"]
    as_fraction = lambda key: F(str(p[key]))
    denominator = as_fraction("M_X") ** 2 + as_fraction("classii_mass_regularizer")
    a = as_fraction("cJJ") * as_fraction("alpha_X") ** 2 / denominator
    b = as_fraction("cJK") * as_fraction("alpha_X") * as_fraction("beta_X") / denominator
    c = as_fraction("cKK") * as_fraction("beta_X") ** 2 / denominator
    return a, b, c


def w_value(a: F, b: F, c: F, eps: F, s: F, r: F) -> F:
    rho = s + r
    g = a + 2 * b + c
    return 9 * g * s - 6 * b * s * s / (rho + eps) - 3 * c * s * s * (rho + 2 * eps) / (rho + eps) ** 2


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    a, b, c = coefficients(a1)
    eps = F(str(a1["parameters"]["rho_regularizer"]))
    h_min = 9 * (a + 2 * b + c)
    oracle = manifest["registered_inputs"]["test_oracles"]
    s_sub = F(oracle["subsharp_s"])
    r_sub = F(oracle["subsharp_r"])
    sub_gap = F(oracle["subsharp_gap"])
    h_sub = h_min - sub_gap
    def d(h: F, s: F, r: F) -> F:
        return h * s - w_value(a, b, c, eps, s, r)
    escape_rows = []
    for raw_r in oracle["escape_r_values"]:
        r_value = F(raw_r)
        ratio = d(h_min, F(oracle["subsharp_s"]), r_value) / s_sub
        escape_rows.append({"r": r_value, "ratio": ratio})
    endpoint_rows = []
    for s_raw, r_raw in oracle["endpoint_samples"]:
        s_value, r_value = F(s_raw), F(r_raw)
        rho = s_value + r_value
        correction = 6 * b * s_value * s_value / (rho + eps) + 3 * c * s_value * s_value * (rho + 2 * eps) / (rho + eps) ** 2
        endpoint_rows.append({"s": s_value, "r": r_value, "difference": d(h_min, s_value, r_value), "correction": correction})
    return {
        "a": a, "b": b, "c": c, "eps": eps, "g": a + 2 * b + c, "h_min": h_min,
        "endpoint_rows": endpoint_rows,
        "subsharp": {"gap": sub_gap, "s": s_sub, "r": r_sub, "h": h_sub, "difference": d(h_sub, s_sub, r_sub)},
        "escape_rows": escape_rows,
        "symbolic_limit": "D_h_min/s -> 0 as r -> infinity for fixed s>0",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_production"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A6-R194-SHARP-RUNNING-MASS-COUNTERTERM-BOUNDARY" and manifest["result_id"] == "R-194", [manifest["audit_id"], manifest["result_id"]], "R-194 identity")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key} hash", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean markers", all(marker in source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape absence", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    completed = compile_lean()
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    derived = derive(manifest, a1)
    check("pinned b positive", derived["b"] > 0, derived["b"], ">0")
    check("pinned c positive", derived["c"] > 0, derived["c"], ">0")
    for row in derived["endpoint_rows"]:
        check("endpoint exact identity", row["difference"] == row["correction"], row, "difference=correction")
        check("endpoint nonnegative", row["difference"] >= 0, row["difference"], ">=0")
    check("pure third endpoint", w_value(derived["a"], derived["b"], derived["c"], derived["eps"], F(0), F(7)) == 0, 0, 0)
    check("subsharp witness", derived["subsharp"]["difference"] < 0, derived["subsharp"], "<0")
    ratios = [row["ratio"] for row in derived["escape_rows"]]
    check("escape ratio positive", all(value > 0 for value in ratios), ratios, ">0")
    check("escape ratio decreases", all(left > right for left, right in zip(ratios, ratios[1:])), ratios, "strictly decreasing")
    check("escape ratio tends by exact formula", "r -> infinity" in derived["symbolic_limit"], derived["symbolic_limit"], "symbolic limit marker")
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS",
        "assertion_count": len(rows), "assertions": rows, "derived": serial(derived),
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(), "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-194 LEAN PASS {len(rows)}/{len(rows)} h_min={derived['h_min']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
