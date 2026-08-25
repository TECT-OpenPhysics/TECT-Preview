import Mathlib

namespace Tect.R276

/- Natural-number support fixtures for EXP-001095.  This is only the fixed
   finite-particle core implication; it does not formalize Q3 evolution or a
   thermodynamic limit. -/

def topOverlap (n k : Nat) : Nat := if k = n - 1 then 1 else 0

def defectAmplitude (n k : Nat) : Nat := n * topOverlap n k

theorem top_overlap_zero_of_core {K n k : Nat}
    (hk : k ≤ K) (hn : K + 1 < n) : topOverlap n k = 0 := by
  unfold topOverlap
  split
  · omega
  · rfl

theorem defect_zero_of_core {K n k : Nat}
    (hk : k ≤ K) (hn : K + 1 < n) : defectAmplitude n k = 0 := by
  simp [defectAmplitude, top_overlap_zero_of_core hk hn]

theorem boundary_level_fixture : topOverlap 8 7 = 1 := by
  norm_num [topOverlap]

theorem core_level_fixture : defectAmplitude 8 5 = 0 := by
  norm_num [defectAmplitude, topOverlap]

theorem scope_fixture :
    (topOverlap 8 5 = 0 ∧ defectAmplitude 8 5 = 0) ∧
    topOverlap 8 7 = 1 := by
  norm_num [topOverlap, defectAmplitude]

end Tect.R276
