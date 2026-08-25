import Mathlib

namespace Tect.R277

/- Finite weighted top-defect fixtures for EXP-001097.  The numerical Q3
   histories remain outside this arithmetic cross-check. -/

def topOverlap (n k : Nat) : Nat := if k = n - 1 then 1 else 0

def weightedDefect (n k : Nat) : Nat := n * n * topOverlap n k

def orientationCount (orientations : List Int) : Nat := orientations.length

theorem weighted_defect_zero_of_core {K n k : Nat}
    (hk : k ≤ K) (hn : K + 1 < n) : weightedDefect n k = 0 := by
  unfold weightedDefect topOverlap
  split
  · omega
  · simp

theorem boundary_weighted_fixture : weightedDefect 8 7 = 64 := by
  norm_num [weightedDefect, topOverlap]

theorem core_weighted_fixture : weightedDefect 8 5 = 0 := by
  norm_num [weightedDefect, topOverlap]

theorem orientation_count_fixture :
    orientationCount ([-1, 1] : List Int) = 2 := by
  rfl

theorem history_zero_anchor_fixture : weightedDefect 3 0 = 0 := by
  norm_num [weightedDefect, topOverlap]

theorem scope_fixture :
    weightedDefect 8 5 = 0 ∧ weightedDefect 8 7 = 64 ∧
      orientationCount ([-1, 1] : List Int) = 2 := by
  norm_num [weightedDefect, topOverlap, orientationCount]

end Tect.R277
