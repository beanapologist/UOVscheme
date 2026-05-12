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
  -- Use c+1 for each bound; need n ≥ 2 so that 2·n⁻¹ ≤ 1
  obtain ⟨Nf, hf'⟩ := hf (c + 1)
  obtain ⟨Ng, hg'⟩ := hg (c + 1)
  refine ⟨max (max Nf Ng) 2, fun n hn => ?_⟩
  have hn_Nf : n ≥ Nf := le_trans (le_trans (le_max_left _ _) (le_max_left _ _)) hn
  have hn_Ng : n ≥ Ng := le_trans (le_trans (le_max_right _ _) (le_max_left _ _)) hn
  have hn_2  : (2 : ℝ) ≤ (n : ℝ) := by exact_mod_cast le_trans (le_max_right _ _) hn
  have hn_pos : (0 : ℝ) < (n : ℝ) := by linarith
  -- n⁻¹ ≤ 1/2 because n ≥ 2
  have hinv_half : (n : ℝ)⁻¹ ≤ 1 / 2 := by
    rw [inv_le hn_pos (by norm_num)]; linarith
  have hpc : 0 ≤ (n : ℝ)⁻¹ ^ c := by positivity
  calc f n + g n
      ≤ (n : ℝ)⁻¹ ^ (c + 1) + (n : ℝ)⁻¹ ^ (c + 1) :=
          add_le_add (hf' n hn_Nf) (hg' n hn_Ng)
    _ = 2 * ((n : ℝ)⁻¹ ^ c * (n : ℝ)⁻¹) := by rw [pow_succ]; ring
    _ ≤ (n : ℝ)⁻¹ ^ c := by
        -- 2 * (n⁻¹^c * n⁻¹) ≤ n⁻¹^c  iff  2 * n⁻¹ ≤ 1  iff  n ≥ 2
        have h2n : 2 * (n : ℝ)⁻¹ ≤ 1 := by linarith
        nlinarith [mul_nonneg hpc (inv_nonneg.mpr (le_of_lt hn_pos))]

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
