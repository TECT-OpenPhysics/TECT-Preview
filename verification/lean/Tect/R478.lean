import Mathlib

namespace Tect.R478

theorem gauge_covariant_edge
    {R : Type} [CommRing R]
    (gW gV gVInv link psiV psiW : R)
    (hInverse : gVInv * gV = 1) :
    gW * psiW - (gW * link * gVInv) * (gV * psiV) =
      gW * (psiW - link * psiV) := by
  calc
    gW * psiW - (gW * link * gVInv) * (gV * psiV) =
        gW * psiW - gW * link * (gVInv * gV) * psiV := by ring
    _ = gW * psiW - gW * link * psiV := by rw [hInverse]; ring
    _ = gW * (psiW - link * psiV) := by ring

theorem forward_gibbs_midpoint (beta energyX energyY : ℝ) :
    -beta * energyX - beta * (energyY - energyX) / 2 =
      -beta * (energyX + energyY) / 2 := by
  ring

theorem reverse_gibbs_midpoint (beta energyX energyY : ℝ) :
    -beta * energyY - beta * (energyX - energyY) / 2 =
      -beta * (energyX + energyY) / 2 := by
  ring

theorem detailed_balance_exponents (beta energyX energyY : ℝ) :
    -beta * energyX - beta * (energyY - energyX) / 2 =
      -beta * energyY - beta * (energyX - energyY) / 2 := by
  rw [forward_gibbs_midpoint, reverse_gibbs_midpoint]

theorem commuting_idempotent_product
    {X : Type}
    (pAut pGauge : X → X)
    (hAut : ∀ x, pAut (pAut x) = pAut x)
    (hGauge : ∀ x, pGauge (pGauge x) = pGauge x)
    (hCommute : ∀ x, pGauge (pAut x) = pAut (pGauge x))
    (x : X) :
    pAut (pGauge (pAut (pGauge x))) = pAut (pGauge x) := by
  calc
    pAut (pGauge (pAut (pGauge x))) =
        pAut (pAut (pGauge (pGauge x))) := by rw [hCommute]
    _ = pAut (pAut (pGauge x)) := by rw [hGauge]
    _ = pAut (pGauge x) := by rw [hAut]

theorem directed_root_half_factor
    (piX piY rateXY rateYX deltaF deltaG : ℝ)
    (hBalance : piX * rateXY = piY * rateYX) :
    (piX * rateXY * deltaF * deltaG +
        piY * rateYX * (-deltaF) * (-deltaG)) / 2 =
      piX * rateXY * deltaF * deltaG := by
  calc
    (piX * rateXY * deltaF * deltaG +
        piY * rateYX * (-deltaF) * (-deltaG)) / 2 =
        (piX * rateXY * deltaF * deltaG +
          (piY * rateYX) * deltaF * deltaG) / 2 := by ring
    _ = (piX * rateXY * deltaF * deltaG +
          (piX * rateXY) * deltaF * deltaG) / 2 := by rw [← hBalance]
    _ = piX * rateXY * deltaF * deltaG := by ring

def conditionVector : List Bool := [true, true, false, false, false]

theorem condition_vector_not_all_pass :
    conditionVector.all id = false := by
  decide

end Tect.R478
