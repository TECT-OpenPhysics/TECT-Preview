import Mathlib

namespace Tect.R210

/-!
  Scalar cross-check for the conditional weighted-recurrence bridge.  The
  graph recurrence and degree bookkeeping remain in the Python dual lanes.
-/

theorem weighted_split_factor (C J z e delta : ℝ) :
    (1 + C * delta) + J * z * e * delta = 1 + (C + J * z * e) * delta := by
  ring

theorem pointwise_weight {w l : ℝ} (hw : 0 < w) :
    l ≤ (w * l) / w := by
  have hne : w ≠ 0 := ne_of_gt hw
  field_simp [hne]
  exact le_rfl

theorem recurrence_identity (a b t : ℝ) :
    (1 + a * t) * (1 + b * t) = 1 + (a + b) * t + a * b * t ^ 2 := by
  ring

end Tect.R210
