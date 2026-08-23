import Mathlib

namespace Tect.R199

/-!
  Exact algebraic cross-check for two nonlinear support closures.  These are
  Laurent-polynomial identities only; they do not assert a stochastic flow or
  a production heat/root owner.
-/

theorem second_nonlinear_support_identity (z : ℂ) (hz : z ≠ 0) :
    ((z⁻¹)^4 * (1 + z)^5) * (z⁻¹ * (1 + z)^5) =
      (z⁻¹)^5 * (1 + z)^10 := by
  field_simp [hz] <;> ring

theorem second_nonlinear_support_closure (z : ℂ) (hz : z ≠ 0) :
    ((z⁻¹)^5 * (1 + z)^10)^2 * (z⁻¹ * (1 + z)^5) =
      (z⁻¹)^11 * (1 + z)^25 := by
  field_simp [hz] <;> ring

theorem all_side16_residues :
    (14 : Int) - (-11) + 1 ≥ 16 := by
  norm_num

end Tect.R199
