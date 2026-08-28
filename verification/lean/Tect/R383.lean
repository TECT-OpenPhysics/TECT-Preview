import Mathlib

namespace Tect.R383

/- R383 formalizes the scalar envelopes used by the frequency-adapted
   endpoint filter.  The finite matrix profiles are executable evidence;
   these lemmas do not assert filter removal, cutoff uniformity, or a
   continuum theorem. -/

theorem filtered_weight_nonnegative (u : ℝ) (hu : 0 ≤ u) :
    0 ≤ 1 / (1 + u) ^ 2 := by
  positivity

theorem filtered_weight_le_one (u : ℝ) (hu : 0 ≤ u) :
    1 / (1 + u) ^ 2 ≤ 1 := by
  have hden : 0 < (1 + u) ^ 2 := by
    positivity
  apply (div_le_iff₀ hden).2
  nlinarith [sq_nonneg u]

theorem filtered_endpoint_half_factor (u : ℝ) (hu : 0 ≤ u) :
    u / (1 + u) ≤ 1 := by
  have hden : 0 < 1 + u := by
    linarith
  apply (div_le_iff₀ hden).2
  linarith

theorem filtered_endpoint_unit_factor (u : ℝ) (hu : 0 ≤ u) :
    u / (1 + u) ^ 2 ≤ 1 := by
  have hden : 0 < (1 + u) ^ 2 := by
    positivity
  apply (div_le_iff₀ hden).2
  nlinarith [sq_nonneg u]

theorem filtered_m2_unit_factor (u : ℝ) (hu : 0 ≤ u) :
    u ^ 2 / (1 + u) ^ 2 ≤ 1 := by
  have hden : 0 < (1 + u) ^ 2 := by
    positivity
  apply (div_le_iff₀ hden).2
  nlinarith

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R383
