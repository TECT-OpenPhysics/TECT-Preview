import Mathlib

namespace Tect.HYB0001

def potential (lambda gamma rho : Rat) : Rat :=
  lambda / 4 * rho ^ 2 + gamma / 6 * rho ^ 3

theorem potential_lower
    {a gamma rho : Rat} (ha : 0 < a) (hg : 0 < gamma) (hrho : 0 <= rho) :
    -(a ^ 3) / (12 * gamma ^ 2) <= potential (-a) gamma rho := by
  have hgamma : gamma ≠ 0 := ne_of_gt hg
  have hfactor :
      potential (-a) gamma rho + (a ^ 3) / (12 * gamma ^ 2) =
        gamma / 6 * (rho - a / gamma) ^ 2 * (rho + a / (2 * gamma)) := by
    unfold potential
    field_simp [hgamma]
    ring
  have hnonneg :
      0 <= gamma / 6 * (rho - a / gamma) ^ 2 * (rho + a / (2 * gamma)) := by
    have hleft : 0 <= gamma / 6 := by positivity
    have hmid : 0 <= (rho - a / gamma) ^ 2 := sq_nonneg _
    have hright : 0 <= rho + a / (2 * gamma) := by positivity
    exact mul_nonneg (mul_nonneg hleft hmid) hright
  have hsum : 0 <= potential (-a) gamma rho + (a ^ 3) / (12 * gamma ^ 2) := by
    rw [hfactor]
    exact hnonneg
  have hsub : 0 <= potential (-a) gamma rho - (-(a ^ 3) / (12 * gamma ^ 2)) := by
    convert hsum using 1 <;> ring
  exact sub_nonneg.mp hsub

theorem classii_form_nonnegative
    {aa bb cc u v : Rat} (haa : 0 < aa) (hdet : 0 <= aa * cc - bb ^ 2) :
    0 <= aa * u ^ 2 + 2 * bb * u * v + cc * v ^ 2 := by
  have hsq : 0 <= (aa * u + bb * v) ^ 2 := sq_nonneg _
  have hrest : 0 <= (aa * cc - bb ^ 2) * v ^ 2 :=
    mul_nonneg hdet (sq_nonneg v)
  have hden : 0 < aa := haa
  have hid :
      aa * u ^ 2 + 2 * bb * u * v + cc * v ^ 2 =
        ((aa * u + bb * v) ^ 2 + (aa * cc - bb ^ 2) * v ^ 2) / aa := by
    field_simp [ne_of_gt haa]
    ring
  rw [hid]
  exact div_nonneg (add_nonneg hsq hrest) (le_of_lt hden)

def gibbsResidual (beta fp fpp : Rat) : Rat :=
  (fpp - beta * fp ^ 2) + (1 / beta) * (-beta * fpp + beta ^ 2 * fp ^ 2)

theorem gibbs_residual_zero {beta fp fpp : Rat} (hbeta : beta ≠ 0) :
    gibbsResidual beta fp fpp = 0 := by
  unfold gibbsResidual
  field_simp [hbeta]
  ring

end Tect.HYB0001
