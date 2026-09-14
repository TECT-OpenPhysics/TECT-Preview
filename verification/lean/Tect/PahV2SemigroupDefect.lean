import Mathlib

namespace Tect.PahV2SemigroupDefect

-- These theorems check the actual analytic exponential/slack/weight bridges.
-- Finite PAH Markov contraction, the Duhamel identity and prime-tail existence
-- are proved in the written synthesis, not encoded in this entrypoint.

theorem exponential_gap_lower (a : Real) (ha : 2/5 ≤ a) :
    4/15 ≤ 2 * Real.exp (-1) * Real.sinh a := by
  have he : (1 : Real)/3 ≤ Real.exp (-1) := by
    rw [Real.exp_neg, ← one_div]
    apply (le_div_iff₀ (Real.exp_pos (1 : Real))).2
    nlinarith [Real.exp_one_lt_three]
  have hs : (2 : Real)/5 ≤ Real.sinh a :=
    ha.trans (Real.self_le_sinh_iff.mpr (by linarith))
  have hm := mul_le_mul he hs (by norm_num : (0 : Real) ≤ 2/5)
    (le_trans (by norm_num : (0 : Real) ≤ 1/3) he)
  nlinarith

theorem fixed_time_error (K J : Real) (hK : 768 ≤ K) (hJ : K ≤ J) :
    (256/K + 256/J)/10 ≤ 1/15 := by
  have hp : 0 < K := by linarith
  have hq : 0 < J := by linarith
  have h1 : (256 : Real)/J ≤ 256/K :=
    (div_le_div_iff₀ hq hp).2 (by nlinarith)
  have h2 : (256 : Real)/K ≤ 1/3 :=
    (div_le_iff₀ hp).2 (by linarith)
  linarith

theorem two_error_lower (z u v : Complex) (hz : (4 : Real)/15 ≤ ‖z‖)
    (he : ‖u‖ + ‖v‖ ≤ (1 : Real)/15) :
    (1 : Real)/5 ≤ ‖z+u-v‖ := by
  have h : ‖z‖ ≤ ‖z+u-v‖ + ‖v‖ + ‖u‖ := by
    calc
      ‖z‖ = ‖((z+u-v)+v)-u‖ := by congr 1; ring
      _ ≤ ‖(z+u-v)+v‖ + ‖u‖ := norm_sub_le _ _
      _ ≤ (‖z+u-v‖ + ‖v‖) + ‖u‖ := by gcongr; exact norm_add_le _ _
  linarith

theorem original_gibbs_square_lower {ι : Type*} (s : Finset ι) (w d : ι → Real)
    (hw : ∀ i ∈ s, 0 ≤ w i) (hd : ∀ i ∈ s, (1 : Real)/5 ≤ d i)
    (hn : ∑ i ∈ s, w i = 1) : (1 : Real)/25 ≤ ∑ i ∈ s, w i * (d i)^2 := by
  have h : ∑ i ∈ s, w i * ((1 : Real)/25) ≤ ∑ i ∈ s, w i * (d i)^2 := by
    apply Finset.sum_le_sum
    intro i hi
    exact mul_le_mul_of_nonneg_left (by nlinarith [hd i hi]) (hw i hi)
  simpa [← Finset.sum_mul, hn] using h

theorem arbitrary_tail_refutes_zero (d : Nat → Real)
    (h : ∀ R, ∃ r, R ≤ r ∧ (1 : Real)/5 ≤ d r) :
    ¬ (∀ e : Real, 0 < e → ∃ R, ∀ r, R ≤ r → d r < e) := by
  intro hz
  obtain ⟨R,hR⟩ := hz ((1 : Real)/5) (by norm_num)
  obtain ⟨r,hr,hd⟩ := h R
  linarith [hR r hr]

end Tect.PahV2SemigroupDefect
