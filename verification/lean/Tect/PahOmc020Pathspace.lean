import Mathlib

/-!
Finite rational checks for the PAH-OMC-020 path-space bridge contract.

These declarations formalize only the finite triangle, footprint, branching,
and ratio consequences used by the executable audit.  They do not construct a
path-space process, prove non-explosion or uniqueness, or identify a process
with the R-512 minimal closed-form semigroup.
-/

namespace Tect.PahOmc020Pathspace

theorem bridge_triangle (state boundary target : Rat)
    (h_state : 0 ≤ state) (h_boundary : 0 ≤ boundary)
    (h_target : 0 ≤ target) :
    state ≤ state + boundary + target := by
  linarith

theorem bridge_budget_nonnegative (state boundary target : Rat)
    (h_state : 0 ≤ state) (h_boundary : 0 ≤ boundary)
    (h_target : 0 ≤ target) :
    0 ≤ state + boundary + target := by
  linarith

theorem source_overlap_formula :
    (16 : Rat) * (4 * 2 + 1) = 144 := by
  norm_num

theorem source_two_copy_formula :
    (2 : Rat) * (16 * (4 * 2 + 1)) = 288 := by
  norm_num

theorem source_first_root_width_two :
    (16 : Rat) * (2 + 2 * 2 + 1) = 112 := by
  norm_num

theorem independent_first_root_width_three :
    (16 : Rat) * (3 + 2 * 2 + 1) = 128 := by
  norm_num

theorem tail_ratio_fixture :
    (288 : Rat) * ((1 : Rat) / 4) / (128 + 1) < 1 := by
  norm_num

theorem tail_ratio_primary_fixture :
    (288 : Rat) * ((1 : Rat) / 4) / (256 + 1) < 1 := by
  norm_num

theorem state_fixture_pair_decreases :
    (4 * (5 / 4 : Rat) * (3 / 2) * (3 / 2) * (1 / 2) ^ (3 - 2)
      + 4 * (5 / 4 : Rat) * (3 / 2) * (3 / 2) * (1 / 2) ^ (4 - 2))
    >
    (4 * (5 / 4 : Rat) * (3 / 2) * (3 / 2) * (1 / 2) ^ (5 - 2)
      + 4 * (5 / 4 : Rat) * (3 / 2) * (3 / 2) * (1 / 2) ^ (6 - 2)) := by
  norm_num

theorem independent_state_fixture_pair_decreases :
    (4 * (7 / 6 : Rat) * (4 / 3) * (4 / 3) * (1 / 3) ^ (3 - 2)
      + 4 * (7 / 6 : Rat) * (4 / 3) * (4 / 3) * (1 / 3) ^ (4 - 2))
    >
    (4 * (7 / 6 : Rat) * (4 / 3) * (4 / 3) * (1 / 3) ^ (5 - 2)
      + 4 * (7 / 6 : Rat) * (4 / 3) * (4 / 3) * (1 / 3) ^ (6 - 2)) := by
  norm_num

theorem explicit_target_defect_fixture :
    (0 : Rat) < 7 / 10 := by
  norm_num

end Tect.PahOmc020Pathspace
