import Mathlib

namespace Tect.R457

theorem plaquette_charge_zero :
    (1 : ℤ) + 1 + (-1) + (-1) = 0 := by
  norm_num

theorem covariant_density_charge_zero :
    (1 : ℤ) + (-1) = 0 := by
  norm_num

theorem current_source_charge_zero :
    (-1 : ℤ) + 1 = 0 := by
  norm_num

theorem current_target_charge_zero :
    (-1 : ℤ) + 1 = 0 := by
  norm_num

theorem gauss_matter_charge_zero :
    (-1 : ℤ) + 1 = 0 := by
  norm_num

theorem coercivity_completion (lam x m : ℚ) (h : lam ≠ 0) :
    lam / 4 * (x + m / lam) ^ 2 - m ^ 2 / (4 * lam) =
      lam * x ^ 2 / 4 + m * x / 2 := by
  field_simp [h]
  ring

theorem poisson_self_bracket_zero (a b : ℚ) :
    a * b - b * a = 0 := by
  ring

def sourceOwnerAdmitted : Bool := false

theorem source_owner_not_admitted :
    sourceOwnerAdmitted = false := by
  rfl

end Tect.R457
