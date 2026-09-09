import Mathlib

/-!
Finite rational cross-check for the PAH-OMC-020 mesh-to-uniform transfer.
This formalizes only the scalar triangle envelope and its monotone refinement;
it does not prove PAH mesh-pointwise convergence or any infinite-volume claim.
-/

namespace Tect.PahOmc020MeshUniform

theorem mesh_triangle_envelope {e m d w x y z : Rat}
    (he : 0 ≤ e) (hm : 0 ≤ m) (hd : 0 ≤ d) (hw : 0 ≤ w)
    (hx : 0 ≤ x) (hy : 0 ≤ y) (hz : 0 ≤ z)
    (hx_le : x ≤ e) (hy_le : y ≤ m * d) (hz_le : z ≤ w) :
    x + y + z ≤ e + m * d + w := by
  nlinarith

theorem mesh_refinement_strict {m d w : Rat}
    (hm : 0 ≤ m) (hd : 0 < d) (hw : 0 ≤ w)
    (hmw : m > 0 ∨ w > 0) :
    m * (d / 2) + w / 2 < m * d + w := by
  rcases hmw with hmp | hwp
  · nlinarith
  · nlinarith

theorem primary_fixture :
    (1 / 100 : Rat) + 3 * (1 / 10) + 1 / 20 = 9 / 25 := by
  norm_num

theorem independent_fixture :
    (1 / 20 : Rat) + (5 / 2) * (1 / 8) + 3 / 40 = 7 / 16 := by
  norm_num

end Tect.PahOmc020MeshUniform
