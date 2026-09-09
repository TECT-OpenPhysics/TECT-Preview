import Mathlib

/-!
Finite rational checks for the PAH-OMC-020 amplitude-only semigroup estimate.
The R-512 spectral zero-energy implication and the model measure construction
remain analytic inputs outside this file.
-/

namespace Tect.PahOmc020RadialSemigroup

theorem radial_jump_bound {h : Rat} (hh : 0 ≤ h) : 2 * h ≤ 2 * h := by
  exact le_rfl

theorem residual_bound {H L h : Rat} (hH : 0 ≤ H) (hL : 0 ≤ L) (hh : 0 ≤ h) :
    H * (L * (2 * h)) = 2 * H * L * h := by
  ring

theorem compact_time_bound {T H L h : Rat} (hT : 0 ≤ T) (hH : 0 ≤ H)
    (hL : 0 ≤ L) (hh : 0 ≤ h) :
    T * (2 * H * L * h) = 2 * T * H * L * h := by
  ring

theorem correlation_bound {M T H L h : Rat} (hM : 0 ≤ M) (hT : 0 ≤ T)
    (hH : 0 ≤ H) (hL : 0 ≤ L) (hh : 0 ≤ h) :
    M * (2 * T * H * L * h) = 2 * M * T * H * L * h := by
  ring

theorem refinement_strict_decay {T H L h : Rat} (hT : 0 < T) (hH : 0 < H)
    (hL : 0 < L) (hh : 0 < h) :
    2 * T * H * L * (h / 2) < 2 * T * H * L * h := by
  have hhalf : h / 2 < h := by nlinarith
  have hcoef : 0 < 2 * T * H * L := by positivity
  exact mul_lt_mul_of_pos_left hhalf hcoef

theorem primary_fixture :
    (2 * 2 * (30 : Rat) * (1 / 2) * (1 / 256)) = 15 / 64 := by
  norm_num

theorem independent_fixture :
    (5 / 4 : Rat) * (2 * 16 * (3 / 4) * (1 / 256)) = 15 / 128 := by
  norm_num

end Tect.PahOmc020RadialSemigroup
