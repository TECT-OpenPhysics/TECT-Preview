import Mathlib

namespace Tect.R177

/-
  Finite two-root ledger for the A1 k,2k chart.  The theorem is deliberately
  structural: common heat is shared by the replicas, root 2 retains feedback
  from root 1, and only the future residual is replicated after root 2.  No
  production estimate is encoded here.
-/

variable {R : Type*} [Field R]

def midpoint (x y : R) : R := (x + y) / 2

def twoReplicaVariance (x y : R) : R :=
  ((x - midpoint x y) ^ 2 + (y - midpoint x y) ^ 2) / 2

theorem two_replica_variance {R : Type*} [Field R] [CharZero R] (x y : R) :
    twoReplicaVariance x y = (x - y) ^ 2 / 4 := by
  simp [twoReplicaVariance, midpoint]
  field_simp
  ring

def root1 (heat r1 : R) : R := heat + r1

def root2 (heat r1 r2 beta : R) : R :=
  heat + beta * root1 heat r1 + r2

def endpoint (heat r1 r2 future beta : R) : R :=
  root2 heat r1 r2 beta + future

theorem common_heat_cancels (heat r1 r2 future future' beta : R) :
    endpoint heat r1 r2 future beta - endpoint heat r1 r2 future' beta =
      future - future' := by
  simp [endpoint, root2, root1]

theorem root2_feedback_dependence (heat r1 r2 beta delta : R) :
    root2 heat (r1 + delta) r2 beta - root2 heat r1 r2 beta = beta * delta := by
  simp only [root2, root1]
  ring

theorem endpoint_feedback_dependence (heat r1 r2 future beta delta : R) :
    endpoint heat (r1 + delta) r2 future beta - endpoint heat r1 r2 future beta =
      beta * delta := by
  simp only [endpoint, root2, root1]
  ring

theorem independent_heat_does_not_cancel
    (heat heat' r1 r2 future beta : R) :
    endpoint heat r1 r2 future beta - endpoint heat' r1 r2 future beta =
      (1 + beta) * (heat - heat') := by
  simp only [endpoint, root2, root1]
  ring

inductive Owner
  | commonHeat
  | rootOne
  | rootTwo
  | futureResidual
  deriving DecidableEq, Repr

def incidence : List Owner :=
  [.commonHeat, .rootOne, .rootTwo, .futureResidual]

def ownerIndex : Owner -> Nat
  | .commonHeat => 0
  | .rootOne => 1
  | .rootTwo => 2
  | .futureResidual => 3

theorem incidence_is_two_root :
    incidence = [.commonHeat, .rootOne, .rootTwo, .futureResidual] := rfl

theorem root_two_after_root_one :
    ownerIndex .rootOne < ownerIndex .rootTwo := by
  decide

theorem future_after_root_two :
    ownerIndex .rootTwo < ownerIndex .futureResidual := by
  decide

end Tect.R177
