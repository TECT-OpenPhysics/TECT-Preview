import Mathlib

namespace Tect.R384

/- R384 formalizes the scalar inequalities behind the finite two-scale
   filter-removal corridor.  The executable matrix audits remain finite;
   these lemmas do not assert a uniform tail, filter removal, or QFT closure. -/

theorem removal_weight_nonnegative (u : ℝ) (hu : 0 ≤ u) :
    0 ≤ (u / (1 + u)) ^ 2 := by
  positivity

theorem low_frequency_factor_bound (u E : ℝ) (hu : 0 ≤ u) (hE : 0 < E)
    (hlo : u ≤ E) :
    u / (1 + u) ≤ E := by
  have hden : 0 < 1 + u := by linarith
  apply (div_le_iff₀ hden).2
  nlinarith

theorem high_frequency_tail_factor (u E : ℝ) (hu : 0 ≤ u) (hE : 0 < E)
    (hhi : E ≤ u) :
    1 ≤ u ^ 2 / E ^ 2 := by
  have hE2 : 0 < E ^ 2 := by positivity
  apply (le_div_iff₀ hE2).2
  nlinarith [sq_nonneg (u - E)]

theorem low_m0_envelope_factor (u E : ℝ) (hu : 0 ≤ u) (hE : 0 < E)
    (hlo : u ≤ E) :
    (u / (1 + u)) ^ 2 ≤ E ^ 2 := by
  have hfactor := low_frequency_factor_bound u E hu hE hlo
  have hnonneg : 0 ≤ u / (1 + u) := by positivity
  nlinarith [sq_nonneg (u / (1 + u) - E)]

theorem endpoint_low_frequency_factor (u : ℝ) (hu : 0 ≤ u) :
    u * (1 - 1 / (1 + u) ^ 2) ≤ 2 * u ^ 2 := by
  have hden : 0 < (1 + u) ^ 2 := by positivity
  have hbound : 1 - 1 / (1 + u) ^ 2 ≤ 2 * u := by
    field_simp
    nlinarith [sq_nonneg u]
  have hprod : u * (1 - 1 / (1 + u) ^ 2) ≤ u * (2 * u) := by
    exact (mul_le_mul_of_nonneg_left hbound hu)
  nlinarith

theorem endpoint_high_frequency_factor (u E : ℝ) (hu : 0 ≤ u) (hE : 0 < E)
    (hhi : E ≤ u) :
    u * (1 - 1 / (1 + u) ^ 2) ≤ u ^ 2 / E := by
  have hEpos : 0 < E := hE
  have hratio : u ≤ u ^ 2 / E := by
    apply (le_div_iff₀ hE).2
    nlinarith
  have hinv_le_one : 1 / (1 + u) ^ 2 ≤ 1 := by
    have hden : 0 < (1 + u) ^ 2 := by positivity
    apply (div_le_iff₀ hden).2
    nlinarith [sq_nonneg u]
  have hfilter : 0 ≤ 1 - 1 / (1 + u) ^ 2 := sub_nonneg.mpr hinv_le_one
  have hprod : u * (1 - 1 / (1 + u) ^ 2) ≤ u := by
    have hcomp : 0 ≤ 1 - (1 - 1 / (1 + u) ^ 2) := by
      convert (show 0 ≤ 1 / (1 + u) ^ 2 by positivity) using 1 <;> ring
    nlinarith [mul_nonneg hu hcomp]
  exact le_trans hprod hratio

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R384
