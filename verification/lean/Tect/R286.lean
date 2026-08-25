import Mathlib

namespace Tect.R286

/- R286 formalizes only the rational coefficient fixtures and the integer
   source-degree gap used by EXP-001114.  It does not formalize unbounded
   Q3 operators, common cores, Duhamel histories, or thermodynamic limits. -/

def G : ℚ := 51 / 35
def c : ℚ := 2 / 3

def topCoeff (m : ℕ) : ℚ := -(m : ℚ) * c * (-G / 4) ^ (m - 1)

theorem coefficient_m1 : topCoeff 1 = -(2 / 3 : ℚ) := by
  norm_num [topCoeff, G, c]

theorem coefficient_m2 : topCoeff 2 = 17 / 35 := by
  norm_num [topCoeff, G, c]

theorem coefficient_m3 : topCoeff 3 = -(2601 / 9800 : ℚ) := by
  norm_num [topCoeff, G, c]

theorem coefficient_m4 : topCoeff 4 = 44217 / 343000 := by
  norm_num [topCoeff, G, c]

theorem coefficient_m5 : topCoeff 5 = -(2255067 / 38416000 : ℚ) := by
  norm_num [topCoeff, G, c]

theorem coefficient_m6 : topCoeff 6 = 345025251 / 13445600000 := by
  norm_num [topCoeff, G, c]

theorem kinetic_degree_gap {m k : ℤ} (hm : 1 ≤ m) (hk : 1 ≤ k) (hkm : k ≤ m) :
    4 * (m - k) - 1 < 4 * m - 3 := by
  omega

theorem target_degree_fixture (m : ℕ) : (4 : ℤ) * (m : ℤ) - 3 = 4 * (m : ℤ) - 3 := by
  rfl

end Tect.R286
