import Mathlib

/-!
  Exact Class-II owner mismatch for the hash-pinned A1 manifest.

  The declared energy differentiates its K term with the cKK*beta_X^2
  coefficient, while the historical residual uses cJK*alpha_X*beta_X.
  This file checks only the finite rational coefficient obstruction.  It
  does not formalise the spatial K current, the divergence, the full A1
  functional, or any continuum or solver statement.
-/

namespace Tect.A1ClassIIOwnerMismatch

def alphaX : Rat := (3 : Rat) / 10
def betaX : Rat := (1 : Rat) / 4
def massX : Rat := 2
def massRegularizer : Rat := (1 : Rat) / 1000000000000
def cJK : Rat := (1 : Rat) / 10
def cKK : Rat := (3 : Rat) / 20

def massDenom : Rat := massX ^ 2 + massRegularizer
def declaredNumerator : Rat := cKK * betaX ^ 2
def residualNumerator : Rat := cJK * alphaX * betaX
def declaredCoeff : Rat := declaredNumerator / massDenom
def residualCoeff : Rat := residualNumerator / massDenom

theorem numerator_fixture :
    And (declaredNumerator = (3 : Rat) / 320)
      (And (residualNumerator = (3 : Rat) / 400)
        (declaredNumerator - residualNumerator = (3 : Rat) / 1600)) := by
  norm_num [declaredNumerator, residualNumerator, cKK, betaX, cJK, alphaX]

theorem mass_denom_positive : 0 < massDenom := by
  norm_num [massDenom, massX, massRegularizer]

theorem coefficient_difference :
    declaredCoeff - residualCoeff = ((3 : Rat) / 1600) / massDenom := by
  have hnum : declaredNumerator - residualNumerator = (3 : Rat) / 1600 := by
    norm_num [declaredNumerator, residualNumerator, cKK, betaX, cJK, alphaX]
  calc
    declaredCoeff - residualCoeff =
        (declaredNumerator - residualNumerator) / massDenom := by
          simp [declaredCoeff, residualCoeff]
          ring
    _ = ((3 : Rat) / 1600) / massDenom := by rw [hnum]

theorem coefficients_are_not_equal : Not (declaredCoeff = residualCoeff) := by
  intro h
  have hz : declaredCoeff - residualCoeff = 0 := sub_eq_zero.mpr h
  rw [coefficient_difference] at hz
  have hnum : Not ((3 : Rat) / 1600 = 0) := by norm_num
  have hden : Not (massDenom = 0) := ne_of_gt mass_denom_positive
  exact (div_ne_zero hnum hden) hz

end Tect.A1ClassIIOwnerMismatch
