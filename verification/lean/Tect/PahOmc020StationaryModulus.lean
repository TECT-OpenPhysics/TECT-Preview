import Mathlib

/-!
Finite rational cross-checks for the PAH-OMC-020 stationary-modulus
correction.  These declarations formalize only the deterministic envelope
algebra and the rare-state weighted-average fixture; they do not construct a
stopping-time process or a PAH counterexample.
-/

namespace Tect.PahOmc020StationaryModulus

def weightedGamma (m eps : Rat) : Rat := 2 * m * eps / (m + eps)

theorem weighted_gamma_rare (m : Rat) (hm : 0 < m) :
    weightedGamma m (1 / m ^ 2) = 2 * m / (m ^ 3 + 1) := by
  unfold weightedGamma
  have hm0 : m ≠ 0 := ne_of_gt hm
  field_simp [hm0]

theorem rare_fixture_m8 :
    weightedGamma 8 (1 / (8 : Rat) ^ 2) = 16 / 513 := by
  norm_num [weightedGamma]

theorem rare_fixture_scale_m8 :
    weightedGamma 8 (1 / (8 : Rat) ^ 2) / 8 < 1 / 32 := by
  norm_num [weightedGamma]

theorem deterministic_envelope_fixture :
    2 * (1 / (1000 : Rat)) * (540 * 2 * (1 / 4 : Rat) ^ 2) +
        2 * (1 / (1000 : Rat)) ^ 2 *
          (60 * 2 * (60 * 2 * (1 / 4 : Rat) ^ 2)) =
      171 / 1250 := by
  norm_num

theorem two_square_sum (a b : Rat) :
    (a + b) ^ 2 ≤ 2 * a ^ 2 + 2 * b ^ 2 := by
  nlinarith [sq_nonneg (a - b)]

end Tect.PahOmc020StationaryModulus
