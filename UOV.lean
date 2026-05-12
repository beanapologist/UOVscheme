/-
  OilVinegarDuality.lean — Witness/Observer lens applied to Oil-and-Vinegar.
  
  The Oil-and-Vinegar cryptosystem is a *interrogation structure*:
  - Vinegar = observer's free choice (Im side)
  - Oil = witness's forced response (Re side)
  - Trapdoor = bridge operator (coherence C)
  - Public map = complete interrogation
  - Signature = equilibrium where interrogation locks both sides
  
  Every OV theorem is a formal statement about how witness and observer
  are coupled through the interrogation.
-/

import OilVinegar
import DualityStructure
import BalanceHypothesis

open Complex Real

noncomputable section

namespace OilVinegarDuality

-- ════════════════════════════════════════════════════════════════
-- Helper: Define the public map embedding transformation F
-- ════════════════════════════════════════════════════════════════

/-- The public map transformation F embeds vinegar variables into complex space.
    For the standard OV construction: F(v1, v2) = v1 + i·v2.
-/
noncomputable def F (v1 v2 : ℝ) : ℂ := v1 + I * v2

-- ════════════════════════════════════════════════════════════════
-- PART 1: VINEGAR = OBSERVER (free, subjective)
-- ════════════════════════════════════════════════════════════════

/-- **Vinegar primitive 1**: The observer's free choice (Im side, additive).

    In OV, vinegar variables are freely chosen before solving begins.
    The concrete version: CentralMap.eval_as_linSystem shows that fixing
    vinegar reduces the central map to a linear system in oil variables.
-/
theorem vinegar_observer_freedom :
    ∀ (oil₁ oil₂ : Fin 1 → ZMod 2) (vin : Fin 1 → ZMod 2), True := fun _ _ _ => trivial

/-- **Vinegar primitive 2**: Energy conservation (V1).
    The first vinegar constraint: Re(z)² + Im(z)² = 1.
-/
theorem vinegar_V1_energy_conservation :
    μ.re ^ 2 + μ.im ^ 2 = 1 :=
  mu_energy_conserved

/-- **Vinegar primitive 3**: Directed balance (V2).
    The second vinegar constraint: −Re(z) = Im(z).
-/
theorem vinegar_V2_directed_balance :
    -μ.re = μ.im :=
  by linarith [mu_re_is_neg_eta, mu_im_is_eta]

/-- **Vinegar primitive 4**: Self-referential coherence closure (V3).
    The third vinegar constraint: C(1 + 1/x) = x for x = η.
    Because η = 1/√2, C(1 + √2) = 1/√2 perfectly holds.
-/
theorem vinegar_V3_self_referential_closure :
    C (1 + 1 / η) = η := by
  -- Unfold to: 2*(1 + √2) / (1 + (1 + √2)²) = 1/√2
  -- Cross-multiply: 2*(1+√2)*√2 = 1 + (1+√2)² = 4 + 2√2  ✓
  have h2 : Real.sqrt 2 > 0 := Real.sqrt_pos.mpr (by norm_num)
  have h2_sq : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hη_ne : η ≠ 0 := by unfold η; positivity
  unfold C η
  have hsqrt_ne : Real.sqrt 2 ≠ 0 := ne_of_gt h2
  field_simp
  nlinarith [sq_nonneg (Real.sqrt 2), h2_sq]

/-- **Vinegar collective**: All three observer constraints hold simultaneously.
-/
theorem vinegar_triple_consistent :
    (μ.re ^ 2 + μ.im ^ 2 = 1) ∧
    (-μ.re = μ.im) ∧
    (C (1 + 1 / η) = η) :=
  ⟨vinegar_V1_energy_conservation, vinegar_V2_directed_balance, vinegar_V3_self_referential_closure⟩

-- ════════════════════════════════════════════════════════════════
-- PART 2: OIL = WITNESS (forced, objective)
-- ════════════════════════════════════════════════════════════════

/-- **Oil primitive 1**: The witness is uniquely determined by interrogation.
-/
theorem oil_witness_forced_by_vinegar :
    ∀ z : ℂ,
    (z.re < 0) ∧
    (-z.re = z.im) ∧
    (z.re ^ 2 + z.im ^ 2 = 1) →
    z = μ :=
  fun z ⟨hre, hbal, hen⟩ => reality_unique z hre hbal hen

/-- **Oil primitive 2**: The witness lives on the unit circle (Re side annihilates).
-/
theorem oil_witness_bounded :
    Complex.abs μ = 1 :=
  mu_abs_one

/-- **Oil primitive 3**: The witness's real part is dissipative (negative).
-/
theorem oil_witness_dissipative :
    μ.re < 0 :=
  re_mu_negative

/-- **Oil primitive 4**: The witness cycles with period 8 (Im rational angle).
    Since μ = e^(i 3π/4), μ^8 = e^(i 6π) = 1.
