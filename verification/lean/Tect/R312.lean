import Mathlib

namespace Tect.R312

/- R312 formalizes the finite spectral-sum cancellation used by EXP-001142.
   It does not formalize matrix diagonalization, unbounded domains, a common
   core, or any volume, beta, cutoff, or QFT limit. -/

def generatorCoeff (gap hbar value : Rat) : Rat := gap * value / hbar

theorem finite_mode_pairing {ι : Type} [Fintype ι]
    (ell gap hbar a b : ι → Rat) (hh : ∀ i, hbar i ≠ 0) :
    (∑ i, ell i * (-(gap i ^ 2) * a i / hbar i ^ 2) * b i) +
      (∑ i, ell i * generatorCoeff (gap i) (hbar i) (a i) *
        generatorCoeff (gap i) (hbar i) (b i)) = 0 := by
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_eq_zero
  intro i hi
  simp [generatorCoeff]
  field_simp [hh i]
  ring

theorem finite_mode_nonnegative {ι : Type} [Fintype ι]
    (ell gap hbar a : ι → Rat)
    (hell : ∀ i, 0 ≤ ell i) :
    0 ≤ ∑ i, ell i * (generatorCoeff (gap i) (hbar i) (a i)) ^ 2 := by
  apply Finset.sum_nonneg
  intro i hi
  exact mul_nonneg (hell i) (sq_nonneg _)

theorem gap_square_fixture : (-(7 : Rat) ^ 2) + 7 ^ 2 = 0 := by
  norm_num

theorem two_sided_factor_fixture : (2 : Rat) * (3 / 2) = 3 := by
  norm_num

end Tect.R312
