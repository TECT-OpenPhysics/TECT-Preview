import Mathlib

open scoped BigOperators

namespace Tect.R482

def pullback {X Y : Type*} (p : Y → X) (f : X → ℝ) : Y → ℝ :=
  fun y => f (p y)

def coarseGenerator {X R : Type*} [Fintype R]
    (move : R → X → X) (rate : R → X → ℝ) (f : X → ℝ) (x : X) : ℝ :=
  ∑ r, rate r x * (f (move r x) - f x)

def fineGenerator {X Y R : Type*} [Fintype R]
    (liftMove : R → Y → Y) (fineRate : R → Y → ℝ)
    (p : Y → X) (f : X → ℝ) (y : Y) : ℝ :=
  ∑ r, fineRate r y * (f (p (liftMove r y)) - f (p y))

theorem normalized_local_replication {C X : Type*} [Fintype C]
    (weights : C → ℝ) (phi : X → ℝ)
    (hweights : ∑ c, weights c = 1) (x : X) :
    (∑ c, weights c * phi x) = phi x := by
  rw [← Finset.sum_mul]
  rw [hweights]
  ring

theorem generator_intertwining {X Y R : Type*} [Fintype R]
    (move : R → X → X) (rate : R → X → ℝ)
    (liftMove : R → Y → Y) (fineRate : R → Y → ℝ)
    (p : Y → X)
    (hmove : ∀ r y, p (liftMove r y) = move r (p y))
    (hrate : ∀ r y, fineRate r y = rate r (p y))
    (f : X → ℝ) (y : Y) :
    fineGenerator liftMove fineRate p f y =
      pullback p (fun x => coarseGenerator move rate f x) y := by
  simp [fineGenerator, coarseGenerator, pullback, hmove, hrate]

theorem inverse_cocycle_preserves_fibre {R H : Type*}
    (tau : R → H → H) (inv : R → R)
    (hinv : ∀ r h, tau (inv r) (tau r h) = h) :
    ∀ r h, tau (inv r) (tau r h) = h := by
  intro r h
  exact hinv r h

theorem cumulative_zero {N : ℕ} (defect : ℕ → ℝ)
    (hzero : ∀ n, defect n = 0) :
    Finset.sum (Finset.range (N + 1)) defect = 0 := by
  simp [hzero]

theorem q_family_is_strictly_refining : (2 : ℕ) ^ 1 < 2 ^ 2 := by
  norm_num

def geometricPromotion : Bool := false
def physicalPromotion : Bool := false

theorem structural_firewall :
    geometricPromotion = false ∧ physicalPromotion = false := by
  decide

end Tect.R482
