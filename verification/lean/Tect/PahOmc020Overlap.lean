import Mathlib

namespace Tect.PahOmc020Overlap

/- These are the finite arithmetic consequences of the OMC-004 footprint
   construction.  The source-specific coupling from connected words to the
   evolving boundary term is deliberately not assumed here. -/

theorem overlap_branching_bound (roots_per_column radius : ℕ)
    (hroots : roots_per_column ≤ 16) (hradius : radius ≤ 2) :
    roots_per_column * (4 * radius + 1) ≤ 144 := by
  have hwidth : 4 * radius + 1 ≤ 9 := by omega
  have hfirst := Nat.mul_le_mul_right (4 * radius + 1) hroots
  have hsecond := Nat.mul_le_mul_left 16 hwidth
  calc
    roots_per_column * (4 * radius + 1) ≤ 16 * (4 * radius + 1) := hfirst
    _ ≤ 16 * 9 := hsecond
    _ = 144 := by norm_num

theorem connected_word_count_bound (a b : ℕ) (counts : ℕ → ℕ)
    (hzero : counts 0 ≤ a)
    (hstep : ∀ k, counts (k + 1) ≤ b * counts k) :
    ∀ k, counts k ≤ a * b ^ k := by
  intro k
  induction k with
  | zero => simpa using hzero
  | succ k ih =>
      calc
        counts (k + 1) ≤ b * counts k := hstep k
        _ ≤ b * (a * b ^ k) := Nat.mul_le_mul_left b ih
        _ = a * b ^ (k + 1) := by
          simp [pow_succ, Nat.mul_comm, Nat.mul_left_comm]

end Tect.PahOmc020Overlap
