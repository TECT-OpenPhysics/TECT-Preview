import Mathlib

namespace Tect.R466

/-!
  R-466 formalises the algebraic kernel of the finite tube interface.
  The source-owned branch embedding, the energy ceiling, the radial partition
  comparison, and all cutoff limits remain explicit hypotheses outside this
  kernel.
-/

theorem box_volume_positive (delta : ℚ) (d : ℕ) (hdelta : 0 < delta) :
    0 < (2 * delta) ^ d := by
  positivity

theorem box_volume_identity (delta : ℚ) (d : ℕ) :
    (2 * delta) ^ d = (2 * delta) ^ d := by
  rfl

theorem tube_mass_lower_ratio (numerator z zUpper : ℚ)
    (hnumerator : 0 ≤ numerator) (hz : 0 < z) (hzUpper : 0 < zUpper)
    (hpartition : z ≤ zUpper) :
    numerator / zUpper ≤ numerator / z := by
  apply (div_le_div_iff₀ hzUpper hz).2
  exact mul_le_mul_of_nonneg_left hpartition hnumerator

theorem lower_ratio_nonnegative (numerator zUpper : ℚ)
    (hnumerator : 0 ≤ numerator) (hzUpper : 0 < zUpper) :
    0 ≤ numerator / zUpper := by
  positivity

end Tect.R466
