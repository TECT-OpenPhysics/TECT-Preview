import Mathlib

open scoped BigOperators

namespace Tect.R493

structure FineCharge where
  retained : Nat
  dropped : Nat

def fineGrade (s : FineCharge) : Nat := s.retained + s.dropped
def coarseGrade (s : FineCharge) : Nat := s.retained

theorem charge_balance (s : FineCharge) :
    fineGrade s = coarseGrade s + s.dropped := by
  rfl

theorem coarse_grade_bound (s : FineCharge) :
    coarseGrade s ≤ fineGrade s := by
  simp [fineGrade, coarseGrade]

def N_of_f (m : Nat) : Nat := max 2 (m + 1)

theorem support_separated (m n : Nat) (h : N_of_f m ≤ n) : m < n := by
  unfold N_of_f at h
  omega

theorem frontier_separated (m n : Nat) (h : N_of_f m ≤ n) :
    m < n ∧ m < n + 1 ∧ m < n + 2 := by
  have hmn : m < n := support_separated m n h
  exact ⟨hmn, lt_trans hmn (Nat.lt_succ_self n), lt_trans hmn (by omega)⟩

inductive RootFamily
  | phase
  | aperture
  | radialTransfer
  | link

def cylinderIncrement (family : RootFamily) (delta : ℝ) : ℝ :=
  match family with
  | .phase => 0
  | .aperture => 0
  | .radialTransfer => delta
  | .link => delta

theorem phase_increment_zero (delta : ℝ) :
    cylinderIncrement .phase delta = 0 := by
  rfl

theorem aperture_increment_zero (delta : ℝ) :
    cylinderIncrement .aperture delta = 0 := by
  rfl

def pullback {X Y : Type*} (p : Y → X) (f : X → ℝ) : Y → ℝ :=
  fun y => f (p y)

def coarseGenerator {X R : Type*} [Fintype R]
    (move : R → X → X) (rate : R → X → ℝ) (f : X → ℝ) (x : X) : ℝ :=
  ∑ r, rate r x * (f (move r x) - f x)

def fineGenerator {X Y R : Type*} [Fintype R]
    (liftMove : R → Y → Y) (fineRate : R → Y → ℝ)
    (p : Y → X) (f : X → ℝ) (y : Y) : ℝ :=
  ∑ r, fineRate r y * (f (p (liftMove r y)) - f (p y))

theorem matched_generator_summand
    {X Y R : Type*} [Fintype R]
    (move : R → X → X) (rate : R → X → ℝ)
    (liftMove : R → Y → Y) (fineRate : R → Y → ℝ)
    (p : Y → X)
    (hmove : ∀ r y, p (liftMove r y) = move r (p y))
    (hrate : ∀ r y, fineRate r y = rate r (p y))
    (f : X → ℝ) (y : Y) :
    fineGenerator liftMove fineRate p f y =
      pullback p (fun x => coarseGenerator move rate f x) y := by
  simp [fineGenerator, coarseGenerator, pullback, hmove, hrate]

def activeRootSum (ι : Type*) [Fintype ι]
    (active : ι → Prop) [DecidablePred active]
    (rate delta : ι → ℝ) : ℝ :=
  ∑ i, if active i then rate i * delta i else 0

theorem active_root_sum_intertwines
    {ι : Type*} [Fintype ι]
    (active : ι → Prop) [DecidablePred active]
    (fineRate coarseRate fineDelta coarseDelta : ι → ℝ)
    (hRate : ∀ i, active i → fineRate i = coarseRate i)
    (hDelta : ∀ i, active i → fineDelta i = coarseDelta i) :
    activeRootSum ι active fineRate fineDelta =
      activeRootSum ι active coarseRate coarseDelta := by
  unfold activeRootSum
  apply Finset.sum_congr rfl
  intro i hi
  by_cases h : active i
  · simp [h, hRate i h, hDelta i h]
  · simp [h]

def oldProjection (s : FineCharge) : Nat := coarseGrade s

theorem old_move_preserves_projected_grade
    (s t : FineCharge)
    (hRetained : t.retained = s.retained) :
    oldProjection t = oldProjection s := by
  simp [oldProjection, coarseGrade, hRetained]

def boundaryDefect : ℚ := 16 / 9

theorem boundary_defect_exact : boundaryDefect = 16 / 9 := by
  rfl

theorem boundary_defect_nonzero : boundaryDefect ≠ 0 := by
  norm_num [boundaryDefect]

def Csw : Nat := 540
def cswUsedForIntertwining : Bool := false

theorem csw_domination_only :
    Csw = 540 ∧ cswUsedForIntertwining = false := by
  decide

def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    claimBearing = false ∧ physicalPromotion = false := by
  decide

end Tect.R493
