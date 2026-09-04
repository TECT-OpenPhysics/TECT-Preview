import Mathlib

namespace Tect.R491

/- The new column can carry the fixed Q=1 quantum.  The declared neutral
   projection drops that column, so the retained charge is zero. -/
def fineCharge : ℕ := 1
def retainedCharge : ℕ := 0

theorem neutral_projection_loses_new_charge :
    fineCharge = 1 ∧ retainedCharge = 0 ∧ retainedCharge ≠ fineCharge := by
  norm_num [fineCharge, retainedCharge]

theorem neutral_projection_not_total_q_one :
    retainedCharge ≠ fineCharge := by
  norm_num [fineCharge, retainedCharge]

/- The support buffer is the preregistered N(f)=max(2,m_f+1). -/
def stabilizationStage (m_f : ℕ) : ℕ := max 2 (m_f + 1)

theorem stabilization_stage_exact (m_f : ℕ) :
    stabilizationStage m_f = max 2 (m_f + 1) := by
  rfl

theorem boundary_support_separated (m_f n : ℕ)
    (hN : stabilizationStage m_f ≤ n) :
    m_f < n := by
  have hsucc : m_f + 1 ≤ stabilizationStage m_f := by
    exact Nat.le_max_right 2 (m_f + 1)
  have hsucc_n : m_f + 1 ≤ n := le_trans hsucc hN
  exact lt_of_lt_of_le (Nat.lt_succ_self m_f) hsucc_n

/- The exact R-484 source witness is retained, not averaged away. -/
def r484BoundaryDefect : ℚ := 16 / 9

theorem r484_boundary_defect_exact :
    r484BoundaryDefect = (16 / 9 : ℚ) ∧ r484BoundaryDefect ≠ 0 := by
  norm_num [r484BoundaryDefect]

/- R-490 C_sw is a domination constant only; it is not encoded as an
   intertwining theorem. -/
def C_sw : ℕ := 540
def cswIntertwiningEvidence : Bool := false

theorem csw_is_domination_only :
    C_sw = 540 ∧ cswIntertwiningEvidence = false := by
  decide

def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    claimBearing = false ∧ physicalPromotion = false := by
  decide

end Tect.R491
