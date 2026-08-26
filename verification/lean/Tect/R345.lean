import Mathlib

namespace Tect.R345

theorem exponential_band_bound
    (beta emin emax ei ej : ℝ)
    (hbeta : 0 ≤ beta)
    (hlo_i : emin ≤ ei) (hhi_i : ei ≤ emax)
    (hlo_j : emin ≤ ej) (hhi_j : ej ≤ emax) :
    Real.exp (beta * (ei - ej) / 2) ≤
      Real.exp (beta * (emax - emin) / 2) := by
  apply Real.exp_le_exp.mpr
  nlinarith

theorem similarity_band_scalar
    (delta band : ℝ)
    (hdelta : 0 ≤ delta) (hband : 0 ≤ band) (hdom : delta ≤ band) :
    delta + delta ≤ 2 * band := by
  nlinarith

end Tect.R345
