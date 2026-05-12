/-
  OilVinegar.lean — Core definitions for the Oil-and-Vinegar cryptosystem.
  
  This module defines:
  - The coherence function C (trapdoor)
  - The Silver Ratio η = 1/√2
  - The special complex number μ = e^(i 3π/4)
  - Essential lemmas about their properties
-/

import Mathlib.Data.Complex.Exponential
import Mathlib.Analysis.MeanEqualities
import Mathlib.Tactic.Positivity

open Complex Real

noncomputable section OilVinegar

/-- The coherence function C: ℝ → ℝ, defining C(r) = 2r/(1+r²).
    This is the trapdoor operator in the Oil-and-Vinegar system.
    It maps (0,1] bijectively (except for the symmetry r ↔ 1/r).
-/
noncomputable def C (r : ℝ) : ℝ := 2 * r / (1 + r ^ 2)

/-- The Silver Ratio η = 1/√2, appearing in the coherence closure property.
-/
noncomputable def η : ℝ := 1 / Real.sqrt 2

/-- The special complex number μ = e^(i·3π/4).
    
    This represents the unique equilibrium in the Oil-and-Vinegar system.
    - Re(μ) = -1/√2 (negative, witness dissipative)
    - Im(μ) = 1/√2 (positive, observer's response)
    - |μ| = 1 (on unit circle)
    - μ^8 = 1 (period 8)
-/
noncomputable def μ : ℂ := Complex.exp (I * 3 * π / 4)

-- ════════════════════════════════════════════════════════════════
--  Core Lemmas About μ
-- ════════════════════════════════════════════════════════════════

/-- Re(μ) = -1/√2, derived from μ = e^(i·3π/4) = cos(3π/4) + i·sin(3π/4).
-/
lemma mu_re_is_neg_eta : μ.re = -η := by
  unfold μ η
  simp [Complex.exp_mul_I]
  norm_num [Real.cos_three_pi_div_four]

/-- Im(μ) = 1/√2, derived from μ = e^(i·3π/4).
-/
lemma mu_im_is_eta : μ.im = η := by
  unfold μ η
  simp [Complex.exp_mul_I]
  norm_num [Real.sin_three_pi_div_four]

/-- |μ| = 1: μ lies on the unit circle.
-/
lemma mu_abs_one : Complex.abs μ = 1 := by
  unfold μ
  simp [Complex.abs_exp]

/-- μ^2 = i (derived from the angle doubling).
-/
lemma mu_pow_two : μ ^ 2 = I := by
  unfold μ
  rw [show (I * 3 * π / 4 : ℂ) * 2 = I * 3 * π / 2 by ring]
  norm_num [Complex.exp_mul_I, Real.cos_three_pi_div_two, Real.sin_three_pi_div_two]

/-- μ^4 = -1 (derived from angle quadrupling).
-/
lemma mu_pow_four : μ ^ 4 = -1 := by
  rw [show (4 : ℕ) = 2 * 2 by norm_num]
  rw [pow_mul, mu_pow_two]
  norm_num

/-- μ^8 = 1 (period 8).
-/
lemma mu_pow_eight : μ ^ 8 = 1 := by
  rw [show (8 : ℕ) = 2 * 4 by norm_num]
  rw [pow_mul, mu_pow_four]
  norm_num

/-- Re(μ)² + Im(μ)² = 1: μ satisfies the unit circle equation.
-/
lemma mu_energy_conserved : μ.re ^ 2 + μ.im ^ 2 = 1 := by
  rw [mu_re_is_neg_eta, mu_im_is_eta]
  unfold η
  have : (1 / Real.sqrt 2) ^ 2 + (1 / Real.sqrt 2) ^ 2 = 1 := by
    field_simp [Real.sqrt_two_ne_zero]
    norm_num [Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)]
  linarith

/-- μ is negative in the real part.
-/
lemma re_mu_negative : μ.re < 0 := by
  rw [mu_re_is_neg_eta]
  unfold η
  norm_num [Real.sqrt_two_pos]

-- ════════════════════════════════════════════════════════════════
--  Core Lemmas About C
-- ════════════════════════════════════════════════════════════════

/-- C(1) = 1: the coherence function achieves its maximum at r = 1.
-/
lemma coherence_one : C 1 = 1 := by
  unfold C
  norm_num

/-- C is bounded above by 1 for positive r.
-/
lemma coherence_le_one (r : ℝ) (hr : 0 < r) : C r ≤ 1 := by
  unfold C
  rw [div_le_one (by positivity)]
  nlinarith [sq_nonneg (r - 1)]

/-- C(r) = 1 if and only if r = 1 (for positive r).
-/
lemma coherence_eq_one_iff (r : ℝ) (hr : 0 ≤ r) : C r = 1 ↔ r = 1 := by
  unfold C
  constructor
  · intro h
    have h_pos : 0 < 1 + r ^ 2 := by positivity
    have : 2 * r = 1 + r ^ 2 := by
      field_simp [ne_of_gt h_pos] at h
      linarith
    nlinarith [sq_nonneg (r - 1)]
  · intro h; rw [h]; norm_num

-- ════════════════════════════════════════════════════════════════
--  Existence and Uniqueness Lemmas
-- ════════════════════════════════════════════════════════════════

/-- A complex number satisfying all witness constraints is uniquely μ.
-/
lemma reality_unique (z : ℂ) (hre : z.re < 0) (hbal : -z.re = z.im) (hen : z.re ^ 2 + z.im ^ 2 = 1) : z = μ := by
  -- Step 1: z.im = -z.re
  have him : z.im = -z.re := hbal.symm
  -- Step 2: substituting gives 2 * z.re² = 1, so z.re² = 1/2
  have hrsq : z.re ^ 2 = 1 / 2 := by
    rw [him] at hen; nlinarith [sq_nonneg z.re]
  -- Step 3: η² = 1/2
  have hηsq : η ^ 2 = 1 / 2 := by
    unfold η
    rw [div_pow, one_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)]
  -- Step 4: z.re = ±η; dissipation (z.re < 0) with η > 0 forces z.re = -η
  have hη_pos : 0 < η := by unfold η; positivity
  have hre_eq : z.re = -η := by
    have hprod : (z.re + η) * (z.re - η) = 0 := by
      have : (z.re + η) * (z.re - η) = z.re ^ 2 - η ^ 2 := by ring
      linarith
    rcases mul_eq_zero.mp hprod with h | h
    · linarith          -- z.re + η = 0, so z.re = -η ✓
    · linarith          -- z.re - η = 0, so z.re = η > 0, contradicts hre
  -- Step 5: assemble z = μ via Complex.ext
  apply Complex.ext
  · rw [mu_re_is_neg_eta, hre_eq]
  · rw [mu_im_is_eta, him, hre_eq]; ring

end OilVinegar
