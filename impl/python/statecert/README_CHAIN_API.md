# SilentVerify chain API (EVM, Solana, Cosmos, XRPL)

Small **stdlib-only** HTTP service that:

1. Accepts a **public** RPC / REST URL and a **state certificate** JSON (`StateCertificate.to_wire_dict()` wire).
2. Fetches a live anchor **server-side** (no browser → chain CORS).
3. Recomputes the field digest `y` for that anchor (same canonical JSON + SHA-256 + XOF path as `statecert.state_hash`) and checks `y == certificate.digest_y`, then runs `StateVerifier.verify_certificate` (UOV `P(σ)=y` + `pubkey_fp`).

## Run

From `impl/python`:

```bash
python -m statecert.api_server
```

Defaults: bind `127.0.0.1:8765`. Override with `SILENTVERIFY_API_HOST`, `SILENTVERIFY_API_PORT`.

### Calling from GitHub Pages (HTTPS)

The hosted mini-site is **HTTPS**. Browsers **block** `fetch()` to `http://127.0.0.1` or any `http://` URL from that page (mixed content). To use chain verify from Pages you need either:

- A **public HTTPS** reverse proxy in front of this API (or a cloud deployment), with `SILENTVERIFY_CORS_ORIGIN` set to your Pages origin (or `*` for demos), or  
- **Local use:** open the static site over **HTTP** (for example `python3 -m http.server` in `web/`) and keep the API at `http://127.0.0.1:8765`.

## Routes

| Method | Path | Role |
|--------|------|------|
| `GET` | `/api/v1/health` | Liveness JSON |
| `POST` | `/api/v1/evm/verify-state-cert` | `eth_getBlockByNumber` → `ChainState` |
| `POST` | `/api/v1/evm/cross-verify-state-cert` | Two EVM fetches → `CrossChainStateTransition` |
| `POST` | `/api/v1/cross-l1/verify-state-cert` | Two heterogeneous fetches → `CrossL1Commitment` |
| `POST` | `/api/v1/solana/verify-state-cert` | `getSlot` / `getBlock` → `SolanaCommitment` |
| `POST` | `/api/v1/cosmos/verify-state-cert` | LCD `.../blocks/{height\|latest}` → `CosmosCommitment` |
| `POST` | `/api/v1/xrp/verify-state-cert` | rippled `ledger` → `XrpLedgerCommitment` |

### EVM body

```json
{
  "rpc_url": "https://ethereum.publicnode.com",
  "block": "latest",
  "caip2_chain_id": "eip155:1",
  "certificate": { "schema_version": "silentverify.state_cert/v1", "...": "..." }
}
```

`block`: omit or `"latest"`, or a decimal **integer** height, or a `0x…` hex quantity (see `statecert.evm_rpc`).

Optional **`policy`** object (machine-checkable depth vs the **same** RPC’s tip):

```json
"policy": { "min_confirmations_behind_tip": 64 }
```

After resolving the anchor block, the server calls `eth_blockNumber` and requires  
`tip_height - anchor_height >= min_confirmations_behind_tip` (non-negative int). Omit `policy` or use `0` to skip. This is **not** a full finality proof; it encodes an explicit operational rule above the digest.

### EVM cross-pair body (`CrossChainStateTransition`)

`POST /api/v1/evm/cross-verify-state-cert` — for certificates issued with `StateVerifier.issue_for_cross_chain` (two `ChainState` legs, typically two networks or two heights).

```json
{
  "certificate": { "schema_version": "silentverify.state_cert/v1", "...": "..." },
  "src": {
    "rpc_url": "https://ethereum.publicnode.com",
    "block": "finalized",
    "caip2_chain_id": "eip155:1"
  },
  "dst": {
    "rpc_url": "https://rpc.ankr.com/arbitrum",
    "block": "finalized"
  },
  "policy": {
    "src": { "min_confirmations_behind_tip": 32 },
    "dst": { "min_confirmations_behind_tip": 64 }
  }
}
```

Per-leg `policy.src` / `policy.dst` are optional; each may include `min_confirmations_behind_tip` checked on that leg’s `rpc_url`.

### Cross-L1 body (`CrossL1Commitment`)

