import Mathlib

namespace Tect.R182

/-
  R-178 supplies the active two-root cross-owner phase Hessian coefficient
  -(field + current*w1*w2) = -(2 + 3*1*2) = -8.  R-181 supplies the
  lower-triangular feedback matrix with beta=1/2.  This file proves the
  exact congruence and its negative quadratic direction.  It is a margin
  requirement for the complete owner, not a production sign theorem.
-/

def feedbackMatrix : Matrix (Fin 2) (Fin 2) Rat :=
  !![1, 0; 1 / 2, 1]

def crossHessian : Matrix (Fin 2) (Fin 2) Rat :=
  !![-8, 8; 8, -8]

def pulledHessian : Matrix (Fin 2) (Fin 2) Rat :=
  !![-2, 4; 4, -8]

theorem feedback_pulled_hessian :
    pulledHessian =
      Matrix.transpose feedbackMatrix * crossHessian * feedbackMatrix := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [feedbackMatrix, crossHessian, pulledHessian,
      Matrix.mul_apply, Fin.sum_univ_succ]

theorem cross_hessian_quadratic (x y : Rat) :
    x * (-8 * x + 8 * y) +
      y * (8 * x - 8 * y) = -8 * (x - y) ^ 2 := by
  ring

theorem pulled_hessian_quadratic (x y : Rat) :
    x * (-2 * x + 4 * y) +
      y * (4 * x - 8 * y) = -2 * (x - 2 * y) ^ 2 := by
  ring

theorem pulled_negative_fixture :
    (0 : Rat) * (-2 * 0 + 4 * 1) +
      1 * (4 * 0 - 8 * 1) = -8 := by
  norm_num

end Tect.R182
