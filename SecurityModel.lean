/-
  SecurityModel.lean — Core definitions for computational security.

  Two ingredients are needed to state security theorems without building
  a full Turing machine model:

    1. Negligible functions — the "close enough to zero" criterion.
    2. PPT algorithms — the "efficient enough" criterion (axiomatized).

  Everything else in the security proof is algebra.
-/

import Mathlib.Analysis.SpecialFunctions.Pow.Real

-- ════════════════════════════════════════════════════════════════
-- Negligible functions
-- ════════════════════════════════════════════════════════════════

/-- A function f : ℕ → ℝ is **negligible** if it vanishes faster than any
    inverse polynomial: for every c : ℕ, eventually f(n) ≤ n^(−c).

    This is the standard definition from provable security.  Probabilities
    that are negligible are "as good as zero" for any practical purpose. -/
def Negligible (f : ℕ → ℝ) : Prop :=
  ∀ c : ℕ, ∃ N : ℕ, ∀ n ≥ N, f n ≤ (n : ℝ)⁻¹ ^ c

namespace Negligible

/-- The constant-zero function is negligible. -/
lemma zero : Negligible (fun _ => 0) :=
  fun c => ⟨1, fun n _ => by positivity⟩

/-- Negligible is downward-closed: if f ≤ g pointwise and g is negligible,
    then so is f.  This is the key lemma for the security reduction. -/
lemma of_le {f g : ℕ → ℝ} (h : ∀ n, f n ≤ g n) (hg : Negligible g) : Negligible f :=
  fun c =>
    let ⟨N, hN⟩ := hg c
    ⟨N, fun n hn => le_trans (h n) (hN n hn)⟩

/-- If f and g are both negligible, their sum is negligible. -/
lemma add {f g : ℕ → ℝ} (hf : Negligible f) (hg : Negligible g) :
    Negligible (fun n => f n + g n) := by
  intro c
  obtain ⟨Nf, hf'⟩ := hf (c + 1)
  obtain ⟨Ng, hg'⟩ := hg (c + 1)
  refine ⟨max Nf Ng + 1, fun n hn => ?_⟩
  have hn1 : n ≥ Nf := le_trans (le_trans (Nat.le_add_right Nf Ng) (Nat.le_succ _)) hn
  have hn2 : n ≥ Ng := le_trans (le_trans (Nat.le_add_left Ng Nf) (Nat.le_succ _)) hn
  have hn_pos : (1 : ℝ) ≤ n := by exact_mod_cast Nat.one_le_iff_ne_zero.mpr (by omega)
  calc f n + g n
      ≤ (n : ℝ)⁻¹ ^ (c + 1) + (n : ℝ)⁻¹ ^ (c + 1) := add_le_add (hf' n hn1) (hg' n hn2)
    _ = 2 * (n : ℝ)⁻¹ ^ (c + 1) := by ring
    _ ≤ (n : ℝ)⁻¹ ^ c := by
        have hinv : (n : ℝ)⁻¹ ≤ 1 := inv_le_one_of_one_le₀ hn_pos
        have : (n : ℝ)⁻¹ ^ (c + 1) ≤ (n : ℝ)⁻¹ ^ c / 2 := by
          rw [pow_succ]
          have hnn : 0 ≤ (n : ℝ)⁻¹ ^ c := by positivity
          nlinarith [mul_le_one₀ (pow_le_one₀ (by positivity) hinv) (by positivity) hinv]
        linarith

end Negligible

-- ════════════════════════════════════════════════════════════════
-- PPT algorithms (axiomatized)
-- ════════════════════════════════════════════════════════════════

/-- The type of **probabilistic polynomial-time** (PPT) algorithms.

    We axiomatize this type rather than building a Turing machine model.
    The key property — polynomial runtime in the security parameter — is
    not formalized; it is a meta-level constraint on how `PPT` is instantiated.

    In a full formalization (e.g., EasyCrypt style), this would be replaced
    by a concrete computational model with an explicit runtime bound. -/
axiom PPT : Type* → Type* → Type*

/-- Run a PPT algorithm on an input.  The output may depend on internal
    randomness; we model this deterministically on a combined input that
    includes the random tape (not exposed to the caller). -/
axiom PPT.run {α β : Type*} : PPT α β → α → β

/-- PPT algorithms compose: if A : α → β and B : β → γ are PPT,
    then so is B ∘ A. -/
axiom PPT.comp {α β γ : Type*} : PPT α β → PPT β γ → PPT α γ
