/-
  SecurityModel.lean — Core definitions for computational security.

    1. `Negligible` — advantage functions vanish faster than any inverse polynomial.
    2. `IsPolynomial` / `PPTAlg` — PPT algorithms with an explicit degree bound.
    3. `PPT` — alias for `PPTAlg` (composition and closure lemmas proved).
-/

import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Nat.Cast.Basic
import Mathlib.Tactic.Linarith

-- ════════════════════════════════════════════════════════════════
-- Negligible functions
-- ════════════════════════════════════════════════════════════════

/-- A function f : ℕ → ℝ is **negligible** if it vanishes faster than any
    inverse polynomial: for every c : ℕ, eventually f(n) ≤ n^(−c). -/
def Negligible (f : ℕ → ℝ) : Prop :=
  ∀ c : ℕ, ∃ N : ℕ, ∀ n ≥ N, f n ≤ (n : ℝ)⁻¹ ^ c

namespace Negligible

lemma zero : Negligible (fun _ => 0) :=
  fun c => ⟨1, fun n _ => by positivity⟩

lemma of_le {f g : ℕ → ℝ} (h : ∀ n, f n ≤ g n) (hg : Negligible g) : Negligible f :=
  fun c =>
    let ⟨N, hN⟩ := hg c
    ⟨N, fun n hn => le_trans (h n) (hN n hn)⟩

/-- Every advantage profile identically zero is negligible. -/
theorem negligible_of_forall_zero {f : ℕ → ℝ} (h : ∀ n, f n = 0) : Negligible f :=
  fun c => ⟨1, fun n _ => by simp [h n]⟩

lemma add {f g : ℕ → ℝ} (hf : Negligible f) (hg : Negligible g) :
    Negligible (fun n => f n + g n) := by
  intro c
  obtain ⟨Nf, hf'⟩ := hf (c + 1)
  obtain ⟨Ng, hg'⟩ := hg (c + 1)
  refine ⟨max (max Nf Ng) 2, fun n hn => ?_⟩
  have hn_Nf : n ≥ Nf := le_trans (le_trans (le_max_left _ _) (le_max_left _ _)) hn
  have hn_Ng : n ≥ Ng := le_trans (le_trans (le_max_right _ _) (le_max_left _ _)) hn
  have hn_2  : (2 : ℝ) ≤ (n : ℝ) := by exact_mod_cast le_trans (le_max_right _ _) hn
  have hn_pos : (0 : ℝ) < (n : ℝ) := by linarith
  have hinv_half : (n : ℝ)⁻¹ ≤ 1 / 2 := by
    simpa using one_div_le_one_div_of_le (by norm_num) hn_2
  have hpc : 0 ≤ (n : ℝ)⁻¹ ^ c := by positivity
  calc f n + g n
      ≤ (n : ℝ)⁻¹ ^ (c + 1) + (n : ℝ)⁻¹ ^ (c + 1) :=
          add_le_add (hf' n hn_Nf) (hg' n hn_Ng)
    _ = 2 * ((n : ℝ)⁻¹ ^ c * (n : ℝ)⁻¹) := by rw [pow_succ]; ring
    _ ≤ (n : ℝ)⁻¹ ^ c := by
        have h2n : 2 * (n : ℝ)⁻¹ ≤ 1 := by linarith
        nlinarith [mul_nonneg hpc (inv_nonneg.mpr (le_of_lt hn_pos))]

end Negligible

-- ════════════════════════════════════════════════════════════════
-- Polynomial growth (cost bounds)
-- ════════════════════════════════════════════════════════════════

/-- `f` is bounded by `(n+1)^d` for all security parameters `n ≥ 1`. -/
def IsPolynomial (f : ℕ → ℕ) : Prop :=
  ∃ d : ℕ, ∀ n ≥ 1, f n ≤ (n + 1) ^ d

namespace IsPolynomial

lemma zero : IsPolynomial (fun _ => 0) :=
  ⟨0, fun n _ => by simp⟩

lemma one : IsPolynomial (fun _ => 1) :=
  ⟨0, fun n _ => by simp⟩

lemma const (k : ℕ) : IsPolynomial (fun _ => k) :=
  ⟨k + 1, fun n hn => by
    rcases k with (_ | k)
    · simp
    have hm : 1 < n + 1 := by omega
    exact le_of_lt (Nat.lt_succ_self (k + 1) |>.trans (Nat.lt_pow_self hm (k + 2)))⟩

