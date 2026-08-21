import Mathlib

namespace Tect.R058

/-
  Exact ordered-field core of the registered R-058 budget obstruction.
  The numerical source ratio c > 9/10 is supplied by the hash-pinned
  primary/independent certificate.  Lean checks only the consequence for
  gamma = 81/50 and p >= 1; it does not reprove the degree-65536 source,
  Fierz/resolvent estimates, or any joint-source/limit statement.
-/

theorem allowance_le_gamma_third {p : ℚ} (hp : (1 : ℚ) ≤ p) :
    (81 : ℚ) / (50 * (3 * p)) ≤ (27 : ℚ) / 50 := by
  have hp0 : (0 : ℚ) < p := by linarith
  have hden : (0 : ℚ) < 50 * (3 * p) := by positivity
  apply (div_le_iff₀ hden).2
  nlinarith

theorem budget_gap {c p : ℚ} (hc : (9 : ℚ) / 10 < c) (hp : (1 : ℚ) ≤ p) :
    (81 : ℚ) / (50 * (3 * p)) < c ∧
      c - (81 : ℚ) / 150 > (3 : ℚ) / 10 := by
  have hallow := allowance_le_gamma_third hp
  constructor
  · linarith
  · linarith

theorem gamma_third_exact : (81 : ℚ) / (50 * 3) = (27 : ℚ) / 50 := by
  norm_num

end Tect.R058
