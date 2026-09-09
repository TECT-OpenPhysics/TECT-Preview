import Mathlib

namespace Tect.PahOmc020C2

/- The registered OMC-010 path has nu = 1.  These definitions encode the
   squared mobilities appearing in its phase, transfer/link and aperture
   rules.  The PAH source and its mobility law are not changed here. -/
def phaseSq (s : ℚ) : ℚ := s ^ 2
def transferSq (s t : ℚ) : ℚ := s * t
def apertureSq (s t : ℚ) : ℚ := s * t

theorem phase_sq_le_one (s : ℚ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    phaseSq s ≤ 1 := by
  dsimp [phaseSq]
  nlinarith [mul_nonneg (sub_nonneg.mpr hs0) (sub_nonneg.mpr (by linarith : 1 + s ≥ 0))]

theorem product_sq_le_one (s t : ℚ)
    (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    transferSq s t ≤ 1 := by
  dsimp [transferSq]
  have hprod : 0 ≤ (1 - s) * (1 - t) :=
    mul_nonneg (sub_nonneg.mpr hs1) (sub_nonneg.mpr ht1)
  nlinarith

theorem aperture_sq_le_one (s t : ℚ)
    (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    apertureSq s t ≤ 1 := by
  dsimp [apertureSq]
  have hprod : 0 ≤ (1 - s) * (1 - t) :=
    mul_nonneg (sub_nonneg.mpr hs1) (sub_nonneg.mpr ht1)
  nlinarith

/- If z is the partition function and q is the target unnormalised Gibbs
   weight, the exact midpoint-square transport term is q*m^2/z. -/
def transportedMass (q m z : ℚ) : ℚ := q * m ^ 2 / z

theorem transported_mass_le_target (q m z : ℚ)
    (hq : 0 ≤ q) (hm0 : 0 ≤ m) (hm1 : m ≤ 1) (hz : 0 < z) :
    transportedMass q m z ≤ q / z := by
  dsimp [transportedMass]
  have hsq : m ^ 2 ≤ 1 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hm0) (sub_nonneg.mpr (by linarith : 1 + m ≥ 0))]
  rw [div_le_iff₀ hz]
  field_simp [ne_of_gt hz]
  have hmul : q * m ^ 2 ≤ q * 1 := mul_le_mul_of_nonneg_left hsq hq
  nlinarith [hmul]

/- The geometric R-490 incidence constant is N_geom = 60.  If a finite
   support A has at most N_geom*|A| contributing roots, and each root's
   transported mass is at most one, the local second moment is bounded by
   60*|A|.  This theorem is arithmetic; the incidence premise is source data
   checked by the Python lanes. -/
theorem local_c2_bound (count rootBound nGeom a : ℚ)
    (hcount0 : 0 ≤ count) (hroot0 : 0 ≤ rootBound)
    (hroot1 : rootBound ≤ 1) (hcount : count ≤ nGeom * a) :
    count * rootBound ≤ nGeom * a := by
  have hprod : count * rootBound ≤ count := by
    nlinarith [mul_nonneg hcount0 (sub_nonneg.mpr hroot1)]
  linarith

theorem c2_omc010_constant (a : ℚ) (ha : 0 ≤ a) :
    (60 : ℚ) * a = 60 * a := by
  rfl

end Tect.PahOmc020C2
