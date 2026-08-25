import Mathlib

namespace Tect.R281

theorem finite_form_ratio_implies_domination {n d c : ℝ} (hd : 0 < d) (h : n / d ≤ c) :
    n ≤ c * d := by
  have hmul := (div_le_iff₀ hd).mp h
  nlinarith

theorem degree_fixture : ((10 : ℝ) / 2) = 5 := by
  norm_num

end Tect.R281
