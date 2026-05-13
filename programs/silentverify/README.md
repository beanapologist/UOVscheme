# SilentVerify on Solana — posting options

The Python stack builds a `StateCertificate` JSON blob (`silentverify.state_cert/v1`). On Solana you usually **do not** re-implement UOV verification on-chain at full security level; you anchor the blob (or its hash) and keep verification in the validator client, an off-chain worker, or a future ZK program.

## Practical patterns

1. **SPL Memo** — Include minified JSON (or a CID string) in a memo instruction; cheap, size-limited.
2. **Custom Anchor program** — Instruction writes `sha256(wire)` to a PDA or emits `msg!` / program data for indexers.
3. **CPI + logs** — Your program emits `sol_log_data` with a commitment; full wire lives off-chain.

## RPC → anchor object

Use `statecert.fetch_solana_commitment` (`impl/python/statecert/solana_rpc.py`) to build a `SolanaCommitment` from `getSlot` / `getBlock`, then `StateVerifier.issue_for_solana` (or `issue_for_anchor`) to bind a certificate digest to that head (or a chosen slot).

Keep `cluster_id` (`mainnet-beta`, `devnet`, …) stable across your deployment so canonical JSON matches operational naming.
