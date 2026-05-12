# UOVscheme Assessment

## What this project is

A **Lean 4 formal verification project** that recasts the Oil-and-Vinegar (OV) cryptographic signature scheme through a "witness/observer duality" lens. It is *not* a cryptographic implementation — there is no executable signing, verification, or key generation code. All values are `noncomputable` and the ambient type is ℝ/ℂ rather than a finite field.

---

## Mathematical objects defined

| Name | Definition | Role claimed |
|------|-----------|--------------|
| `C : ℝ → ℝ` | `2r / (1 + r²)` | "Trapdoor" / coherence bridge |
| `η : ℝ` | `1 / √2` | "Silver ratio" |
| `μ : ℂ` | `exp(i · 3π/4)` | "Unique equilibrium / signature" |
| `F : ℝ → ℝ → ℂ` | `v₁ + i·v₂` | Vinegar embedding into ℂ |

---

## Proof inventory

### Complete proofs (11)

| Lemma / theorem | Statement | Notes |
|-----------------|-----------|-------|
| `mu_re_is_neg_eta` | `μ.re = -η` | Follows from `cos(3π/4)` |
| `mu_im_is_eta` | `μ.im = η` | Follows from `sin(3π/4)` |
| `mu_abs_one` | `|μ| = 1` | Standard `Complex.abs_exp` |
| `mu_pow_two` | `μ² = i` | Angle doubling |
| `mu_pow_four` | `μ⁴ = -1` | Via `mu_pow_two` |
| `mu_pow_eight` | `μ⁸ = 1` | Via `mu_pow_four` |
| `mu_energy_conserved` | `μ.re² + μ.im² = 1` | Via η² + η² = 1 |
| `re_mu_negative` | `μ.re < 0` | From `mu_re_is_neg_eta` |
| `coherence_one` | `C 1 = 1` | Immediate arithmetic |
| `coherence_eq_one_iff` | `C r = 1 ↔ r = 1` | Clean `nlinarith` proof |
| `trapdoor_bijection_forward_side` | `C r = C s → r = s ∨ r = 1/s` | Good algebraic factoring proof |
| `trapdoor_unique_in_family` | Identifies `a = 2` | Straightforward |
| `trapdoor_reveals_alignment` | Combines the two `C` lemmas | Trivially assembled |
| `vinegar_V2_directed_balance` | `-μ.re = μ.im` | Via `linarith` on the two main lemmas |
| Several collective theorems | Bundle of the above | No new content |

### Incomplete proofs — `sorry` stubs (9 substantive gaps)

| Location | What is missing | Severity |
|----------|----------------|----------|
| `reality_unique` (OilVinegar.lean:142) | Uniqueness of μ under three constraints | **High** — the main lemma driving `signature_uniqueness` and `oil_witness_forced_by_vinegar` |
| `coherence_le_one` (OilVinegar.lean:121) | `C r ≤ 1` | **High** — see bug section below |
| `vinegar_V3_self_referential_closure` | `C(1 + 1/η) = η` | Medium — algebraically true but not proved |
| `public_map_embedding_T` | `F η (-η) = μ` | Medium — see bug section below |
| `public_map_interrogation_F` | String-typed; vacuous | Low |
| `public_map_composition` | String-typed; vacuous | Low |
| `public_map_is_interrogation` | String-typed; vacuous | Low |
| `signature_equilibrium_point` | String-typed; vacuous | Low |
| `trapdoor_hardness_requires_observer_frame` | String-typed; vacuous | Low |
| `unified_balance` (BalanceHypothesis.lean:50) | Existence-uniqueness of constrained z | Medium |
| All four `DualityStructure` theorems | String-typed; vacuous | Low |

---

## Bugs and errors

### 1. `coherence_le_one` — broken calc chain (OilVinegar.lean:113–121)

```lean
lemma coherence_le_one (r : ℝ) (hr : 0 < r) : C r ≤ 1 := by
  ...
  calc 2 * r / (1 + r ^ 2)
    ≤ (1 + r ^ 2) ^ 2 / (1 + r ^ 2) := ...   -- establishes C r ≤ 1 + r²
    _ = 1 + r ^ 2 := by field_simp
    _ ≥ 1 := by nlinarith [sq_nonneg r]        -- shows 1 + r² ≥ 1, not ≤ 1
  sorry
```

The calc chain proves `C r ≤ 1 + r²` and `1 + r² ≥ 1`, which together say nothing about `C r ≤ 1`. The direction of the last step is wrong; the chain does not compose into the goal. The `sorry` is unavoidable here as written. A direct proof works cleanly:

```lean
lemma coherence_le_one (r : ℝ) (hr : 0 < r) : C r ≤ 1 := by
  unfold C
  rw [div_le_one (by positivity)]
  nlinarith [sq_nonneg (r - 1)]
```

### 2. `public_map_embedding_T` — theorem is false as stated (UOV.lean:212–219)

The theorem claims `F η (-η) = μ`, i.e., `η + i·(-η) = μ`.

- `F η (-η) = η - i·η`, which has argument `-π/4` (fourth quadrant, angle 315°).
- `μ = e^(i·3π/4)` has argument `135°` (second quadrant).

