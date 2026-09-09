/-
  Finite fail-closed logic for the PAH-OMC-020 K/D term ledger.

  These declarations formalize only the admission predicate.  They do not
  construct a comparison map, a path process, an unbounded estimate, or a
  semigroup limit.
-/

namespace Tect.PahOmc020KD

def admitted (j state stabilization boundary common uniformK target dLimit : Bool) : Bool :=
  j && state && stabilization && boundary && common && uniformK && target && dLimit

def ownerAdmitted (ownerAuthorized conditional : Bool)
    (j state stabilization boundary common uniformK target dLimit : Bool) : Bool :=
  ownerAuthorized && (!conditional) && admitted j state stabilization boundary common uniformK target dLimit

theorem all_fields_admit :
    admitted true true true true true true true true = true := by
  decide

theorem missing_common_rejects :
    admitted true true true true false true true true = false := by
  decide

theorem missing_uniform_rejects :
    admitted true true true true true false true true = false := by
  decide

theorem missing_target_rejects :
    admitted true true true true true true false true = false := by
  decide

theorem missing_d_limit_rejects :
    admitted true true true true true true true false = false := by
  decide

theorem conditional_result_not_owner_admitted :
    ownerAdmitted true true true true true true true true true true = false := by
  decide

theorem unowned_result_not_admitted :
    ownerAdmitted false false true true true true true true true true = false := by
  decide

end Tect.PahOmc020KD
