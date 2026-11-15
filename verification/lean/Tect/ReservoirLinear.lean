import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Tect.ReservoirLinear

-- Parameterized real block algebra, not the full functional or lattice proof.
theorem paired_square_first (d c x : Real) :
    (d+c)*((-d+c)*x) = (c*c-d*d)*x := by ring

theorem paired_square_second (d c y : Real) :
    (-d+c)*((d+c)*y) = (c*c-d*d)*y := by ring

theorem conserved_elliptic_energy (d c x y : Real) :
    2*(d-c)*x*((d+c)*y) + 2*(d+c)*y*((-d+c)*x) = 0 := by ring

theorem jordan_group (q t s x y : Real) :
    (y-2*q*s*x)-2*q*t*x = y-2*q*(s+t)*x := by ring

theorem shear_norm_squared (q t : Real) :
    (1:Real)^2+(-2*q*t)^2 = 1+4*q^2*t^2 := by ring

theorem norm_ratio_bound (d c : Real) (h : 17*c ≤ 15*d) :
    d+c ≤ 16*(d-c) := by linarith

end Tect.ReservoirLinear
