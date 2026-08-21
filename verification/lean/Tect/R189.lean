import Mathlib

namespace Tect.R189

/-!
  A production-cylinder lower-bound lemma used by the R-189 diagnostic.
  The actual A1 two-mode e3 energy is bounded below by this scalar cubic
  after writing `t = a^2`, `u = b^2`, and `s = t + u`.
-/

def lowerPoly (s : Rat) : Rat :=
  s / 10 - (387 / 6400) * s ^ 2 + (27 / 1280) * s ^ 3

theorem lowerPoly_factor (s : Rat) :
    lowerPoly s = s * (135 * s ^ 2 - 387 * s + 640) / 6400 := by
  norm_num [lowerPoly]
  ring

theorem lowerPoly_positive {s : Rat} (hs : 0 < s) : 0 < lowerPoly s := by
  have hsq : 0 ≤ (270 * s - 387) ^ 2 := sq_nonneg _
  have hquad : 0 < 135 * s ^ 2 - 387 * s + 640 := by
    nlinarith
  have hprod : 0 < s * (135 * s ^ 2 - 387 * s + 640) :=
    mul_pos hs hquad
  rw [lowerPoly_factor]
  positivity

theorem two_mode_energy_lower_bound {t u : Rat}
    (ht : 0 ≤ t) (hu : 0 ≤ u)
    : 0 ≤ lowerPoly (t + u) := by
  by_cases hs : 0 < t + u
  · exact le_of_lt (lowerPoly_positive hs)
  · have hz : t + u = 0 := by linarith
    simp [hz, lowerPoly]

def cylinderPoly (q1 q2 t u : Rat) : Rat :=
  q1 * t + q2 * u - (129 / 3200) * (t ^ 2 + 4 * t * u + u ^ 2) +
    (27 / 320) * (t ^ 3 + (21 / 2) * t ^ 2 * u + 9 * t * u ^ 2 + u ^ 3)

theorem cylinderPoly_nonnegative {q1 q2 t u : Rat}
    (hq1 : 1 / 10 ≤ q1) (hq2 : 1 / 10 ≤ q2)
    (ht : 0 ≤ t) (hu : 0 ≤ u) :
    0 ≤ cylinderPoly q1 q2 t u := by
  let s : Rat := t + u
  have hs : 0 ≤ s := by
    dsimp [s]
    linarith
  have hq : (1 / 10) * s ≤ q1 * t + q2 * u := by
    dsimp [s]
    nlinarith [mul_nonneg (sub_nonneg.mpr hq1) ht,
      mul_nonneg (sub_nonneg.mpr hq2) hu]
  have hqform : 0 ≤ 135 * s ^ 2 - 387 * s + 640 := by
    have hsq : 0 ≤ (270 * s - 387) ^ 2 := sq_nonneg _
    nlinarith
  have hlow : 0 ≤ lowerPoly s := by
    rw [lowerPoly_factor]
    have hprod : 0 ≤ s * (135 * s ^ 2 - 387 * s + 640) :=
      mul_nonneg hs hqform
    nlinarith
  have hquartic : t ^ 2 + 4 * t * u + u ^ 2 ≤ (3 / 2) * s ^ 2 := by
    dsimp [s]
    nlinarith [sq_nonneg (t - u)]
  have hsextic :
      (1 / 4) * s ^ 3 ≤ t ^ 3 + (21 / 2) * t ^ 2 * u +
        9 * t * u ^ 2 + u ^ 3 := by
    dsimp [s]
    have ht2u : 0 ≤ t ^ 2 * u := mul_nonneg (sq_nonneg t) hu
    have htu2 : 0 ≤ t * u ^ 2 := mul_nonneg ht (sq_nonneg u)
    nlinarith [ht2u, htu2]
  dsimp [cylinderPoly]
  dsimp [s] at hq hlow hquartic hsextic
  nlinarith

end Tect.R189
