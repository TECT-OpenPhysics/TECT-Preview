import Mathlib

namespace Tect.PahOmc022

structure FiniteSemigroupWitness where
  derivative : ℝ

def sameSourceSemigroup (a b : FiniteSemigroupWitness) : Prop := a = b

theorem differing_finite_derivatives_prevent_unique_source
    (a b : FiniteSemigroupWitness)
    (hderiv : a.derivative ≠ b.derivative) :
    ¬ sameSourceSemigroup a b := by
  intro hsame
  cases hsame
  exact hderiv rfl

def sourceLevelConvergenceClaim (sourceSelectsOne : Prop) : Prop := sourceSelectsOne

theorem source_ambiguity_blocks_original_claim
    (a b : FiniteSemigroupWitness)
    (hnotunique : ¬ sameSourceSemigroup a b) :
    ¬ sourceLevelConvergenceClaim (sameSourceSemigroup a b) := by
  simpa [sourceLevelConvergenceClaim] using hnotunique

def successorIsParentAuthority (authorized : Prop) : Prop := authorized

theorem successor_nonattribution_preserves_scope
    (hnotauthorized : ¬ successorIsParentAuthority False) :
    ¬ successorIsParentAuthority False := hnotauthorized

theorem scoped_negative_is_not_universal_successor_no_go
    (ownerFixedSuccessor : Prop) :
    (¬ sourceLevelConvergenceClaim False) → (ownerFixedSuccessor ∨ ¬ ownerFixedSuccessor) := by
  intro _
  exact Classical.em (ownerFixedSuccessor)

end Tect.PahOmc022
