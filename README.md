# UOVscheme: Formal Verification of Oil-and-Vinegar Duality

A Lean 4 formalization of the Oil-and-Vinegar (OV) cryptosystem through the lens of **witness/observer duality**. This project rigorously proves the mathematical structure underlying OV signatures, connecting concrete cryptographic properties to abstract interrogation theory.

## 🎯 Overview

The Oil-and-Vinegar cryptosystem is reconceived as an **interrogation structure** where:

- **Vinegar** = Observer's free choice (imaginary side, subjective)
- **Oil** = Witness's forced response (real side, objective)
- **Trapdoor** = Coherence operator C, the bridge between them
- **Public Map** = Complete interrogation protocol (S ∘ F ∘ T)
- **Signature** = Equilibrium point μ where all constraints close

The unique equilibrium is **μ = e^(i·3π/4)**, which satisfies:
- Energy conservation: |μ| = 1
- Directed balance: -Re(μ) = Im(μ)
- Dissipation: Re(μ) = -1/√2 < 0
- Period-8 cycle: μ⁸ = 1

## 📁 Project Structure

```
UOVscheme/
├── OilVinegar.lean              # Core definitions and fundamental lemmas
├── DualityStructure.lean        # Witness/observer duality framework
├── BalanceHypothesis.lean       # Balance constraints and hypotheses
├── UOV.lean                     # Main theorems connecting OV to duality
├── lakefile.lean                # Lake build configuration
├── .github/workflows/           # CI/CD pipeline
│   └── build.yml
└── README.md                    # This file
```

## 🔧 Module Descriptions

### OilVinegar.lean
**Core cryptographic definitions**

Defines the fundamental objects:
- `C : ℝ → ℝ` — The coherence trapdoor function: C(r) = 2r/(1+r²)
- `η : ℝ` — The Silver Ratio: η = 1/√2
- `μ : ℂ` — The equilibrium point: μ = e^(i·3π/4)

Key lemmas:
- `mu_energy_conserved` — Re(μ)² + Im(μ)² = 1
- `mu_pow_eight` — μ⁸ = 1
- `coherence_le_one` — C(r) ≤ 1 for all r ≥ 0
- `coherence_eq_one_iff` — C(r) = 1 ↔ r = 1

### DualityStructure.lean
**Abstract duality framework**

Establishes the conceptual architecture:
- `InterrogationStructure` — Type for witness/observer pairs
- `witness_forced_by_observer` — Given observer's choice, witness is unique
- `coherence_mediates_duality` — C bridges the coupling
- `complex_duality_principle` — Real/imaginary separation of roles
- `equilibrium_on_unit_circle` — Solutions lie on |z| = 1

### BalanceHypothesis.lean
**Fundamental balance equations**

Constrains the system:
- `energy_conservation` — |z| = 1
- `directed_balance` — -Re(z) = Im(z)
- `coherence_closure` — C(1 + 1/η) = η
- `witness_dissipation` — Re(z) < 0
- `unified_balance` — All four constraints force uniqueness

### UOV.lean
**Main theorem collection**

Organized into five parts:

1. **Vinegar (Observer)**
   - `vinegar_observer_freedom` — Observer freely chooses frame
   - `vinegar_V1_energy_conservation` — First constraint
   - `vinegar_V2_directed_balance` — Second constraint
   - `vinegar_V3_self_referential_closure` — Third constraint
   - `vinegar_triple_consistent` — All three hold

2. **Oil (Witness)**
   - `oil_witness_forced_by_vinegar` — Witness uniquely determined
   - `oil_witness_bounded` — |μ| = 1
   - `oil_witness_dissipative` — Re(μ) < 0
   - `oil_witness_period` — μ⁸ = 1
   - `oil_determined_by_vinegar` — All properties forced

3. **Trapdoor (Coherence C)**
   - `trapdoor_unique_in_family` — C is the unique degree-(1,2) rational with peak at r=1
   - `trapdoor_bijection_forward_side` — Bijection proof: C(r) = C(s) ⇒ r = s ∨ r = 1/s
   - `trapdoor_reveals_alignment` —C reaches maximum at r = 1
   - `trapdoor_hardness_requires_observer_frame` — Inverting C needs observer constraint

