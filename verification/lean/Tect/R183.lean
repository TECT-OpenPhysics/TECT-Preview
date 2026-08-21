import Mathlib

namespace Tect.R183

/-
  R-182 leaves the active cross block negative.  This file proves the exact
  diagonal reserve required to pay that block after the beta=1/2 feedback
  pullback.  It is a conditional margin theorem, not a production estimate.
-/

def feedbackMatrix : Matrix (Fin 2) (Fin 2) Rat :=
  !![1, 0; 1 / 2, 1]

def reserveHessian (a d1 d2 : Rat) : Matrix (Fin 2) (Fin 2) Rat :=
  !![d1 - a, a; a, d2 - a]

def pulledReserveHessian (a d1 d2 : Rat) : Matrix (Fin 2) (Fin 2) Rat :=
  Matrix.transpose feedbackMatrix * reserveHessian a d1 d2 * feedbackMatrix

def qform (a p q x y : Rat) : Rat :=
  x * (p * x + a * y) + y * (a * x + q * y)

theorem pulled_reserve_matrix (a d1 d2 : Rat) :
    pulledReserveHessian a d1 d2 =
      !![d1 - a + a + (d2 - a) / 4,
         a + (d2 - a) / 2;
         a + (d2 - a) / 2, d2 - a] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [pulledReserveHessian, feedbackMatrix, reserveHessian,
      Matrix.mul_apply, Fin.sum_univ_succ]
    <;> ring

theorem pulled_reserve_qform (a d1 d2 x y : Rat) :
    x * ((d1 - a + a + (d2 - a) / 4) * x +
      (a + (d2 - a) / 2) * y) +
      y * ((a + (d2 - a) / 2) * x + (d2 - a) * y) =
      qform a (d1 - a) (d2 - a) x (x / 2 + y) := by
  dsimp [qform]
  ring

theorem reserve_completion (a p r x y : Rat) (hp : 0 < p) :
    qform a p (a ^ 2 / p + r) x y =
      p * (x + (a / p) * y) ^ 2 + r * y ^ 2 := by
  dsimp [qform]
  field_simp [ne_of_gt hp]
  ring

theorem reserve_nonneg (a p r x y : Rat) (hp : 0 < p) (hr : 0 <= r) :
    0 <= qform a p (a ^ 2 / p + r) x y := by
  rw [reserve_completion a p r x y hp]
  exact add_nonneg
    (mul_nonneg (le_of_lt hp) (sq_nonneg _))
    (mul_nonneg hr (sq_nonneg _))

theorem pulled_reserve_nonneg (a d1 d2 x y : Rat)
    (hp : 0 < d1 - a)
    (hr : 0 <= d2 - a - a ^ 2 / (d1 - a)) :
    0 <= x * ((d1 - a + a + (d2 - a) / 4) * x +
      (a + (d2 - a) / 2) * y) +
      y * ((a + (d2 - a) / 2) * x + (d2 - a) * y) := by
  rw [pulled_reserve_qform]
  have hq : d2 - a = a ^ 2 / (d1 - a) +
      (d2 - a - a ^ 2 / (d1 - a)) := by ring
  rw [hq]
  exact reserve_nonneg a (d1 - a) (d2 - a - a ^ 2 / (d1 - a))
    x (x / 2 + y) hp hr

theorem necessary_reserve_witness (a p q : Rat) (hp : 0 < p) :
    qform a p q (-(a / p)) 1 = q - a ^ 2 / p := by
  dsimp [qform]
  field_simp [ne_of_gt hp]
  ring

theorem isotropic_completion (a d x y : Rat) :
    qform a (d - a) (d - a) x y =
      d / 2 * (x + y) ^ 2 + (d - 2 * a) / 2 * (x - y) ^ 2 := by
  dsimp [qform]
  ring

theorem isotropic_nonneg (a d x y : Rat) (ha : 0 <= a) (hd : 2 * a <= d) :
    0 <= qform a (d - a) (d - a) x y := by
  rw [isotropic_completion]
  exact add_nonneg
    (mul_nonneg (by linarith) (sq_nonneg _))
    (mul_nonneg (by linarith) (sq_nonneg _))

theorem isotropic_failure_below (a d : Rat) (hd : d < 2 * a) :
    qform a (d - a) (d - a) 1 (-1) < 0 := by
  dsimp [qform]
  nlinarith

end Tect.R183
