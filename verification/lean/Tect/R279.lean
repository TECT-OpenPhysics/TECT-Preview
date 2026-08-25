import Mathlib

namespace Tect.R279

/- A fifth-moment Markov bridge for the weighted top-tail condition.
   The hypothesis is deliberately scalar: it does not assert that an onsite
   Q3 energy controls a harmonic-number cutoff, nor does it supply a Q3
   Gibbs/history estimate. -/

theorem fifth_moment_to_weighted_top_tail {p : Nat → ℝ} {C : ℝ}
    (hbound : ∀ n : Nat, 1 ≤ n →
      0 ≤ (n : ℝ) ^ 5 * p n ∧ (n : ℝ) ^ 5 * p n ≤ C) :
    Filter.Tendsto (fun n : Nat => (n : ℝ) ^ 2 * p n)
      Filter.atTop (nhds 0) := by
  have hinv : Filter.Tendsto (fun n : Nat => (n : ℝ)⁻¹)
      Filter.atTop (nhds 0) :=
    tendsto_inv_atTop_zero.comp tendsto_natCast_atTop_atTop
  have hpow : Filter.Tendsto (fun n : Nat => ((n : ℝ)⁻¹) ^ (3 : Nat))
      Filter.atTop (nhds 0) := by
    simpa using hinv.pow 3
  have hupper : Filter.Tendsto (fun n : Nat => C / (n : ℝ) ^ (3 : Nat))
      Filter.atTop (nhds 0) := by
    simpa [div_eq_mul_inv, inv_pow] using (tendsto_const_nhds.mul hpow)
  have hge : ∀ᶠ n : Nat in Filter.atTop, 1 ≤ n :=
    Filter.eventually_atTop.2 ⟨1, by intro b hb; exact hb⟩
  refine squeeze_zero' ?_ ?_ hupper
  · filter_upwards [hge] with n hn
    have hnpos : (0 : ℝ) < (n : ℝ) := by
      exact_mod_cast (Nat.zero_lt_of_lt hn)
    have hn5 : 0 < (n : ℝ) ^ (5 : Nat) := by positivity
    have hp : 0 ≤ p n := by nlinarith [((hbound n hn).1), hn5]
    positivity
  · filter_upwards [hge] with n hn
    have hnpos : (0 : ℝ) < (n : ℝ) := by
      exact_mod_cast (Nat.zero_lt_of_lt hn)
    have hfive := (hbound n hn).2
    calc
      (n : ℝ) ^ 2 * p n = ((n : ℝ) ^ 5 * p n) / (n : ℝ) ^ (3 : Nat) := by
        field_simp [hnpos.ne']
      _ ≤ C / (n : ℝ) ^ (3 : Nat) := by
        exact div_le_div_of_nonneg_right hfive (by positivity)

theorem fifth_moment_fixture :
    (∀ n : Nat, 1 ≤ n → 0 ≤ (n : ℝ) ^ 5 * (1 / (n : ℝ) ^ 5 : ℝ) ∧
      (n : ℝ) ^ 5 * (1 / (n : ℝ) ^ 5 : ℝ) ≤ 1) := by
  intro n hn
  have hnpos : (0 : ℝ) < (n : ℝ) := by exact_mod_cast (Nat.zero_lt_of_lt hn)
  constructor
  · positivity
  · field_simp [hnpos.ne']
    norm_num

end Tect.R279
