import Mathlib

/-!
Finite algebra for PAH-OMC-020 R-549.

The scalar declarations encode the weighted-incidence factorization.  The
primary replay checks the corresponding non-commuting finite matrices; this
file does not construct a PAH comparison map or a source-owned estimate.
-/

namespace Tect.PahOmc020Generator

def sourceGen (bs ws : ℚ) : ℚ := bs * ws * bs

def targetGen (bt wt : ℚ) : ℚ := bt * wt * bt

def gradientDefect (bt u c bs : ℚ) : ℚ := bt * u - c * bs

def divergenceDefect (bt wt c u bs ws : ℚ) : ℚ := bt * wt * c - u * bs * ws

def residual (bt wt u bs ws : ℚ) : ℚ := targetGen bt wt * u - u * sourceGen bs ws

def decomposed (bt wt c u bs ws : ℚ) : ℚ :=
  divergenceDefect bt wt c u bs ws * bs +
    bt * wt * gradientDefect bt u c bs

theorem factorization_identity (bt wt c u bs ws : ℚ) :
    residual bt wt u bs ws = decomposed bt wt c u bs ws := by
  dsimp [residual, decomposed, divergenceDefect, gradientDefect, targetGen, sourceGen]
  ring

theorem factorization_fixture :
    residual 2 3 1 2 3 = decomposed 2 3 1 2 2 3 := by
  norm_num [residual, decomposed, divergenceDefect, gradientDefect, targetGen, sourceGen]

theorem divergence_fixture_is_nonzero :
    divergenceDefect 2 3 1 2 3 2 = -6 := by
  norm_num [divergenceDefect]

theorem gradient_fixture_is_nonzero :
    gradientDefect 2 1 3 2 = -4 := by
  norm_num [gradientDefect]

theorem omitted_term_can_change_residual :
    residual 3 4 2 1 2 = 68 ∧
      decomposed 3 4 1 2 1 2 = 68 ∧
      divergenceDefect 3 4 1 2 1 2 * 1 ≠ 0 := by
  norm_num [residual, decomposed, divergenceDefect, gradientDefect, targetGen, sourceGen]

def ownerPacketComplete (comparison rootTransfer gradientBound divergenceBound core temporal : Bool) : Bool :=
  comparison && rootTransfer && gradientBound && divergenceBound && core && temporal

theorem missing_owner_field_blocks (rootTransfer gradientBound divergenceBound core temporal : Bool) :
    ownerPacketComplete false rootTransfer gradientBound divergenceBound core temporal = false := by
  simp [ownerPacketComplete]

theorem owner_packet_requires_all_fields
    (comparison rootTransfer gradientBound divergenceBound core temporal : Bool)
    (h : ownerPacketComplete comparison rootTransfer gradientBound divergenceBound core temporal = true) :
    comparison = true ∧ rootTransfer = true ∧ gradientBound = true ∧
      divergenceBound = true ∧ core = true ∧ temporal = true := by
  simp only [ownerPacketComplete, Bool.and_eq_true] at h
  rcases h with ⟨⟨⟨⟨⟨hc, hr⟩, hg⟩, hd⟩, hcore⟩, ht⟩
  exact ⟨hc, hr, hg, hd, hcore, ht⟩

end Tect.PahOmc020Generator
