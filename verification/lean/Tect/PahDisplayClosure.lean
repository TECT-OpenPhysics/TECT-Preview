import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Tect.PahDisplayClosure

-- Partial algebraic bridges. Source energies, root enumeration, conditional
-- expectation and the finite semigroup argument remain analytic obligations.
theorem no_fibre_factorization {X Y : Type*} (d : X -> Y)
    (v : X -> Real) (x y : X) (hxy : d x = d y) (hneq : v x ≠ v y) :
    ¬ ∃ k : Y -> Real, v = k ∘ d := by
  rintro ⟨k, hk⟩
  apply hneq
  rw [hk]
  simp only [Function.comp_apply, hxy]

theorem positive_rate_gap (a : Real) (ha : 0 < a) :
    0 < 2 * Real.exp a - 2 * Real.exp (-a) := by
  have h : Real.exp (-a) < Real.exp a := Real.exp_lt_exp.mpr (by linarith)
  linarith

theorem two_value_variance (a b : Real) :
    ((2*a-(a+b))^2+(2*b-(a+b))^2)/2 = (a-b)^2 := by
  ring

theorem positive_fibre_contribution (mass a b : Real)
    (hm : 0 < mass) (hab : a ≠ b) : 0 < mass*(a-b)^2 := by
  exact mul_pos hm (sq_pos_of_ne_zero (sub_ne_zero.mpr hab))

end Tect.PahDisplayClosure
