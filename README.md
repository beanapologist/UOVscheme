# UOVscheme: Formal Verification of Oil-and-Vinegar

A Lean 4 project with two layers:

1. **Duality formalization** — the original witness/observer lens on OV, proving properties of the coherence function `C`, the silver ratio `η`, and the equilibrium point `μ = e^(i·3π/4)`.
2. **Actual cryptographic formalization** — the UOV signature scheme over a finite field `ZMod q`, with a proved correctness theorem and a stated (but necessarily axiomatized) EUF-CMA security theorem.

---

## Alice, Bob, and Eve

**Key generation** (Alice runs this once):

Alice picks a random central map `F` (a set of `o` quadratic polynomials with no oil×oil terms) and a random invertible linear map `T`. She keeps both secret and publishes the composed map `P = F ∘ T` as her public key — `o` quadratic equations in `o+v` unknowns over `𝔽_q`.

**Signing** (Alice signs a message for Bob):

Alice wants to sign message `m` whose hash is `y = H(m) ∈ 𝔽_q^o`.

1. She picks random **vinegar** values `vin ∈ 𝔽_q^v` (her free choice — the observer's frame).
2. Substituting `vin` into `F` turns it affine-linear in the **oil** variables: `M(vin) · oil = y − b(vin)`.
3. She solves this linear system for `oil` (fast — it's Gaussian elimination, not quadratic).
4. She returns `σ = T⁻¹(oil ‖ vin)` as the signature.

Alice can sign efficiently because she knows the oil-vinegar structure. Without it, step 3 is a system of quadratic equations — the MQ problem.

**Verification** (Bob checks the signature):

Bob computes `P(σ)` using the public key and checks whether `P(σ) = H(m)`. One evaluation of `o` quadratic polynomials. Accept if equal, reject otherwise.

**Forgery attempt** (Eve tries to break the scheme):

Eve has `P` and a target `y = H(m)`. To forge she must find `σ` with `P(σ) = y` — exactly the MQ inversion problem on a random-looking system of `o` quadratic equations in `o+v` unknowns over `𝔽_q`. No efficient algorithm is known; the best attacks are exponential in `v` for typical parameters (e.g. `q=2, v=64`).

---

## The OV Trapdoor Matrix

The scheme has a natural Re/Im duality. Each column is a consistent world; the central map is the bridge between them.

| Oil-and-Vinegar (crypto) | bridge | Witness/Observer (duality) |
|---|:---:|---|
| Vinegar `vin ∈ 𝔽_q^v` | free choice | Observer's frame (Im side) |
| Oil `oil ∈ 𝔽_q^o` | forced response | Witness's reply (Re side) |
| Central map `F(oil, vin)` | evaluation | Coherence `C(r) = 2r/(1+r²)` |
| Fix vinegar → linear in oil | pins observer, forces witness | `M(vin) · oil = y − b(vin)` |
| Secret transform `T` | hides the split | Trapdoor |
| Public map `P = F ∘ T` | full interrogation | `μ` constraints close |
| Signature `σ : P(σ) = y` | equilibrium | `μ = e^(i·3π/4)` : all rows fire |
| Forging = inverting `P` | hard without split | MQ hardness assumption |

**Why Alice can sign but Eve cannot forge:**
Alice knows which variables are oil and which are vinegar (the Re/Im split). This turns `P(σ) = y` from a quadratic problem into a linear one. Eve only sees `P`, which looks like a random quadratic map — she has no way to recover the split without solving MQ.

---

## Project Structure

```
UOVscheme/
├── lakefile.lean
├── UOVscheme/                   # Lean source (all modules)
│   ├── OilVinegar.lean          #   C, η, μ and their properties (all proved)
│   ├── DualityStructure.lean    #   Abstract witness/observer framework
│   ├── BalanceHypothesis.lean   #   Four constraints + uniqueness theorem
│   ├── UOV.lean                 #   Duality lens applied to OV
│   ├── CentralMap.lean          #   Actual UOV map over ZMod q; linearization
│   ├── SchemeCorrectness.lean   #   UOVKey, Sign, Verify, correctness theorem
│   ├── SecurityModel.lean       #   Negligible, PPT (axiomatized)
│   ├── MQProblem.lean           #   MQ adversary, MQ.hard axiom
│   └── UOVSecurity.lean         #   EUF-CMA theorem (proved from two axioms)
└── Test/                        # Empirical tests (native_decide + #eval)
    ├── CentralMapTest.lean      #   Linearization checks over ZMod 7
    └── SchemeTest.lean          #   Sign/Verify round trips, forged sig rejection
```

---

## What Is Proved

### Duality layer (UOVscheme/OilVinegar.lean, UOVscheme/BalanceHypothesis.lean)

| Theorem | Statement |
|---|---|
| `mu_re_is_neg_eta` | `μ.re = −η` |
| `mu_im_is_eta` | `μ.im = η` |
| `mu_abs_one` | `|μ| = 1` |
| `mu_pow_eight` | `μ⁸ = 1` |
| `mu_energy_conserved` | `μ.re² + μ.im² = 1` |
| `coherence_le_one` | `C r ≤ 1` for `r > 0` |
| `coherence_eq_one_iff` | `C r = 1 ↔ r = 1` |
| `trapdoor_bijection_forward_side` | `C r = C s → r = s ∨ rs = 1` |
| `vinegar_V3_self_referential_closure` | `C(1 + 1/η) = η` |
| `reality_unique` | The three constraints uniquely determine `μ` |
| `unified_balance` | `∃! w : ℂ, |w| = 1 ∧ −w.re = w.im ∧ w.re < 0` |

### Cryptographic layer (UOVscheme/CentralMap.lean, UOVscheme/SchemeCorrectness.lean)

| Theorem | Statement |
|---|---|
| `CentralMapComp.eval_affine` | `F_k(oil, vin) = ⟨oil, linCoeff(vin)⟩ + vinConst(vin)` |
| `CentralMap.eval_as_linSystem` | `F(oil, vin) = M(vin) ·ᵥ oil + b(vin)` |
| `UOVKey.correctness` | Sign always produces a valid signature |
| `forgery_iff_mq_preimage` | A valid forgery iff `publicEval σ = y` |

### Security layer (UOVscheme/SecurityModel.lean, UOVscheme/UOVSecurity.lean)

| Theorem | Statement |
|---|---|
| `Negligible.of_le` | Negligibility is downward-closed |
| `Negligible.add` | Sum of negligible functions is negligible |
| `uov_euf_cma` | `Negligible (UOV.advantage A)` — proved from two axioms |

---

## What Is Axiomatized

| Axiom | Why it cannot be proved |
|---|---|
| `PPT`, `PPT.run`, `PPT.comp` | No Turing machine model is formalized |
| `MQ.advantage` | Requires probability distributions over key space |
| `MQ.hard` | Average-case MQ hardness — an open complexity assumption |
| `UOV.advantage` | Same as `MQ.advantage` |
| `uov_reduces_to_mq` | Requires showing UOV keys are pseudorandom among MQ instances |

The security proof `uov_euf_cma` uses exactly two cryptographic axioms (`MQ.hard` and `uov_reduces_to_mq`) and one proved lemma (`Negligible.of_le`). Everything else in the proof chain is a real theorem.

---

## Building

```bash
git clone https://github.com/beanapologist/UOVscheme
cd UOVscheme
lake build
```

Requires Lean 4 and Lake. Mathlib is fetched automatically.

---

## References

- Patarin, J. (1997). *The Oil and Vinegar Signature Scheme.* Dagstuhl Workshop on Cryptography.
- NIST PQC: UOV specification (2023 onward).
- Lean 4: https://lean-lang.org / Mathlib: https://leanprover-community.github.io
