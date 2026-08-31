import Mathlib

namespace Tect.R467

theorem dimension_split_identity
    (active normal ambient : ℕ) (h : active + normal = ambient) :
    active + normal = ambient := by
  exact h

theorem chart_volume_positive
    (active normal : ℕ) (active_side normal_side : ℚ)
    (hactive : 0 < active_side) (hnormal : 0 < normal_side) :
    0 < active_side ^ active * normal_side ^ normal := by
  positivity

theorem jacobian_chart_volume_positive
    (active normal : ℕ) (jacobian active_side normal_side : ℚ)
    (hjacobian : 0 < jacobian) (hactive : 0 < active_side)
    (hnormal : 0 < normal_side) :
    0 < jacobian * (active_side ^ active * normal_side ^ normal) := by
  positivity

theorem compensated_mass_ratio_positive
    (jacobian chart_volume partition_upper : ℚ)
    (hjacobian : 0 < jacobian) (hvolume : 0 < chart_volume)
    (hpartition : 0 < partition_upper) :
    0 < jacobian * chart_volume / partition_upper := by
  exact div_pos (mul_pos hjacobian hvolume) hpartition

theorem log_budget_decomposition
    (log_jacobian log_chart_volume beta ceiling log_partition : ℚ) :
    (log_jacobian + log_chart_volume - beta * ceiling - log_partition) =
      (log_jacobian + log_chart_volume) - beta * ceiling - log_partition := by
  ring

end Tect.R467
