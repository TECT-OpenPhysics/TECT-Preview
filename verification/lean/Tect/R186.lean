import Mathlib

namespace Tect.R186

theorem temporal_weighted_cauchy_fixture :
    ((1 : Rat) / 2 * 1 + 1 / 2 * 2) ^ 2 <=
      (1 / 2 * 1 ^ 2 + 1 / 2 * 2 ^ 2) := by
  norm_num

theorem temporal_douglas_energy_fixture :
    (((1 : Rat) / 2 * 1 + 1 / 2 * 2) * 3) ^ 2 /
        (1 / 2 * 1 ^ 2 + 1 / 2 * 2 ^ 2) <= 3 ^ 2 := by
  norm_num

theorem complete_packet_identity
    (base fresh future traceFresh traceFuture : Rat) :
    ((base + fresh + future) ^ 2 - base ^ 2) / 2 -
        traceFresh / 2 - traceFuture / 2 =
      base * fresh + fresh ^ 2 / 2 - traceFresh / 2 +
        (base + fresh) * future + future ^ 2 / 2 - traceFuture / 2 := by
  ring

theorem complete_packet_fixture :
    ((7 : Rat) / 10 + 3 / 10 - 1 / 5) ^ 2 / 2 -
        (7 / 10) ^ 2 / 2 - 3 / 25 / 2 - 1 / 20 / 2 +
      ((-2 : Rat) / 5 + 3 / 5 + 1 / 2) ^ 2 / 2 -
        ((-2 : Rat) / 5) ^ 2 / 2 - (-7 / 100) / 2 - 9 / 100 / 2 =
      29 / 200 := by
  norm_num

theorem retained_cross_fixture :
    (3 / 10 : Rat) * (-1 / 5) + (3 / 5) * (1 / 2) = 6 / 25 := by
  norm_num

end Tect.R186
