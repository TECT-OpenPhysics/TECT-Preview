import Mathlib

namespace Tect.R448

structure StaticData where
  h1 : ℚ
  h2 : ℚ
  c1 : ℚ
  c2 : ℚ

structure Dynamics where
  static : StaticData
  first_factor : ℚ
  second_factor : ℚ

def StaticEquivalent (a b : Dynamics) : Prop := a.static = b.static

theorem static_equiv_refl (a : Dynamics) : StaticEquivalent a a := by
  rfl

theorem static_equiv_symm {a b : Dynamics} :
    StaticEquivalent a b → StaticEquivalent b a := by
  intro h
  exact h.symm

theorem static_equiv_trans {a b c : Dynamics} :
    StaticEquivalent a b → StaticEquivalent b c → StaticEquivalent a c := by
  intro hab hbc
  exact hab.trans hbc

def staticSetoid : Setoid Dynamics where
  r := StaticEquivalent
  iseqv := ⟨static_equiv_refl, static_equiv_symm, static_equiv_trans⟩

def pinned : StaticData :=
  { h1 := 1, h2 := 2, c1 := 1, c2 := 1 / 2 }

def mapA : Dynamics :=
  { static := pinned, first_factor := 1 / 2, second_factor := 1 / 4 }

def mapB : Dynamics :=
  { static := pinned, first_factor := 1 / 4, second_factor := 1 / 2 }

def dynamicObservable (d : Dynamics) (x : ℚ × ℚ) : ℚ × ℚ :=
  (d.first_factor * x.1, d.second_factor * x.2)

theorem static_signature_inverse :
    pinned.h1 * pinned.c1 = 1 ∧ pinned.h2 * pinned.c2 = 1 := by
  norm_num [pinned]

theorem maps_static_equivalent : StaticEquivalent mapA mapB := by
  rfl

theorem maps_distinct : mapA ≠ mapB := by
  intro h
  have factor_equality : mapA.first_factor = mapB.first_factor :=
    congrArg Dynamics.first_factor h
  norm_num [mapA, mapB] at factor_equality

theorem probe_separates :
    dynamicObservable mapA (1, 0) ≠ dynamicObservable mapB (1, 0) := by
  norm_num [dynamicObservable, mapA, mapB]

theorem static_class_non_singleton :
    ∃ a b : Dynamics, StaticEquivalent a b ∧ a ≠ b := by
  exact ⟨mapA, mapB, maps_static_equivalent, maps_distinct⟩

end Tect.R448
