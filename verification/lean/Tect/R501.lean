import Mathlib

namespace Tect.R501

/- A conditional identifiability lemma for PAH-OMC-014.  The two delta
   weights below are counterfactual admissible probability laws used only to
   show underdetermination; no PAH sector law is supplied by this file. -/

def mix {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ) : ℝ :=
  ∑ i, w i * phi i f

def deltaWeight {ι : Type*} [DecidableEq ι] (q : ι) (i : ι) : ℝ :=
  if i = q then 1 else 0

theorem mix_deltaWeight {ι X : Type*} [Fintype ι] [DecidableEq ι]
    (q : ι) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ) :
    mix (deltaWeight q) phi f = phi q f := by
  classical
  unfold mix deltaWeight
  simp [Finset.sum_ite_eq']

theorem delta_mixtures_separate {ι X : Type*} [Fintype ι] [DecidableEq ι]
    (q0 q1 : ι) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ)
    (h0 : phi q0 f = 0) (h1 : 0 < phi q1 f) :
    mix (deltaWeight q0) phi f ≠ mix (deltaWeight q1) phi f := by
  rw [mix_deltaWeight, mix_deltaWeight, h0]
  exact (ne_of_gt h1).symm

theorem positive_witness_implies_nonidentifiable
    {ι X : Type*} [Fintype ι] [DecidableEq ι]
    (q0 q1 : ι) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ)
    (h0 : phi q0 f = 0) (hpositive : 0 < phi q1 f) :
    ∃ w0 w1 : ι → ℝ,
      (∀ i, 0 ≤ w0 i) ∧ (∑ i, w0 i = 1) ∧
      (∀ i, 0 ≤ w1 i) ∧ (∑ i, w1 i = 1) ∧
      mix w0 phi f ≠ mix w1 phi f := by
  refine ⟨deltaWeight q0, deltaWeight q1, ?_, ?_, ?_, ?_, ?_⟩
  · intro i
    by_cases hi : i = q0 <;> simp [deltaWeight, hi]
  · classical
    simp [deltaWeight]
  · intro i
    by_cases hi : i = q1 <;> simp [deltaWeight, hi]
  · classical
    simp [deltaWeight]
  · exact delta_mixtures_separate q0 q1 phi f h0 hpositive

end Tect.R501
