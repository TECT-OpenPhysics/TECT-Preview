import Mathlib

namespace Tect.PahOmc020Projective

/- These declarations check only the finite rational envelope used by the
   projective local-correlation audit.  They do not formalize a measure,
   a coupling, a completed Hilbert space, or any anchored limit. -/

def tailTerm (a b t : ℚ) (d : ℕ) : ℚ :=
  a * b ^ (d - 1) * t ^ d / (d.factorial : ℚ)

def stateError (f d q : ℚ) (level stage : ℕ) : ℚ :=
  4 * f * d * q ^ (level - stage)

theorem source_overlap_formula :
    (16 : ℚ) * (4 * 2 + 1) = 144 := by
  norm_num

theorem source_two_copy_formula :
    (2 : ℚ) * ((16 : ℚ) * (4 * 2 + 1)) = 288 := by
  norm_num

theorem source_first_root_formula :
    (16 : ℚ) * (2 + 2 * 2 + 1) = 112 := by
  norm_num

theorem independent_first_root_formula :
    (16 : ℚ) * (3 + 2 * 2 + 1) = 128 := by
  norm_num

theorem tail_ratio_fixture :
    (288 : ℚ) * (1 / 4 : ℚ) / (256 + 1) < 1 := by
  norm_num

theorem tail_term_nonnegative (a b t : ℚ) (d : ℕ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (ht : 0 ≤ t) :
    0 ≤ tailTerm a b t d := by
  unfold tailTerm
  positivity

theorem tail_term_fixture_positive :
    0 < tailTerm (112 : ℚ) 288 (1 / 4 : ℚ) 256 := by
  unfold tailTerm
  positivity

theorem two_copy_tail_argument (a b t : ℚ) (d : ℕ) :
    (2 : ℚ) ^ (d + 1) * (a * b ^ d * t ^ (d + 1)) =
      2 * a * (2 * b) ^ d * t ^ (d + 1) := by
  rw [show (2 : ℚ) ^ (d + 1) = 2 * 2 ^ d by rw [pow_succ]; ring]
  rw [show (2 * b) ^ d = 2 ^ d * b ^ d by rw [mul_pow]]
  ring

theorem finite_word_cutoff_precedes_n : (6 : ℕ) < 12 := by
  norm_num

theorem state_fixture_pair_decreases :
    stateError (5 / 4 : ℚ) (3 / 2 : ℚ) (1 / 2 : ℚ) 5 2
      < stateError (5 / 4 : ℚ) (3 / 2 : ℚ) (1 / 2 : ℚ) 3 2 := by
  norm_num [stateError]

theorem state_fixture_pair_second_decreases :
    stateError (5 / 4 : ℚ) (3 / 2 : ℚ) (1 / 2 : ℚ) 7 2
      < stateError (5 / 4 : ℚ) (3 / 2 : ℚ) (1 / 2 : ℚ) 5 2 := by
  norm_num [stateError]

end Tect.PahOmc020Projective
