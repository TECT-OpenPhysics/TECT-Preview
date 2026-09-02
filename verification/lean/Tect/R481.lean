import Mathlib

namespace Tect.R481

theorem edge_fibre_difference
    (kappa retained delta hidden₁ hidden₂ : ℝ) :
    kappa * (((retained + delta - hidden₁) ^ 2 -
        (retained - hidden₁) ^ 2) / 2) -
      kappa * (((retained + delta - hidden₂) ^ 2 -
        (retained - hidden₂) ^ 2) / 2) =
      -kappa * delta * (hidden₁ - hidden₂) := by
  ring

theorem transported_log_rate_factor
    (beta kappa retained delta hidden₁ hidden₂ : ℝ) :
    -beta *
        (kappa * (((retained + delta - hidden₁) ^ 2 -
          (retained - hidden₁) ^ 2) / 2) -
          kappa * (((retained + delta - hidden₂) ^ 2 -
            (retained - hidden₂) ^ 2) / 2)) / 2 =
      beta * kappa * delta * (hidden₁ - hidden₂) / 2 := by
  ring

theorem positive_scalar_transport_log_defect_nonzero
    (beta kappa delta hidden₁ hidden₂ : ℝ)
    (hbeta : 0 < beta)
    (hkappa : 0 < kappa)
    (hdelta : 0 < delta)
    (hdistinct : hidden₁ ≠ hidden₂) :
    beta * kappa * delta * (hidden₁ - hidden₂) / 2 ≠ 0 := by
  have hβ : beta ≠ 0 := ne_of_gt hbeta
  have hκ : kappa ≠ 0 := ne_of_gt hkappa
  have hδ : delta ≠ 0 := ne_of_gt hdelta
  have hz : hidden₁ - hidden₂ ≠ 0 := sub_ne_zero.mpr hdistinct
  have hprod : beta * kappa * delta * (hidden₁ - hidden₂) ≠ 0 :=
    mul_ne_zero (mul_ne_zero (mul_ne_zero hβ hκ) hδ) hz
  exact div_ne_zero hprod (by norm_num)

end Tect.R481
