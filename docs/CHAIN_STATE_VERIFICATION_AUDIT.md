# Audit: “Verification between chain states” — purpose and limits

This note is grounded in the current **SilentVerify / `statecert`** implementation (Python `impl/python/statecert`, chain API). It answers: **what does chain-backed verification actually check**, **what failures it helps catch**, and **what it does not protect against**.

---

## 1. What “verification” means here (precisely)

There are **up to three** checks after a certificate is parsed from wire JSON (the third is optional and EVM-only):

1. **Anchor binding (`digest_binds_to_anchor`)**  
   The verifier recomputes the field vector **`y_live`** from a **live** chain anchor (fetched via RPC/REST in the HTTP API path, or supplied as a structured object in library tests) using the **same** pipeline as issuance: canonical JSON → SHA-256 → domain-separated XOF → `GF(q)^o` (`state_hash.py`, `chain_api._binding_report`).

   It compares **`y_live` to `certificate.digest_y`**.  
   So the certificate is tied to **exactly the canonical fields** in `ChainState`, `SolanaCommitment`, `CosmosCommitment`, `XrpLedgerCommitment`, or (at issuance time) composite types `CrossChainStateTransition` / `CrossL1Commitment` encoded in `state_hash.py`.

2. **UOV cryptographic validity (`certificate_crypto_ok` / `certificate_full_ok`)**  
   **`P(σ) = y`** under the embedded public key, plus **`pubkey_fp`** consistency with that public key (`certificate.py`).

3. **Optional EVM depth policy** (`chain_api.enforce_evm_min_confirmations_behind_tip`, wired through HTTP `policy` fields)  
   After fetching an anchor block, optionally require `eth_blockNumber − anchor_height ≥ N` on the **same** RPC. This is **policy above `state_hash`**, not part of `P(σ)=y`.

The chain API’s advertised behavior is explicit in `README_CHAIN_API.md`: fetch live anchor → recompute `y` → equality check → UOV verify.

---

## 2. Purpose (why this exists)

**Purpose:** produce a **portable, auditable artifact** (state certificate) whose meaning is:  
*“The issuer signed this **specific digest**, which was derived from **this exact canonical representation** of one or more chain commitments.”*

Downstream parties can **re-run the same deterministic digest pipeline** against **their own** view of the chain (or against a node they trust) and confirm the signature still matches that digest.

So the value is **not** “replace bridge security” or “prove arbitrary chain execution.” It is:

- **Binding clarity** — the signed object is a **defined JSON shape** (sorted keys, fixed field names), shrinking ambiguity about *what* was attested.
- **Replayable verification** — anyone with the cert, the public key material, and access to chain data can re-check **digest match + signature**.
- **Separation of duties** — the optional HTTP server fetches RPC results **server-side** so a browser does not need chain CORS privileges (`README_CHAIN_API.md`).

---

## 3. What this helps prevent or catch (realistic)

These are the main **honest mistakes, integration bugs, and tampering attempts** the design is aimed at:

| Class | How the check helps |
|--------|---------------------|
| **Wrong / stale anchor** | If someone presents a cert but the live chain at the requested block/slot/height has a different root/hash than the one encoded in the digest path, **`digest_binds_to_anchor` is false**. |
| **Certificate tampering** | Editing `digest_y`, `sigma`, `pubkey`, or `pubkey_fp` in the JSON should break **crypto** or **fingerprint** checks. |
| **Schema / version skew (within supported wire)** | Parsing validates `schema_version` and `pubkey_fp` vs embedded key; unsupported wire fails early (`certificate.py`). |
| **Non-canonical re-implementation bugs** | Two implementations that disagree on `to_canonical_dict()` / JSON sorting will disagree on `y`; binding fails until fixed. |
| **“We signed the wrong thing” at issuance** | If issuance used `issue_for_*` on structured anchors, the digest is a deterministic function of those fields; verification forces the **same** semantics at check time. |

For **cross-domain statements** encoded as `CrossChainStateTransition` (two `ChainState`s) or `CrossL1Commitment` (heterogeneous pair), issuance signs a digest over **both legs’ canonical objects** (`state_hash.py`). That helps prevent **“we only meant one chain”** ambiguity **inside the signed object** — the pair is explicit in the preimage.

---

## 4. What this does **not** prevent (scope limits)

These are **outside** what digest + UOV verification can fix:

| Limit | Reason |
|--------|--------|
| **Malicious or wrong RPC** | You ultimately trust whoever supplies block/header data. A hostile RPC can return a fake block that *passes* binding for an attacker-chosen anchor while the real network differs. |
| **Bridge / multisig / governance compromise** | Confirmed nine-figure losses are often **trusted parties, keys, or logic bugs** in bridge contracts — not lack of a separate UOV digest object. |
| **Liveness / finality confusion** | Using `latest` vs finalized head, reorgs, or wrong `chain_id` / CAIP-2 metadata can still make a **locally consistent** verification **globally wrong** for your policy. The code checks **consistency of the cert with the node’s answer**, not “this is the economically final truth for your application.” Optional **EVM depth policy** (`min_confirmations_behind_tip` vs `eth_blockNumber` on the same RPC) is a **machine-checkable rule** you can enable on single-anchor and cross-pair routes—it still trusts that RPC’s view of the tip. |
| **Oracle manipulation, MEV, economic attacks** | Losses often exploit **prices, governance, or contract logic** — not the presence of a state-root certificate. |
| **Consensus attacks (51%, long-range, …)** | If the underlying chain’s consensus is broken, the “true” anchor is undefined; this layer does not add economic security to the remote chain. |

**API scope:** Single-anchor routes exist for EVM, Solana, Cosmos, and XRPL. **`POST /api/v1/evm/cross-verify-state-cert`** covers **`CrossChainStateTransition`**. **`POST /api/v1/cross-l1/verify-state-cert`** covers **`CrossL1Commitment`** with per-leg `kind` (`evm` / `solana` / `cosmos` / `xrp`). See `README_CHAIN_API.md`.

---

## 5. One-sentence positioning (defensible)

**SilentVerify chain-state verification is a deterministic “anchor → digest → signature” harness that catches tampering and many binding mistakes between a certificate and *a supplied view of chain data*; it does not replace bridge trust assumptions, honest RPC, or finality policy.**

---

## 6. Suggested pairing with your attack taxonomy

- **Strong fit:** incidents where the failure mode is **“we verified / signed the wrong header fields”** or **non-replayable ad-hoc hashing** between teams — your stack pushes those into **named canonical structs + one digest pipeline + signature**.  
- **Weak / no fit:** **guardian compromise**, **contract exploit**, **oracle / economic manipulation** — keep those in separate rows of the taxonomy; do not imply this layer removes them.

