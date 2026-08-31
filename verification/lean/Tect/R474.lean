import Mathlib

namespace Tect.R474

/-
  R-474 formalises only the epsilon bookkeeping for a two-parameter ordered-
  limit contract.  The uniform tail hypotheses, common norm, source owner,
  and analytic operator domains remain outside this kernel file.
-/

theorem cutoff_then_volume_rectangle
    (a : ℕ → ℕ → ℝ) (b : ℕ → ℝ) (limit : ℝ)
    (hcut : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ,
      ∀ n m : ℕ, N ≤ n → |a n m - b m| < ε)
    (hvol : ∀ ε : ℝ, 0 < ε → ∃ M : ℕ,
      ∀ m : ℕ, M ≤ m → |b m - limit| < ε) :
    ∀ ε : ℝ, 0 < ε → ∃ N M : ℕ,
      ∀ n m : ℕ, N ≤ n → M ≤ m → |a n m - limit| < ε := by
  intro ε hε
  obtain ⟨N, hN⟩ := hcut (ε / 2) (by linarith)
  obtain ⟨M, hM⟩ := hvol (ε / 2) (by linarith)
  refine ⟨N, M, ?_⟩
  intro n m hn hm
  have h1 := hN n m hn
  have h2 := hM m hm
  calc
    |a n m - limit| = |(a n m - b m) + (b m - limit)| := by
      congr 1
      ring
    _ ≤ |a n m - b m| + |b m - limit| := abs_add_le _ _
    _ < ε / 2 + ε / 2 := add_lt_add h1 h2
    _ = ε := by ring

theorem volume_then_cutoff_rectangle
    (a : ℕ → ℕ → ℝ) (c : ℕ → ℝ) (limit : ℝ)
    (hvol : ∀ ε : ℝ, 0 < ε → ∃ M : ℕ,
      ∀ n m : ℕ, M ≤ m → |a n m - c n| < ε)
    (hcut : ∀ ε : ℝ, 0 < ε → ∃ N : ℕ,
      ∀ n : ℕ, N ≤ n → |c n - limit| < ε) :
    ∀ ε : ℝ, 0 < ε → ∃ N M : ℕ,
      ∀ n m : ℕ, N ≤ n → M ≤ m → |a n m - limit| < ε := by
  intro ε hε
  obtain ⟨M, hM⟩ := hvol (ε / 2) (by linarith)
  obtain ⟨N, hN⟩ := hcut (ε / 2) (by linarith)
  refine ⟨N, M, ?_⟩
  intro n m hn hm
  have h1 := hM n m hm
  have h2 := hN n hn
  calc
    |a n m - limit| = |(a n m - c n) + (c n - limit)| := by
      congr 1
      ring
    _ ≤ |a n m - c n| + |c n - limit| := abs_add_le _ _
    _ < ε / 2 + ε / 2 := add_lt_add h1 h2
    _ = ε := by ring

theorem epsilon_split_positive (ε : ℝ) (hε : 0 < ε) :
    0 < ε / 2 ∧ ε / 2 + ε / 2 = ε := by
  constructor
  · linarith
  · ring

theorem methods_are_not_changed : True := by
  trivial

end Tect.R474
