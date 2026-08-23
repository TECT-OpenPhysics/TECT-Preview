import Mathlib

namespace Tect.R198

/-!
  Exact algebraic cross-check for the nonlinear F_ref root-filtration witness.
  The identity is a finite Laurent-polynomial calculation; it does not assert
  a production heat-root map or a continuum theorem.
-/

theorem nonlinear_mode_mix_identity (z : ℂ) (hz : z ≠ 0) :
    (2 + z + z⁻¹)^2 * (z + z^2) = z⁻¹ * (1 + z)^5 := by
  field_simp [hz]
  ring

theorem nonlinear_mode_mix_coefficients (z : ℂ) (hz : z ≠ 0) :
    z^2 * ((2 + z + z⁻¹)^2 * (z + z^2)) =
      z + 5 * z^2 + 10 * z^3 + 10 * z^4 + 5 * z^5 + z^6 := by
  field_simp [hz]
  ring

end Tect.R198
