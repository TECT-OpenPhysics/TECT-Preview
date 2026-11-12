import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Tect.ExchangeReadout

-- Parameterized algebra only; the physical state and detector are not encoded.
theorem weighted_transfer (e y : Real) : (4*e*y)/2 + (-2*e*y) = 0 := by
  ring

theorem same_sector_witness (q : Real) : (2*(q-q^2))/2+q^2 = q := by
  ring

theorem opposite_nonzero_current (e v r p : Real)
    (he : 0 < e) (hv : 0 < v) (hr : 0 < r) (hp : 0 < p) :
    -(2*e*v*r*p) ≠ 2*e*v*r*p := by
  have h : 0 < 2*e*v*r*p := by positivity
  linarith

theorem no_value_only_drift {X Y : Type*} (obs : X -> Y) (drift : X -> Real)
    (x y : X) (same : obs x = obs y) (different : drift x ≠ drift y) :
    ¬ (∃ b : Y -> Real, ∀ z, drift z = b (obs z)) := by
  rintro ⟨b, hb⟩
  apply different
  rw [hb x, hb y, same]

theorem energy_with_interaction (a b c : Real) (h : a+b+c = 0) :
    a+b = -c := by linarith

end Tect.ExchangeReadout
