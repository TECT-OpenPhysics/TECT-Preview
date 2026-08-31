import Mathlib

namespace Tect.R470

def segmentSlot (i : Nat) : Nat := i + 2

theorem segment_count (n : Nat) : (List.range n).length = n := by
  simp

theorem header_slot_at_least_two (i : Nat) : 2 ≤ segmentSlot i := by
  unfold segmentSlot
  omega

theorem header_slot_injective {i j : Nat}
    (h : segmentSlot i = segmentSlot j) : i = j := by
  unfold segmentSlot at h
  omega

theorem empty_drm_has_no_segments : List.range 0 = [] := by
  simp

theorem eight_segment_fixture : (List.range 8).length = 8 := by
  decide

end Tect.R470
