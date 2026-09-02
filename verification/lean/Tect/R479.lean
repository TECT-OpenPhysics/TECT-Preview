import Mathlib

namespace Tect.R479

theorem inverse_closed_partial_move
    {X : Type} (forward backward : X → X)
    (hForwardBackward : ∀ x, backward (forward x) = x)
    (x : X) :
    backward (forward x) = x := by
  exact hForwardBackward x

theorem equivariant_generator_summand
    {X Root Sym : Type}
    (act : Sym → X → X)
    (rootAct : Sym → Root → Root)
    (move : Root → X → X)
    (rate : Root → X → ℝ)
    (observable : X → ℝ)
    (hMove : ∀ a r x, move (rootAct a r) (act a x) = act a (move r x))
    (hRate : ∀ a r x, rate (rootAct a r) (act a x) = rate r x)
    (a : Sym) (r : Root) (x : X) :
    rate (rootAct a r) (act a x) *
        (observable (move (rootAct a r) (act a x)) - observable (act a x)) =
      rate r x *
        ((fun y => observable (act a y)) (move r x) -
          (fun y => observable (act a y)) x) := by
  rw [hMove, hRate]

theorem commuting_projection_preserves_core
    {V : Type} (projection generator : V → V)
    (hCommute : ∀ x, projection (generator x) = generator (projection x))
    (x : V) (hx : projection x = x) :
    projection (generator x) = generator x := by
  rw [hCommute, hx]

theorem directed_root_half_factor
    (piX piY rateXY rateYX deltaF deltaG : ℝ)
    (hBalance : piX * rateXY = piY * rateYX) :
    (piX * rateXY * deltaF * deltaG +
        piY * rateYX * (-deltaF) * (-deltaG)) / 2 =
      piX * rateXY * deltaF * deltaG := by
  calc
    (piX * rateXY * deltaF * deltaG +
        piY * rateYX * (-deltaF) * (-deltaG)) / 2 =
        (piX * rateXY * deltaF * deltaG +
          (piY * rateYX) * deltaF * deltaG) / 2 := by ring
    _ = (piX * rateXY * deltaF * deltaG +
          (piX * rateXY) * deltaF * deltaG) / 2 := by rw [← hBalance]
    _ = piX * rateXY * deltaF * deltaG := by ring

theorem free_vertex_fibre_difference
    (kappa s delta z₁ z₂ : ℝ) :
    kappa * (((s + delta - z₁) ^ 2 - (s - z₁) ^ 2) / 2) -
        kappa * (((s + delta - z₂) ^ 2 - (s - z₂) ^ 2) / 2) =
      -kappa * delta * (z₁ - z₂) := by
  ring

theorem free_vertex_fibre_difference_nonzero
    (kappa delta z₁ z₂ : ℝ)
    (hKappa : 0 < kappa)
    (hDelta : 0 < delta)
    (hDistinct : z₁ ≠ z₂) :
    -kappa * delta * (z₁ - z₂) ≠ 0 := by
  have hk : kappa ≠ 0 := ne_of_gt hKappa
  have hd : delta ≠ 0 := ne_of_gt hDelta
  have hz : z₁ - z₂ ≠ 0 := sub_ne_zero.mpr hDistinct
  exact mul_ne_zero (mul_ne_zero (neg_ne_zero.mpr hk) hd) hz

def finiteCommonDynamicsPassed : Bool := true
def nontrivialRefinementPassed : Bool := false

theorem finite_pass_does_not_close_refinement :
    finiteCommonDynamicsPassed && nontrivialRefinementPassed = false := by
  decide

end Tect.R479
