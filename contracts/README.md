# SilentVerify — on-chain posting & verifier options

Python issues certificates off-chain (`impl/python/statecert/` + `uov/certificate.py`). Putting **something** on-chain is usually about *availability*, *ordering*, or *composability* with other contracts—not re-running full UOV verification inside every block.

## EVM (`contracts/evm/`)

### Foundry

From `contracts/`:

```bash
forge install foundry-rs/forge-std@v1.9.4 --no-git   # once
forge test -vvv
```

Tests read ``test/fixtures/state_cert_wire.json`` (UTF-8 JSON from ``impl/python/scripts/gen_foundry_fixture.py``) and ``pubkey_fp.bin``. ``postCommitmentOnly`` is exercised with ``keccak256(wire)`` computed in Solidity to match Ethereum’s hash of the same bytes.

`SilentVerifyAnchorRegistry.sol` implements two common patterns:

| Function | On-chain cost model | Who recovers the certificate |
|----------|---------------------|------------------------------|
| `postFullWire(pubkeyFp, wire, note)` | Higher (calldata) | Anyone: event carries full bytes |
| `postCommitmentOnly(pubkeyFp, keccak256(wire), note)` | Lower | Off-chain / DA must publish `wire` |

`pubkeyFp` should match the SilentVerify JSON `pubkey_fp` field (32-byte hex interpreted as `bytes32` left-padded if you standardize that way in tooling).

### Future: verify on-chain

Reasonable tracks (pick one per product):

1. **Optimistic / challenge** — post commitment; challenger runs UOV verify off-chain; slash on fraud proof.
2. **SNARK wrapper** — prove `verify_opening(digest, σ, pk) = true` inside a circuit; on-chain checks the proof.
3. **Threshold / oracle network** — small committee signs an attestation that off-chain verify passed.

Raw quadratic evaluation at NIST-sized `o, v` is usually impractical as pure EVM bytecode.

## Solana (`programs/silentverify/README.md`)

Typical patterns: **Memo program** (instruction data), **Anchor** program that logs or stores a `keccak`/`sha256` of the wire, or a dedicated account per certificate batch.

## Cosmos / CosmWasm (`contracts/cosmos/README.md`)

Store `wire_hash` in module state or emit a **Tendermint event** from a custom message; full `wire` in transaction `memo` (size-limited) or referenced via IPFS CID in the message body.
