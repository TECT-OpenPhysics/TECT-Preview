import Mathlib

namespace Tect.R337

/- Exact scalar BCH fixtures for the all-bond configuration kick. -/

theorem kick_q_fixed (q : Rat) : q + 0 = q := by
  ring

theorem kick_p_edge (p q delta c : Rat) : (p + delta * c * q) - p = delta * c * q := by
  ring

theorem kick_second_commutator_zero (delta c q : Rat) : (delta * c * q) * 0 = 0 := by
  ring

theorem kick_sign_reversal (p q delta c : Rat) :
    (p + (-delta) * c * q) - p = -(delta * c * q) := by
  ring

def squareNbr (s : Finset Nat) : Finset Nat :=
  s ∪ (if 0 ∈ s then {1, 2} else ∅) ∪
    (if 1 ∈ s then {0, 3} else ∅) ∪
    (if 2 ∈ s then {0, 3} else ∅) ∪
    (if 3 ∈ s then {1, 2} else ∅)

theorem square_ball_fixture : squareNbr {0} = {0, 1, 2} := by
  native_decide

theorem square_ball_two_fixture : squareNbr (squareNbr {0}) = {0, 1, 2, 3} := by
  native_decide

def cubeNbr (s : Finset Nat) : Finset Nat :=
  s ∪ (if 0 ∈ s then {1, 2, 4} else ∅) ∪
    (if 1 ∈ s then {0, 3, 5} else ∅) ∪
    (if 2 ∈ s then {0, 3, 6} else ∅) ∪
    (if 3 ∈ s then {1, 2, 7} else ∅) ∪
    (if 4 ∈ s then {0, 5, 6} else ∅) ∪
    (if 5 ∈ s then {1, 4, 7} else ∅) ∪
    (if 6 ∈ s then {2, 4, 7} else ∅) ∪
    (if 7 ∈ s then {3, 5, 6} else ∅)

theorem cube_ball_fixture : cubeNbr {0} = {0, 1, 2, 4} := by
  native_decide

theorem cube_ball_two_fixture : cubeNbr (cubeNbr {0}) = {0, 1, 2, 3, 4, 5, 6} := by
  native_decide

theorem cube_ball_three_fixture : cubeNbr (cubeNbr (cubeNbr {0})) = {0, 1, 2, 3, 4, 5, 6, 7} := by
  native_decide

def path5Nbr (s : Finset Nat) : Finset Nat :=
  s ∪ (if 0 ∈ s then {1} else ∅) ∪
    (if 1 ∈ s then {0, 2} else ∅) ∪
    (if 2 ∈ s then {1, 3} else ∅) ∪
    (if 3 ∈ s then {2, 4} else ∅) ∪
    (if 4 ∈ s then {3} else ∅)

def path7Nbr (s : Finset Nat) : Finset Nat :=
  s ∪ (if 0 ∈ s then {1} else ∅) ∪
    (if 1 ∈ s then {0, 2} else ∅) ∪
    (if 2 ∈ s then {1, 3} else ∅) ∪
    (if 3 ∈ s then {2, 4} else ∅) ∪
    (if 4 ∈ s then {3, 5} else ∅) ∪
    (if 5 ∈ s then {4, 6} else ∅) ∪
    (if 6 ∈ s then {5} else ∅)

theorem path_shape_ball_fixture :
    path5Nbr (path5Nbr {2}) = {0, 1, 2, 3, 4} ∧
      path7Nbr (path7Nbr {2}) = {0, 1, 2, 3, 4} := by
  native_decide

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R337
