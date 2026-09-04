import Mathlib

namespace Tect.R499

/-
  Conditional full-Q consequence bridge for PAH-OMC-014.

  The finite mixture below is abstract: a future source-owned law supplies the
  weights and component expectations.  No weight formula, state space or
  projective kernel is chosen here.
-/

def mix {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ) : ℝ :=
  ∑ i, w i * phi i f

theorem mix_strictly_positive_of_witness
    {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ) (i0 : ι)
    (hw : ∀ i, 0 ≤ w i)
    (hphi : ∀ i, 0 ≤ phi i f)
    (hw0 : 0 < w i0)
    (hphi0 : 0 < phi i0 f) :
    0 < mix w phi f := by
  unfold mix
  have hnonneg : ∀ i, 0 ≤ w i * phi i f := by
    intro i
    exact mul_nonneg (hw i) (hphi i)
  have hpos : 0 < w i0 * phi i0 f := mul_pos hw0 hphi0
  exact Finset.sum_pos' (fun i _ => hnonneg i) ⟨i0, Finset.mem_univ _, hpos⟩

theorem stationarity_limit_of_abs_error
    {t error : ℕ → ℝ}
    (hbound : ∀ n, |t n| ≤ error n)
    (herror : Filter.Tendsto error Filter.atTop (nhds 0)) :
    Filter.Tendsto t Filter.atTop (nhds 0) := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  refine squeeze_zero'
    (f := fun n => ‖t n‖) (g := error)
    (Filter.Eventually.of_forall (fun n => norm_nonneg (t n))) ?_ ?_
  · filter_upwards [] with n
    simpa [Real.norm_eq_abs] using hbound n
  · exact herror

theorem stationarity_limit_of_eventual_zero
    {t : ℕ → ℝ} (hzero : ∀ᶠ n in Filter.atTop, t n = 0) :
    Filter.Tendsto t Filter.atTop (nhds 0) := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  refine squeeze_zero'
    (f := fun n => ‖t n‖) (g := fun _ : ℕ => (0 : ℝ))
    (Filter.Eventually.of_forall (fun n => norm_nonneg (t n))) ?_ ?_
  · filter_upwards [hzero] with n hn
    simp [hn]
  · exact tendsto_const_nhds

end Tect.R499
