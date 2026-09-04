import Mathlib

namespace Tect.R498

/-
  Conditional boundary-error bridge for PAH-OMC-014.

  The sequence s is one already-defined cylinder expectation.  bulk and
  boundary are additive error budgets supplied by a future source-owned
  estimate.  No sector weights, state, topology, or physical interpretation
  is defined here; the theorem only preserves the R-484 boundary term instead
  of cancelling or averaging it away.
-/

theorem tendsto_add_error {bulk boundary : ℕ → ℝ}
    (hbulk : Filter.Tendsto bulk Filter.atTop (nhds 0))
    (hboundary : Filter.Tendsto boundary Filter.atTop (nhds 0)) :
    Filter.Tendsto (fun n => bulk n + boundary n) Filter.atTop (nhds 0) := by
  simpa using hbulk.add hboundary

theorem tendsto_zero_of_eventually_zero {boundary : ℕ → ℝ}
    {N : ℕ} (hzero : ∀ n, N ≤ n → boundary n = 0) :
    Filter.Tendsto boundary Filter.atTop (nhds 0) := by
  have hconst : Filter.Tendsto (fun _ : ℕ => (0 : ℝ))
      Filter.atTop (nhds 0) := tendsto_const_nhds
  apply hconst.congr'
  filter_upwards [Filter.eventually_atTop.2 ⟨N, fun n hn => hn⟩] with n hn
  exact (hzero n hn).symm

theorem add_error_nonnegative {bulk boundary : ℕ → ℝ}
    (hbulk : ∀ n, 0 ≤ bulk n)
    (hboundary : ∀ n, 0 ≤ boundary n) :
    ∀ n, 0 ≤ bulk n + boundary n := by
  intro n
  exact add_nonneg (hbulk n) (hboundary n)

theorem cauchy_of_bulk_boundary {s bulk boundary : ℕ → ℝ}
    (hbound : ∀ n m, n ≤ m → |s n - s m| ≤ bulk n + boundary n)
    (hbulk : Filter.Tendsto bulk Filter.atTop (nhds 0))
    (hboundary : Filter.Tendsto boundary Filter.atTop (nhds 0)) :
    CauchySeq s := by
  refine cauchySeq_of_le_tendsto_0' (fun n => bulk n + boundary n) ?_
    (tendsto_add_error hbulk hboundary)
  intro n m hnm
  rw [Real.dist_eq]
  exact hbound n m hnm

theorem limit_exists_of_bulk_boundary {s bulk boundary : ℕ → ℝ}
    (hbound : ∀ n m, n ≤ m → |s n - s m| ≤ bulk n + boundary n)
    (hbulk : Filter.Tendsto bulk Filter.atTop (nhds 0))
    (hboundary : Filter.Tendsto boundary Filter.atTop (nhds 0)) :
    ∃ omega : ℝ, Filter.Tendsto s Filter.atTop (nhds omega) := by
  exact cauchySeq_tendsto_of_complete
    (cauchy_of_bulk_boundary hbound hbulk hboundary)

theorem cauchy_of_eventual_boundary_zero {s bulk boundary : ℕ → ℝ}
    (hbound : ∀ n m, n ≤ m → |s n - s m| ≤ bulk n + boundary n)
    (hbulk : Filter.Tendsto bulk Filter.atTop (nhds 0))
    {N : ℕ} (hzero : ∀ n, N ≤ n → boundary n = 0) :
    CauchySeq s := by
  exact cauchy_of_bulk_boundary hbound hbulk
    (tendsto_zero_of_eventually_zero hzero)

theorem no_tendsto_zero_of_eventual_floor {boundary : ℕ → ℝ} {c : ℝ}
    (hc : 0 < c)
    (hfloor : ∀ᶠ n in Filter.atTop, c ≤ boundary n) :
    ¬ Filter.Tendsto boundary Filter.atTop (nhds 0) := by
  intro hlim
  have hlt : ∀ᶠ n in Filter.atTop, boundary n < c := by
    have hnbhd : Set.Iio c ∈ nhds (0 : ℝ) := Iio_mem_nhds hc
    exact hlim hnbhd
  rcases (Filter.eventually_atTop.1 hfloor) with ⟨n_floor, hfloor'⟩
  rcases (Filter.eventually_atTop.1 hlt) with ⟨n_lt, hlt'⟩
  let n := max n_floor n_lt
  have hfloor_n : c ≤ boundary n := hfloor' n (le_max_left _ _)
  have hlt_n : boundary n < c := hlt' n (le_max_right _ _)
  exact (not_lt_of_ge hfloor_n) hlt_n

end Tect.R498
