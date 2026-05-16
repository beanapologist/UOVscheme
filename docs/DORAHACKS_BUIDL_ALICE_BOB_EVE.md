# DoraHacks BUIDL — AWS Activate Program for Web3 Startups

**Track:** Infrastructure / Middleware (Tier 1)  
**Prize pool:** Up to $10,000 in AWS credits (per program rules)

**Repository:** [github.com/beanapologist/UOVscheme](https://github.com/beanapologist/UOVscheme)

**NIST Round 3 / FIPS vs UOV (sizes, benchmarks, gas):** [PQC_NIST_AND_BENCHMARKS.md](PQC_NIST_AND_BENCHMARKS.md) · selection report [NIST IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf)

---

## Project name

**SilentVerify** — post-quantum-capable **state certificates**: compact UOV signatures checked with a single public-map evaluation **P(σ) = y**, aligned with the machine-checked Lean 4 corpus in **UOVscheme**. **RootCert** names the binding story: canonical state bytes → hash → digest **y** → UOV. The digest lives in **GF(q)^o** (field-theoretic output space of the public map).

---

## Alice, Bob, and Eve (how SilentVerify works)

**Alice (issuer)** runs the **signing** side once she has a UOV **secret** key: central map **F**, invertible mix **T**, and **T⁻¹**. A *state claim* is turned into a vector **y ∈ GF(q)^o** — for example by hashing canonical chain bytes (**RootCert** path: state → bytes → hash → field expansion). Alice samples **vinegar**, solves the induced **linear** system for **oil**, and returns **σ = T⁻¹(oil ‖ vinegar)**. She can publish the **public** map **P = F ∘ T** (and the rest of the public key material) without ever handing out **T⁻¹** or her oil–vinegar split.

**Bob (verifier)** is *any* counterparty — another chain, a wallet, an indexer, a compliance bot. Bob **never** runs chain execution as a “validator.” He performs **one stateless read**: evaluate the public quadratic map at **σ** and check **P(σ) = y**. If it matches, the certificate is cryptographically consistent with the embedded public key and the digest **y**; if not, he rejects. That is the **SilentVerify** posture: verification shaped like a **read**, not a live consensus role.

**Eve (forger)** sees only **P** and a target digest **y**. To forge a valid **σ** without the trapdoor, she must solve a system that *looks like* random multivariate quadratics — the **MQ** viewpoint. The Lean security story (`UOVSecurity.lean`, `MQProblem.lean`) states EUF-CMA-style conclusions **from explicit axioms** (MQ hardness, reduction layer); those axioms are not `sorry`, but they are not proven from pure logic alone.

**Takeaway:** Alice and Bob split **issuance** vs **verification**; Eve’s best path is assumed hard. SilentVerify packages **(y, σ)** plus **public** key JSON so Bob’s check is portable across ecosystems.

---

## Elevator pitch (one paragraph)

SilentVerify is **not** a validator; it is a **verifier-shaped service**. Issuance needs the secret key; verification needs **only** public parameters and one evaluation **P(σ) = y**. No chain-specific circuit is required at verify time. Trust is anchored in standard cryptographic assumptions (recorded as axioms in Lean where the probabilistic story is not yet fully formalized), not in “no assumptions” colloquially.

---

## What is machine-checked here (no `sorry`)

- Algebraic **correctness** of UOV signing vs verification — `SchemeCorrectness.lean` (`correctness`, `sign_then_verify`).
- **Linearization** of the central map after fixing vinegar — `CentralMap.lean` (`eval_as_linSystem`).
- Duality / balance lemmas — `OilVinegar.lean`, `BalanceHypothesis.lean`, `UOV.lean`.
- CRT encode/decode as a **bijective** synchrony story — `CRTBridge.lean`.
- EUF-CMA **statement** from explicit axioms — `UOVSecurity.lean` + `MQProblem.lean`.

---

## Problem

Cross-ecosystem state is cheap to **emit** but expensive to **trust**: bridges (custody / multisig risk), light clients (cost / chain-specific proofs), and “run a full node” (ops burden). A **portable certificate** that separates **issuance** (Alice) from **verification** (Bob) is natural middleware.

---

## Solution: state certificate = (y, σ) + public key material

1. **Bind** — Canonicalize state → bytes → **y** (domain-separated hashing; see `impl/python/uov/message_hash.py` and `impl/python/statecert/` for multi-chain anchors).
2. **Issue (Alice)** — UOV sign **y** → **σ** (vinegar draw → linear solve → **T⁻¹**).
3. **Verify (Bob)** — Check **P(σ) = y** with **public** data only.

**Wire format:** `impl/python/uov/certificate.py` — schema **`silentverify.state_cert/v1`**; legacy read: **`fieldcert.state_cert/v1`**, **`eigenverse.state_cert/v1`**.

---

## Witness / observer duality (same story, different vocabulary)

| UOV (crypto) | Alice / Bob / Eve lens | Lean module |
|--------------|------------------------|-------------|
| Vinegar | Alice’s *observer frame* (randomized choice that linearizes the system) | `CentralMap.lean`, `DualityStructure.lean` |
| Oil | Alice’s *witness response* (solved linear unknowns) | `CentralMap.eval_as_linSystem` |
| Central map **F** | Hidden structure Alice uses | `CentralMap.lean` |
| Public map **P = F ∘ T** | **All Bob ever sees** | `SchemeCorrectness.lean` (`publicEval`, `verify`) |
| Certificate **(y, σ)** | The portable object Alice gives the world | `Certificate.lean` |
| Forgery | **Eve** must invert **P** without the split | `UOVSecurity.lean`, `MQProblem.lean` |

CRT (`CRTBridge.lean`) is a **lossless** “two moduli, one class” story — pedagogically “two channels, one witness,” not a one-way bridge.

---

## Technical architecture (short)

**Lean 4 + Mathlib:** modules listed above; prime-field **ZMod q** in the reference formalization (distinct from NIST’s GF(2^k) UOV parameter packaging in the standard document).

**NIST context:** The **main** PQC Round 3 (2020–2022) standardized **Dilithium / Falcon / SPHINCS+** as **ML-DSA**, **FN-DSA**, and **SLH-DSA** (FIPS 204/206/205). Separately, [NIST IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf) records why **UOV** and eight other schemes advanced from **Additional Signatures Round 2 → Round 3** (May 2026). IR 8610 §3.11: UOV offers **very short σ** and **fast verification**, but **large public keys** and ongoing parameter hardening after wedge/small-field analysis. SilentVerify: check **P(σ) = y** off-chain. Full tables: [PQC_NIST_AND_BENCHMARKS.md](PQC_NIST_AND_BENCHMARKS.md).

**Python:** `impl/python/uov/` (UOV + certificates), `impl/python/statecert/` (anchors, multi-chain RPC helpers, verifier), tests under `impl/python/tests/`.

**On-chain posting (optional):** `contracts/evm/SilentVerifyAnchorRegistry.sol` — emit full wire or anchor **keccak256(wire)**; full UOV verify on-chain at production scale is a separate R&D track (SNARK / optimistic / oracle patterns). See `contracts/README.md`.

---

## AWS Activate fit (Tier 1 — infrastructure)

| Service | Use |
|---------|-----|
| EC2 (e.g. Graviton) | Batch signing / Gaussian elimination throughput |
| Lambda + API Gateway | Stateless **P(σ) ?=? y** verification endpoint |
| S3 | Published public keys + certificate blobs |
| CloudWatch | Latency / error budgets |

Optional Bedrock **only** for non-cryptographic analytics — never as the trust root for verification.

---

## Roadmap

| Phase | Deliverable |
|-------|-------------|
| **Now** | Lean correctness + security story; Python cert pipeline v1; static explainer site (`web/`) |
| **Next** | Broader on-chain anchoring / verifier prototypes consuming the same wire format |
| **Later** | Tighter Lean formalization of distributions (replace axioms where feasible) |

---

## Repository and build

- **Repo:** [UOVscheme](https://github.com/beanapologist/UOVscheme) — `lake build`, `impl/python` pytest, Foundry tests under `contracts/`.
- **Certificate schema:** `silentverify.state_cert/v1` — see `uov/certificate.py`.

---

## Honest assumptions (reviewer Q&A)

1. **Binding:** The meaning of “state” is in how **y** is derived (hash, domain separation, canonicalization). UOV proves **P(σ) = y**, not fork choice or social consensus.
2. **Security:** EUF-CMA in Lean uses **axioms** for the probabilistic layer and MQ hardness; see `UOVSecurity.lean`.
3. **CRT:** Bijective synchrony, not a hardness assumption.

---

*Draft for DoraHacks / BUIDL “Details” — technical source of truth remains the cited Lean and Python modules.*
