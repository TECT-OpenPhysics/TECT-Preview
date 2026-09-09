import Mathlib

namespace Tect.PahOmc029Uniqueness

open Filter Topology

-- Closedness is explicit. The model crosswalk and radial density are analytic.
theorem closed_graph_radial_kernel {H : Type*} [TopologicalSpace H] [Zero H]
    (D : Set H) (G : H → H) (u : ℕ → H) (f : H)
    (hclosed : IsClosed {p : H × H | p.1 ∈ D ∧ p.2 = G p.1})
    (hu : Tendsto u atTop (𝓝 f))
    (hd : ∀ n, u n ∈ D) (hz : ∀ n, G (u n) = 0) : f ∈ D ∧ G f = 0 := by
  have ht : Tendsto (fun n => (u n, (0 : H))) atTop (𝓝 (f, 0)) :=
    hu.prodMk_nhds tendsto_const_nhds
  have hm := hclosed.mem_of_tendsto ht
    (Eventually.of_forall fun n => ⟨hd n, (hz n).symm⟩)
  exact ⟨hm.1, hm.2.symm⟩

-- A common comparison, not equality of generators on a merely dense set.
theorem common_comparison_forces_equality {H : Type*} [MetricSpace H]
    (x y : H)
    (h : ∀ e : ℝ, 0 < e → ∃ z : H, dist x z ≤ e ∧ dist y z ≤ e) : x = y := by
  by_contra hxy
  have hd : 0 < dist x y := dist_pos.mpr hxy
  obtain ⟨z, hx, hy⟩ := h (dist x y / 4) (by positivity)
  have ht := dist_triangle x z y
  rw [dist_comm z y] at ht
  linarith

-- Localization removal requires a vanishing norm error, not just high probability.
theorem two_error_uniqueness (d : ℝ) (hd : 0 ≤ d)
    (h : ∀ e : ℝ, 0 < e → d ≤ 2 * e) : d = 0 := by
  by_contra hn
  have hp : 0 < d := lt_of_le_of_ne hd (Ne.symm hn)
  have hh := h (d/4) (by positivity)
  linarith

theorem quadratic_rate_envelope_coefficients :
    (((1 : ℚ)+5) * (1-1/2)^2/2 + 2*5*(2/(1/2)) = 163/4) ∧
    ((1-(1/2 : ℚ)^2)/2 + 5*(2/(1/2)) = 163/8) := by
  norm_num

theorem sublinear_log_coefficient_negative (r delta : ℝ)
    (hr : 0 < r) (hd : delta < 1) : -(1-delta)/r < 0 := by
  exact div_neg_of_neg_of_pos (by linarith) hr

-- This closes only the displayed Young-type scalar estimate after y>=0.
theorem cubic_optimization_bound (b delta y z : ℝ)
    (hd : 0 < delta) (hy : 0 ≤ y) (hz : 0 ≤ z)
    (hcrit : b = 3*delta*z^2) :
    b*y-delta*y^3 ≤ 2*delta*z^3 := by
  have h := mul_nonneg (sq_nonneg (y-z)) (show 0 ≤ y+2*z by linarith)
  have hh := mul_nonneg (le_of_lt hd) h
  rw [hcrit]
  nlinarith

end Tect.PahOmc029Uniqueness
