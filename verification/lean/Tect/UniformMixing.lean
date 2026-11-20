import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

namespace Tect.UniformMixing

theorem moment_envelope (r s : Real) (hr : 0 <= r) :
    r^2 <= (s+1/4)*r + r*(r-s)^2 := by
  nlinarith only [mul_nonneg hr (sq_nonneg (r-s-1/2))]

theorem young_pinned (u v : Real) :
    (1/16:Real)*u*v <= (27/100)*v^2+(25/6912)*u^2 := by
  nlinarith only [sq_nonneg (216*v-25*u)]

theorem remainder_positive (mu : Real) (hmu : mu < 1/3) :
    0 < 1/2-mu-25/6912 := by linarith

theorem gap_absorbed (gap mu n R u v w : Real) (hmu : mu < 1/3)
    (hu : u^2=n) (hv : v^2=R)
    (he : gap+(27/100)*R+(1/2-mu)*n <= (1/16)*(w+u*v)) :
    gap <= (1/16)*w := by
  rw [<-hu, <-hv] at he
  have hn := mul_nonneg (le_of_lt (remainder_positive mu hmu)) (sq_nonneg u)
  nlinarith only [he,young_pinned u v,hn]

theorem charge_product (gap eps w d m n q x : Real) (hg : 0 <= gap)
    (heps : 0 < eps) (hd : 0 < d) (hq : 0 < q)
    (hb : gap <= eps*w) (hw : w^2=d*m*n)
    (hm : m=2*q*x) (hn : n=q*(1-x)) :
    gap^2/(2*eps^2*d*q^2) <= x*(1-x) := by
  have hs := mul_nonneg (sub_nonneg.mpr hb) (add_nonneg hg (le_trans hg hb))
  have hsq : gap^2 <= (eps*w)^2 := by nlinarith only [hs]
  have hden : 0 < 2*eps^2*d*q^2 := by positivity
  apply (div_le_iff₀ hden).2
  calc
    gap^2 <= (eps*w)^2 := hsq
    _ = x*(1-x)*(2*eps^2*d*q^2) := by rw [mul_pow,hw,hm,hn]; ring

theorem pair_moment_split (z n T d m R u v w : Real) (hn : 0 <= n)
    (hu : 0 <= u) (hv : 0 <= v) (hw : 0 <= w)
    (hus : u^2=n) (hvs : v^2=R) (hws : w^2=d*m*n)
    (hc : z^2 <= n*T) (ht : T <= d*m+R) : z <= w+u*v := by
  have h1 := mul_le_mul_of_nonneg_left ht hn
  have huv := mul_nonneg hu hv
  have h2 := mul_nonneg hw huv
  have heq : (u*v)^2=n*R := by rw [mul_pow, hus, hvs]
  by_contra! hh
  have h3 := mul_pos (sub_pos.mpr hh) (show 0 < z+(w+u*v) by linarith)
  nlinarith only [hc,h1,hws,heq,h2,h3]

end Tect.UniformMixing
