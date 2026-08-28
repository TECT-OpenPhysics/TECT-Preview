import Mathlib

namespace Tect.R391

theorem conditional_mutual_information_split {sab sbc sb sabc : ℝ} :
    sab + sbc - sb - sabc = (sab - sb) + (sbc - sabc) := by
  ring

theorem recoverability_scale_nonnegative {q : ℝ} (_hq : 0 ≤ q) :
    0 ≤ Real.sqrt (2 * q) := by
  positivity

theorem trace_distance_range {d : ℝ} (h0 : 0 ≤ d) (h1 : d ≤ 1) :
    d ∈ Set.Icc (0 : ℝ) 1 := by
  exact ⟨h0, h1⟩

theorem qcmI_clamp_nonnegative {q : ℝ} : 0 ≤ max q 0 := by
  exact le_max_right q 0

theorem scope_fixture :
    (0 ≤ (1 : ℝ) / 4) ∧ ((1 : ℝ) / 4 + (3 : ℝ) / 4 = 1) := by
  norm_num

end Tect.R391
