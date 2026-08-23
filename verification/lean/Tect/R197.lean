import Mathlib

namespace Tect.R197

/-!
  Exact algebraic core for the finite F_ref stochastic-quantization candidate.
  The finite-dimensional analytic existence statement and the R-192 spatial
  owner slots remain outside this rational cross-check.
-/

def gibbsResidual (beta fp fpp : Rat) : Rat :=
  (fpp - beta * fp^2) + (1 / beta) * (-beta * fpp + beta^2 * fp^2)

theorem gibbs_residual_zero {beta fp fpp : Rat} (hbeta : beta ≠ 0) :
    gibbsResidual beta fp fpp = 0 := by
  unfold gibbsResidual
  field_simp
  ring

theorem quadratic_positive_of_negative_discriminant
    {a b c x : Rat} (ha : 0 < a) (hdisc : b^2 - 4 * a * c < 0) :
    0 < a * x^2 + b * x + c := by
  have hs : 0 ≤ (2 * a * x + b)^2 := sq_nonneg (2 * a * x + b)
  nlinarith

theorem classii_square_completion
    {a b c u v : Rat} (ha : a ≠ 0) :
    a * u^2 + 2 * b * u * v + c * v^2 =
      ((a * u + b * v)^2 + (a * c - b^2) * v^2) / a := by
  field_simp
  ring

theorem classii_form_nonnegative
    {a b c u v : Rat} (ha : 0 < a) (hdet : 0 ≤ a * c - b^2) :
    0 ≤ a * u^2 + 2 * b * u * v + c * v^2 := by
  rw [classii_square_completion (ne_of_gt ha)]
  have hs : 0 ≤ (a * u + b * v)^2 := sq_nonneg (a * u + b * v)
  have ht : 0 ≤ (a * c - b^2) * v^2 :=
    mul_nonneg hdet (sq_nonneg v)
  exact div_nonneg (add_nonneg hs ht) (le_of_lt ha)

end Tect.R197
