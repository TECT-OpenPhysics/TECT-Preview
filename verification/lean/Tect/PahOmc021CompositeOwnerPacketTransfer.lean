import Mathlib

namespace Tect.PahOmc021

inductive FieldStatus where
  | finitePresent
  | finitePresentNotSufficient
  | asymptoticMissing
  | sourceOwnerIneligible
  deriving DecidableEq

def required : FieldStatus → Prop
  | .finitePresent => True
  | .finitePresentNotSufficient => False
  | .asymptoticMissing => False
  | .sourceOwnerIneligible => False

def packetAdmitted (authority : FieldStatus) (root common n1 n2b n2c n2d j d verification : FieldStatus) : Prop :=
  required authority ∧ required root ∧ required common ∧ required n1 ∧ required n2b ∧ required n2c ∧
    required n2d ∧ required j ∧ required d ∧ required verification

theorem finite_fields_do_not_admit
    (authority root common n1 n2b n2c n2d j d verification : FieldStatus)
    (ha : authority = .sourceOwnerIneligible)
    (hn1 : n1 = .asymptoticMissing) :
    ¬ packetAdmitted authority root common n1 n2b n2c n2d j d verification := by
  intro h
  exact (by simp [packetAdmitted, required, ha, hn1] at h)

theorem status_only_asymptotic_fill_does_not_admit
    (root common verification : FieldStatus) :
    ¬ packetAdmitted .sourceOwnerIneligible root common .asymptoticMissing .asymptoticMissing
      .asymptoticMissing .asymptoticMissing .asymptoticMissing .asymptoticMissing verification := by
  intro h
  simp [packetAdmitted, required] at h

theorem finite_common_fields_are_not_ordered_fields :
    required .finitePresent ∧ ¬ required .finitePresentNotSufficient ∧ ¬ required .asymptoticMissing := by
  simp [required]

end Tect.PahOmc021
