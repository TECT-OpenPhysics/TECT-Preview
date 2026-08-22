import Mathlib
import Tect.R183
import Tect.R184
import Tect.R191

namespace Tect.R192

/-!
  R-192 is the bounded T-058 integration trial.  The finite algebraic
  prerequisites are imported from R-183, R-184, and R-191.  The production
  owner is represented by an ordered slot ledger; a `false` slot is a
  documented missing map, not silently treated as zero.
 -/

inductive OwnerSlot
  | heatRootIncidence
  | covarianceBases
  | complement
  | historicalLow
  | forest
  | returnedMean
  | source
  | sextic
  deriving DecidableEq, Repr

def slotOrder : List OwnerSlot :=
  [.heatRootIncidence, .covarianceBases, .complement, .historicalLow,
   .forest, .returnedMean, .source, .sextic]

def productionMapped : OwnerSlot → Bool
  | .heatRootIncidence => false
  | .covarianceBases => true
  | .complement => false
  | .historicalLow => false
  | .forest => false
  | .returnedMean => false
  | .source => false
  | .sextic => false

def firstMissingFrom : List OwnerSlot → Option OwnerSlot
  | [] => none
  | slot :: rest => if productionMapped slot then firstMissingFrom rest else some slot

def firstMissing : Option OwnerSlot := firstMissingFrom slotOrder

def complete : Bool := slotOrder.all productionMapped

theorem first_missing_is_heat_root :
    firstMissing = some OwnerSlot.heatRootIncidence := by
  rfl

theorem production_ledger_incomplete : complete = false := by
  rfl

theorem reserve_threshold_fixture (x y : Rat) :
    0 ≤ Tect.R183.qform (8 : Rat) (16 - 8) (16 - 8) x y := by
  exact Tect.R183.isotropic_nonneg 8 16 x y (by norm_num) (by norm_num)

theorem reserve_below_threshold_fixture :
    Tect.R183.qform (8 : Rat) (15 - 8) (15 - 8) 1 (-1) < 0 := by
  exact Tect.R183.isotropic_failure_below 8 15 (by norm_num)

theorem temporal_douglas_fixture :
    ((3 : Rat) * 5 + 4 * (-2)) ^ 2 + ((3 : Rat) * (-2) - 4 * 5) ^ 2 =
      ((3 : Rat) ^ 2 + 4 ^ 2) * (5 ^ 2 + (-2 : Rat) ^ 2) := by
  exact Tect.R184.fixture_identity

theorem temporal_douglas_gap_fixture :
    ((3 : Rat) ^ 2 + 4 ^ 2) * (5 ^ 2 + (-2 : Rat) ^ 2) -
      ((3 : Rat) * 5 + 4 * (-2)) ^ 2 = 26 ^ 2 := by
  exact Tect.R184.fixture_gap

theorem endpoint_telescope_fixture (q1 q2 h r1 r2 f1 f2 : Rat) :
    Tect.R191.owner q1 q2 (Tect.R191.stage3A h r1 r2 f1)
        (Tect.R191.stage3B h r1 r2 f2) -
        Tect.R191.owner q1 q2 (Tect.R191.stage0A h) (Tect.R191.stage0B h) =
      (Tect.R191.owner q1 q2 (Tect.R191.stage1A h r1)
          (Tect.R191.stage1B h r1) -
        Tect.R191.owner q1 q2 (Tect.R191.stage0A h) (Tect.R191.stage0B h)) +
      (Tect.R191.owner q1 q2 (Tect.R191.stage2A h r1 r2)
          (Tect.R191.stage2B h r1 r2) -
        Tect.R191.owner q1 q2 (Tect.R191.stage1A h r1)
          (Tect.R191.stage1B h r1)) +
      (Tect.R191.owner q1 q2 (Tect.R191.stage3A h r1 r2 f1)
          (Tect.R191.stage3B h r1 r2 f2) -
        Tect.R191.owner q1 q2 (Tect.R191.stage2A h r1 r2)
          (Tect.R191.stage2B h r1 r2)) := by
  exact Tect.R191.incidence_telescope q1 q2 h r1 r2 f1 f2

end Tect.R192
