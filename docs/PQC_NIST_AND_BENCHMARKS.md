# NIST PQC landscape and benchmarks (UOV vs ML-DSA / FN-DSA / SLH-DSA)

This page is the **submission-facing** comparison for GitHub and DoraHacks materials. **“Round 3” appears twice in NIST messaging** — do not mix them:

1. **Main NIST PQC Round 3 (2020–2022)** — lattice and hash-based **finalists** (Dilithium, Falcon, SPHINCS+) selected for standardization.
2. **FIPS standards (2024–2025)** — those finalists became **ML-DSA** ([FIPS 204](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.204.pdf)), **SLH-DSA** ([FIPS 205](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.205.pdf)), and **FN-DSA** ([FIPS 206](https://csrc.nist.gov/pubs/fips/206/final)).
3. **Additional Digital Signatures for PQC** — a **separate** NIST program for new signature families. On **14 May 2026**, NIST [advanced nine candidates to that program’s third round](https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc), including **UOV**. The **second-round status report** — [NIST IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf) ([DOI 10.6028/NIST.IR.8610](https://doi.org/10.6028/NIST.IR.8610)) — documents evaluation criteria, per-candidate analysis (§3.11 for UOV), and why each scheme advanced or was dropped. Any scheme eventually standardized is intended to **augment** FIPS 204, 205, 186-5, and SP 800-208 (per IR 8610 abstract). Third-round submitter tweaks are due **14 August 2026**; the next [NIST PQC conference](https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc) is planned for the first half of **2027**.

Recommended **UOV** parameter sets (`OV-Ip`, `OV-III`, …) are documented under [PQC Digital Signature Schemes](https://csrc.nist.gov/projects/pqc-dig-sig) and summarized in ecosystem tables (e.g. [liboqs UOV](https://openquantumsafe.org/liboqs/algorithms/sig/uov.html)).

**SilentVerify / UOVscheme** implements UOV over a **prime field** `ZMod q` for Lean and Python reference code. That is **not** byte-for-byte the NIST **GF(2^k)** UOV packaging (`OV-Ip`, `OV-III`, …). See `impl/python/uov/params.py` and the **prime-field timings** below.

---

## Two “Round 3” tracks (signatures)

### Main PQC Round 3 → FIPS (already standardized)

| Round 3 name (informal) | NIST standard | Primary use case |
|-------------------------|---------------|------------------|
| CRYSTALS-Dilithium | **ML-DSA** (FIPS 204) | General-purpose PQ signatures |
| Falcon | **FN-DSA** (FIPS 206) | Compact signatures |
| SPHINCS+ | **SLH-DSA** (FIPS 205) | Conservative hash-based signatures |

### Additional Digital Signatures — Round 3 (May 2026)

NIST’s [May 2026 announcement](https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc) names these **third-round** candidates:

| FAEST | HAWK | MAYO | MQOM | QR-UOV | SDitH | SNOVA | SQIsign | **UOV** |
|-------|------|------|------|--------|-------|-------|---------|---------|

**UOV** (the family behind SilentVerify) is in this pool — **not** in the 2020–2022 lattice/hash Round 3 that produced FIPS 204/205/206.

### What [NIST IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf) says about UOV (§3.11)

| Topic | NIST summary (May 2026) |
|-------|-------------------------|
| **Role** | Foundational multivariate design (1990s); NIST values **algorithmic diversity** and a **small-σ / fast-verify** option, but sees UOV as suited to **certain applications**, not as a general-purpose replacement for ML-DSA. |
| **Performance** | Signatures as small as **96 B** at category 1; verification on the order of **tens of thousands of cycles** on some platforms; expanded public keys **>200 KB**. |
| **Second-round cryptanalysis** | **Wedge** and **small-field** attacks reduced margins on three of four proposed sets (`uov-Ip`, `uov-III`, `uov-V`); NIST expects **reparameterization**, not abandonment of the construction. |
| **Third-round direction** | Submitters may refine parameters; IR notes **odd-characteristic** UOV appeared **more resilient** to the cited attacks than characteristic-2 sets — relevant when comparing to this repo’s **prime-field** reference (`ZMod q`). |
| **SilentVerify fit** | Verifier-shaped **P(σ) = y** matches the “fast verification” story; **large pk** and **off-chain verify** remain the practical deployment pattern (see gas section below). |

---

## Key and signature sizes (bytes)

Sizes for standardized schemes are from **FIPS tables** (August 2024 / 2025 publications). UOV rows are **liboqs** identifiers aligned with the NIST UOV parameter naming (`OV-Ip`, `OV-III`, …).

### Category 1 (~128-bit claimed strength)

| Scheme | Parameter set | |sk| | |pk| | |σ| |
|--------|---------------|-----|-----|-----|
| ML-DSA | ML-DSA-44 | 2,560 | 1,312 | 2,420 |
| FN-DSA | FN-DSA-512 | 1,281 | 897 | 666 |
| SLH-DSA | SLH-DSA-SHA2-128s | 64† | 32 | 7,856 |
| UOV | OV-Ip | 237,896 | 278,432 | **128** |
| UOV (pkc) | OV-Ip-pkc | 237,896 | 43,576 | **128** |

### Category 3

| Scheme | Parameter set | |sk| | |pk| | |σ| |
|--------|---------------|-----|-----|-----|
| ML-DSA | ML-DSA-65 | 4,032 | 1,952 | 3,309 |
| SLH-DSA | SLH-DSA-SHA2-192s | 96† | 48 | 16,224 |
| UOV | OV-III | 1,044,320 | 1,225,440 | **200** |
| UOV (pkc) | OV-III-pkc | 1,044,320 | 189,232 | **200** |

### Category 5 (~256-bit claimed strength)

| Scheme | Parameter set | |sk| | |pk| | |σ| |
|--------|---------------|-----|-----|-----|
| ML-DSA | ML-DSA-87 | 4,896 | 2,592 | 4,627 |
| FN-DSA | FN-DSA-1024 | 2,305 | 1,793 | 1,280 |
| SLH-DSA | SLH-DSA-SHA2-256s | 128† | 64 | 29,792 |
| UOV | OV-V | 2,436,704 | 2,869,440 | **260** |

† **SLH-DSA** secret keys are **4n** bytes in the FIPS encoding (e.g. 64 B for `n = 16`); signing keys are often stored/regenerated from seed + public components.

**Takeaway for SilentVerify:** UOV’s on-wire **signature** can be **tens of bytes** (category 1: 128 B for `OV-Ip`) while ML-DSA/FN-DSA signatures are **hundreds to thousands** of bytes — but UOV **public keys** are **hundreds of KB to MB**, so verification data is dominated by **pk** unless you use **pkc** / off-chain key distribution.

**Sources:** FIPS 204 Table 2; FIPS 205 Table 2; FN-DSA sizes per [IETF COSE FN-DSA draft](https://www.ietf.org/archive/id/draft-ietf-cose-falcon-04.html) (aligned with FIPS 206); UOV from [liboqs](https://openquantumsafe.org/liboqs/algorithms/sig/uov.html).

---

## CPU time (sign / verify)

### Standardized schemes (indicative)

Use **liboqs** or your platform’s **OQS speed** build for apples-to-apples numbers on `ML-DSA-*`, `FN-DSA-*`, `SLH-DSA-*`, and `OV-*`. Published community benches vary widely by CPU and `-march` flags; we do **not** pin a single cross-scheme table here to avoid stale or non-reproducible figures.

**Qualitative pattern (typical on desktop/server CPUs):**

- **ML-DSA / FN-DSA:** verify **faster** than sign; FN-DSA signatures smaller than ML-DSA at similar category.
- **SLH-DSA:** **slow** sign and verify vs lattice schemes; **s** variants smaller signatures than **f** variants.
- **UOV:** sign/verify often **competitive** in wall time vs ML-DSA at similar security category in liboqs reports, but with **much larger** keys and different constant-time / side-channel profiles — treat production timing as implementation-specific.

### This repository (prime-field reference, measured)

Command (from repo root):

```bash
python3 impl/python/scripts/bench_uov_prime_profiles.py
```

**Sample run** (macOS x86_64, Python 3.9.6, May 2026 — **re-run locally** for your hardware):

| Profile | (q, o, v) | keygen | sign (ms/op) | verify (ms/op) |
|---------|-----------|--------|----------------|----------------|
| `NIST_STYLE_PRIME_I_MIN` | (251, 8, 24) | 0.15 s | ~4.0 | ~2.3 |
| `NIST_STYLE_PRIME_III` | (1009, 16, 40) | 0.81 s | ~13.0 | ~11.1 |

These profiles are **SilentVerify demo defaults**, not `OV-Ip` / `OV-III` byte lengths or GF(2^8) arithmetic.

---

## On-chain gas (EVM)

| Approach | Status in this repo | Gas notes |
|----------|---------------------|-----------|
| **ML-DSA verify** | Not implemented on-chain here | [EIP-8051](https://eips.ethereum.org/EIPS/eip-8051) (draft) proposes an ML-DSA **verification precompile**; discussion targets on the order of **~4.5k gas** per verify (draft — not final). |
| **FN-DSA / SLH-DSA** | Not implemented | No standard Ethereum precompile as of this writing; gas is dominated by hash + NTT / tree walks in a Solidity port. |
| **UOV verify** | Not implemented | Naive `P(σ)=y` over a **full** public key is **impractical** on EVM: **hundreds of KB–MB** of coefficients vs contract size and memory limits. Production patterns: **off-chain verify**, **SNARK**, **optimistic** challenge, or **anchor-only** (see below). |
| **SilentVerify anchor** | `SilentVerifyAnchorRegistry.sol` | Emits **keccak256(wire)** or full wire bytes — **O(1)** store/log gas, **no** UOV math on-chain. |

**SilentVerify positioning:** chain posts are **commitments** to certificates verified **off-chain** (or via future specialized verifiers), not a claim that UOV verification is cheap in the EVM execution layer today.

---

## How this repo uses UOV

| Layer | Role |
|-------|------|
| **Lean** | Proof of **algebraic** correctness and conditional EUF-CMA statement (`SchemeCorrectness.lean`, `UOVSecurity.lean`). |
| **Python** | Reference sign/verify + `silentverify.state_cert/v1` wire format. |
| **Contracts** | Anchor registry only — not a full PQ verifier precompile. |

For hackathon reviewers: compare **certificate size** (especially **σ**) and **verifier work** (one public-map evaluation) against ML-DSA-sized artifacts when reasoning about middleware and cross-chain attestations — after reading the **size** and **gas** tradeoffs above.

---

## References

- [FIPS 204 — ML-DSA](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.204.pdf)
- [FIPS 205 — SLH-DSA](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.205.pdf)
- [FIPS 206 — FN-DSA](https://csrc.nist.gov/pubs/fips/206/final)
- [NIST IR 8610 — Second-round status report (PDF, May 2026)](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf) · [DOI 10.6028/NIST.IR.8610](https://doi.org/10.6028/NIST.IR.8610)
- [NIST: nine candidates advance to Additional Signatures Round 3 (news, May 2026)](https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc)
- [NIST PQC Digital Signature Schemes (parent project)](https://csrc.nist.gov/projects/pqc-dig-sig)
- [liboqs UOV parameters](https://openquantumsafe.org/liboqs/algorithms/sig/uov.html)
- [EIP-8051 — ML-DSA precompile (draft)](https://eips.ethereum.org/EIPS/eip-8051)
- This repo: `impl/python/uov/params.py`, `impl/python/scripts/bench_uov_prime_profiles.py`
