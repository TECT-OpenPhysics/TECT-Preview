import Mathlib

namespace Tect.R179

def ownerHalf (forest variance : Rat) : Rat := forest / 2 - variance / 4

theorem replica_owner_half (forest variance : Rat) :
    2 * ownerHalf forest variance = forest - variance / 2 := by
  dsimp [ownerHalf]
  ring

theorem omission_cost (forest variance : Rat) :
    ownerHalf forest variance + variance / 4 = forest / 2 := by
  dsimp [ownerHalf]
  ring

theorem constant_translation (s : Rat) :
    ownerHalf 0 (4 * s) = -s := by
  dsimp [ownerHalf]
  ring

theorem positive_variance_rebate {forest variance : Rat} (h : 0 <= variance) :
    ownerHalf forest variance <= forest / 2 := by
  dsimp [ownerHalf]
  linarith

theorem zero_variance_rebate (forest : Rat) :
    ownerHalf forest 0 = forest / 2 := by
  dsimp [ownerHalf]
  ring

end Tect.R179

