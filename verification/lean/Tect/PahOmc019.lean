import Mathlib

namespace Tect.PahOmc019

open Filter Topology

/- Abstract Hilbert-space consequences only. The analytic certificate supplies
the R-510 state, R-511 dense domain and exact generator/form identification.
No model-specific measure construction is formalized here. -/

variable {H K D : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H]
variable [NormedAddCommGroup K] [InnerProductSpace ℝ K]

theorem no_ghost (i : D → H) (j : D → K) (s : D → H)
    (hd : DenseRange j)
    (hp : ∀ x y, inner ℝ (j x) (j y) = inner ℝ (i x) (s y))
    (u : ℕ → D) (v : K)
    (hu : Tendsto (fun n => i (u n)) atTop (𝓝 0))
    (hv : Tendsto (fun n => j (u n)) atTop (𝓝 v)) : v = 0 := by
  apply hd.eq_zero_of_inner_left ℝ
  intro y
  have hleft : Tendsto (fun n => inner ℝ (j (u n)) (j y)) atTop
      (𝓝 (inner ℝ v (j y))) := hv.inner tendsto_const_nhds
  have hright : Tendsto (fun n => inner ℝ (i (u n)) (s y)) atTop
      (𝓝 (inner ℝ (0 : H) (s y))) := hu.inner tendsto_const_nhds
  have heq : (fun n => inner ℝ (j (u n)) (j y)) =
      (fun n => inner ℝ (i (u n)) (s y)) := funext fun n => hp (u n) y
  rw [heq] at hleft
  simpa using tendsto_nhds_unique hleft hright

theorem closability_criterion [CompleteSpace K]
    (i : D → H) (j : D → K) (s : D → H)
    (hd : DenseRange j)
    (hp : ∀ x y, inner ℝ (j x) (j y) = inner ℝ (i x) (s y))
    (u : ℕ → D)
    (hu : Tendsto (fun n => i (u n)) atTop (𝓝 0))
    (hc : CauchySeq (fun n => j (u n))) :
    Tendsto (fun n => j (u n)) atTop (𝓝 0) := by
  obtain ⟨v, hv⟩ := cauchySeq_tendsto_of_complete hc
  have hz := no_ghost i j s hd hp u v hu hv
  simpa [hz] using hv

theorem energy_tends_zero [CompleteSpace K]
    (i : D → H) (j : D → K) (s : D → H)
    (hd : DenseRange j)
    (hp : ∀ x y, inner ℝ (j x) (j y) = inner ℝ (i x) (s y))
    (u : ℕ → D)
    (hu : Tendsto (fun n => i (u n)) atTop (𝓝 0))
    (hc : CauchySeq (fun n => j (u n))) :
    Tendsto (fun n => ‖j (u n)‖ ^ 2) atTop (𝓝 0) := by
  have h := (closability_criterion i j s hd hp u hu hc).norm.pow 2
  simpa using h

theorem quotient_representer_zero (i : D → H) (s : D → H)
    (hd : DenseRange i)
    (hsym : ∀ x y, inner ℝ (i x) (s y) = inner ℝ (i y) (s x))
    (x : D) (hx : i x = 0) : s x = 0 := by
  apply hd.eq_zero_of_inner_right ℝ
  intro y
  rw [hsym y x, hx]
  simp

theorem completion_kernel_zero (i : K →L[ℝ] H) (j : D → K) (s : D → H)
    (hd : DenseRange j)
    (hp : ∀ v x, inner ℝ v (j x) = inner ℝ (i v) (s x))
    (v : K) (hv : i v = 0) : v = 0 := by
  apply hd.eq_zero_of_inner_left ℝ
  intro x
  rw [hp, hv]
  simp

theorem completion_injective (i : K →L[ℝ] H) (j : D → K) (s : D → H)
    (hd : DenseRange j)
    (hp : ∀ v x, inner ℝ v (j x) = inner ℝ (i v) (s x)) :
    Function.Injective i := by
  intro u v h
  apply sub_eq_zero.mp
  apply completion_kernel_zero i j s hd hp
  simp [h]

omit [InnerProductSpace ℝ H] [InnerProductSpace ℝ K] in
theorem radial_graph_limit (W : Set (H × K)) (hw : IsClosed W)
    (u : ℕ → H) (h : H)
    (hu : Tendsto u atTop (𝓝 h)) (hin : ∀ n, (u n, (0 : K)) ∈ W) :
    (h, (0 : K)) ∈ W := by
  exact hw.mem_of_tendsto (hu.prodMk_nhds tendsto_const_nhds) (Eventually.of_forall hin)

theorem zero_energy_cross (e a b : ℝ) (h : e ^ 2 ≤ a * b) (ha : a = 0) :
    e = 0 := by
  rw [ha] at h
  nlinarith [sq_nonneg e]

theorem radial_form_norm (norm2 energy : ℝ) (h : energy = 0) :
    norm2 + energy = norm2 := by simp [h]

end Tect.PahOmc019
