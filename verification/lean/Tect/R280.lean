import Mathlib

namespace Tect.R280

/- The symbolic N^5 audit assigns one half of anisotropic order to each
   creation/annihilation factor.  The noncommutative expansion is checked by
   the executable lanes; this file formalizes the scalar degree envelope used
   by that audit and deliberately does not assert a Q3 form-domain theorem. -/

theorem anisotropic_order_bound {degree : Nat} (hdegree : degree ≤ 10) :
    (degree : ℝ) / 2 ≤ 5 := by
  have hreal : (degree : ℝ) ≤ 10 := by
    exact_mod_cast hdegree
  nlinarith

theorem degree_fixture : ((10 : ℝ) / 2) = 5 := by
  norm_num

end Tect.R280
