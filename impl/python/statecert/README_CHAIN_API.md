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

The anchor key mirrors the family: `chain_state`, `solana_commitment`, `cosmos_commitment`, or `xrp_ledger_commitment`.

Errors: `400` validation, `502` RPC / schema failures.

## SSRF / dev

By default, **localhost** and **private / loopback IPs** in URLs are rejected. For local nodes:

```bash
export SILENTVERIFY_ALLOW_LOOPBACK_RPC=1
python -m statecert.api_server
```

CORS: `SILENTVERIFY_CORS_ORIGIN` (default `*`) for browser calls from the static `web/` UI.

## Certificate type

Binding uses **`statecert.state_hash`** digests. Issue with `StateVerifier.issue_for_chain_state`, `issue_for_solana`, `issue_for_cosmos`, `issue_for_xrp` (or `issue_for_anchor`). Certs from the **WASM UTF-8 message** demo use a different hash path and will not match these anchors.

## XRPL model

`XrpLedgerCommitment` is a new anchor kind in this repo (rippled `ledger` JSON-RPC). It is included in `ChainAnchor` and may appear as a leg of `CrossL1Commitment`.
