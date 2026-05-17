# SilentVerify API

Unified **Agent PKI** + **multi-chain** state certificates (EVM, Solana, Cosmos, XRPL, cross-chain, cross-L1).

## Quick start

```bash
cd /path/to/UOVscheme/impl/python
./run_saas.sh
```

1. Open **http://127.0.0.1:8765/docs** (Try API) or **/swagger** (advanced)
2. Set **X-API-Key** → `sv_dev_test_key` (Try page) or **Authorize** in Swagger
3. **Getting started → GET /api/v1/chains** — see all hooks
4. **Agent PKI → POST /api/v1/certs/agent/issue** — use the built-in example body

## Route map (intuitive paths)

| What you want | Endpoint |
|---------------|----------|
| List chain hooks | `GET /api/v1/chains` |
| Agent cert | `POST /api/v1/certs/agent/issue` |
| Verify agent (offline crypto) | `POST /api/v1/certs/agent/verify` |
| State cert (you supply anchor) | `POST /api/v1/certs/state/issue` |
| **EVM: fetch block + issue** | `POST /api/v1/chains/evm/issue` |
| **EVM: verify on live RPC** | `POST /api/v1/chains/evm/verify` |
| Solana issue / verify | `/api/v1/chains/solana/issue` · `…/verify` |
| Cosmos issue / verify | `/api/v1/chains/cosmos/issue` · `…/verify` |
| XRPL issue / verify | `/api/v1/chains/xrp/issue` · `…/verify` |
| Two EVM RPC legs | `/api/v1/chains/evm-cross/issue` · `…/verify` |
| Heterogeneous L1 pair | `/api/v1/chains/cross-l1/issue` · `…/verify` |

Legacy URLs (`/api/v1/issue/agent-cert`, `/api/v1/evm/verify-state-cert`, …) still work.

## Request tips

- **Authorize once** in Swagger; all protected routes share the key.
- Use **`cert`** or **`certificate`** in verify bodies (both accepted).
- Chain **issue** responses include an **`anchor`** field (what was fetched from RPC).
- Chain **verify** responses use `{ "result": { "ok": true, … } }`.

## Local dev RPC

Public RPC URLs only by default. For Anvil/Hardhat:

```bash
export SILENTVERIFY_ALLOW_LOOPBACK_RPC=1
```

## Environment

See root of this folder’s previous README sections for `SILENTVERIFY_ISSUER_SEED`, `SILENTVERIFY_API_KEYS`, `SILENTVERIFY_UOV_PROFILE`, etc.

## Stdlib-only chain server

The lightweight server without FastAPI is still available:

```bash
python3 -m statecert.api_server
```

The FastAPI app supersedes it for new integrations (same verify semantics, plus **issue** hooks per chain).