lemma id : IsPolynomial id :=
  ⟨1, fun n _ => by simp⟩

lemma add {f g : ℕ → ℕ} (hf : IsPolynomial f) (hg : IsPolynomial g) :
    IsPolynomial (fun n => f n + g n) := by
  rcases hf with ⟨df, hf⟩
  rcases hg with ⟨dg, hg⟩
  refine ⟨df + dg + 1, fun n hn => ?_⟩
  have hn' : 1 ≤ n + 1 := by omega
  have h2 : 2 ≤ n + 1 := by omega
  have hpow_df : (n + 1) ^ df ≤ (n + 1) ^ (df + dg) :=
    Nat.pow_le_pow_right hn' (by omega)
  have hpow_dg : (n + 1) ^ dg ≤ (n + 1) ^ (df + dg) :=
    Nat.pow_le_pow_right hn' (by omega)
  calc
    f n + g n ≤ (n + 1) ^ df + (n + 1) ^ dg :=
      add_le_add (hf n hn) (hg n hn)
    _ ≤ 2 * (n + 1) ^ (df + dg) := by
      calc (n + 1) ^ df + (n + 1) ^ dg
          ≤ (n + 1) ^ (df + dg) + (n + 1) ^ (df + dg) := Nat.add_le_add hpow_df hpow_dg
        _ = 2 * (n + 1) ^ (df + dg) := by ring_nf
    _ ≤ (n + 1) ^ (df + dg + 1) := by
      calc 2 * (n + 1) ^ (df + dg) ≤ (n + 1) * (n + 1) ^ (df + dg) :=
          Nat.mul_le_mul_right _ h2
        _ = (n + 1) ^ (df + dg + 1) := by ring_nf

end IsPolynomial

-- ════════════════════════════════════════════════════════════════
-- PPT algorithms
-- ════════════════════════════════════════════════════════════════

/-- A **probabilistic polynomial-time** algorithm, presented as:

  - `eval` — input/output behaviour (random coins folded into the input type);
  - `cost` — a conservative step-count upper bound as a function of `n`;
  - `cost_poly` — proof that `cost` is polynomial in the security parameter.

  This is not a Turing-machine formalization, but the polynomial bound is
  **internal to the proof** rather than a meta-level axiom. -/
structure PPTAlg (α β : Type*) where
  eval : α → β
  cost : ℕ → ℕ
  cost_poly : IsPolynomial cost

namespace PPTAlg

/-- Evaluate the algorithm (alias: `PPT.run`). -/
protected def run (A : PPTAlg α β) (x : α) : β :=
  A.eval x

/-- Sequential composition: run `A` then `B`.  Cost adds at each security level. -/
def comp (A : PPTAlg α β) (B : PPTAlg β γ) : PPTAlg α γ where
  eval := fun x => B.eval (A.eval x)
  cost := fun n => A.cost n + B.cost n
  cost_poly := IsPolynomial.add A.cost_poly B.cost_poly

/-- Wrap any function with unit constant cost (useful for tests and oracles). -/
def ofFn (f : α → β) : PPTAlg α β where
  eval := f
  cost := fun _ => 1
  cost_poly := IsPolynomial.one

/-- Cost of composition is the sum of component costs (proved). -/
theorem comp_cost (A : PPTAlg α β) (B : PPTAlg β γ) (n : ℕ) :
    (A.comp B).cost n = A.cost n + B.cost n :=
  rfl

theorem comp_run (A : PPTAlg α β) (B : PPTAlg β γ) (x : α) :
    (A.comp B).run x = B.run (A.run x) :=
  rfl

/-- Post-process output without increasing the asymptotic cost bound. -/
def map (A : PPTAlg α β) (f : β → γ) : PPTAlg α γ where
  eval := fun x => f (A.eval x)
  cost := A.cost
  cost_poly := A.cost_poly

theorem map_run (A : PPTAlg α β) (f : β → γ) (x : α) :
    (A.map f).run x = f (A.run x) :=
  rfl

end PPTAlg

/-- Notation alias used throughout the security development. -/
abbrev PPT (α β : Type*) := PPTAlg α β

namespace PPT

def run {α β} (A : PPT α β) (x : α) : β := PPTAlg.run A x

def comp {α β γ} (A : PPT α β) (B : PPT β γ) : PPT α γ := PPTAlg.comp A B

end PPT
