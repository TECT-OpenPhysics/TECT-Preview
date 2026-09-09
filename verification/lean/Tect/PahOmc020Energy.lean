import Mathlib

namespace Tect.PahOmc020Energy

def weightedEnergy (mass slope delta : ℚ) : ℚ :=
  mass * (slope * delta) ^ 2 / 2

def twoStateEnergy (rate : ℚ) : ℚ :=
  ((1 / 2 : ℚ) * rate * (1 : ℚ) ^ 2
    + (1 / 2 : ℚ) * rate * (1 : ℚ) ^ 2) / 2

theorem weighted_conductance_transfer
    (sourceMass targetMass kappa delta : ℚ)
    (hdom : targetMass * kappa ^ 2 ≤ sourceMass)
    (hhalf : 0 ≤ (1 / 2 : ℚ)) :
    weightedEnergy targetMass kappa delta
      ≤ weightedEnergy sourceMass 1 delta := by
  have hsq : 0 ≤ delta ^ 2 := sq_nonneg delta
  have hmul := mul_le_mul_of_nonneg_right hdom hsq
  have hhalf_mul := mul_le_mul_of_nonneg_left hmul hhalf
  dsimp [weightedEnergy]
  nlinarith

theorem weighted_transfer_fixture :
    weightedEnergy (3 / 2 : ℚ) (1 / 2 : ℚ) (3 / 2 : ℚ)
      ≤ weightedEnergy 1 1 (3 / 2 : ℚ) := by
  norm_num [weightedEnergy]

theorem static_l2_identity_contraction :
    (1 / 2 : ℚ) ≤ 1 / 2 := by
  norm_num

theorem static_energy_witness_source :
    twoStateEnergy 1 = (1 / 2 : ℚ) := by
  norm_num [twoStateEnergy]

theorem static_energy_witness_target :
    twoStateEnergy 2 = (1 : ℚ) := by
  norm_num [twoStateEnergy]

theorem static_energy_witness_strict :
    twoStateEnergy 1 < twoStateEnergy 2 := by
  norm_num [twoStateEnergy]

end Tect.PahOmc020Energy
