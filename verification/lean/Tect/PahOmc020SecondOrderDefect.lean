import Mathlib

namespace Tect.PahOmc020SecondOrderDefect

theorem cubic_factorization (x : ℝ) :
    x + x ^ 2 - 1 - x ^ 3 = -((x - 1) ^ 2 * (x + 1)) := by
  ring

theorem exp_third_gt_one : 1 < Real.exp (1 / 3 : ℝ) := by
  have h := Real.add_one_lt_exp (show (1 / 3 : ℝ) ≠ 0 by norm_num)
  nlinarith

theorem factorized_residual_negative :
    (1 / 2 : ℝ) * Real.exp (-25 / 8 : ℝ) *
        (Real.exp (1 / 3 : ℝ) + Real.exp (2 / 3 : ℝ) - 1 - Real.exp (1 : ℝ)) < 0 := by
  let x : ℝ := Real.exp (1 / 3 : ℝ)
  have hx : 1 < x := by
    dsimp [x]
    exact exp_third_gt_one
  have htwo : Real.exp (2 / 3 : ℝ) = x ^ 2 := by
    dsimp [x]
    rw [show (2 / 3 : ℝ) = 1 / 3 + 1 / 3 by norm_num, Real.exp_add]
    ring_nf
  have hthree : Real.exp (1 : ℝ) = x ^ 3 := by
    dsimp [x]
    rw [show (1 : ℝ) = 1 / 3 + 1 / 3 + 1 / 3 by norm_num]
    rw [Real.exp_add, Real.exp_add]
    ring_nf
  have hbracket : x + x ^ 2 - 1 - x ^ 3 < 0 := by
    rw [cubic_factorization]
    have hsq : 0 < (x - 1) ^ 2 := sq_pos_of_pos (sub_pos.mpr hx)
    have hplus : 0 < x + 1 := by linarith
    exact neg_lt_zero.mpr (mul_pos hsq hplus)
  rw [htwo, hthree]
  change (1 / 2 : ℝ) * Real.exp (-25 / 8 : ℝ) *
      (x + x ^ 2 - 1 - x ^ 3) < 0
  exact mul_neg_of_pos_of_neg (mul_pos (by norm_num) (Real.exp_pos _)) hbracket

def claimBearing : Bool := false
def activeGateChange : Bool := false

theorem finite_defect_nonpromotion :
    claimBearing = false ∧ activeGateChange = false := by
  rfl

end Tect.PahOmc020SecondOrderDefect