`POST /api/v1/cross-l1/verify-state-cert` — for certificates from `StateVerifier.issue_for_cross_l1`. Each leg is a JSON object with required string **`kind`**: `evm` | `solana` | `cosmos` | `xrp`.

**EVM leg:** `kind`, `rpc_url`, optional `block`, `caip2_chain_id` (same as single-anchor EVM).

**Solana leg:** `kind`, `rpc_url`, optional `cluster_id`, `slot`, `commitment`.

**Cosmos leg:** `kind`, `rest_base`, `chain_id`, optional `height`.

**XRPL leg:** `kind`, `rpc_url`, `network_id`, optional `ledger_index`.

Optional top-level **`policy`** with `src` / `dst` objects: only **evm** legs apply `min_confirmations_behind_tip`.

Example (EVM mainnet + Solana mainnet-beta):

```json
{
  "certificate": { "schema_version": "silentverify.state_cert/v1", "...": "..." },
  "src": {
    "kind": "evm",
    "rpc_url": "https://ethereum.publicnode.com",
    "block": "finalized",
    "caip2_chain_id": "eip155:1"
  },
  "dst": {
    "kind": "solana",
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "cluster_id": "mainnet-beta",
    "commitment": "finalized"
  },
  "policy": {
    "src": { "min_confirmations_behind_tip": 32 }
  }
}
```

**Not interchangeable:** `CrossChainStateTransition` (two EVM `ChainState` legs, nested `CrossChainStateTransition` in JSON) uses a **different** canonical tree than `CrossL1Commitment` (wrapper `kind: CrossL1Commitment`). Issue and verify with the **same** flow (`issue_for_cross_chain` + `/evm/cross-verify-…`, or `issue_for_cross_l1` + `/cross-l1/…`).

### Solana body

```json
{
  "rpc_url": "https://api.mainnet-beta.solana.com",
  "cluster_id": "mainnet-beta",
  "slot": 300000000,
  "commitment": "finalized",
  "certificate": { }
}
```

`slot`: omit to use current head from `getSlot`. `cluster_id` / `commitment` are passed through to `fetch_solana_commitment`.

### Cosmos body

```json
{
  "rest_base": "https://lcd-cosmoshub.keplr.app",
  "chain_id": "cosmoshub-4",
  "height": 18000000,
  "certificate": { }
}
```

`height`: omit for `latest`. `chain_id` is the Cosmos SDK chain identifier (not the REST hostname).

### XRPL body

```json
{
  "rpc_url": "https://s1.ripple.com",
  "network_id": "xrpl-mainnet",
  "ledger_index": "validated",
  "certificate": { }
}
```

`network_id` is stored **verbatim** in `XrpLedgerCommitment` (must match issuance). `ledger_index`: `"validated"`, `"current"`, `"closed"`, or a non-negative integer.

## Response shape

`200`:

```json
{
  "result": {
    "ok": true,
    "digest_binds_to_anchor": true,
    "certificate_crypto_ok": true,
    "certificate_full_ok": true,
    "computed_digest_y": […],
    "chain_state": { … }
  }
}
```

The anchor key mirrors the family: `chain_state`, `cross_chain_state_transition`, `cross_l1_commitment`, `solana_commitment`, `cosmos_commitment`, or `xrp_ledger_commitment`.

Errors: `400` validation, `502` RPC / schema failures.

## SSRF / dev

By default, **localhost** and **private / loopback IPs** in URLs are rejected. For local nodes:

```bash
export SILENTVERIFY_ALLOW_LOOPBACK_RPC=1
python -m statecert.api_server
```

CORS: `SILENTVERIFY_CORS_ORIGIN` (default `*`) for browser calls from the static `web/` UI.

## Certificate type

Binding uses **`statecert.state_hash`** digests. Issue with `StateVerifier.issue_for_chain_state`, `issue_for_cross_chain` (two EVM `ChainState`), `issue_for_cross_l1` (heterogeneous pair), `issue_for_solana`, `issue_for_cosmos`, `issue_for_xrp` (or `issue_for_anchor`). Certs from the **WASM UTF-8 message** demo use a different hash path and will not match these anchors.

## XRPL model

`XrpLedgerCommitment` is a new anchor kind in this repo (rippled `ledger` JSON-RPC). It is included in `ChainAnchor` and may appear as a leg of `CrossL1Commitment`.
