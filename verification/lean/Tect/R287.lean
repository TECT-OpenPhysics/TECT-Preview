import Mathlib

namespace Tect.R287

/- R287 checks only the rational threshold fixtures inherited from the R286
   full-generator coefficient.  It does not formalize exponential limits,
   Q3 domains, word incidence, or thermodynamic histories. -/

def G : ℚ := 51 / 35
def c : ℚ := 2 / 3
def t : ℚ := 1 / 3
def sigmaGood : ℚ := 1 / 5
def sigmaBad : ℚ := 1 / 10
def rate : ℚ := t * G / 4

def topCoeff (m : ℕ) : ℚ := -(m : ℚ) * c * (-G / 4) ^ (m - 1)

theorem rate_fixture : rate = 17 / 140 := by
  norm_num [rate, t, G]

theorem good_margin_fixture : sigmaGood - rate = 11 / 140 := by
  norm_num [sigmaGood, rate, t, G]

theorem bad_margin_fixture : rate - sigmaBad = 3 / 140 := by
  norm_num [sigmaBad, rate, t, G]

theorem prefactor_fixture : c * t = 2 / 9 := by
  norm_num [c, t]

theorem threshold_order_fixture : sigmaBad < rate ∧ rate < sigmaGood := by
  norm_num [sigmaBad, rate, t, G, sigmaGood]

theorem top_coefficient_m2 : topCoeff 2 = 17 / 35 := by
  norm_num [topCoeff, c, G]

end Tect.R287
