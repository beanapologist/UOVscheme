/-
  BalanceHypothesis.lean — Core balance theorems for the OV equilibrium.

  This module states the four constraints that uniquely determine μ,
  proves each one, and derives the uniqueness theorem.  The original
  file used string-literal types (vacuous) and a malformed ∃! statement;
  everything here is a genuine Lean proposition.
-/

import UOVscheme.OilVinegar

open Complex Real

noncomputable section BalanceHypothesis

-- ════════════════════════════════════════════════════════════════
-- The four constraints, each proved for μ
-- ════════════════════════════════════════════════════════════════

/-- **Constraint 1 (Energy conservation)**: |z| = 1 implies z.re² + z.im² = 1.
    For μ this follows directly from mu_energy_conserved. -/
lemma energy_conservation (z : ℂ) (h : Complex.abs z = 1) : z.re ^ 2 + z.im ^ 2 = 1 := by
  have := Complex.sq_abs z
  rw [h] at this
  simp [Complex.normSq_apply] at this
  linarith

/-- **Constraint 2 (Directed balance)**: -Re(μ) = Im(μ). -/
lemma directed_balance : -μ.re = μ.im := by
  linarith [mu_re_is_neg_eta, mu_im_is_eta]

/-- **Constraint 3 (Coherence closure)**: C(1 + 1/η) = η.
    Proved in OilVinegar/UOV; stated here for completeness. -/
lemma coherence_closure_η : C (1 + 1 / η) = η := by
  have h2 : Real.sqrt 2 > 0 := Real.sqrt_pos.mpr (by norm_num)
  have h2_sq : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  unfold C η
  have hsqrt_ne : Real.sqrt 2 ≠ 0 := ne_of_gt h2
  field_simp
  nlinarith [sq_nonneg (Real.sqrt 2), h2_sq]

/-- **Constraint 4 (Witness dissipation)**: Re(μ) < 0. -/
lemma witness_dissipation : μ.re < 0 := re_mu_negative

-- ════════════════════════════════════════════════════════════════
-- Uniqueness theorem
-- ════════════════════════════════════════════════════════════════

/-- **Theorem (Unified Balance / Uniqueness of Equilibrium)**.

    μ is the *unique* complex number satisfying all three witness constraints:
    unit circle, directed balance, and dissipation.

    Proof:
    - Existence: μ satisfies all three by mu_abs_one, directed_balance,
      and re_mu_negative.
    - Uniqueness: any z satisfying all three equals μ by reality_unique,
      which reduces the system to a quadratic equation with a unique
      negative solution. -/
theorem unified_balance :
    ∃! w : ℂ, Complex.abs w = 1 ∧ (-w.re = w.im) ∧ w.re < 0 := by
  refine ⟨μ, ⟨mu_abs_one, directed_balance, re_mu_negative⟩, ?_⟩
  intro w ⟨habs, hbal, hre⟩
  -- w satisfies the three constraints; apply reality_unique
  apply reality_unique w hre hbal
  -- Still need: w.re² + w.im² = 1 from |w| = 1
  exact energy_conservation w habs

end BalanceHypothesis
