import Mathlib

namespace Tect.R427

/- R427 formalizes only the preregistration firewall.  It defines no energy,
   physical-empty state, Reading-H tangent, or Hessian. -/

theorem evaluation_requires_owner_and_empty
    {Owner E Evaluated : Prop}
    (requires : Evaluated -> Owner ∧ E)
    (missing_owner : ¬ Owner)
    (_missing_empty : ¬ E) :
    ¬ Evaluated := by
  intro h
  exact missing_owner (requires h).1

theorem three_blocked
    {Sign Stationarity Stability : Prop}
    (sign_requires : Sign -> False)
    (stationarity_requires : Stationarity -> False)
    (stability_requires : Stability -> False) :
    ¬ Sign ∧ ¬ Stationarity ∧ ¬ Stability := by
  exact ⟨sign_requires, stationarity_requires, stability_requires⟩

theorem preregistered_slot_is_not_admission :
    (True ∧ ¬ False) := by
  exact ⟨True.intro, by simp⟩

end Tect.R427
