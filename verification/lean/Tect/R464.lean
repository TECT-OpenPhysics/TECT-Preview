import Mathlib

namespace Tect.R464

/- The pinned A1 parameters have lambda = -ell with ell >= 0.  This is the
   algebraic core of the finite-cutoff coercive comparison used by R-464. -/
theorem large_branch_nonnegative
    (gamma ell t : ℚ)
    (_hgamma : 0 < gamma)
    (_hell : 0 ≤ ell)
    (_ht : 0 ≤ t)
    (hlarge : 3 * ell ≤ gamma * t) :
    0 ≤ gamma / 12 * t ^ 3 - ell / 4 * t ^ 2 := by
  have hfactor : gamma / 12 * t ^ 3 - ell / 4 * t ^ 2 =
      (t ^ 2) * (gamma * t - 3 * ell) / 12 := by ring
  rw [hfactor]
  have hsq : 0 ≤ t ^ 2 := sq_nonneg t
  have hgap : 0 ≤ gamma * t - 3 * ell := by linarith
  exact div_nonneg (mul_nonneg hsq hgap) (by norm_num)

theorem small_branch_nonnegative
    (gamma ell t T : ℚ)
    (hgamma : 0 ≤ gamma)
    (_hell : 0 ≤ ell)
    (_ht : 0 ≤ t)
    (hT : 0 ≤ T)
    (hsmall : t ≤ T) :
    0 ≤ gamma / 12 * t ^ 3 + ell / 4 * (T ^ 2 - t ^ 2) := by
  have hsum : 0 ≤ T + t := by linarith
  have hdiff : 0 ≤ T - t := by linarith
  have hsquare : 0 ≤ T ^ 2 - t ^ 2 := by
    have hprod : 0 ≤ (T - t) * (T + t) := mul_nonneg hdiff hsum
    nlinarith
  have hcube : 0 ≤ t ^ 3 := by positivity
  have hfirst : 0 ≤ gamma / 12 * t ^ 3 := by positivity
  have hsecond : 0 ≤ ell / 4 * (T ^ 2 - t ^ 2) := by positivity
  linarith

theorem cubic_lower_bound
    (mu gamma ell t T C : ℚ)
    (hmu : 0 ≤ mu)
    (_hgamma : 0 < gamma)
    (_hell : 0 ≤ ell)
    (_ht : 0 ≤ t)
    (hT : gamma * T = 3 * ell)
    (hC : 4 * C = ell * T ^ 2) :
    mu / 2 * t - ell / 4 * t ^ 2 + gamma / 6 * t ^ 3 ≥
      gamma / 12 * t ^ 3 - C := by
  have hTnonneg : 0 ≤ T := by nlinarith
  by_cases hlarge : 3 * ell ≤ gamma * t
  · have hlarge_term := large_branch_nonnegative gamma ell t _hgamma _hell _ht hlarge
    nlinarith
  · have hsmall : t ≤ T := by
      have hlt : gamma * t < 3 * ell := lt_of_not_ge hlarge
      nlinarith
    have hsmall_term := small_branch_nonnegative gamma ell t T (le_of_lt _hgamma) _hell _ht hTnonneg hsmall
    nlinarith

theorem pure_singlet_codimension_positive (m : ℕ) (hm : 0 < m) :
    0 < 4 * m ∧ 4 * m < 6 * m := by omega

theorem positive_mass_conditional_normalization
    (mass event : ℚ)
    (hmass : 0 < mass)
    (hevent : 0 ≤ event)
    (hle : event ≤ mass) :
    0 ≤ event / mass ∧ event / mass ≤ 1 := by
  constructor
  · exact div_nonneg hevent (le_of_lt hmass)
  · apply (div_le_iff₀ hmass).2
    nlinarith [hle]

end Tect.R464
