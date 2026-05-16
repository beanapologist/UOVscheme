# DoraHacks BUIDL — AWS Activate Program for Web3 Startups

**Track:** Infrastructure / Middleware (Tier 1)  
**Prize pool:** Up to $10,000 in AWS credits (per program rules)

---

## Project name

**SilentVerify** — post-quantum-capable **state certificates**: compact UOV signatures checked with a single public-map evaluation \(P(\sigma) = y\), aligned with the machine-checked Lean 4 corpus in this repository (**UOVscheme**). **RootCert** names the binding story: canonical state bytes → hash → digest \(y\) → UOV. The proof object lives in **GF(q)^o** (field-theoretic digest space). **Logo:** [`../branding/silentverify-logo.png`](../branding/silentverify-logo.png).

**Alternate BUIDL “Details” narrative (Alice / Bob / Eve):** [DORAHACKS_BUIDL_ALICE_BOB_EVE.md](DORAHACKS_BUIDL_ALICE_BOB_EVE.md) — paste-friendly for DoraHacks.

**NIST PQC context & benchmarks:** [PQC_NIST_AND_BENCHMARKS.md](PQC_NIST_AND_BENCHMARKS.md) — main Round 3 → FIPS 204/205/206; **UOV in Additional Signatures Round 3** ([news](https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc), [IR 8610 PDF](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf)); byte sizes, gas, prime-field bench script.

---

## Elevator pitch

**SilentVerify** is **not** a validator; it is a **verifier-shaped service**. Verification is a **single stateless read**: \(P(\sigma) = y\) with the public map only — no validator role, no chain execution. For a chosen digest \(y \in \mathbb{F}_q^o\) (for example \(y = H(\text{canonical state bytes})\) — the **RootCert** binding path), the issuer who holds a UOV secret key produces a short signature \(\sigma\). Any counterparty checks **one** public predicate — **`publicEval` / \(P(\sigma) = y\)** — using only public parameters. No chain-specific circuit is required at verification time; trust is shifted to standard assumptions (MQ hardness and the axiomatized distribution layer spelled out in `UOVSecurity.lean`), **not** to “no assumptions” in the colloquial sense.

**What is machine-checked here (no `sorry`):** algebraic correctness of UOV (`SchemeCorrectness.lean`), linearization of the central map (`CentralMap.lean`), duality and balance lemmas (`OilVinegar.lean`, `BalanceHypothesis.lean`, `UOV.lean`), CRT encode/decode bijections (`CRTBridge.lean`), and the EUF-CMA **statement** conditional on explicit axioms (`UOVSecurity.lean` + `MQProblem.lean`). See **Honest assumptions** below.

---

## Problem

Cross-ecosystem state is cheap to *emit* but expensive to *trust*: bridges (custody / multisig risk), on-chain light clients (cost / chain-specific proofs), and “run a full node” (ops burden). A **portable certificate** that separates **issuance** (secret key + field arithmetic) from **verification** (public quadratic evaluation only) is a natural middleware primitive.

---

## Solution: state certificate = \((y, \sigma)\) + public key material

1. **Bind** a claim to \(y\) (e.g. hash-then-sign over a canonical encoding of state — domain-separated; see `impl/python/uov/message_hash.py`).
2. **Issue** \(\sigma\) with the UOV signing path (vinegar sample → linear solve → apply \(T^{-1}\)).
3. **Verify** \(P(\sigma) = y\) with the public map only.

The Lean layer proves **completeness**: legitimate signatures always verify (`correctness` / `sign_then_verify` in `SchemeCorrectness.lean`). The **issuance / verification pipeline** for interoperability is implemented in Python as versioned JSON: `impl/python/uov/certificate.py` (schema **`silentverify.state_cert/v1`**; legacy payloads **`fieldcert.state_cert/v1`** and **`eigenverse.state_cert/v1`** are still accepted on parse).

---

## Witness / observer duality (formal map)

| UOV (crypto) | Role | Lean module |
|--------------|------|----------------|
| Vinegar | Observer-chosen frame | `DualityStructure.lean`, `CentralMap.lean` |
| Oil | Witness response | `CentralMap.eval_as_linSystem` |
| Central map \(F\) | Coherence / interrogation | `CentralMap.lean` |
| Public map \(P = F \circ T\) | Verifier entry point | `SchemeCorrectness.lean` (`publicEval`, `verify`) |
| Certificate \((y,\sigma)\) | Equilibrium bundle | `Certificate.lean` (`StateCertificate`) |
| Balance \(\mu\) | Complex-analytic narrative anchor | `OilVinegar.lean`, `BalanceHypothesis.unified_balance` |

CRT (`CRTBridge.lean`) is a **lossless** “two moduli, one class” isomorphism for coprime moduli — pedagogically aligned with “two channels, one witness,” **not** a one-way bridge; see module docstring.

---

## Technical architecture

