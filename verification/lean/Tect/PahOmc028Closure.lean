import Mathlib

namespace Tect.PahOmc028Closure

open Filter Topology

noncomputable def clip (x : ℝ) : ℝ := max 0 (min 1 x)

theorem paired_energy_shortcut_false :
    ((clip 1 - clip 0) - (clip 2 - clip 1)) ^ 2 >
      (((1 : ℝ) - 0) - (2 - 1)) ^ 2 := by
  norm_num [clip]

theorem paired_form_norm_shortcut_false :
    (((clip 1 - clip 0)^2 + (clip 2 - clip 1)^2) / 2 +
      ((clip 1 - clip 0) - (clip 2 - clip 1))^2) >
    ((((1 : ℝ)-0)^2 + (2-1)^2) / 2 + (((1 : ℝ)-0)-(2-1))^2) := by
  norm_num [clip]

theorem single_root_contraction (eta : ℝ → ℝ)
    (h : ∀ a b, |eta a - eta b| ≤ |a - b|) (a b w : ℝ) (hw : 0 ≤ w) :
    w * (eta a - eta b)^2 ≤ w * (a - b)^2 := by
  have ha := h a b
  have hs : |eta a - eta b|^2 ≤ |a-b|^2 := by
    nlinarith [abs_nonneg (eta a-eta b), abs_nonneg (a-b)]
  have hs' : (eta a - eta b)^2 ≤ (a-b)^2 := by simpa [sq_abs] using hs
  exact mul_le_mul_of_nonneg_left hs' hw

-- Universal closed-epigraph passage. Closedness is an explicit hypothesis:
-- the analytic certificate proves it from the R-512 form Hilbert completion.
theorem closed_epigraph_transfer {H : Type*} [TopologicalSpace H]
    (V : Set H) (q : H → ℝ) (eta : H → H) (u : ℕ → H) (f : H)
    (hclosed : IsClosed {p : H × ℝ | p.1 ∈ V ∧ q p.1 ≤ p.2})
    (heta : Continuous eta) (hu : Tendsto u atTop (𝓝 f))
    (hq : Tendsto (fun n => q (u n)) atTop (𝓝 (q f)))
    (hd : ∀ n, eta (u n) ∈ V)
    (he : ∀ n, q (eta (u n)) ≤ q (u n)) :
    eta f ∈ V ∧ q (eta f) ≤ q f := by
  have ht : Tendsto (fun n => (eta (u n), q (u n))) atTop
      (𝓝 (eta f, q f)) := (heta.tendsto f |>.comp hu).prodMk_nhds hq
  exact hclosed.mem_of_tendsto ht (Eventually.of_forall fun n => ⟨hd n, he n⟩)

-- Algebraic consequence used by the variational proof of the resolvent.
theorem zero_energy_cross_term (a b : ℝ) (h : ∀ t : ℝ, 0 ≤ 2*t*a+t^2*b) :
    a = 0 := by
  by_contra ha
  have habs : 0 < |b| + 1 := by positivity
  have hh := h (-a / (|b|+1))
  have hs : 0 < a^2 := sq_pos_of_ne_zero ha
  have hb : b ≤ |b| := le_abs_self b
  field_simp at hh
  nlinarith [sq_nonneg b, abs_nonneg b]

end Tect.PahOmc028Closure
