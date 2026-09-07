import Mathlib

namespace Tect.PahOmc018

/- Algebraic and finite-sum bridge. Integral passages and operator domains
remain in the analytic certificate. -/

theorem square_weight (a b m Z : Real) (ha : a ≠ 0) (hZ : Z ≠ 0) :
    (a^2/Z)*(m*b/a)^2=m^2*b^2/Z := by
  field_simp

theorem conductance_balance (a b m Z : Real) (ha : a ≠ 0) (hb : b ≠ 0)
    (hZ : Z ≠ 0) : (a^2/Z)*(m*b/a)=(b^2/Z)*(m*a/b) := by
  field_simp

theorem exponent_half (x y : Real) : -x+2*(-(y-x)/2)=-y := by ring

theorem cross_exponent (x y z : Real) : -x-(y-x)/2-(z-x)/2=-(y+z)/2 := by ring

theorem inverse_pair_form (f ft g gt c : Real) :
    -c*(f*(gt-g)+ft*(g-gt))=c*(ft-f)*(gt-g) := by ring

theorem directed_sum_bound {I : Type*} (s : Finset I) (u : I → Real) :
    (∑ i ∈ s, u i)^2 ≤ (s.card : Real) * ∑ i ∈ s, (u i)^2 :=
  sq_sum_le_card_mul_sum_sq

theorem radial_form_coefficient (H L h : Real) :
    H*(2*L*h)^2/2=2*H*L^2*h^2 := by ring

theorem radial_square_coefficient (H L h : Real) :
    H*(H*(2*L*h)^2)=(2*H*L*h)^2 := by ring

theorem tail_control (x K : Real) (hK : 0 < K) (hx : K ≤ |x|) :
    |x| ≤ x^2/K := by
  apply (le_div_iff₀ hK).2
  have hh := mul_le_mul_of_nonneg_left hx (abs_nonneg x)
  nlinarith [sq_abs x]

theorem amplitude_null (c f : Real) : c*(f-f)=0 := by ring

theorem aperture_positive (c : Real) (hc : 0 < c) :
    0 < c*((1:Real)-1/2)^2/2 := by positivity

end Tect.PahOmc018