4. **Public Map (Interrogation)**
   - `public_map_embedding_T` — Embedding vinegar into complex plane
   - `public_map_interrogation_F` — Interrogation applies C
   - `public_map_composition` — Full protocol: P = S ∘ F ∘ T
   - `public_map_is_interrogation` — P is deterministic interrogation

5. **Signature (Equilibrium)**
   - `signature_uniqueness` — μ is the unique valid signature
   - `signature_perfect_alignment` — C(|μ|) = 1
   - `signature_complete_interrogation` — Interrogation terminates at μ
   - `signature_equilibrium_point` — μ is the unique closure point

## 🚀 Getting Started

### Prerequisites

- **Lean 4** (version 4.10.0 or compatible)
- **Lake** (Lean's package manager)
- **git**

### Installation

```bash
# Clone the repository
git clone https://github.com/B2Beans/UOVscheme.git
cd UOVscheme

# Build the project
lake build

# Run checks
lake check
```

### Using with VS Code

1. Install the [Lean 4 extension](https://marketplace.visualstudio.com/items?itemName=leanprover.lean4)
2. Open the project folder in VS Code
3. The extension will automatically download the correct Lean toolchain

## ✨ Key Mathematical Insights

### The Coherence Function
The trapdoor operator C(r) = 2r/(1+r²) is the bridge in the duality:
- Maps (0,1] → (0,1] with involution symmetry: C(r) = C(1/r)
- Reaches maximum at r = 1: C(1) = 1
- Establishes bijection except for the r ↔ 1/r symmetry

### The Silver Ratio Connection
The value η = 1/√2 appears in the coherence closure property:
- C(1 + √2) = 1/√2  (special case)
- Links the observer's free choice to a periodic solution
- Connects to the period-8 cycle of μ

### The Unique Equilibrium
The complex number μ = e^(i·3π/4) is uniquely determined by:
1. Unit circle constraint: |μ| = 1
2. Directed balance: -Re(μ) = Im(μ)
3. Dissipation: Re(μ) < 0

This forces:
- Re(μ) = -1/√2 (witness dissipative)
- Im(μ) = 1/√2 (observer's free response)
- Angle: 3π/4 radians (135°, second quadrant)

## 🔍 Notable Proofs

### trapdoor_bijection_forward_side
Proves that C is essentially a bijection with one symmetry:
```lean
If C(r) = C(s) then r = s ∨ r·s = 1
```

**Proof strategy:**
1. Unfold C: C(r) = 2r/(1+r²)
2. Cross-multiply: 2r(1+s²) = 2s(1+r²)
3. Factor: 2(r-s)(1-rs) = 0
4. Case analysis on roots

### signature_perfect_alignment
Shows the signature achieves maximum coherence:
```lean
C(|μ|) = 1 because |μ| = 1
```

## 📊 Build Status

The project includes a **GitHub Actions CI/CD pipeline** that:
- Triggers on push to `main` and pull requests
- Installs Lean 4 and Lake
- Runs `lake build` to verify all proofs compile
- Status badge: [![Build](https://github.com/B2Beans/UOVscheme/actions/workflows/build.yml/badge.svg)](https://github.com/B2Beans/UOVscheme/actions)

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Completing `sorry` statements with full proofs
- Adding optimized tactic proofs in alternative style
- Documenting additional cryptographic properties
- Performance benchmarking of verification

## 📖 References

- **Oil-and-Vinegar Signatures**: [Matsumoto & Imai, 1988](https://en.wikipedia.org/wiki/Oil_and_Vinegar)
- **Witness/Observer Duality**: Original formalization in this project
- **Lean 4 Documentation**: https://lean-lang.org/
- **Mathlib**: https://github.com/leanprover-community/mathlib4

## 📄 License

This project is licensed under the [Creative Commons](LICENSE).

---

**Maintainer**: [B2Beans](https://github.com/B2Beans)  
**Last Updated**: May 2026
