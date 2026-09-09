import Mathlib

/-!
Minimal dependency ledger for PAH-OMC-020.

These declarations formalize only the logical separation between the
conditional ordered-epsilon bridge, the restricted radial input, and the
full-domain owner obligations.  They do not construct any PAH owner packet or
prove a semigroup, infinite-volume, or physical result.
-/

namespace Tect.PahOmc020MinimalDependency

def FullReady (rootOwner commonMap fixedJ anchoredD : Prop) : Prop :=
  rootOwner ∧ commonMap ∧ fixedJ ∧ anchoredD

def RadialReady (fixedJ anchoredD : Prop) : Prop := fixedJ ∧ anchoredD

theorem full_ready_of_all_fields
    (rootOwner commonMap fixedJ anchoredD : Prop)
    (hroot : rootOwner) (hcommon : commonMap)
    (hfixed : fixedJ) (hanchored : anchoredD) :
    FullReady rootOwner commonMap fixedJ anchoredD := by
  exact ⟨hroot, hcommon, hfixed, hanchored⟩

theorem open_root_blocks_full
    (commonMap fixedJ anchoredD : Prop)
    (hnot : ¬ (commonMap ∧ fixedJ ∧ anchoredD)) :
    ¬ FullReady False commonMap fixedJ anchoredD := by
  intro h
  exact hnot ⟨h.2.1, h.2.2.1, h.2.2.2⟩

theorem radial_support_is_not_full_without_owner
    (fixedJ anchoredD : Prop) :
    RadialReady fixedJ anchoredD →
      ¬ FullReady False False fixedJ anchoredD := by
  intro _ hfull
  exact hfull.1

theorem conditional_bridge_needs_both
    (fixedJ anchoredD : Prop) :
    FullReady True True fixedJ anchoredD → RadialReady fixedJ anchoredD := by
  intro h
  exact ⟨h.2.2.1, h.2.2.2⟩

end Tect.PahOmc020MinimalDependency
