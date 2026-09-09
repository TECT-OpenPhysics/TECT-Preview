"""Hostile checks for the non-importing polynomial audit, not proof acceptance."""
from contextlib import redirect_stderr
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import io
import json
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/q3lock_nonimporting_algebra.py"
SPEC = spec_from_file_location("nonimporting_algebra", SCRIPT)
ALG = module_from_spec(SPEC)
SPEC.loader.exec_module(ALG)


class PolynomialAuditTests(unittest.TestCase):
    def test_fraction_cancellation_and_zero_derivative(self):
        a = ALG.variable("a")
        self.assertEqual(F(1, 3)*a + F(2, 3)*a - a, 0)
        self.assertEqual(ALG.P(7).diff("a"), 0)

    def test_monomial_multiplication_is_commutative(self):
        a, b = ALG.variable("a"), ALG.variable("b")
        self.assertEqual((a*b)**3, a**3*b**3)
        self.assertEqual((a*b)**3, b**3*a**3)

    def test_mixed_derivatives_commute(self):
        a, b = ALG.variable("a"), ALG.variable("b")
        polynomial = (a-b)**2*(a*a+b*b)
        self.assertEqual(polynomial.diff("a").diff("b"), polynomial.diff("b").diff("a"))
        self.assertEqual(polynomial.diff("a").diff("b"), -6*a*a+8*a*b-6*b*b)

    def test_signed_evaluation_and_parity(self):
        a, b = ALG.variable("a"), ALG.variable("b")
        polynomial = (a-b)**2*(a*a+b*b)
        self.assertEqual(polynomial.sign_flip({"a", "b"}), polynomial)
        self.assertEqual(polynomial.value({"a": F(1, 2), "b": F(-2, 3)}),
                         (F(1, 2)+F(2, 3))**2*(F(1, 2)**2+F(2, 3)**2))

    def test_negative_and_fractional_powers_fail(self):
        for exponent in (-1, F(1, 2)):
            with self.assertRaises(ValueError):
                ALG.variable("a")**exponent

    def test_all_recorded_identities_have_zero_coefficient_residual(self):
        payload = ALG.algebra()
        self.assertTrue(payload["checks"])
        self.assertEqual(payload["assertions_passed"], len(payload["checks"]))
        self.assertTrue(all(row["pass"] for row in payload["checks"]))
        self.assertTrue(all(row["residual"] == [] for row in payload["identities"]))

    def test_broken_differentiator_is_detected_by_ring_oracle(self):
        with patch.object(ALG.P, "diff", return_value=ALG.P()):
            with self.assertRaises(AssertionError):
                ALG.algebra()

    def test_atomic_result_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            ALG.write_new(target, {"historical": True})
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                ALG.write_new(target, {"replacement": True})
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(list(Path(folder).glob("*.tmp")), [])

    def test_missing_result_fails_before_builder(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "missing.json"
            with patch.object(ALG, "build_payload") as builder, redirect_stderr(io.StringIO()):
                self.assertEqual(ALG.main(["--output", str(target)]), 1)
                builder.assert_not_called()
            self.assertFalse(target.exists())

    def test_stale_identity_is_not_accepted_or_rewritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            ALG.write_new(target, {"replay": {"identity": "old"}})
            before = target.read_bytes()
            with patch.object(ALG, "build_payload", return_value={"identity": "changed"}):
                with redirect_stderr(io.StringIO()):
                    self.assertEqual(ALG.main(["--output", str(target)]), 1)
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(json.loads(before)["replay"]["identity"], "old")


if __name__ == "__main__":
    unittest.main()
