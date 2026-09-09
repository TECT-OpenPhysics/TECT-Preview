#!/usr/bin/env python3
"""Exact, non-importing algebra cross-check for the Q3LOCK draft.

Build the full eight-coordinate onsite polynomial from the Hamiltonian and
differentiate it in a sparse rational ring. Compare coefficient dictionaries,
not sampled parameter values. This is an executable algebra audit, not a
proof-kernel certificate, analytic limit proof, or independent reviewer signature.
Default --check is read-only; --write-new refuses an existing result.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import platform
import sys
import tempfile

__version__ = "0.2.0"
ROOT = Path(__file__).resolve().parents[2]
PAPER = "publish/papers/q3lock-phase-coexistence/"
MANUSCRIPT = PAPER + "manuscript.tex"
NOTE = PAPER + "verification/nonimporting-algebra-audit.md"
TEST = "verification/tests/test_q3lock_nonimporting_algebra.py"
FROZEN = "strategy/q3lock-exp782-independent-result-manifest-260905.json"
PACKAGE = PAPER + "verification/package-manifest.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-nonimporting-algebra-source-review-v1/result.json"
SOURCE_BASE_COMMIT = "e0765cf7c5d66284684e0830c59527339de88550"
INTERNAL_DIMENSION = 3  # Model input: binary cube Q3, not a derived count.


class P:
    """Sparse polynomial over Q. Monomials are sorted (name, power) tuples."""
    def __init__(self, value=0):
        if isinstance(value, P):
            self.terms = dict(value.terms)
        elif isinstance(value, dict):
            self.terms = {key: F(coef) for key, coef in value.items() if coef}
        else:
            self.terms = {} if not value else {(): F(value)}

    def __add__(self, other):
        terms = dict(self.terms)
        for key, coefficient in P(other).terms.items():
            terms[key] = terms.get(key, F(0)) + coefficient
        return P(terms)

    __radd__ = __add__

    def __neg__(self):
        return P({key: -value for key, value in self.terms.items()})

    def __sub__(self, other):
        return self + -P(other)

    def __rsub__(self, other):
        return P(other) + -self

    def __mul__(self, other):
        terms = {}
        for left, a in self.terms.items():
            for right, b in P(other).terms.items():
                powers = dict(left)
                for name, exponent in right:
                    powers[name] = powers.get(name, 0) + exponent
                key = tuple(sorted(powers.items()))
                terms[key] = terms.get(key, F(0)) + a * b
        return P(terms)

    __rmul__ = __mul__

    def __pow__(self, power):
        if not isinstance(power, int) or power < 0:
            raise ValueError("Only nonnegative integer polynomial powers.")
        value = P(1)
        for _ in range(power):
            value = value * self
        return value

    def __eq__(self, other):
        return self.terms == P(other).terms

    def diff(self, variable):
        result = {}
        for monomial, coefficient in self.terms.items():
            powers = dict(monomial)
            exponent = powers.get(variable, 0)
            if exponent:
                if exponent == 1:
                    del powers[variable]
                else:
                    powers[variable] = exponent - 1
                key = tuple(sorted(powers.items()))
                result[key] = result.get(key, F(0)) + exponent * coefficient
        return P(result)

    def value(self, values):
        total = F(0)
        for monomial, coefficient in self.terms.items():
            for name, exponent in monomial:
                coefficient *= F(values[name]) ** exponent
            total += coefficient
        return total

    def sign_flip(self, variables):
        return P({key: value * (-1) ** sum(power for name, power in key if name in variables)
                  for key, value in self.terms.items()})

    def rows(self):
        return [{"powers": dict(key), "coefficient": str(value)}
                for key, value in sorted(self.terms.items())]


def variable(name):
    return P({((name, 1),): F(1)})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"))
                          .encode("utf-8")).hexdigest()


def algebra():
    checks = []
    identities = []

    def check(name, ok, actual, expected):
        if not ok:
            raise AssertionError(name + ": " + str(actual))
        checks.append({"name": name, "pass": True,
                       "actual": str(actual), "expected": str(expected)})

    def identity(name, left, right, equation):
        residual = left - right
        check(name, residual == 0, len(residual.terms), "zero residual coefficients")
        identities.append({"name": name, "manuscript_equation": equation,
                           "left": left.rows(), "right": right.rows(),
                           "residual": residual.rows()})

    # Ring sanity checks are test oracles, not physical input.
    a, b = variable("a"), variable("b")
    identity("ring-binomial-oracle", (a + b)**2, a*a + 2*a*b + b*b, "tooling")
    identity("ring-leibniz-oracle", ((a*a + b)*(a-b)).diff("a"),
             2*a*(a-b) + a*a+b, "tooling")
    check("ring-evaluation-oracle", ((a+b)**3).value({"a": F(1, 2), "b": F(-1, 3)}) == F(1, 216),
          ((a+b)**3).value({"a": F(1, 2), "b": F(-1, 3)}), F(1, 216))

    vertices = tuple(range(2**INTERNAL_DIMENSION))
    edges = tuple((i, j) for i, j in combinations(vertices, 2)
                  if (i ^ j).bit_count() == 1)
    degree = {i: sum(i in edge for edge in edges) for i in vertices}
    check("cube-regularity", set(degree.values()) == {INTERNAL_DIMENSION},
          sorted(set(degree.values())), INTERNAL_DIMENSION)
    d = len(vertices)
    q_names = tuple("q" + str(i) for i in vertices)
    q = tuple(variable(name) for name in q_names)
    r, g, lam, c = (variable(name) for name in ("r", "g", "lambda", "c"))
    S = sum((z*z for z in q), P())
    D = sum(((q[i]-q[j])**2 for i, j in edges), P())
    locking = sum(((q[i]-q[j])**2 * (q[i]**2+q[j]**2) for i, j in edges), P())
    # These Hamiltonian coefficients are model INPUTS from eq:potential.
    U = F(1, 2)*r*S + F(1, 4)*g*sum((z**4 for z in q), P()) + F(1, 4)*lam*locking

    def common_derivative(poly):
        return sum((poly.diff(name) for name in q_names), P())

    # Printed coefficients below are independent manuscript test ORACLES.
    B = F(1, d)*common_derivative(common_derivative(U))
    identity("full-collective-hessian", B, r + F(3, d)*g*S + F(1, d)*lam*D,
             "eq:collective-hessian")
    fourth = U
    for _ in range(4):
        fourth = common_derivative(fourth)
    identity("unit-collective-fourth-derivative", F(1, d*d)*fourth, F(6, d)*g,
             "eq:potential")
    identity("zero-source-parity", U.sign_flip(set(q_names)), U, "eq:potential")
    identity("graph-square-expansion", D,
             INTERNAL_DIMENSION*S - 2*sum((q[i]*q[j] for i, j in edges), P()),
             "eq:collective-graph-expectation")

    for i, j in combinations(vertices, 2):
        actual = -U.diff(q_names[i]).diff(q_names[j])
        expected = (F(1, 4)*lam*((q[i]+q[j])**2 + 5*(q[i]-q[j])**2)
                    if (i, j) in edges else P())
        identity("mixed-log-density-" + str(i) + "-" + str(j), actual, expected,
                 "eq:log-supermodular")

    bond = F(1, 2)*c*(a-b)**2
    shifted_bond = bond.diff("a") + bond.diff("b")
    identity("spatial-common-shift-cancels", shifted_bond, P(), "eq:collective-hessian")
    identity("spatial-mixed-log-density", -bond.diff("a").diff("b"), c,
             "eq:log-supermodular")

    # Expectation symbols are formal variables, NOT a pointwise positivity claim.
    s, dint, moment = (variable(name) for name in ("Sbar", "Dbar", "Mbar"))
    b_expectation = r + F(3, d)*g*s + F(1, d)*lam*dint
    deficit_sum = 3*(g+lam)*(moment-F(1, d)*s) + b_expectation + F(1, d)*lam*(3*s-dint)
    identity("conditional-moment-certificate", 3*(g+lam)*moment+r, deficit_sum,
             "eq:theta-q")

    m, theta, x, t, integral = (variable(name) for name in ("m", "theta", "x", "t", "I3"))
    # t denotes tanh(x); polynomial algebra does not prove this analytic relation.
    beta_on_root = 4*m*theta*x*t
    a0 = 8*c*m*theta**2
    identity("denominator-cleared-threshold", 2*beta_on_root*c*theta*t - x*integral,
             x*(a0*t*t-integral), "eq:threshold-algebra")

    # Hostile alternatives must differ as polynomials, not merely at sample points.
    check("reject-extra-hbar-square", B != F(9, 4)*B, "different", "different")
    check("reject-missing-locking-curvature", B != r+F(3, d)*g*S, "different", "different")
    first_i, first_j = edges[0]
    log_mixed = -U.diff(q_names[first_i]).diff(q_names[first_j])
    check("reject-energy-hessian-sign", log_mixed != -log_mixed, "different", "different")
    check("reject-half-threshold-amplitude",
          2*beta_on_root*c*theta*t != x*(F(1, 2)*a0*t*t), "different", "different")
    check("reject-doubled-graph-expectation-coefficient",
          deficit_sum != 3*(g+lam)*(moment-F(1, d)*s) + b_expectation
          + F(1, d)*lam*(6*s-dint), "different", "different")

    alternating = {name: (-1)**i.bit_count() for i, name in enumerate(q_names)}
    point_s, point_d = S.value(alternating), D.value(alternating)
    check("expectation-bound-not-pointwise", point_d > INTERNAL_DIMENSION*point_s,
          {"D": str(point_d), "S": str(point_s)}, "D > degree*S on alternating vector")

    return {"checks": checks, "assertions_passed": len(checks), "identities": identities,
            "model": {"internal_dimension": INTERNAL_DIMENSION, "components": d,
                      "edges": [list(edge) for edge in edges], "potential": U.rows()},
            "scope": "Exact polynomial identities for the printed finite local model; expectation inequalities require their separately reviewed analytic premises."}


def build_payload():
    if not __debug__:
        raise ValueError("Use assertion-enabled Python, without -O.")
    package = json.loads((ROOT / PACKAGE).read_text(encoding="utf-8"))
    expected_scope = {"result_id": "R-497", "tier": "T0",
                      "claim_bearing": False, "publication_status": "RESEARCH_ONLY"}
    if (package.get("claim_status") != expected_scope
            or package.get("status") != "UNFROZEN_CONTENT_REVIEW"
            or package.get("pdf_status") != "DEFERRED"):
        raise ValueError("Current package scope or PDF boundary changed.")
    frozen = json.loads((ROOT / FROZEN).read_text(encoding="utf-8"))
    if frozen["tier"] != "T0" or frozen["claim_bearing"] is not False:
        raise ValueError("Unexpected result scope.")
    protected = {row["path"]: row["sha256"] for row in frozen["source_files"]}
    for path, expected in protected.items():
        if sha(ROOT / path) != expected:
            raise ValueError("Frozen authority changed: " + path)

    syntax = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            if node.level:
                raise ValueError("Relative imports are not allowed in this audit.")
            imports.add(node.module.split(".")[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "__import__", "compile"}:
                raise ValueError("Dynamic execution is not allowed in this audit.")
    allowed = {"fractions", "itertools", "pathlib", "argparse", "ast", "hashlib",
               "json", "os", "platform", "sys", "tempfile"}
    if not imports <= allowed:
        raise ValueError("Non-standard or undeclared import.")
    result = algebra()
    sources = (MANUSCRIPT, NOTE, FROZEN,
               Path(__file__).resolve().relative_to(ROOT).as_posix())
    result.update({"schema": "tect/q3lock-nonimporting-algebra/1.0", "status": "PASS",
                   "script_version": __version__, "result_id": "R-497",
                   "tier": "T0", "claim_bearing": False, "pdf_status": "DEFERRED",
                   "source_base_commit": SOURCE_BASE_COMMIT,
                   "source_hashes": {path: sha(ROOT / path) for path in sources},
                   "authority_files_verified": len(protected),
                   "static_import_roots": sorted(imports),
                   "independence": "No repository implementation is loaded or run. Authored in the same research task; not a separate reviewer or proof-kernel acceptance."})
    return result


def write_new(path, content):
    if os.path.lexists(path):
        raise FileExistsError("Refusing to overwrite: " + str(path))
    data = (json.dumps(content, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write-new", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    try:
        if not __debug__:
            raise ValueError("Use assertion-enabled Python, without -O.")
        if args.self_test:
            payload = algebra()
            print("ALGEBRA SELF-TEST: PASS", payload["assertions_passed"])
            return 0
        if args.write_new and os.path.lexists(args.output):
            raise FileExistsError("Refusing to overwrite: " + str(args.output))
        before = None if args.write_new else args.output.read_bytes()
        payload = build_payload()
        environment = {"python": sys.version, "implementation": platform.python_implementation(),
                       "platform": platform.platform(), "arithmetic": "exact rational coefficients"}
        if args.write_new:
            write_new(args.output, {"replay": payload, "producer_environment": environment})
        else:
            # Producer environment is historical metadata, not silently rewritten.
            # Source hashes, every identity and all assertions must match exactly.
            if json.loads(before)["replay"] != payload or args.output.read_bytes() != before:
                raise ValueError("Stored algebra differs; investigate, never replace history.")
        print("Q3LOCK NONIMPORTING ALGEBRA: PASS", payload["assertions_passed"],
              "checks;", len(payload["identities"]), "coefficient identities;",
              "replay SHA256", encoded_hash(payload))
        print("Current interpreter:", platform.python_version(), platform.python_implementation())
        return 0
    except (OSError, ValueError, AssertionError, KeyError, TypeError) as error:
        print("Q3LOCK NONIMPORTING ALGEBRA: FAIL:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
