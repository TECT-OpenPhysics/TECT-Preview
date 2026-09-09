"""Hostile finite checks for the Q3LOCK FSS applicability audit."""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import TestCase


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/q3lock_fss_applicability_audit.py"
SPEC = spec_from_file_location("q3lock_fss_applicability_audit", SCRIPT)
AUDIT = module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class FSSApplicabilityTests(TestCase):
    def test_payload_is_finite_and_non_claim_bearing(self):
        payload = AUDIT.build_payload()
        self.assertEqual(payload["status"], "PASS")
        self.assertFalse(payload["claim_bearing"])
        self.assertEqual(payload["assertions_passed"], len(payload["assertions"]))
        self.assertTrue(all(row["pass"] for row in payload["assertions"]))

    def test_backward_difference_has_zero_sum_adjoint(self):
        size = 4
        values = {site: F(site[0] - site[1] + site[2])
                  for site in AUDIT.vertices(size)}
        source = AUDIT.B_field(size, AUDIT.G_field(size, values))
        self.assertEqual(sum(source.values()), F(0))

    def test_wrong_vertex_norm_is_not_the_poisson_norm(self):
        size = 4
        values = {site: F(site[0] * site[1] + site[2] ** 2)
                  for site in AUDIT.vertices(size)}
        gradient = AUDIT.G_field(size, values)
        source = AUDIT.B_field(size, gradient)
        self.assertNotEqual(sum(value ** 2 for value in gradient.values()),
                            sum(value ** 2 for value in source.values()))

    def test_nonradial_witness_has_equal_norm_and_unequal_quartic(self):
        a = [F(1), F(0), F(0), F(0), F(0), F(0), F(0), F(0)]
        b = [F(1, 2), F(1, 2), F(1, 2), F(1, 2), F(0), F(0), F(0), F(0)]
        self.assertEqual(AUDIT.norm_sq(a), AUDIT.norm_sq(b))
        self.assertNotEqual(sum(value ** 4 for value in a),
                            sum(value ** 4 for value in b))


if __name__ == "__main__":
    import unittest
    unittest.main()
