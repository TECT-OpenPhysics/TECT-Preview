import Mathlib

/-!
Finite rational checks for the PAH-OMC-020 non-coordinate coupling candidate.

These declarations formalize only the two-point maximal-overlap fixture and
its conditional-expectation contraction/recovery bound.  They do not define a
PAH owner packet, prove an energy intertwining, establish N2b/N2c/N2d, or
construct a stationary semigroup.
-/

namespace Tect.PahOmc020Coupling

theorem overlap_mass :
    min (3 / 5 : Rat) (1 / 2) + min (2 / 5 : Rat) (1 / 2) = 9 / 10 := by
  norm_num

theorem mismatch_mass :
    1 - (min (3 / 5 : Rat) (1 / 2) + min (2 / 5 : Rat) (1 / 2)) = 1 / 10 := by
  norm_num

theorem coupling_rows :
    (1 / 2 : Rat) + 1 / 10 = 3 / 5 ∧ (0 : Rat) + 2 / 5 = 2 / 5 := by
  norm_num

theorem coupling_columns :
    (1 / 2 : Rat) + 0 = 1 / 2 ∧ (1 / 10 : Rat) + 2 / 5 = 1 / 2 := by
  norm_num

theorem conditional_expectation_contraction (a b : Rat) :
    (3 / 5 : Rat) * (((1 / 2) * a + (1 / 10) * b) / (3 / 5)) ^ 2
      + (2 / 5 : Rat) * (((2 / 5) * b) / (2 / 5)) ^ 2
      ≤ (1 / 2 : Rat) * a ^ 2 + (1 / 2 : Rat) * b ^ 2 := by
  field_simp
  nlinarith [sq_nonneg (a - b)]

theorem local_recovery_bound (f0 f1 B : Rat)
    (hB : 0 ≤ B) (h0 : -B ≤ f0) (h0' : f0 ≤ B)
    (h1 : -B ≤ f1) (h1' : f1 ≤ B) :
    (3 / 5 : Rat) * (((1 / 2) * f0 + (1 / 10) * f1) / (3 / 5) - f0) ^ 2
      + (2 / 5 : Rat) * (((2 / 5) * f1) / (2 / 5) - f1) ^ 2
      ≤ 4 * B ^ 2 * (1 / 10 : Rat) := by
  have hdiff : (f1 - f0) ^ 2 ≤ 4 * B ^ 2 := by
    nlinarith [sq_nonneg (f0 + f1)]
  field_simp
  nlinarith

end Tect.PahOmc020Coupling
