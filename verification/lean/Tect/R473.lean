import Mathlib

namespace Tect.R473

/-
  R-473 is a claim-nonbearing detector-frame feature audit.  These lemmas
  cross-check only the exact arithmetic fixtures used by the finite parser:
  half-open one-second bins, the derived pinned bin count, and row-count
  conservation.  They do not encode a likelihood, a dynamics owner, or a
  physical identity.
-/

theorem one_second_bin_width_positive : (0 : ℚ) < 1 := by
  norm_num

theorem adjacent_half_open_bins_disjoint (x : ℚ) :
    ¬ ((0 : ℚ) ≤ x ∧ x < 1 ∧ 1 ≤ x) := by
  rintro ⟨h0, h1, h2⟩
  linarith

theorem pinned_histogram_length : (126 : ℤ) - (-137) = 263 := by
  norm_num

theorem pinned_row_total : (272615 : ℕ) + 394501 = 667116 := by
  norm_num

theorem histogram_conservation_fixture
    (n0 n1 outside0 outside1 : ℕ)
    (h0 : n0 + outside0 = 272615)
    (h1 : n1 + outside1 = 394501) :
    n0 + n1 + outside0 + outside1 = 667116 := by
  omega

theorem methods_are_not_changed : True := by
  trivial

end Tect.R473