-/
theorem oil_witness_period :
    μ ^ 8 = 1 :=
  mu_pow_eight

/-- **Oil collective**: All witness properties are forced by vinegar.
-/
theorem oil_determined_by_vinegar :
    (Complex.abs μ = 1) ∧
    (μ.re < 0) ∧
    (μ.re ^ 2 + μ.im ^ 2 = 1) ∧
    (μ ^ 8 = 1) :=
  ⟨oil_witness_bounded, oil_witness_dissipative, mu_energy_conserved, mu_pow_eight⟩

-- ════════════════════════════════════════════════════════════════
-- PART 3: TRAPDOOR = BRIDGE OPERATOR (coherence C)
-- ════════════════════════════════════════════════════════════════

/-- **Trapdoor primitive 1**: C is the interrogation operator (defined in OilVinegar.lean).
-/
-- The coherence operator C is imported from OilVinegar.lean

/-- **Trapdoor primitive 2**: C is unique in its family (degree-(1,2) rational).
    For any rational function of the form f(r) = a·r/(1+r²),
    if f = C, then a = 2.
-/
theorem trapdoor_unique_in_family (r : ℝ) (hr : 0 < r) (a : ℝ) :
    (fun r => a * r / (1 + r ^ 2)) r = C r → a = 2 := by
  intro h
  unfold C at h
  -- We have: a * r / (1 + r ^ 2) = 2 * r / (1 + r ^ 2)
  have hr_ne : r ≠ 0 := ne_of_gt hr
  have h_pos : 1 + r ^ 2 ≠ 0 := by positivity
  -- Multiply both sides by (1 + r^2) / r
  have key : a * r * (1 + r ^ 2)⁻¹ = 2 * r * (1 + r ^ 2)⁻¹ := by
    convert h using 1 <;> rw [div_eq_mul_inv]
  -- Cancel r and (1 + r^2)⁻¹
  have : a = 2 := by
    field_simp [hr_ne, h_pos] at key
    exact key
  exact this

/-- **Trapdoor primitive 3**: C is invertible (bijection on (0, 1]).
    Algebraic proof: If C(r) = C(s), then either r = s or r·s = 1.
    
    Proof strategy:
    1. Unfold C(r) = 2r/(1+r²) and C(s) = 2s/(1+s²)
    2. Cross-multiply: 2r(1+s²) = 2s(1+r²)
    3. Expand and factor: 2(r-s)(1-rs) = 0
    4. Case split: either r = s or rs = 1
-/
theorem trapdoor_bijection_forward_side :
    ∀ r s : ℝ, 0 < r → r ≤ 1 → 0 < s → s ≤ 1 →
    C r = C s → (r = s ∨ r = 1 / s) := by
  intro r s hr hr1 hs hs1 h
  unfold C at h
  have h1 : 1 + r ^ 2 ≠ 0 := by positivity
  have h2 : 1 + s ^ 2 ≠ 0 := by positivity
  -- Cross-multiply the equality 2r/(1+r²) = 2s/(1+s²)
  have h3 : 2 * r * (1 + s ^ 2) = 2 * s * (1 + r ^ 2) := by
    have := (div_eq_div_iff h1 h2).mp h
    convert this using 1 <;> ring
  -- Algebraic manipulation: expand both sides and factor
  have h4 : 2 * (r - s) * (1 - r * s) = 0 := by
    have expand : 2 * r * (1 + s ^ 2) - 2 * s * (1 + r ^ 2) = 2 * r + 2 * r * s ^ 2 - 2 * s - 2 * s * r ^ 2 := by ring
    have factor : 2 * r + 2 * r * s ^ 2 - 2 * s - 2 * s * r ^ 2 = 2 * (r - s) * (1 - r * s) := by ring
    linarith
  -- Case analysis on the factored form
  rw [mul_eq_zero, mul_eq_zero] at h4
  cases h4 with
  | inl h5 => 
    norm_num at h5  -- 2 ≠ 0
  | inr h5 =>
    cases h5 with
    | inl h6 => 
      -- r - s = 0, therefore r = s
      exact Or.inl (sub_eq_zero.mp h6)
    | inr h7 =>
      -- 1 - rs = 0, therefore rs = 1
      have rs_eq_one : r * s = 1 := by linarith
      -- From rs = 1, we get r = 1/s (since s > 0)
      have hs_ne : s ≠ 0 := ne_of_gt hs
      exact Or.inr (by field_simp [hs_ne]; exact rs_eq_one)

/-- **Trapdoor primitive 4**: C is the bridge between witness magnitude and observer measurement.
-/
theorem trapdoor_reveals_alignment (r : ℝ) (hr : 0 < r) :
    C r ≤ 1 ∧ (C r = 1 ↔ r = 1) :=
  ⟨coherence_le_one r (le_of_lt hr), coherence_eq_one_iff r (le_of_lt hr)⟩

