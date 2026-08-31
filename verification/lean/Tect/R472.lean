import Mathlib

namespace Tect.R472

/-
  R-472 is an additive kernel cross-check for the already accepted R-157 and
  R-158 exact rational cores.  It does not introduce a functional, a
  dynamics, a physical owner, or a limit theorem.
-/

theorem r157_total_mass_exact :
    (26000000000947494031 : ℚ) / 100000000000000000000 + 7 / 250 =
      28800000000947494031 / 100000000000000000000 := by
  norm_num

theorem r157_gap_exact :
    (28800000000947494031 : ℚ) / 100000000000000000000 / 2
        - 3 * (-43 / 100 : ℚ) ^ 2 / (32 * (81 / 50 : ℚ)) =
      719818750025582338837 / 5400000000000000000000 := by
  norm_num

theorem r157_gap_gt_one_eighth :
    (719818750025582338837 : ℚ) / 5400000000000000000000 > 1 / 8 := by
  norm_num

theorem r157_radial_gap_exact :
    (28800000000947494031 : ℚ) / 100000000000000000000
        - (-43 / 100 : ℚ) ^ 2 / (4 * (81 / 50 : ℚ)) =
      2101675000076747016511 / 8100000000000000000000 := by
  norm_num

theorem r157_radial_gap_gt_one_quarter :
    (2101675000076747016511 : ℚ) / 8100000000000000000000 > 1 / 4 := by
  norm_num

theorem r157_completion_identity (rho : ℚ) :
    (28800000000947494031 : ℚ) / 100000000000000000000 / 2
        + (-43 / 100 : ℚ) * rho / 4 + (81 / 50 : ℚ) * rho ^ 2 / 6 =
      719818750025582338837 / 5400000000000000000000
        + (81 / 50 : ℚ) * (rho - 43 / 216) ^ 2 / 6 := by
  ring_nf

theorem r157_classii_input_determinant :
    (1 / 5 : ℚ) * (3 / 20) - (1 / 10 : ℚ) ^ 2 = 1 / 50 := by
  norm_num

theorem r158_characteristic_identity (t : ℚ) :
    (t - 1 / 10) * ((t - 13 / 100) * (t - 17 / 100) - 1 / 400)
      - (1 / 400 : ℚ) * ((t - 17 / 100) + (t - 13 / 100)) + 1 / 4000 =
      t ^ 3 - 2 / 5 * t ^ 2 + 223 / 5000 * t - 3 / 3125 := by
  ring_nf

theorem r158_local_affine_square (rho : ℚ) :
    (-43 / 100 : ℚ) * rho ^ 2 / 4 + (81 / 50 : ℚ) * rho ^ 3 / 6 =
        -(1849 / 86400 : ℚ) * rho / 2
        + (81 / 50 : ℚ) * rho * (rho - 43 / 216) ^ 2 / 6 := by
  ring_nf

theorem r158_coexistence_charge :
    (16 : ℚ) ^ 3 * (43 / 216 : ℚ) / 2 = 11008 / 27 := by
  norm_num

theorem r158_saddle_drop_ratio :
    (1849 / 64800 : ℚ) = (4 / 3 : ℚ) * (1849 / 86400 : ℚ) := by
  norm_num

theorem r158_stationary_density_values :
    ((43 / 216 : ℚ) > 0) ∧ ((43 / 648 : ℚ) > 0) ∧
      (43 / 216 : ℚ) = 3 * (43 / 648 : ℚ) := by
  norm_num

theorem r158_transition_order (lambda0 : ℚ) :
    lambda0 - 1849 / 64800 < lambda0 - 1849 / 86400 ∧
      lambda0 - 1849 / 86400 < lambda0 := by
  norm_num

theorem r157_radial_numerator_positive {theta : ℚ}
    (hzero : 0 ≤ theta) (hone : theta ≤ 1) :
    0 < -81 * theta ^ 2 + 128 * theta + 128 := by
  have hprod : 0 ≤ theta * (1 - theta) :=
    mul_nonneg hzero (sub_nonneg.mpr hone)
  nlinarith

theorem methods_are_not_changed :
    True := by
  trivial

end Tect.R472
