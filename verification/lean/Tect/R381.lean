import Mathlib

namespace Tect.R381

/- R381 formalizes the scalar square-root Cauchy envelope used for the
   endpoint modular-moment bridge.  The finite matrix Cauchy reduction and
   all Gibbs/thermodynamic limits remain executable evidence. -/

theorem scalar_cauchy_envelope (m0 m2 z : ℝ)
    (hm0 : 0 ≤ m0) (hm2 : 0 ≤ m2) (hz : 0 ≤ z)
    (hprod : z ^ 2 ≤ m0 * m2) :
    z ≤ Real.sqrt (m0 * m2) := by
  have hnonneg : 0 ≤ m0 * m2 := mul_nonneg hm0 hm2
  have hsquare : (Real.sqrt (m0 * m2)) ^ 2 = m0 * m2 := by
    simpa using Real.sq_sqrt hnonneg
  have hsqrt : 0 ≤ Real.sqrt (m0 * m2) := Real.sqrt_nonneg _
  nlinarith

theorem beta_scaled_cauchy (beta m0 m2 z : ℝ)
    (hbeta : 0 ≤ beta) (hm0 : 0 ≤ m0) (hm2 : 0 ≤ m2) (hz : 0 ≤ z)
    (hprod : z ^ 2 ≤ m0 * m2) :
    beta * z ≤ beta * Real.sqrt (m0 * m2) := by
  have h := scalar_cauchy_envelope m0 m2 z hm0 hm2 hz hprod
  nlinarith

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R381
