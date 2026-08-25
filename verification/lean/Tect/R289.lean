import Mathlib

namespace Tect.R289

/- R289 checks only rational source-radius and factorial fixtures.  It does not
   formalize the coefficient completion, Q3 operators, commutator histories,
   or any thermodynamic/QFT limit. -/

def sourceRadius : ℚ := 1 / 4
def reducedSourceRadius : ℚ := 1 / 8
def comparisonBase : ℚ := 12
def sourceRate : ℚ := 1382807 / 7168

theorem source_radius_fixture : sourceRadius = 1 / 4 := by
  norm_num [sourceRadius]

theorem reduced_radius_fixture : 0 < reducedSourceRadius ∧ reducedSourceRadius < sourceRadius := by
  norm_num [reducedSourceRadius, sourceRadius]

theorem source_rate_fixture : sourceRate = 1382807 / 7168 := by
  norm_num [sourceRate]

theorem branch_fixture : comparisonBase = 12 := by
  norm_num [comparisonBase]

theorem order_eight_derivative_ratio :
    (Nat.factorial 8 : ℚ) / sourceRadius ^ 8 = 2642411520 := by
  norm_num [sourceRadius, Nat.factorial]

theorem order_eight_branch_power : (comparisonBase : ℚ) ^ 8 = 429981696 := by
  norm_num [comparisonBase]

theorem order_eight_derivative_exceeds_branch :
    (Nat.factorial 8 : ℚ) / sourceRadius ^ 8 > comparisonBase ^ 8 := by
  norm_num [sourceRadius, comparisonBase, Nat.factorial]

theorem order_thirty_two_factorial_square :
    (32 : ℚ) / 2 < (Nat.factorial 32 : ℚ) ^ (2 : ℕ) := by
  norm_num [Nat.factorial]

theorem order_thirty_two_lower_bound_integer :
    (16 : ℚ) ^ 16 ≤ (Nat.factorial 32 : ℚ) := by
  norm_num [Nat.factorial]

theorem order_thirty_two_lower_bound :
    (Nat.factorial 32 : ℚ) / sourceRadius ^ 32 > comparisonBase ^ 32 := by
  norm_num [sourceRadius, comparisonBase, Nat.factorial]

theorem radius_loss_scope :
    0 < reducedSourceRadius ∧ reducedSourceRadius < sourceRadius := by
  exact reduced_radius_fixture

end Tect.R289
