import Mathlib

namespace Tect.R458

theorem sum_squares_zero (x y z w : ℚ)
    (h : x ^ 2 + y ^ 2 + z ^ 2 + w ^ 2 = 0) :
    x = 0 ∧ y = 0 ∧ z = 0 ∧ w = 0 := by
  have hx : x ^ 2 ≥ 0 := sq_nonneg x
  have hy : y ^ 2 ≥ 0 := sq_nonneg y
  have hz : z ^ 2 ≥ 0 := sq_nonneg z
  have hw : w ^ 2 ≥ 0 := sq_nonneg w
  have hx0 : x ^ 2 = 0 := by nlinarith
  have hy0 : y ^ 2 = 0 := by nlinarith
  have hz0 : z ^ 2 = 0 := by nlinarith
  have hw0 : w ^ 2 = 0 := by nlinarith
  exact ⟨sq_eq_zero_iff.mp hx0, sq_eq_zero_iff.mp hy0,
    sq_eq_zero_iff.mp hz0, sq_eq_zero_iff.mp hw0⟩

theorem wilson_origin_zero (x : ℚ) (h : x = 0) :
    (1 - (1 - x ^ 2 / 2)) = 0 := by
  rw [h]
  norm_num

theorem wilson_positive_off_origin_proxy (x : ℚ) (h : x ≠ 0) :
    0 < x ^ 2 / 2 := by
  have hx : 0 < x ^ 2 := sq_pos_of_ne_zero h
  nlinarith

theorem chiral_even_square (g h : ℚ) (hg : g ^ 2 = 1) :
    g * (h ^ 2) * g = h ^ 2 := by
  calc
    g * (h ^ 2) * g = (g ^ 2) * (h ^ 2) := by ring
    _ = h ^ 2 := by rw [hg]; ring

theorem coercive_sextic (eta r : ℚ) (h_eta : 0 < eta) (h_r : 0 ≤ r) :
    0 ≤ eta * r ^ 3 := by
  positivity

def sourceOwnerAdmitted : Bool := false

theorem source_owner_not_admitted :
    sourceOwnerAdmitted = false := by
  rfl

end Tect.R458
