import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Tect.FixedSector

-- Parameterized algebra only. Spectral certificates, finite Hamiltonian
-- stability and constrained minimizer existence are not encoded here.
theorem fixed_charge_trial (rho0 r : Real) :
    (rho0 - 2*r^2)/2 + r^2 = rho0/2 := by
  ring

theorem bdg_product (c d : Real) :
    (c-d)*(c+d) = c^2-d^2 := by
  ring

theorem positive_bdg_square (c d : Real) (hd : 0 < d) (hdc : d < c) :
    0 < c^2-d^2 := by
  have hc : 0 < c := lt_trans hd hdc
  have hp : 0 < (c-d)*(c+d) :=
    mul_pos (sub_pos.mpr hdc) (add_pos hc hd)
  nlinarith

theorem pure_order_below_reservoir (q mu : Real)
    (hq : 0 < q) (hm : mu < 1/2) :
    mu*q < q/2 + q^2/4 := by
  have hp : 0 < (1/2-mu)*q := mul_pos (sub_pos.mpr hm) hq
  nlinarith [sq_nonneg q]

theorem tensor_density_square (a b c : Real) :
    a^2+b^2+c^2+2*a*b+2*a*c+2*b*c = (a+b+c)^2 := by
  ring

theorem conserved_energy_not_minimum {X : Type*} (H : X -> Real)
    (x y : X) (minimum : Real) (hcons : H y = H x)
    (hhigh : minimum < H x) : H y ≠ minimum := by
  linarith

end Tect.FixedSector
