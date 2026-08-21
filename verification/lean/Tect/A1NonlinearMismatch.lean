import Mathlib

/-!
  Exact core of the A1 nonlinear-owner mismatch.

  The historical manifest declares the nonlinear density
    lambda/2 * rho^2 + gamma/3 * rho^3,
  while the audited residual uses lambda*rho + gamma*rho^2 as its scalar
  coefficient.  Differentiating the declared density in the real field gives
  twice the residual coefficient.  This file checks only that rational
  algebraic core; it does not formalise the spatial functional, Class-II
  cKK/cJK mismatch, shell measure, or any continuum statement.
-/

namespace Tect.A1NonlinearMismatch

def lambda0 : Rat := -(43 : Rat) / 100
def gamma0 : Rat := (81 : Rat) / 50

def declaredCoeff (rho : Rat) : Rat := 2 * lambda0 * rho + 2 * gamma0 * rho ^ 2
def residualCoeff (rho : Rat) : Rat := lambda0 * rho + gamma0 * rho ^ 2

theorem declared_is_twice_residual (rho : Rat) :
    declaredCoeff rho = 2 * residualCoeff rho := by
  simp [declaredCoeff, residualCoeff]
  ring

theorem manifest_fixture :
    And (residualCoeff (1 / 4) = -(1 : Rat) / 160)
      (And (declaredCoeff (1 / 4) = -(1 : Rat) / 80)
        (declaredCoeff (1 / 4) - residualCoeff (1 / 4) = -(1 : Rat) / 160)) := by
  norm_num [lambda0, gamma0, declaredCoeff, residualCoeff]

theorem equality_zeroes (rho : Rat) :
    declaredCoeff rho = residualCoeff rho <->
      Or (rho = 0) (rho = (43 : Rat) / 162) := by
  rw [declared_is_twice_residual]
  constructor
  case mp =>
    intro h
    have hz : residualCoeff rho = 0 := by linarith
    have hfactor : rho * (lambda0 + gamma0 * rho) = residualCoeff rho := by
      simp [residualCoeff]
      ring
    have hz_factor : rho * (lambda0 + gamma0 * rho) = 0 := by
      rw [hfactor]
      exact hz
    rcases mul_eq_zero.mp hz_factor with hzero | hlinear
    case inl => exact Or.inl hzero
    case inr =>
      norm_num [lambda0, gamma0] at hlinear
      right
      linarith
  case mpr =>
    intro h
    rcases h with rfl | h
    case inl => simp [residualCoeff]
    case inr =>
      subst rho
      norm_num [lambda0, gamma0, declaredCoeff, residualCoeff]

end Tect.A1NonlinearMismatch
