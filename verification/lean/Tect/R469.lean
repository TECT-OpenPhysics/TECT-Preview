import Mathlib

namespace Tect.R469

def strictOverlap (start stop q : ℚ) : Prop := stop > q ∧ start < q

theorem left_endpoint_not_strict_overlap
    {start stop : ℚ} : ¬ strictOverlap start stop stop := by
  intro h
  exact (lt_irrefl stop) h.1

theorem right_endpoint_not_strict_overlap
    {start stop : ℚ} : ¬ strictOverlap start stop start := by
  intro h
  exact (lt_irrefl start) h.2

theorem adjacent_endpoint_no_match
    {a b c q : ℚ} (hq : q = b) :
    ¬ strictOverlap a b q ∧ ¬ strictOverlap b c q := by
  subst q
  constructor
  · intro h
    exact (lt_irrefl b) h.1
  · intro h
    exact (lt_irrefl b) h.2

theorem fallback_before_first
    {q first last : ℚ} (h : q < first) :
    (if q < first then (0 : ℚ) else last) = 0 := by
  simp [h]

theorem fallback_after_or_inside
    {q first last : ℚ} (h : first ≤ q) :
    (if q < first then (0 : ℚ) else last) = last := by
  simp [not_lt.mpr h]

theorem first_index_delegation
    {i : ℕ} (h : i = 0) : i = 0 := by
  exact h

end Tect.R469
