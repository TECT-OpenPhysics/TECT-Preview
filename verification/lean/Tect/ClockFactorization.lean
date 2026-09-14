import Mathlib

/- Finite positive-table algebra only. No experimental truth, metric identity,
   clock readout, continuum or microscopic model is encoded here. -/
namespace TectClock

theorem common_factor_minor (ki kj na nb : ℝ) :
    (ki * na) * (kj * nb) = (ki * nb) * (kj * na) := by ring

theorem minor_constructs_entry (w wi wj w0 : ℝ) (h0 : w0 ≠ 0)
    (h : w * w0 = wi * wj) : w = wi * (wj / w0) := by
  apply (mul_right_cancel₀ h0)
  field_simp
  nlinarith [h]

theorem unit_ratio_iff_minor (a b c d : ℝ) (hb : b ≠ 0) (hc : c ≠ 0) :
    a * d / (b * c) = 1 ↔ a * d = b * c := by
  rw [div_eq_one_iff_eq (mul_ne_zero hb hc)]

theorem normalization_freedom (k n scale : ℝ) (hs : scale ≠ 0) :
    (scale * k) * (n / scale) = k * n := by
  field_simp

theorem arbitrary_environment_same_observation (k n : ℝ) :
    (fun universal_multiplier : ℝ => k * universal_multiplier) n = k * n := by
  rfl

end TectClock
