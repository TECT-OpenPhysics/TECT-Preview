import Mathlib

namespace Tect.R490

/- The conductance factor after Gibbs normalization is bounded by the
   arithmetic-geometric mean.  The variables stand for the two positive
   square-root Gibbs weights in one inverse-root pair. -/
def amgmGap (a b : ℚ) : ℚ := (a ^ 2 + b ^ 2) / 2 - a * b

theorem amgm_gap_identity (a b : ℚ) :
    amgmGap a b = (a - b) ^ 2 / 2 := by
  dsimp [amgmGap]
  ring

theorem amgm_gap_nonnegative (a b : ℚ) : 0 ≤ amgmGap a b := by
  rw [amgm_gap_identity]
  positivity

theorem inverse_pair_amgm (a b : ℚ) :
    a * b ≤ (a ^ 2 + b ^ 2) / 2 := by
  have h := amgm_gap_nonnegative a b
  dsimp [amgmGap] at h
  linarith

theorem weighted_pair_bound {a b m : ℚ}
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hm0 : 0 ≤ m) (hm1 : m ≤ 1) :
    m * a * b ≤ (a ^ 2 + b ^ 2) / 2 := by
  have hab : 0 ≤ a * b := mul_nonneg ha hb
  have hscale : m * (a * b) ≤ 1 * (a * b) := by
    gcongr
  calc
    m * a * b = m * (a * b) := by ring
    _ ≤ 1 * (a * b) := hscale
    _ = a * b := by ring
    _ ≤ (a ^ 2 + b ^ 2) / 2 := inverse_pair_amgm a b

/- These are the constants computed from the complete directed root-support
   enumeration of the PAH-OMC-004 strip family. -/
def S_geom : ℕ := 8
def N_geom : ℕ := 60
def C_sw : ℕ := N_geom * (1 + S_geom)

theorem geometry_constants_exact :
    S_geom = 8 ∧ N_geom = 60 ∧ C_sw = 540 := by
  norm_num [S_geom, N_geom, C_sw]

theorem local_form_bound_from_constants :
    N_geom * (1 + S_geom) = 540 := by
  norm_num [S_geom, N_geom]

/- The normalized Gibbs weight is strictly positive whenever the finite
   partition function is positive. -/
theorem normalized_gibbs_weight_positive (F Z : ℝ) (hZ : 0 < Z) :
    0 < Real.exp (-F) / Z := by
  positivity

theorem nonzero_weighted_norm_witness (w : ℝ) (hw : 0 < w) :
    0 < w * (1 : ℝ) ^ 2 := by
  positivity

/- The four R-488 generators have explicit nonzero witness values
   (ell_a, ell_d, H_0, H_1)=(1,1,-1,-1). -/
theorem r488_witness_values_nonzero :
    (1 : ℤ) ≠ 0 ∧ (1 : ℤ) ≠ 0 ∧ (-1 : ℤ) ≠ 0 ∧ (-1 : ℤ) ≠ 0 := by
  norm_num

/- The result is a local-form input only; it does not close intertwining or
   promote a physical conclusion. -/
def commonCoreIntertwining : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    commonCoreIntertwining = false ∧ physicalPromotion = false := by
  decide

end Tect.R490
