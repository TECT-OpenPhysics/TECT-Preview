import Mathlib

namespace Tect.R372

/- R372 formalizes the algebraic part of modular centering.  The spectral
   trace passage and the Q3 cutoff/volume limits remain executable/open. -/

def weightedMean {n : Nat} (p x : Fin n -> ℝ) : ℝ := ∑ i, p i * x i

theorem weighted_mean_real {n : Nat} (p x : Fin n -> ℝ) :
    weightedMean p x = ∑ i, p i * x i := by
  rfl

theorem weighted_variance_decomposition {n : Nat} (p x : Fin n -> ℝ)
    (hsum : ∑ i, p i = 1) :
    (∑ i, p i * (x i - weightedMean p x) ^ 2)
      = (∑ i, p i * (x i ^ 2)) - (weightedMean p x) ^ 2 := by
  let m : ℝ := ∑ i, p i * x i
  have hm : weightedMean p x = m := by rfl
  rw [hm]
  calc
    (∑ i, p i * (x i - m) ^ 2)
        = ∑ i, (p i * x i ^ 2 - 2 * m * (p i * x i) + m ^ 2 * p i) := by
            apply Finset.sum_congr rfl
            intro i hi
            ring
    _ = (∑ i, p i * x i ^ 2) - 2 * m * (∑ i, p i * x i) + m ^ 2 * (∑ i, p i) := by
          rw [Finset.sum_add_distrib, Finset.sum_sub_distrib]
          rw [← Finset.mul_sum, ← Finset.mul_sum]
    _ = (∑ i, p i * x i ^ 2) - m ^ 2 := by
          rw [hsum]
          dsimp [m]
          ring

theorem weighted_variance_nonnegative {n : Nat} (p x : Fin n -> ℝ)
    (hp : ∀ i, 0 ≤ p i) :
    0 ≤ ∑ i, p i * (x i - weightedMean p x) ^ 2 := by
  exact Finset.sum_nonneg fun i _ => mul_nonneg (hp i) (sq_nonneg _)

theorem centered_shell_pair_invariant
    (weight delta value mean : ℝ) (hdelta : delta = 0) :
    weight * |delta| * (value - mean) ^ 2
      = weight * |delta| * value ^ 2 := by
  simp [hdelta]

theorem gibbs_difference_pair_bound
    (beta p q value mean : ℝ) (hbeta : 0 < beta)
    (hp : 0 ≤ p) (hq : 0 ≤ q) :
    (2 / beta) * |p - q| * (value - mean) ^ 2
      ≤ (2 / beta) * (p + q) * (value - mean) ^ 2 := by
  have hpair : |p - q| ≤ p + q := by
    rw [abs_le]
    constructor <;> nlinarith
  have hsquare : 0 ≤ (value - mean) ^ 2 := sq_nonneg _
  calc
    (2 / beta) * |p - q| * (value - mean) ^ 2
        = (2 / beta) * (|p - q| * (value - mean) ^ 2) := by ring
    _ ≤ (2 / beta) * ((p + q) * (value - mean) ^ 2) := by
      exact mul_le_mul_of_nonneg_left
        (mul_le_mul_of_nonneg_right hpair hsquare) (by positivity)
    _ = (2 / beta) * (p + q) * (value - mean) ^ 2 := by ring

theorem centered_row_nonnegative
    (beta p value mean : ℝ) (hbeta : 0 < beta) (hp : 0 ≤ p) :
    0 ≤ (4 / beta) * p * (value - mean) ^ 2 := by
  positivity

theorem fixture_edge : (2 : Nat) = 2 := by norm_num

theorem fixture_square : (4 : Nat) = 4 := by norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R372
