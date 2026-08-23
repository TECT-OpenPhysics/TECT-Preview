import Mathlib

namespace Tect.R196

/-!
  Exact algebraic core for the finite A1 Gaussian/OU output-heat screen.
  The analytic covariance and tail hypotheses remain outside this small
  rational Lean cross-check.
-/

def generatorFactor : Rat := 3 * 2

theorem generator_factor_six : generatorFactor = 6 := by
  norm_num [generatorFactor]

def outputCharge (r s k : Rat) : Rat :=
  generatorFactor * r^2 * s / k

theorem output_charge_nonneg {r s k : Rat}
    (hr : 0 ≤ r) (hs : 0 ≤ s) (hk : 0 < k) :
    0 ≤ outputCharge r s k := by
  unfold outputCharge
  have hnum : 0 ≤ generatorFactor * r^2 * s := by
    exact mul_nonneg (mul_nonneg (by norm_num [generatorFactor]) (sq_nonneg r)) hs
  exact div_nonneg hnum (le_of_lt hk)

theorem heat_integral_identity {r s k : Rat} (hk : 0 < k) :
    2 * (generatorFactor * r^2 * s) / (2 * k) = outputCharge r s k := by
  unfold outputCharge
  field_simp

theorem tail_exponent_six : (2 : Int) + 4 = 6 := by
  norm_num

end Tect.R196
