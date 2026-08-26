import Mathlib

namespace Tect.R349

theorem moment_energy_assembly
    (moment coefficient energy : Rat)
    (h_moment : 0 ≤ moment)
    (h_coefficient : 0 ≤ coefficient)
    (h_energy : 0 ≤ energy)
    (h_transfer : moment ≤ coefficient * energy) :
    moment ≤ coefficient * energy := by
  exact h_transfer

theorem positive_quotient_envelope
    (two_slice moment coefficient energy : Rat)
    (h_two_slice : 0 ≤ two_slice)
    (h_moment : two_slice ≤ moment)
    (h_transfer : moment ≤ coefficient * energy) :
    two_slice ≤ coefficient * energy := by
  linarith

end Tect.R349