These are different complex numbers. The correct statement would be `F (-η) η = μ` (swap signs), or alternatively define F differently. As stated, no proof exists because the claim is false. The `sorry` is hiding an incorrect theorem.

### 3. Vacuous string-typed theorems

Lean 4 allows a string literal as a type. `"some text" : Type` is valid syntax; the string literal `"some text"` is simultaneously the type and its unique inhabitant. Any `sorry` for such a theorem is therefore trivially provable with `rfl`, and the theorem carries zero mathematical content.

Examples:
```lean
theorem trapdoor_hardness_requires_observer_frame :
    "Inverting C without knowing (Re < 0) is hard (conjectured)" := sorry
```
This proves nothing about hardness. Replace with a real Prop or remove entirely.

### 4. `BalanceHypothesis` hypotheses are vacuous or mistyped

```lean
hypothesis directed_balance : ∀ z : ℂ, -z.re = z.im → "Witness and observer are in opposite quadrants"
hypothesis coherence_closure : ∀ η : ℝ, "C(1 + 1/η) = η for the Silver Ratio η"
hypothesis witness_dissipation : ∀ z : ℂ, z.re < 0 → "Witness is in dissipative regime"
```

All three return string types, so they are trivially inhabited and assert nothing. `coherence_closure` also universally quantifies η over all reals — but the property only holds for η = 1/√2. The module provides no usable mathematical hypotheses.

### 5. `reality_unique` — key lemma is unproven (OilVinegar.lean:142)

This drives `signature_uniqueness` and `oil_witness_forced_by_vinegar`, the two "oil is determined" results. The proof is feasible (it reduces to a geometric argument: on the unit circle, Re < 0 and Im = -Re forces the angle to 3π/4), but requires connecting `Complex.abs` and `Complex.arg` machinery in Mathlib. Leaving it `sorry` means all downstream "uniqueness" results have no proof.

A sketch:
```lean
-- From z.re² + z.im² = 1 and -z.re = z.im:
-- substitute: z.re² + z.re² = 1 → z.re = ±1/√2
-- z.re < 0 forces z.re = -1/√2 = -η, z.im = η
-- Then z = ⟨-η, η⟩ = μ by mu_re_is_neg_eta, mu_im_is_eta and Complex.ext
```

---

## Conceptual gaps

### ℝ/ℂ instead of a finite field

Standard UOV (and NIST PQC variant UOV/MAYO/Rainbow variants) operates over a finite field 𝔽_q. The multivariate quadratic maps, key generation, and hardness of polynomial-system solving are all properties of finite field arithmetic. This formalization works entirely in ℝ and ℂ, which:
- Have no notion of polynomial system hardness.
- Admit transcendental functions (`exp`, `sin`, `cos`) that are meaningless in 𝔽_q.
- Do not correspond to any known OV instantiation.

The project is a mathematical structure *inspired by* OV rather than a formalization *of* OV.

### No cryptographic content

There is no:
- Key generation (sampling random polynomials in 𝔽_q[x₁…xₙ]).
- Signing (solving a linear system after fixing vinegar values).
- Verification (evaluating the public quadratic map).
- Hardness reduction (relating forgery to MQ-problem hardness).
- Hash function or message binding.

### The "trapdoor" `C(r) = 2r/(1+r²)` is not a cryptographic trapdoor

A cryptographic trapdoor is easy to compute, hard to invert without extra information, and efficiently invertible with the private key. `C` is a smooth function from ℝ to ℝ. Its inverse is explicitly computable (roots of the quadratic `r² - (2/c)r + 1 = 0`), so it offers no computational hardness. The theorem `trapdoor_hardness_requires_observer_frame` (which is also vacuous) gestures at hardness without establishing it.

---

## What the project does well

1. **Modular structure** — clear separation across four files with consistent namespacing.
2. **Correct proofs for the proofs that exist** — `trapdoor_bijection_forward_side`, `mu_pow_eight`, and the family of μ-properties are clean and complete.
3. **Good use of `noncomputable`** — correctly signals that no executable code is intended.
4. **CI pipeline** — GitHub Actions runs `lake build`, catching regressions.
5. **The algebraic identity `C(1 + √2) = 1/√2`** — mathematically correct and the coherence closure is a genuine (if aesthetically motivated) fixed-point property.

---

## Priority fixes

| Priority | Issue | Action |
|----------|-------|--------|
| P0 | `coherence_le_one` calc is broken | Replace with `div_le_one` + `nlinarith [sq_nonneg (r-1)]` |
| P0 | `public_map_embedding_T` is false | Fix sign: use `F (-η) η` or redefine F |
| P1 | `reality_unique` is unproven | Prove via `Complex.ext` + quadratic constraints |
| P1 | `vinegar_V3_self_referential_closure` | Prove numerically: `C(1 + √2) = 1/√2` |
| P2 | String-typed theorems | Replace with real Props or delete |
| P2 | `BalanceHypothesis` hypotheses | Fix return types to be actual propositions |
| P3 | Add finite-field abstraction | Align formalization scope with actual OV |
