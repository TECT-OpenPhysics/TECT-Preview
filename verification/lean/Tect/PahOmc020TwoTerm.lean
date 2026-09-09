import Mathlib

/-!
Finite rational cross-check for the PAH-OMC-020 two-term sequential route.
Only the scalar triangle and epsilon budget are formalized.  The R-536
source-authorized owner route and the ordered limit remain hypotheses outside
this finite Lean file.
-/

namespace Tect.PahOmc020TwoTerm

theorem two_term_triangle {j d e : Rat}
    (hj : 0 ≤ j) (hd : 0 ≤ d) (hje : j ≤ e) (hde : d ≤ e) :
    j + d ≤ 2 * e := by
  nlinarith

theorem epsilon_split {j d eps : Rat}
    (hj : 0 ≤ j) (hd : 0 ≤ d) (heps : 0 < eps)
    (hj_eps : j < eps / 2) (hd_eps : d < eps / 2) :
    j + d < eps := by
  nlinarith

theorem primary_fixture :
    (3 / 100 : Rat) + 1 / 20 = 2 / 25 := by
  norm_num

theorem independent_fixture :
    (1 / 12 : Rat) + 1 / 15 = 3 / 20 := by
  norm_num

end Tect.PahOmc020TwoTerm
