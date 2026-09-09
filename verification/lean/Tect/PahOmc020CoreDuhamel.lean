import Mathlib

/-!
Finite rational obligations for the PAH-OMC-020 common-core Duhamel contract.

The declarations verify only the conditional norm budget and its monotonicity.
They do not construct a comparison map, a process, or a physical time model.
-/

namespace Tect.PahOmc020CoreDuhamel

def corrBound (normF initF initG residual normG : Rat) : Rat :=
  normF * (initG + residual) + initF * normG

theorem corr_bound_nonnegative (normF initF initG residual normG : Rat)
    (hF : 0 ≤ normF) (hIf : 0 ≤ initF) (hIg : 0 ≤ initG)
    (hR : 0 ≤ residual) (hG : 0 ≤ normG) :
    0 ≤ corrBound normF initF initG residual normG := by
  dsimp [corrBound]
  positivity

theorem duhamel_triangle (error component residual normF initF initG normG : Rat)
    (h_component : error ≤ component + initF * normG)
    (h_component_bound : component ≤ normF * (initG + residual)) :
    error ≤ corrBound normF initF initG residual normG := by
  dsimp [corrBound]
  linarith

theorem compact_time_epsilon (error eps normF initF initG residual normG : Rat)
    (h_error : error ≤ corrBound normF initF initG residual normG)
    (h_budget : corrBound normF initF initG residual normG ≤ eps) :
    error ≤ eps := by
  exact le_trans h_error h_budget

theorem corr_bound_monotone (normF normF' initF initF' initG initG' residual residual' normG normG' : Rat)
    (hF : 0 ≤ normF) (hIf : 0 ≤ initF) (hIg : 0 ≤ initG)
    (hR : 0 ≤ residual) (hG : 0 ≤ normG)
    (hF' : normF ≤ normF') (hIf' : initF ≤ initF')
    (hIg' : initG ≤ initG') (hR' : residual ≤ residual')
    (hG' : normG ≤ normG') :
    corrBound normF initF initG residual normG ≤
      corrBound normF' initF' initG' residual' normG' := by
  dsimp [corrBound]
  have hsum : initG + residual ≤ initG' + residual' := by linarith
  have hsum_nonneg : 0 ≤ initG + residual := by linarith
  have hprod : normF * (initG + residual) ≤ normF' * (initG' + residual') := by
    calc
      normF * (initG + residual) ≤ normF' * (initG + residual) := by
        exact mul_le_mul_of_nonneg_right hF' hsum_nonneg
      _ ≤ normF' * (initG' + residual') := by
        exact mul_le_mul_of_nonneg_left hsum (by linarith)
  have hprod2 : initF * normG ≤ initF' * normG' := by
    calc
      initF * normG ≤ initF' * normG := by
        exact mul_le_mul_of_nonneg_right hIf' hG
      _ ≤ initF' * normG' := by
        exact mul_le_mul_of_nonneg_left hG' (by linarith)
  linarith

theorem omitted_initial_defect_is_unsound :
    corrBound 0 (1 / 4) (1 / 8) (1 / 16) 2 = 1 / 2 ∧
      0 < corrBound 0 (1 / 4) (1 / 8) (1 / 16) 2 := by
  norm_num [corrBound]

theorem omitted_residual_is_unsound :
    corrBound 2 0 0 (1 / 8) 1 = 1 / 4 ∧
      0 < corrBound 2 0 0 (1 / 8) 1 := by
  norm_num [corrBound]

def ownerPacketComplete (common correlation initial residual uniform target : Bool) : Bool :=
  common && correlation && initial && residual && uniform && target

theorem missing_owner_field_blocks (correlation initial residual uniform target : Bool) :
    ownerPacketComplete false correlation initial residual uniform target = false := by
  simp [ownerPacketComplete]

theorem owner_packet_requires_all_fields (common correlation initial residual uniform target : Bool)
    (h : ownerPacketComplete common correlation initial residual uniform target = true) :
    common = true ∧ correlation = true ∧ initial = true ∧ residual = true ∧ uniform = true ∧ target = true := by
  simp only [ownerPacketComplete, Bool.and_eq_true] at h
  rcases h with ⟨⟨⟨⟨⟨hc, hcorr⟩, hi⟩, hr⟩, hu⟩, ht⟩
  exact ⟨hc, hcorr, hi, hr, hu, ht⟩

end Tect.PahOmc020CoreDuhamel