### Formal verification (Lean 4 + Mathlib)

| Module | What it contributes |
|--------|---------------------|
| `OilVinegar.lean` | \(\mu\), \(\eta\), coherence \(C\); `reality_unique`, `mu_abs_one`, … |
| `BalanceHypothesis.lean` | Packaged uniqueness `unified_balance` |
| `CentralMap.lean` | `eval_as_linSystem` |
| `SchemeCorrectness.lean` | `UOVKey`, `sign`, `verify`, `correctness`, **`sign_then_verify`** (alias); `sign` / `correctness` assume **`[Fact (Nat.Prime q)]`** (so `ZMod q` is a field and `det T ≠ 0` gives `IsUnit (det T)`) |
| `Certificate.lean` | `StateCertificate`, `isValid_iff`, `valid_of_sign` |
| `CRTBridge.lean` | `decode_encode`, `encode_bijective`, … |
| `UOVSecurity.lean` | `forgery_iff_mq_preimage`, `uov_euf_cma` (from axioms) |
| `MQProblem.lean`, `SecurityModel.lean` | Adversary types, `Negligible`, `MQ.hard` axiom |

**Axioms (cryptographic / probabilistic layer):** as documented in the repository README and in-file docstrings — e.g. `MQ.advantage`, `MQ.hard`, `UOV.advantage`, `uov_reduces_to_mq`. These are **explicit**; they are not `sorry`, but they are not proven from Lean’s logic alone.

### Implementations

- **Python** (`impl/python/uov/`): reference UOV + **JSON certificate** issuance/verification (`certificate.py`), tests in `impl/python/tests/`.
- **Rust / C++**: existing reference implementations (see `README.md`).

### NIST landscape & performance (reviewer cheat sheet)

| | ML-DSA (Dilithium) | FN-DSA (Falcon) | SLH-DSA (SPHINCS+) | UOV (`OV-Ip` / `OV-III`) |
|--|---------------------|-----------------|---------------------|---------------------------|
| NIST track | Main R3 → **FIPS 204** | Main R3 → **FIPS 206** | Main R3 → **FIPS 205** | **Additional sigs R3** ([May 2026](https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc)) |
| Typical |σ| (cat 1 / 3) | 2,420 / 3,309 B | 666 B (cat 1) | 7,856 / 16,224 B (SHA2-*s*) | **128 / 200 B** |
| Typical |pk| | ~1.3 / ~2.0 KB | ~0.9 KB (cat 1) | 32 / 48 B (+ huge σ) | **~272 KB / ~1.2 MB** (classic) |
| SilentVerify verify | N/A (not our primitive) | N/A | N/A | **One** public map eval **P(σ)=y** |
| On-chain (this repo) | EIP-8051 precompile (draft) | R&D | R&D | **Anchor hash only** — see [PQC_NIST_AND_BENCHMARKS.md](PQC_NIST_AND_BENCHMARKS.md) |

Full tables, CPU script, and gas discussion: **[PQC_NIST_AND_BENCHMARKS.md](PQC_NIST_AND_BENCHMARKS.md)**.

---

## AWS Activate fit (Tier 1 — infrastructure)

| Service | Use |
|---------|-----|
| EC2 (e.g. Graviton) | Batch signing / Gaussian elimination throughput |
| Lambda + API Gateway | Stateless `P(σ) ?=? y` verification endpoint |
| S3 | Published public keys + certificate objects |
| CloudWatch | Latency / error budgets |

Optional Bedrock only for **non-cryptographic** analytics (fraud / traffic patterns), never as a trust root for verification.

---

## Roadmap (concise)

| Phase | Deliverable |
|-------|-------------|
| **Now** | Lean correctness + security story; Python cert pipeline v1 |
| **Next** | On-chain verifier prototypes (EVM / Solana) consuming the same wire format |
| **Later** | Tighter Lean formalization of distributions (replace axioms where feasible) |

---

## Repository and build

- **This repo:** [UOVscheme](https://github.com/beanapologist/UOVscheme) — `lake build`, `impl/python` pytest.
- **Certificate schema:** `silentverify.state_cert/v1` — see `uov/certificate.py` (legacy read: `fieldcert.state_cert/v1`, `eigenverse.state_cert/v1`).

---

## Honest assumptions (reviewer Q&A)

1. **Binding:** The meaning of “state” lives in how \(y\) is derived from bytes (hash function, domain separation, canonicalization). The UOV proof is about **\(P(\sigma)=y\)**, not about fork choice or social consensus.
2. **Security:** EUF-CMA-style conclusion in Lean uses **axioms** for the probabilistic reduction and MQ hardness; see `UOVSecurity.lean`.
3. **CRT:** Bijective synchrony, not hardness; composes with the narrative, not with MQ inversion.

---

*Draft maintained for hackathon submission; technical source of truth is the Lean and Python modules cited above.*
