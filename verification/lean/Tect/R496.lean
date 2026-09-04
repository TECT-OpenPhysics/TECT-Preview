import Mathlib

namespace Tect.R496

/- Conditional cylinder-limit criteria only.  The sequence represents one
   already-fixed cylinder observable after the source owner has supplied the
   finite-sector mixture.  No sector weights, topology, or PAH state are
   defined here. -/

theorem cauchy_of_abs_error {s b : ℕ → ℝ}
    (hbound : ∀ n m, n ≤ m → |s n - s m| ≤ b n)
    (hlim : Filter.Tendsto b Filter.atTop (nhds 0)) :
    CauchySeq s := by
  refine cauchySeq_of_le_tendsto_0' b ?_ hlim
  intro n m hnm
  rw [Real.dist_eq]
  exact hbound n m hnm

theorem limit_exists_of_abs_error {s b : ℕ → ℝ}
    (hbound : ∀ n m, n ≤ m → |s n - s m| ≤ b n)
    (hlim : Filter.Tendsto b Filter.atTop (nhds 0)) :
    ∃ omega : ℝ, Filter.Tendsto s Filter.atTop (nhds omega) := by
  exact cauchySeq_tendsto_of_complete (cauchy_of_abs_error hbound hlim)

theorem limit_unique {s : ℕ → ℝ}
    {omega₁ omega₂ : ℝ}
    (h₁ : Filter.Tendsto s Filter.atTop (nhds omega₁))
    (h₂ : Filter.Tendsto s Filter.atTop (nhds omega₂)) :
    omega₁ = omega₂ := by
  exact tendsto_nhds_unique h₁ h₂

theorem limit_nonnegative {s : ℕ → ℝ} {omega : ℝ}
    (hlim : Filter.Tendsto s Filter.atTop (nhds omega))
    (hpos : ∀ n, 0 ≤ s n) :
    0 ≤ omega := by
  exact isClosed_Ici.mem_of_tendsto hlim (Filter.Eventually.of_forall hpos)

theorem limit_one {s : ℕ → ℝ} {omega : ℝ}
    (hlim : Filter.Tendsto s Filter.atTop (nhds omega))
    (hone : ∀ n, s n = 1) :
    omega = 1 := by
  have hs : s = (fun _ : ℕ => (1 : ℝ)) := by
    funext n
    exact hone n
  have hconst : Filter.Tendsto s Filter.atTop (nhds (1 : ℝ)) := by
    rw [hs]
    exact tendsto_const_nhds
  exact tendsto_nhds_unique hlim hconst

theorem limit_zero {s : ℕ → ℝ} {omega : ℝ}
    (hlim : Filter.Tendsto s Filter.atTop (nhds omega))
    (hzero : ∀ n, s n = 0) :
    omega = 0 := by
  have hs : s = (fun _ : ℕ => (0 : ℝ)) := by
    funext n
    exact hzero n
  have hconst : Filter.Tendsto s Filter.atTop (nhds (0 : ℝ)) := by
    rw [hs]
    exact tendsto_const_nhds
  exact tendsto_nhds_unique hlim hconst

end Tect.R496
