import Mathlib

namespace Tect.PahOmc015
open Filter
open scoped Topology

/- Exact finite Gibbs algebra and the analytic squeeze used in the certificate.
The PAH incidence-to-energy and counting translations are separately audited.
No common infinite-volume state or physical interpretation is encoded. -/

theorem conditional_weight_cancellation (a zq z : Real) (hq : zq ≠ 0) :
    (zq / z) * (a / zq) = a / z := by
  field_simp

theorem midpoint_exponent (x y : Real) :
    -x - (y-x)/2 = -(x+y)/2 := by ring

theorem gibbs_root_flux (x y m z : Real) :
    (Real.exp (-x) / z) * (m * Real.exp (-(y-x)/2)) =
    (Real.exp (-y) / z) * (m * Real.exp (-(x-y)/2)) := by
  have h : -x + (-(y-x)/2) = -y + (-(x-y)/2) := by ring
  calc
    _ = (m / z) * Real.exp (-x + (-(y-x)/2)) := by rw [Real.exp_add]; ring
    _ = (m / z) * Real.exp (-y + (-(x-y)/2)) := by rw [h]
    _ = _ := by rw [Real.exp_add]; ring

theorem finite_mass_bound {I : Type*} [Fintype I]
    (num : I → Real) (z0 z A : Real)
    (h0 : 0 < z0) (hz : z0 ≤ z) (hA : 0 ≤ A)
    (hn : (∑ i, num i) ≤ A*z0) :
    (∑ i, num i) / z ≤ A := by
  apply (div_le_iff₀ (lt_of_lt_of_le h0 hz)).2
  exact hn.trans (mul_le_mul_of_nonneg_left hz hA)

theorem exponential_reciprocal_bound (c : Real) (hc : 0 ≤ c) :
    Real.exp (-c) ≤ 1/(1+c) := by
  rw [Real.exp_neg, inv_eq_one_div]
  apply one_div_le_one_div_of_le (by linarith)
  simpa [add_comm] using Real.add_one_le_exp c

theorem positive_prefactor_no_finite_zero (A c : Real) (hA : 0 < A) :
    0 < A * Real.exp (-c) := mul_pos hA (Real.exp_pos _)

theorem cutoff_squeeze (b c : Nat → Real) (A : Real)
    (hc : Tendsto c atTop atTop)
    (h0 : ∀ r, 0 ≤ b r)
    (hbound : ∀ r, b r ≤ A * Real.exp (-c r)) :
    Tendsto b atTop (𝓝 0) := by
  have hexp := Real.tendsto_exp_neg_atTop_nhds_zero.comp hc
  have hup : Tendsto (fun r => A * Real.exp (-c r)) atTop (𝓝 0) := by
    simpa using hexp.const_mul A
  exact squeeze_zero h0 hbound hup

theorem charge_penalty_diverges :
    Tendsto (fun r : Nat => (r:Real)^2/8+(r:Real)^4/4+(r:Real)^6/6)
      atTop atTop := by
  have hbase : Tendsto (fun r : Nat => (r:Real)/8) atTop atTop :=
    Filter.Tendsto.atTop_div_const (by norm_num) (tendsto_natCast_atTop_atTop (R := Real))
  apply tendsto_atTop_mono (fun r => ?_) hbase
  have h4 : 0 ≤ (r:Real)^4 := pow_nonneg (Nat.cast_nonneg r) _
  have h6 : 0 ≤ (r:Real)^6 := pow_nonneg (Nat.cast_nonneg r) _
  have hsq : (r:Real) ≤ (r:Real)^2 := by
    by_cases hr : r = 0
    · subst r; norm_num
    · have hr1 : (1:Real) ≤ r := by exact_mod_cast (Nat.one_le_iff_ne_zero.mpr hr)
      nlinarith
  linarith

theorem binary_character_square (h : Real) (hh : h = 1 ∨ h = -1) : h^2 = 1 := by
  rcases hh with hh | hh <;> rw [hh] <;> norm_num

end Tect.PahOmc015
