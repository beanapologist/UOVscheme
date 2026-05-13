# SilentVerify on Cosmos (SDK / CosmWasm)

## LCD / REST anchors (Python)

`statecert.fetch_cosmos_commitment(rest_base, chain_id="cosmoshub-4")` hits:

`GET {rest_base}/cosmos/base/tendermint/v1beta1/blocks/{height|latest}`

and packs `header.height` + `header.app_hash` into `CosmosCommitment` for digest binding.

## On-chain posting

Typical choices:

- **Wasm contract** — `execute` stores `wire_hash: [u8;32]` and optional `cid` string; verifiers pull full JSON from IPFS/DA.
- **SDK module** — Emit ABCI events `silentverify_commitment` with hash + pubkey fingerprint; no heavy state.
- **Tx memo** — Human-readable / CID pointer; size limits apply.

Full UOV verification in CosmWasm gas is usually reserved for toy parameters or wrapped in a ZK proof of verification.
