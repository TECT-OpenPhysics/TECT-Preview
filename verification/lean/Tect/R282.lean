import Mathlib

namespace Tect.R282

/- Scalar core of the energy-to-number corollary.  The Q3 Shubin graph
   equivalence and the normal-order expansion are cited premises in the
   surrounding manifest; this file checks only their algebraic composition. -/

theorem young_with_equal_scales {s x y : ℝ}
    (hs : 0 ≤ s) (_hx : 0 ≤ x) (hy : 0 ≤ y) (hxy : x ≤ y) :
    s * x * y ≤ s * y ^ 2 := by
  have hxy_mul : x * y ≤ y * y := by
    have hnonneg : 0 ≤ y * (y - x) := mul_nonneg hy (sub_nonneg.mpr hxy)
    nlinarith
  have hscale : 0 ≤ s * (y * y - x * y) := mul_nonneg hs (sub_nonneg.mpr hxy_mul)
  nlinarith

theorem energy_to_number_form_constant {s g x y : ℝ}
    (hs : 0 ≤ s) (hg : 0 ≤ g) (hx : 0 ≤ x) (hy : 0 ≤ y) (hxy : x ≤ y) :
    s * g * x * y ≤ s * g * y ^ 2 := by
  have h := young_with_equal_scales (s := s * g) (x := x) (y := y)
    (mul_nonneg hs hg) hx hy hxy
  nlinarith

theorem top_tail_decay {C m : ℝ} (_hC : 0 ≤ C) (_hm : 0 ≤ m) :
    Filter.Tendsto
      (fun n : Nat => C * m * (((n : ℝ) + 1) ^ 2 / (n : ℝ) ^ 5))
      Filter.atTop (nhds 0) := by
  have hinv : Filter.Tendsto (fun n : Nat => (n : ℝ)⁻¹)
      Filter.atTop (nhds 0) :=
    tendsto_inv_atTop_zero.comp tendsto_natCast_atTop_atTop
  have hpow : Filter.Tendsto (fun n : Nat => ((n : ℝ)⁻¹) ^ (3 : Nat))
      Filter.atTop (nhds 0) := by
    simpa using hinv.pow 3
  have hratio_base : Filter.Tendsto
      (fun n : Nat => (1 : ℝ) + (n : ℝ)⁻¹)
      Filter.atTop (nhds 1) := by
    simpa using tendsto_const_nhds.add hinv
  have hratio : Filter.Tendsto
      (fun n : Nat => ((n : ℝ) + 1) / (n : ℝ))
      Filter.atTop (nhds 1) := by
    apply hratio_base.congr'
    filter_upwards [Filter.eventually_atTop.2 ⟨1, by intro n hn; exact hn⟩] with n hn
    have hnpos : (n : ℝ) ≠ 0 := by
      exact_mod_cast (Nat.ne_of_gt (Nat.zero_lt_of_lt hn))
    field_simp [hnpos]
  have hprod : Filter.Tendsto
      (fun n : Nat => (((n : ℝ) + 1) / (n : ℝ)) ^ 2 * ((n : ℝ)⁻¹) ^ 3)
      Filter.atTop (nhds 0) := by
    simpa using (hratio.pow 2).mul hpow
  have hscaled : Filter.Tendsto
      (fun n : Nat => C * m * ((((n : ℝ) + 1) / (n : ℝ)) ^ 2 * ((n : ℝ)⁻¹) ^ 3))
      Filter.atTop (nhds 0) := by
    simpa using (tendsto_const_nhds.mul hprod)
  apply hscaled.congr'
  filter_upwards [Filter.eventually_atTop.2 ⟨1, by intro n hn; exact hn⟩] with n hn
  have hnpos : (n : ℝ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt (Nat.zero_lt_of_lt hn))
  field_simp [hnpos]

theorem history_top_tail_decay {C m T S : ℝ}
    (hC : 0 ≤ C) (hm : 0 ≤ m) (hS : 0 ≤ S) :
    Filter.Tendsto
      (fun n : Nat => C * Real.exp T * S ^ 5 * m *
        (((n : ℝ) + 1) ^ 2 / (n : ℝ) ^ 5))
      Filter.atTop (nhds 0) := by
  apply top_tail_decay (C := C * Real.exp T * S ^ 5) (m := m)
  · positivity
  · exact hm

theorem scope_fixture :
    (0 : ℝ) < 87496 ∧ (0 : ℝ) < 1286 ∧ ((10 : ℝ) / 2 = 5) := by
  norm_num

end Tect.R282
