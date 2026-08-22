import Mathlib

namespace Tect.R193

/-!
  R-193 formalizes the interface obstruction exposed by R-192.  A static
  quadratic/covariance pair does not determine a heat/root map: two different
  diagonal contractions satisfy the same static compatibility assumptions and
  reverse the relative decay order.  This is an interface theorem only; it is
  not a counterexample to the A1 functional or to the complete A13 owner.
 -/

structure StaticData where
  h1 : Rat
  h2 : Rat
  c1 : Rat
  c2 : Rat

def staticInverse (d : StaticData) : Prop :=
  d.h1 * d.c1 = 1 ∧ d.h2 * d.c2 = 1

def diagonalHeat (a b : Rat) (x : Rat × Rat) : Rat × Rat :=
  (a * x.1, b * x.2)

def admissibleDiagonal (d : StaticData) (a b : Rat) : Prop :=
  staticInverse d ∧ 0 < a ∧ a < 1 ∧ 0 < b ∧ b < 1

def pinnedStatic : StaticData :=
  { h1 := 1, h2 := 2, c1 := 1, c2 := 1 / 2 }

theorem pinned_static_inverse : staticInverse pinnedStatic := by
  norm_num [staticInverse, pinnedStatic]

theorem map_a_admissible :
    admissibleDiagonal pinnedStatic (1 / 2) (1 / 4) := by
  norm_num [admissibleDiagonal, staticInverse, pinnedStatic]

theorem map_b_admissible :
    admissibleDiagonal pinnedStatic (1 / 4) (1 / 2) := by
  norm_num [admissibleDiagonal, staticInverse, pinnedStatic]

theorem map_a_zero : diagonalHeat (1 / 2) (1 / 4) (0, 0) = (0, 0) := by
  norm_num [diagonalHeat]

theorem map_b_zero : diagonalHeat (1 / 4) (1 / 2) (0, 0) = (0, 0) := by
  norm_num [diagonalHeat]

theorem maps_distinct :
    diagonalHeat (1 / 2) (1 / 4) ≠ diagonalHeat (1 / 4) (1 / 2) := by
  intro h
  have hx := congrFun h (1, 0)
  norm_num [diagonalHeat] at hx

theorem relative_order_a : (1 / 4 : Rat) < 1 / 2 := by
  norm_num

theorem relative_order_b : (1 / 4 : Rat) < 1 / 2 := by
  norm_num

theorem two_static_compatible_heat_maps :
    admissibleDiagonal pinnedStatic (1 / 2) (1 / 4) ∧
      admissibleDiagonal pinnedStatic (1 / 4) (1 / 2) ∧
        diagonalHeat (1 / 2) (1 / 4) ≠ diagonalHeat (1 / 4) (1 / 2) := by
  exact ⟨map_a_admissible, map_b_admissible, maps_distinct⟩

theorem nonidentifiability_for_any_static_data (d : StaticData)
    (hd : staticInverse d) :
    admissibleDiagonal d (1 / 2) (1 / 4) ∧
      admissibleDiagonal d (1 / 4) (1 / 2) ∧
        diagonalHeat (1 / 2) (1 / 4) ≠ diagonalHeat (1 / 4) (1 / 2) := by
  have ha : admissibleDiagonal d (1 / 2) (1 / 4) := by
    norm_num [admissibleDiagonal, hd]
  have hb : admissibleDiagonal d (1 / 4) (1 / 2) := by
    norm_num [admissibleDiagonal, hd]
  exact ⟨ha, hb, maps_distinct⟩

end Tect.R193
