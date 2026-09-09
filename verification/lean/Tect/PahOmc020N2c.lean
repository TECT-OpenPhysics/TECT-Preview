import Mathlib

namespace Tect.PahOmc020N2c

/- These declarations formalize only the algebraic bridge that is still
   missing from PAH-OMC-020: a pathwise boundary-energy input B must be paired
   with the static C2 coefficient.  They do not construct a process, prove
   non-explosion, or identify a minimal form. -/

def n4Budget (T C2 B eta : ℚ) : ℚ := T * eta

theorem n4_squared_budget (T C2 B eta : ℚ)
    (hT : 0 ≤ T) (hC2 : 0 ≤ C2) (hB : 0 ≤ B)
    (hpoint : eta ^ 2 ≤ C2 * B) :
    (n4Budget T C2 B eta) ^ 2 ≤ T ^ 2 * (C2 * B) := by
  have hmul := mul_le_mul_of_nonneg_left hpoint (sq_nonneg T)
  unfold n4Budget
  calc
    (T * eta) ^ 2 = T ^ 2 * eta ^ 2 := by ring
    _ ≤ T ^ 2 * (C2 * B) := hmul

theorem n4_zero_when_pathwise_budget_zero (T C2 B eta : ℚ)
    (hpoint : eta ^ 2 ≤ C2 * B) (hBzero : B = 0) :
    n4Budget T C2 B eta = 0 := by
  have hzero : eta ^ 2 ≤ 0 := by simpa [hBzero] using hpoint
  have heta : eta = 0 := by nlinarith [sq_nonneg eta]
  simp [n4Budget, heta]

theorem static_c2_is_only_a_coefficient (T C2 B eta : ℚ)
    (hT : 0 ≤ T) (hC2 : 0 ≤ C2) (hB : 0 ≤ B)
    (hpoint : eta ^ 2 ≤ C2 * B) :
    (n4Budget T C2 B eta) ^ 2 ≤ T ^ 2 * C2 * B := by
  have h := n4_squared_budget T C2 B eta hT hC2 hB hpoint
  nlinarith

end Tect.PahOmc020N2c
