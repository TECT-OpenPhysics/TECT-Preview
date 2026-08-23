import Mathlib

namespace Tect.R202

/-!
  Finite full-residue cross-check for the nonlinear F_ref stochastic candidate.
  The two-root witness is not a closed proper coordinate subspace after the
  nonlinear operation; this file only checks the finite residue/cardinality
  side of that statement. It does not assert a production heat-root map.
-/

def rootPair : Finset (Fin 16) := {1, 2}

theorem side16_card : Fintype.card (Fin 16) = 16 := by
  decide

theorem root_pair_card : rootPair.card = 2 := by
  decide

theorem root_pair_is_proper : rootPair ≠ (Finset.univ : Finset (Fin 16)) := by
  decide

theorem saturated_interval_has_at_least_side16_residues :
    (14 : Int) - (-11) + 1 ≥ 16 := by
  norm_num

theorem finite_residue_index_bound (k : Fin 16) : k.val < 16 := by
  exact k.isLt

end Tect.R202
