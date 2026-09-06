import Mathlib

namespace Tect.PahOmc016

/- The finite-dimensional measure construction and its integration-by-parts
translation are proved in the analytic certificate. These declarations
cross-check the exact algebra and bounds used after that translation. -/

theorem amplitude_injection (h ell : Real) : (h/2)*(2*ell)=h*ell := by ring

theorem signed_edge_expansion (t w J sign : Real) (hs : sign^2=1) :
    J*(t-sign*w)^2/2-J*w^2/2=J*t^2/2-J*sign*w*t := by
  calc
    _ = J*t^2/2-J*sign*w*t+J*w^2/2*(sign^2-1) := by ring
    _ = _ := by rw [hs]; ring

theorem cubic_moment_barrier (x : Real)
    (h : x^3 ≤ 1+10*x) : x ≤ 4 := by
  by_contra! hbad
  have hs : 16 < x^2 := by nlinarith [sq_nonneg (x-4)]
  have hp : 0 < x*(x^2-16) := mul_pos (by linarith) (by linarith)
  nlinarith

theorem neighbor_event_bound (bad good : Real)
    (hbad : bad ≤ 5*4/(8:Real)^2) (hgood : good=1-bad) :
    (11:Real)/16 ≤ good := by norm_num at hbad ⊢; linarith

theorem conditional_cost :
    (2:Real)^6/6+2^4/4+11*2^2/2+80*2 = 590/3 := by norm_num

theorem linear_tail_absorption (t : Real) (ht : 4 ≤ t) :
    80*t ≤ t^6/12 := by
  have h5 : (4:Real)^5 ≤ t^5 := by gcongr
  have hp : 0 ≤ t*(t^5-960) := mul_nonneg (by linarith) (by norm_num at h5; linarith)
  nlinarith

theorem integrable_tail_comparison (t : Real) (ht : 4 ≤ t) :
    t ≤ t^6/12 := by
  have h := linear_tail_absorption t ht
  linarith

theorem lower_bound_assembly (p g : Real)
    (hp : (1:Real)/5 * Real.exp (-(1550:Real)/3) ≤ p)
    (hg : (11:Real)/16 ≤ g) :
    (11:Real)/80 * Real.exp (-(1550:Real)/3) ≤ g*p := by
  have he := Real.exp_pos (-(1550:Real)/3)
  have hprod := mul_le_mul hg hp
    (by positivity : 0 ≤ (1:Real)/5 * Real.exp (-(1550:Real)/3))
    (by linarith : 0 ≤ g)
  nlinarith

theorem bound_strictly_positive :
    0 < (11:Real)/80 * Real.exp (-(1550:Real)/3) := by positivity

theorem exponent_assembly : (590:Real)/3+320=1550/3 := by norm_num

end Tect.PahOmc016
