import Mathlib

namespace Tect.R310

/- R310 formalizes the rational spectral cancellation coefficients behind
   EXP-001140.  It does not formalize finite matrix diagonalization, the
   Kubo-Mori integral, operator domains, or a thermodynamic/QFT limit. -/

def generatorCoeff (gap hbar value : Rat) : Rat := gap * value / hbar

theorem generator_pairing_scalar_fixture (ell gap hbar a b : Rat) (hh : hbar ≠ 0) :
    ell * (-(gap ^ 2) * a / hbar ^ 2) * b +
      ell * generatorCoeff gap hbar a * generatorCoeff gap hbar b = 0 := by
  simp [generatorCoeff]
  field_simp [hh]
  ring

theorem skew_adjoint_scalar_fixture (ell gap hbar a b : Rat) (hh : hbar ≠ 0) :
    ell * (-gap * a / hbar) * b + ell * a * (gap * b / hbar) = 0 := by
  field_simp [hh]
  ring

theorem modular_coefficient_fixture :
    (-1 : Rat) * 7 = -7 := by
  norm_num

theorem orientation_sum_fixture :
    (3 / 20 : Rat) + 1 / 20 = 1 / 5 := by
  norm_num

end Tect.R310
