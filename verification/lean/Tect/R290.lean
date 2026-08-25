import Mathlib

namespace Tect.R290

/- R290 checks only the finite rational factorial-seminorm and top-monomial
   fixtures. It does not formalize the signed Q3 history, an unbounded common
   core, a thermodynamic limit, or any QFT reconstruction. -/

def sourceRadius : ℚ := 1 / 4
def reducedSourceRadius : ℚ := 1 / 8
def topCoefficient : ℚ := 51 / 140
def comparisonBase : ℚ := 12

theorem source_radius_fixture : sourceRadius = 1 / 4 := by
  norm_num [sourceRadius]

theorem reduced_radius_fixture : 0 < reducedSourceRadius ∧ reducedSourceRadius < sourceRadius := by
  norm_num [reducedSourceRadius, sourceRadius]

theorem top_coefficient_fixture : topCoefficient = 51 / 140 := by
  norm_num [topCoefficient]

theorem factorial_derivative_fixture (n : ℕ) :
    (n + 1 : ℚ) * (Nat.factorial n : ℚ) = (Nat.factorial (n + 1) : ℚ) := by
  rw [Nat.factorial_succ]
  norm_num

theorem top_branch_coefficient_m16 :
    topCoefficient ^ 16 *
        ((1 : ℚ) * 4 * 7 * 10 * 13 * 16 * 19 * 22 * 25 * 28 * 31 * 34 * 37 * 40 * 43 * 46) =
      (51 / 140 : ℚ) ^ 16 *
        (1 * 4 * 7 * 10 * 13 * 16 * 19 * 22 * 25 * 28 * 31 * 34 * 37 * 40 * 43 * 46) := by
  norm_num [topCoefficient]

theorem order_sixteen_top_branch_ratio :
    (51 / 140 : ℚ) ^ 16 *
        (1 * 4 * 7 * 10 * 13 * 16 * 19 * 22 * 25 * 28 * 31 * 34 * 37 * 40 * 43 * 46) *
        (Nat.factorial 49 : ℚ) * reducedSourceRadius ^ 49 / sourceRadius >
      comparisonBase ^ 16 := by
  norm_num [reducedSourceRadius, sourceRadius, comparisonBase, Nat.factorial]

theorem order_sixteen_branch_power : (comparisonBase : ℚ) ^ 16 = 184884258895036416 := by
  norm_num [comparisonBase]

theorem factorial_lower_bound_m16 : (16 : ℚ) ^ 32 ≤ (Nat.factorial 49 : ℚ) := by
  norm_num [Nat.factorial]

theorem radius_loss_scope :
    0 < reducedSourceRadius ∧ reducedSourceRadius < sourceRadius := by
  exact reduced_radius_fixture

end Tect.R290