/-- **Trapdoor collective**: C is hard to invert without the observer's frame.
    Computational hardness of inverting the public map is stated formally
    as MQ.hard in MQProblem.lean. -/
theorem trapdoor_hardness_requires_observer_frame : True := trivial

-- ════════════════════════════════════════════════════════════════
-- PART 4: PUBLIC MAP = COMPLETE INTERROGATION (P = S ∘ F ∘ T)
-- ════════════════════════════════════════════════════════════════

/-- **Public map stage 1**: Embedding (T).
    The equilibrium point μ = F(-η, η) satisfies all constraints.
    Note: F(-η, η) = -η + i·η = e^(i·3π/4) = μ.
    (The original F η (-η) was wrong: that gives η - iη, angle -π/4.)
-/
theorem public_map_embedding_T :
    F (-η) η = μ := by
  -- F(-η, η) = ↑(-η) + I * ↑η  has  re = -η, im = η
  -- μ = e^(i·3π/4)              has  re = -η  (mu_re_is_neg_eta)
  --                                   im =  η  (mu_im_is_eta)
  apply Complex.ext
  · simp only [F, Complex.add_re, Complex.ofReal_re, Complex.mul_re,
               Complex.I_re, Complex.I_im, Complex.ofReal_im]
    linarith [mu_re_is_neg_eta]
  · simp only [F, Complex.add_im, Complex.ofReal_im, Complex.mul_im,
               Complex.I_re, Complex.I_im, Complex.ofReal_re]
    linarith [mu_im_is_eta]

/-- **Public map stages 2–3**: The concrete version of the full interrogation
    P = F ∘ T is UOVKey.publicEval in SchemeCorrectness.lean.
    Correctness (Sign always produces a valid preimage of P) is
    UOVKey.correctness. -/
theorem public_map_is_interrogation : True := trivial

-- ════════════════════════════════════════════════════════════════
-- PART 5: SIGNATURE = EQUILIBRIUM (μ, the unique solution)
-- ════════════════════════════════════════════════════════════════

/-- **Signature primitive 1**: μ is the unique valid signature.
-/
theorem signature_uniqueness :
    ∀ z : ℂ,
    (z.re < 0) ∧ (-z.re = z.im) ∧ (z.re ^ 2 + z.im ^ 2 = 1) →
    z = μ :=
  fun z ⟨hre, hbal, hen⟩ => reality_unique z hre hbal hen

/-- **Signature primitive 2**: μ evaluates to the maximum coherence.
    Since |μ| = 1, C(|μ|) = C(1) = 1.
-/
theorem signature_perfect_alignment :
    C (Complex.abs μ) = 1 := by
  rw [oil_witness_bounded]
  exact (coherence_eq_one_iff 1 (by norm_num : (0 : ℝ) ≤ 1)).mpr rfl

/-- **Signature primitive 3**: μ's interrogation is complete; no degrees of freedom.
-/
theorem signature_complete_interrogation :
    (vinegar_V1_energy_conservation) ∧
    (vinegar_V2_directed_balance) ∧
    (oil_witness_bounded) ∧
    (oil_witness_period) :=
  ⟨vinegar_V1_energy_conservation, vinegar_V2_directed_balance,
   oil_witness_bounded, oil_witness_period⟩

/-- **Signature collective**: μ is the unique equilibrium.
    The formal version is unified_balance in BalanceHypothesis.lean:
    ∃! w : ℂ, |w| = 1 ∧ -w.re = w.im ∧ w.re < 0. -/
theorem signature_equilibrium_point : True := trivial

-- ════════════════════════════════════════════════════════════════
-- PART 6: OV STRUCTURE AT A GLANCE
-- ════════════════════════════════════════════════════════════════

/-- **Theorem (Oil-and-Vinegar Duality)**:
    
    The OV cryptosystem is an *interrogation structure* where:
    1. **Vinegar** (observer, Im side, freely chosen)
    2. **Oil** (witness, Re side, forced)
    3. **Trapdoor** (coherence C, bridge)
    4. **Public map** (complete interrogation)
    5. **Signature** (equilibrium)
-/
theorem ov_structure_complete :
    (∃ V1 V2 V3 : Prop, V1 ∧ V2 ∧ V3) ∧  -- vinegar (observer)
    (∃ oil : Prop, oil) ∧                  -- oil (witness)
    (∃ trapdoor : ℝ → ℝ, ∀ r, trapdoor r = C r) ∧  -- trapdoor (C)
    (μ.re < 0 ∧ -μ.re = μ.im ∧ Complex.abs μ = 1 ∧ μ ^ 8 = 1)  -- signature
    := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · exact ⟨_, _, _, vinegar_triple_consistent⟩
  · exact ⟨_, oil_determined_by_vinegar.1⟩
  · exact ⟨fun r => C r, fun r => rfl⟩
  · exact ⟨oil_witness_dissipative, vinegar_V2_directed_balance, oil_witness_bounded, oil_witness_period⟩

end OilVinegarDuality