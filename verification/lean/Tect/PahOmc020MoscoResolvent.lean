import Mathlib

/-!
Finite rational obligations for the PAH-OMC-020 Mosco-resolvent contract.

The declarations verify the scalar variational minimizer and fail-closed
owner-field logic only.  They do not import a convergence theorem or build a
PAH process.
-/

namespace Tect.PahOmc020MoscoResolvent

def objective (k lambda f u : Rat) : Rat :=
  k * u ^ 2 + lambda * (u - f) ^ 2

def minimizer (k lambda f : Rat) : Rat :=
  lambda * f / (k + lambda)

theorem minimizer_le (k lambda f u : Rat) (hk : 0 ≤ k) (hl : 0 < lambda) :
    objective k lambda f (minimizer k lambda f) ≤ objective k lambda f u := by
  have hp : 0 < k + lambda := by linarith
  have hsq : 0 ≤ (k + lambda) * (u - minimizer k lambda f) ^ 2 := by positivity
  have hid : objective k lambda f u - objective k lambda f (minimizer k lambda f) =
      (k + lambda) * (u - minimizer k lambda f) ^ 2 := by
    dsimp [objective, minimizer]
    field_simp
    ring
  linarith

theorem minimizer_unique (k lambda f u : Rat) (hk : 0 ≤ k) (hl : 0 < lambda)
    (h_eq : objective k lambda f u = objective k lambda f (minimizer k lambda f)) :
    u = minimizer k lambda f := by
  have hp : 0 < k + lambda := by linarith
  have hid : objective k lambda f u - objective k lambda f (minimizer k lambda f) =
      (k + lambda) * (u - minimizer k lambda f) ^ 2 := by
    dsimp [objective, minimizer]
    field_simp
    ring
  have hsquare : (u - minimizer k lambda f) ^ 2 = 0 := by
    nlinarith [hid, h_eq]
  nlinarith [hsquare]

theorem oracle_target_minimizer :
    minimizer 2 1 3 = 1 := by
  norm_num [minimizer]

theorem oracle_sequence_error_decreases :
    |minimizer 3 1 3 - minimizer 2 1 3| >
      |minimizer (5 / 2) 1 3 - minimizer 2 1 3| ∧
    |minimizer (5 / 2) 1 3 - minimizer 2 1 3| >
      |minimizer (9 / 4) 1 3 - minimizer 2 1 3| := by
  norm_num [minimizer]

def ownerPacketComplete (common liminf recovery data target norm semigroup : Bool) : Bool :=
  common && liminf && recovery && data && target && norm && semigroup

theorem missing_liminf_blocks (common recovery data target norm semigroup : Bool) :
    ownerPacketComplete common false recovery data target norm semigroup = false := by
  simp [ownerPacketComplete]

theorem owner_packet_requires_all_fields (common liminf recovery data target norm semigroup : Bool)
    (h : ownerPacketComplete common liminf recovery data target norm semigroup = true) :
    common = true ∧ liminf = true ∧ recovery = true ∧ data = true ∧ target = true ∧ norm = true ∧ semigroup = true := by
  simp only [ownerPacketComplete, Bool.and_eq_true] at h
  rcases h with ⟨⟨⟨⟨⟨⟨hc, hl⟩, hr⟩, hd⟩, ht⟩, hn⟩, hs⟩
  exact ⟨hc, hl, hr, hd, ht, hn, hs⟩

end Tect.PahOmc020MoscoResolvent
