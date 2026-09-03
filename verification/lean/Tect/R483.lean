import Mathlib

open scoped BigOperators

namespace Tect.R483

/- Exact rational values reproduced from the Q=0 PAH aperture/Wilson fixture. -/
def coarseDelta : ℚ := (1 : ℚ) / 8
def fineEvenDelta : ℚ := (1 : ℚ) / 4
def fineOddDelta : ℚ := -(55 : ℚ) / 36

theorem coarse_delta_exact : coarseDelta = (1 : ℚ) / 8 := by
  rfl

theorem fine_even_delta_exact : fineEvenDelta = (1 : ℚ) / 4 := by
  rfl

theorem fine_odd_delta_exact : fineOddDelta = -(55 : ℚ) / 36 := by
  rfl

theorem hidden_diagonal_defect_exact :
    fineEvenDelta - fineOddDelta = (16 : ℚ) / 9 := by
  norm_num [fineEvenDelta, fineOddDelta]

theorem hidden_diagonal_defect_nonzero :
    fineEvenDelta - fineOddDelta ≠ (0 : ℚ) := by
  norm_num [fineEvenDelta, fineOddDelta]

theorem incidence_edge_change :
    (5 : ℕ) - 4 = 1 := by
  norm_num

theorem incidence_face_change :
    (2 : ℕ) - 1 = 1 := by
  norm_num

theorem aperture_mobility_square :
    ((1 : ℚ) / 2) * 1 = (1 : ℚ) / 2 := by
  norm_num

theorem local_energy_envelope :
    ((1 : ℚ) / 8) + 5 * ((1 : ℚ) / 8) + 4 * 4 = (67 : ℚ) / 4 := by
  norm_num

theorem local_rate_exponent :
    ((1 : ℚ) * ((67 : ℚ) / 4)) / 2 = (67 : ℚ) / 8 := by
  norm_num

/- A split at level n touches columns n and n+1.  A cylinder whose
   interaction closure ends at m is therefore unaffected for n>m. -/
def localDefect (m n : ℕ) : ℚ := if n ≤ m then 1 else 0

theorem eventual_zero_local_defect {m n : ℕ} (h : m < n) :
    localDefect m n = (0 : ℚ) := by
  simp [localDefect, Nat.not_le.mpr h]

theorem tail_cumulative_zero {m N : ℕ} (d : ℕ → ℚ)
    (hzero : ∀ n, m < n → d n = 0) :
    Finset.sum (Finset.Ico (m + 1) (N + 1)) d = 0 := by
  apply Finset.sum_eq_zero
  intro n hn
  exact hzero n ((Finset.mem_Ico.mp hn).1)

def geometricPromotion : Bool := false
def physicalPromotion : Bool := false

theorem structural_firewall :
    geometricPromotion = false ∧ physicalPromotion = false := by
  decide

end Tect.R483
