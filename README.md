# UOVscheme: Formal Verification of Oil-and-Vinegar

[![Lean](https://github.com/beanapologist/UOVscheme/actions/workflows/lean.yml/badge.svg)](https://github.com/beanapologist/UOVscheme/actions/workflows/lean.yml)
[![Python](https://github.com/beanapologist/UOVscheme/actions/workflows/python.yml/badge.svg)](https://github.com/beanapologist/UOVscheme/actions/workflows/python.yml)
[![Pages](https://github.com/beanapologist/UOVscheme/actions/workflows/pages.yml/badge.svg)](https://github.com/beanapologist/UOVscheme/actions/workflows/pages.yml)
[![C++](https://github.com/beanapologist/UOVscheme/actions/workflows/cpp.yml/badge.svg)](https://github.com/beanapologist/UOVscheme/actions/workflows/cpp.yml)
[![Rust](https://github.com/beanapologist/UOVscheme/actions/workflows/rust.yml/badge.svg)](https://github.com/beanapologist/UOVscheme/actions/workflows/rust.yml)
[![Release](https://github.com/beanapologist/UOVscheme/actions/workflows/release.yml/badge.svg)](https://github.com/beanapologist/UOVscheme/actions/workflows/release.yml)

A Lean 4 project with two layers:

1. **Duality formalization** — the original witness/observer lens on OV, proving properties of the coherence function `C`, the silver ratio `η`, and the equilibrium point `μ = e^(i·3π/4)`.
2. **Actual cryptographic formalization** — the UOV signature scheme over a finite field `ZMod q`, with a proved correctness theorem and a stated (but necessarily axiomatized) EUF-CMA security theorem.

**Public mini-site:** static explainer + certificate JSON viewer in [`web/`](web/) — deploy free on **GitHub Pages** (see [`web/README.md`](web/README.md); enable *Settings → Pages → GitHub Actions*).

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

## Duality ↔ Cryptography (name map)

The **ℝ/ℂ** story (`OilVinegar.lean`, `BalanceHypothesis.lean`, `UOV.lean`) is a separate lens from the **finite-field** UOV construction (`CentralMap.lean`, `SchemeCorrectness.lean`, `UOVSecurity.lean`).  The table links narrative names in `UOV.lean` to the lemmas or axioms where the real mathematics lives.

| Narrative (`UOV.lean`) | Cryptographic counterpart |
|:---|:---|
| `vinegar_observer_linearizes` | Same statement as `CentralMap.eval_as_linSystem` — fixing vinegar, `F` is affine in oil |
| `trapdoor_hardness_mq` | Same content as axiom `MQ.hard` — average-case MQ / preimage hardness |
| `public_map_is_interrogation` | Definitional expansion of `UOVKey.publicEval` (`SchemeCorrectness.lean`) |
| `signature_equilibrium_point` | Theorem `BalanceHypothesis.unified_balance` — uniqueness of `μ` on `S¹` |
| Coherence `C`, silver ratio `η`, equilibrium `μ` | **Not** a substitute for a computational trapdoor; the actual trapdoor is `(F, T)` over `ZMod q` |
| `CRTBridge.encode` / `decode` | Mathlib `ZMod.chineseRemainder` — **bidirectional** CRT glue for coprime moduli (pedagogical “synchrony”; not one-way) |

Security of the signature scheme is still only as strong as the two axioms in `UOVSecurity.lean` (`uov_reduces_to_mq`, `MQ.hard`); see the expanded docstrings there and in `MQProblem.lean` for what a full formalization would have to prove.

---

## Project Structure

```
UOVscheme/
├── docs/                        # Hackathon / assessment write-ups
│   ├── README.md
│   ├── DORAHACKS_SUBMISSION.md  #   SilentVerify / RootCert (AWS Activate draft)
│   └── ASSESSMENT.md
├── branding/
│   └── silentverify-logo.png    #   SilentVerify + pen mark
├── contracts/                   # On-chain posting / verifier strategy (see contracts/README.md)
│   ├── README.md
│   ├── foundry.toml             #   forge test (AnchorRegistry + fixtures)
│   ├── evm/SilentVerifyAnchorRegistry.sol
│   ├── test/AnchorRegistry.t.sol
│   ├── test/fixtures/           #   state_cert_wire.json (regen: impl/python/scripts/gen_foundry_fixture.py)
│   └── cosmos/README.md
├── programs/silentverify/       # Solana posting patterns (README)
├── web/                         # Static consumer mini-site (GitHub Pages)
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── assets/silentverify-logo.png
│   └── README.md
├── lakefile.lean
├── UOVscheme/                   # Lean source (all modules)
│   ├── OilVinegar.lean          #   C, η, μ and their properties (all proved)
│   ├── DualityStructure.lean    #   Abstract witness/observer framework
│   ├── CRTBridge.lean           #   CRT as encode/decode (ZMod; pedagogical)
│   ├── BalanceHypothesis.lean   #   Four constraints + uniqueness theorem
│   ├── UOV.lean                 #   Duality lens applied to OV
│   ├── CentralMap.lean          #   Actual UOV map over ZMod q; linearization
│   ├── SchemeCorrectness.lean   #   UOVKey, Sign, Verify, correctness, sign_then_verify
│   ├── Certificate.lean         #   StateCertificate bundle (Lean)
│   ├── SecurityModel.lean       #   Negligible, PPT (axiomatized)
│   ├── MQProblem.lean           #   MQ adversary, MQ.hard axiom
│   └── UOVSecurity.lean         #   EUF-CMA theorem (proved from two axioms)
├── Test/                        # Empirical tests (native_decide + #eval)
│   ├── CentralMapTest.lean
│   ├── SchemeTest.lean
│   └── CertificateTest.lean
└── impl/                        # Runnable implementations
    ├── python/                  # Pure-Python (no dependencies)
    │   ├── uov/                 #   Core UOV: field, central_map, scheme, keygen, certificate
    │   ├── statecert/           #   SilentVerify: anchors, digests, evm/solana/cosmos RPC, verifier
    │   ├── demos/               #   silentverify_demo.py — end-to-end walkthrough
    │   ├── examples/            #   demo.py (Alice/Bob/Eve), issue_certificate_demo.py
    │   └── tests/               #   pytest (uov + statecert + certificates)
    ├── cpp/                     # C++17 header-only library
    │   ├── include/uov/         #   field.hpp, central_map.hpp, scheme.hpp, keygen.hpp
    │   ├── src/demo.cpp         #   Alice/Bob/Eve walkthrough
    │   ├── tests/               #   13 ctest tests (all green)
    │   └── CMakeLists.txt
    └── rust/                    # Rust crate (no external dependencies)
        ├── src/                 #   field, central_map, scheme, keygen modules
        ├── examples/demo.rs     #   Alice/Bob/Eve walkthrough
        ├── tests/correctness.rs #   15 cargo tests (all green)
        └── Cargo.toml
```

### Running the implementations

**Python** (requires Python 3.8+, pytest optional):
```bash
cd impl/python
python examples/demo.py          # Alice/Bob/Eve (cryptographic walkthrough)
python demos/silentverify_demo.py   # SilentVerify: CRT → chain state → cert → verify
python -m pytest tests/ -v       # Full pytest suite
```

**Multi-chain anchors (stdlib RPC):** build canonical objects, then `StateVerifier.issue_for_anchor` (or the typed helpers):

| Stack | Fetcher | Anchor type |
|-------|---------|-------------|
| EVM | `statecert.fetch_chain_state_evm` | `ChainState` (`eip155:…`, `state_root_hex`) |
| Solana | `statecert.fetch_solana_commitment` | `SolanaCommitment` (cluster, slot, blockhash b58) |
| Cosmos (Tendermint LCD) | `statecert.fetch_cosmos_commitment` | `CosmosCommitment` (chain id, height, `app_hash`) |

Cross-ecosystem pairs use `CrossL1Commitment` + `issue_for_cross_l1`. Intra-chain stepping uses `issue_for_intra_solana` / `issue_for_intra_cosmos` (or existing EVM `issue_for_intra_chain`).

**On-chain posting / verifier options:** see [`contracts/README.md`](contracts/README.md) — EVM registry `contracts/evm/SilentVerifyAnchorRegistry.sol` (`postFullWire` vs `postCommitmentOnly`), plus Solana / Cosmwasm notes under `programs/silentverify/` and `contracts/cosmos/`. Full UOV verification on-chain at production parameters is expected to use optimistic, SNARK, or oracle patterns rather than naive bytecode.

**C++** (requires CMake 3.14+, C++17 compiler):
```bash
cd impl/cpp && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$(nproc)
./uov_demo          # demo
ctest               # 13 tests
```

**Rust** (requires Rust 2021 edition / cargo):
```bash
cd impl/rust
cargo run --example demo   # demo
cargo test                 # 15 tests
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
| `MQ.hard` | Average-case MQ hardness — **standard cryptographic assumption**, not a consequence of Lean's logic or of P ≠ NP alone.  Conceptually bundles a probability space, a success event, PPT adversaries, and negligibility; see the module doc at the top of `MQProblem.lean`. |
| `UOV.advantage` | Same as `MQ.advantage` |
| `uov_reduces_to_mq` | Requires distributions + pseudorandomness of UOV keys among MQ instances — **standard assumption**, spelled out as proof obligations in the axiom's docstring in `UOVSecurity.lean`. |

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

## CI/CD

Each component has its own GitHub Actions pipeline triggered by path filters so unrelated changes don't run unnecessary jobs.

| Workflow | Triggers on | What it checks |
|---|---|---|
| **GitHub Pages** | `web/**`, `.github/workflows/pages.yml` | Deploy static SilentVerify mini-site |
| **Lean** | `UOVscheme/**`, `lakefile.lean` | `lake build`, `sorry` scan |
| **Python** | `impl/python/**` | pytest × {3.9, 3.11, 3.12}, ruff lint + format, combined `uov`+`statecert` coverage ≥ 88% |
| **Foundry** | `contracts/**` | `forge test` on `SilentVerifyAnchorRegistry` + Python-generated wire fixture |
| **C++** | `impl/cpp/**` | cmake/ninja × {gcc, clang} × {Debug, Release}, ASAN+UBSAN, clang-tidy |
| **Rust** | `impl/rust/**` | cargo test × {stable, beta}, rustfmt, clippy -D warnings, Miri |
| **Release** | `v*` tag push | Packages Python wheel, C++ header zip, Rust `.crate` → GitHub Release |

### Creating a release

```bash
git tag v0.2.0
git push origin v0.2.0
```

The release workflow builds all three language artifacts, creates a GitHub Release with auto-generated notes, and attaches the packages as assets. Pre-release tags (e.g. `v0.2.0-rc1`) are automatically marked as pre-release.

---

## References

- Patarin, J. (1997). *The Oil and Vinegar Signature Scheme.* Dagstuhl Workshop on Cryptography.
- NIST PQC: UOV specification (2023 onward).
- Lean 4: https://lean-lang.org / Mathlib: https://leanprover-community.github.io
