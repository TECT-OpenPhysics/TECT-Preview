import Mathlib

namespace Tect.R451

noncomputable def shellTail (n : ℕ) : ℝ :=
  3 * (4 * (n : ℝ) ^ 2 + 8 * (n : ℝ) + 14) * ((1 / 2 : ℝ) ^ (n - 1))

theorem two_orientation_fourth_power {a b C t : ℝ}
    (ha4 : a ^ 4 ≤ C * t ^ 4) (hb4 : b ^ 4 ≤ C * t ^ 4) :
    (a + b) ^ 4 ≤ 16 * C * t ^ 4 := by
  have hsq1 : (a + b) ^ 2 ≤ 2 * (a ^ 2 + b ^ 2) := by
    nlinarith [sq_nonneg (a - b)]
  have hsq1_nonneg : 0 ≤ (a + b) ^ 2 := sq_nonneg (a + b)
  have hright_nonneg : 0 ≤ 2 * (a ^ 2 + b ^ 2) := by positivity
  have hsq1_sq : ((a + b) ^ 2) ^ 2 ≤ (2 * (a ^ 2 + b ^ 2)) ^ 2 := by
    have hprod := mul_nonneg (sub_nonneg.mpr hsq1) (add_nonneg hsq1_nonneg hright_nonneg)
    nlinarith
  have hsq2 : (a ^ 2 + b ^ 2) ^ 2 ≤ 2 * (a ^ 4 + b ^ 4) := by
    nlinarith [sq_nonneg (a ^ 2 - b ^ 2)]
  have hfour : (a + b) ^ 4 ≤ 8 * (a ^ 4 + b ^ 4) := by
    nlinarith [hsq1_sq, hsq2]
  nlinarith [hfour, ha4, hb4]

theorem shell_tail_base : shellTail 1 = 78 := by
  norm_num [shellTail]

theorem shell_tail_ratio {n : ℕ} (hn : 1 ≤ n) :
    shellTail (n + 1) ≤ (23 / 26 : ℝ) * shellTail n := by
  have hnrepr : n = (n - 1) + 1 := by omega
  have hpow : (1 / 2 : ℝ) ^ n = (1 / 2 : ℝ) ^ (n - 1) * (1 / 2 : ℝ) := by
    calc
      (1 / 2 : ℝ) ^ n = (1 / 2 : ℝ) ^ ((n - 1) + 1) := by congr 1
      _ = (1 / 2 : ℝ) ^ (n - 1) * (1 / 2 : ℝ) := by rw [pow_succ]
  have hnsub : n + 1 - 1 = n := by omega
  unfold shellTail
  rw [hnsub, hpow]
  have hn_one : (1 : ℝ) ≤ (n : ℝ) := by exact_mod_cast hn
  have hpoly : 0 ≤ ((n : ℝ) - 1) * (5 * (n : ℝ) + 2) := by
    exact mul_nonneg (sub_nonneg.mpr hn_one) (by nlinarith)
  have hu : 0 ≤ (1 / 2 : ℝ) ^ (n - 1) := by positivity
  have hprod : 0 ≤ (1 / 2 : ℝ) ^ (n - 1) * (((n : ℝ) - 1) * (5 * (n : ℝ) + 2)) :=
    mul_nonneg hu hpoly
  norm_num [Nat.cast_add, Nat.cast_one] at ⊢
  nlinarith [hprod]

theorem shell_tail_geometric_bound {n : ℕ} (hn : 1 ≤ n) :
    shellTail n ≤ 78 * (23 / 26 : ℝ) ^ (n - 1) := by
  induction n, hn using Nat.le_induction with
  | base =>
      norm_num [shellTail]
  | succ n hn ih =>
      have hstep := shell_tail_ratio (n := n) (by omega)
      have hq : 0 ≤ (23 / 26 : ℝ) := by norm_num
      have htail_nonneg : 0 ≤ shellTail n := by
        unfold shellTail
        positivity
      have hpow : (23 / 26 : ℝ) ^ (n + 1 - 1) =
          (23 / 26 : ℝ) ^ (n - 1) * (23 / 26 : ℝ) := by
        have hnr : n + 1 - 1 = n := by omega
        calc
          (23 / 26 : ℝ) ^ (n + 1 - 1) = (23 / 26 : ℝ) ^ n := by rw [hnr]
          _ = (23 / 26 : ℝ) ^ ((n - 1) + 1) := by congr 1; omega
          _ = (23 / 26 : ℝ) ^ (n - 1) * (23 / 26 : ℝ) := by rw [pow_succ]
      rw [hpow]
      have hmul := mul_le_mul_of_nonneg_right ih hq
      nlinarith

end Tect.R451
