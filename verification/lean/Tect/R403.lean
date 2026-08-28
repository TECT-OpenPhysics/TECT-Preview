import Mathlib

namespace Tect.R403

/- R403 formalizes only scalar positivity and finite diagnostic arithmetic for
   the increasing-cutoff stress.  It does not formalize the finite matrices,
   Gibbs rows, cutoff profile, or any uniform/continuum limit. -/

theorem positive_ratio {a b : ℝ} (ha : 0 < a) (hb : 0 < b) :
    0 < b / a := by
  positivity

theorem finite_cutoff_growth :
    (0 : ℝ) < (1 : ℝ) / 2 ∧ ((1 : ℝ) / 2 ≤ 1) := by
  norm_num

theorem finite_scope :
    (0 : ℝ) ≤ 1 := by
  norm_num

end Tect.R403
