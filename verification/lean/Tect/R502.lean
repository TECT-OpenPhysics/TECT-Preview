import Mathlib

namespace Tect.R502

/- A quantitative consequence of the PAH-OMC-014 non-identifiability boundary.
   The weights are variables, not a proposed PAH sector law.  When one
   component has zero value and another has a strictly positive value, the
   grade-blind mixture is positive exactly when the positive component receives
   positive weight. -/

def twoSectorValue (w0 w1 a1 : ℝ) : ℝ := w0 * 0 + w1 * a1

theorem twoSectorValue_factor (w0 w1 a1 : ℝ) :
    twoSectorValue w0 w1 a1 = w1 * a1 := by
  simp [twoSectorValue]

theorem twoSectorValue_nonzero_iff
    {w0 w1 a1 : ℝ}
    (hw1 : 0 ≤ w1) (ha1 : 0 < a1) :
    twoSectorValue w0 w1 a1 ≠ 0 ↔ 0 < w1 := by
  rw [twoSectorValue_factor]
  constructor
  · intro h
    exact lt_of_le_of_ne hw1 (Ne.symm (by
      intro hzero
      apply h
      rw [hzero]
      simp))
  · intro h
    exact mul_pos h ha1 |>.ne'

theorem lower_bound_requires_positive_weight
    {w0 w1 a1 delta : ℝ}
    (hw1 : 0 ≤ w1) (hdelta : 0 < delta)
    (hmixture : delta ≤ twoSectorValue w0 w1 a1) :
    0 < w1 := by
  rw [twoSectorValue_factor] at hmixture
  by_contra hnot
  have hw1zero : w1 = 0 := le_antisymm (not_lt.mp hnot) hw1
  rw [hw1zero] at hmixture
  linarith

end Tect.R502
