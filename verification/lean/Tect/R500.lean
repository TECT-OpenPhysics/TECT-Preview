import Mathlib

namespace Tect.R500

/-!
  Conditional projective-mixture bridge for PAH-OMC-014.

  The theorem is deliberately abstract: a future source-owned cross-Q kernel
  and weight recursion are hypotheses.  No PAH sector weights, state, or
  projective map are instantiated here.
-/

def weightedSum {ι : Type*} [Fintype ι]
    (w : ι → ℝ) (v : ι → ℝ) : ℝ :=
  ∑ i, w i * v i

theorem coarse_weight_nonnegative
    {ιf ιc : Type*} [Fintype ιf]
    (wf : ιf → ℝ) (K : ιf → ιc → ℝ) (wc : ιc → ℝ)
    (hrec : ∀ qc, wc qc = ∑ qf, wf qf * K qf qc)
    (hw : ∀ qf, 0 ≤ wf qf)
    (hK : ∀ qf qc, 0 ≤ K qf qc) :
    ∀ qc, 0 ≤ wc qc := by
  intro qc
  rw [hrec qc]
  exact Finset.sum_nonneg (fun qf _ => mul_nonneg (hw qf) (hK qf qc))

theorem coarse_weight_normalized
    {ιf ιc : Type*} [Fintype ιf] [Fintype ιc]
    (wf : ιf → ℝ) (K : ιf → ιc → ℝ) (wc : ιc → ℝ)
    (hrec : ∀ qc, wc qc = ∑ qf, wf qf * K qf qc)
    (hw_sum : ∑ qf, wf qf = 1)
    (hK_row : ∀ qf, ∑ qc, K qf qc = 1) :
    ∑ qc, wc qc = 1 := by
  calc
    ∑ qc, wc qc = ∑ qc, ∑ qf, wf qf * K qf qc := by
      apply Finset.sum_congr rfl
      intro qc hqc
      rw [hrec qc]
    _ = ∑ qf, ∑ qc, wf qf * K qf qc := by
      rw [Finset.sum_comm]
    _ = ∑ qf, wf qf * (∑ qc, K qf qc) := by
      apply Finset.sum_congr rfl
      intro qf hqf
      rw [Finset.mul_sum]
    _ = ∑ qf, wf qf * 1 := by
      apply Finset.sum_congr rfl
      intro qf hqf
      rw [hK_row qf]
    _ = 1 := by simpa using hw_sum

theorem projective_mixture_identity
    {ιf ιc : Type*} [Fintype ιf] [Fintype ιc]
    (wf : ιf → ℝ) (K : ιf → ιc → ℝ)
    (wc : ιc → ℝ) (fine : ιf → ℝ) (coarse : ιc → ℝ)
    (hrec : ∀ qc, wc qc = ∑ qf, wf qf * K qf qc)
    (hpush : ∀ qf, fine qf = ∑ qc, K qf qc * coarse qc) :
    weightedSum wf fine = weightedSum wc coarse := by
  unfold weightedSum
  calc
    ∑ qf, wf qf * fine qf =
        ∑ qf, wf qf * (∑ qc, K qf qc * coarse qc) := by
          apply Finset.sum_congr rfl
          intro qf hqf
          rw [hpush qf]
    _ = ∑ qf, ∑ qc, (wf qf * K qf qc) * coarse qc := by
          apply Finset.sum_congr rfl
          intro qf hqf
          rw [Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro qc hqc
          ring
    _ = ∑ qc, ∑ qf, (wf qf * K qf qc) * coarse qc := by
          rw [Finset.sum_comm]
    _ = ∑ qc, (∑ qf, wf qf * K qf qc) * coarse qc := by
          apply Finset.sum_congr rfl
          intro qc hqc
          rw [Finset.sum_mul]
    _ = ∑ qc, wc qc * coarse qc := by
          apply Finset.sum_congr rfl
          intro qc hqc
          rw [hrec qc]
    _ = weightedSum wc coarse := by rfl

theorem projective_mixture_preserves_probability
    {ιf ιc : Type*} [Fintype ιf] [Fintype ιc]
    (wf : ιf → ℝ) (K : ιf → ιc → ℝ) (wc : ιc → ℝ)
    (hrec : ∀ qc, wc qc = ∑ qf, wf qf * K qf qc)
    (hw : ∀ qf, 0 ≤ wf qf)
    (hw_sum : ∑ qf, wf qf = 1)
    (hK : ∀ qf qc, 0 ≤ K qf qc)
    (hK_row : ∀ qf, ∑ qc, K qf qc = 1) :
    (∀ qc, 0 ≤ wc qc) ∧ ∑ qc, wc qc = 1 := by
  constructor
  · exact coarse_weight_nonnegative wf K wc hrec hw hK
  · exact coarse_weight_normalized wf K wc hrec hw_sum hK_row

end Tect.R500
