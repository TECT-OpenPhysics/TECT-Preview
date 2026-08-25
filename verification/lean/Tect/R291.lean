import Mathlib

namespace Tect.R291

/- R291 checks only the finite rational signed source-slice fixtures. It does
   not formalize the multivariate Q3 commutator, an unbounded common core, a
   thermodynamic limit, or any QFT reconstruction. -/

def sourceRadius : ℚ := 1 / 4
def reducedSourceRadius : ℚ := 1 / 8
def quarticCoefficient : ℚ := 51 / 140
def comparisonBase : ℚ := 12

theorem slice_fixture :
    (-quarticCoefficient : ℚ) = -51 / 140 ∧ (-(2 : ℚ)) = -2 := by
  norm_num [quarticCoefficient]

theorem orientation_fixture :
    (-51 / 140 : ℚ) = (-51 / 140 : ℚ) := by
  norm_num

theorem degree_fixture : (1 + 3 * 16 : ℕ) = 49 := by
  norm_num

theorem signed_top_product_fixture :
    (-quarticCoefficient : ℚ) ^ 16 *
        (1 * 4 * 7 * 10 * 13 * 16 * 19 * 22 * 25 * 28 * 31 * 34 * 37 * 40 * 43 * 46) =
      (51 / 140 : ℚ) ^ 16 *
        (1 * 4 * 7 * 10 * 13 * 16 * 19 * 22 * 25 * 28 * 31 * 34 * 37 * 40 * 43 * 46) := by
  norm_num [quarticCoefficient]

theorem order_sixteen_signed_slice_ratio :
    (51 / 140 : ℚ) ^ 16 *
        (1 * 4 * 7 * 10 * 13 * 16 * 19 * 22 * 25 * 28 * 31 * 34 * 37 * 40 * 43 * 46) *
        (Nat.factorial 49 : ℚ) * reducedSourceRadius ^ 49 / sourceRadius >
      comparisonBase ^ 16 := by
  norm_num [reducedSourceRadius, sourceRadius, comparisonBase, Nat.factorial]

theorem signed_slice_branch_power : (comparisonBase : ℚ) ^ 16 = 184884258895036416 := by
  norm_num [comparisonBase]

theorem signed_slice_scope :
    0 < reducedSourceRadius ∧ reducedSourceRadius < sourceRadius := by
  norm_num [reducedSourceRadius, sourceRadius]

end Tect.R291
