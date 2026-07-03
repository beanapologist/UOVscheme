export const TAB_ACTIONS = {
    CASES: "cases",
    AGENT: "agent",
    STATE: "state",
    VERIFY: "verify",
    PRINT: "print",
    CERTS: "certs",
} as const;

export const USE_PROCESS = [
    {
        title: "AI agent identity (PKI)",
        description:
            "Give a deploy bot or MCP agent a post-quantum identity before it signs or acts on your infra.",
        steps: [
            "Issue agent cert with DID + capabilities",
            "Verify on every request",
            "Print for your security review",
        ],
        action: {
            type: "agent_pki",
            label: "Start this flow",
            variant: "default",
        },
    },
    {
        title: "Prove chain state at block N",
        description:
            "Anchor an EVM (or other) state root so counterparties can verify what you saw on-chain.",
        steps: [
            "Issue state cert with chain + height + root",
            "Share cert JSON or print PDF",
            "Peer verifies with state/verify",
        ],
        action: {
            type: "state_proof",
            label: "Start this flow",
            variant: "default",
        },
    },
    {
        title: "Gate a payout or release",
        description:
            "Only release funds or secrets after cryptographic verify passes - no trust in raw JSON.",
        steps: [
            "Paste cert from issuer",
            "Run verify (agent or state)",
            "Check valid: true in results",
        ],
        action: {
            type: "gate_verify",
            label: "Start this flow",
            variant: "default",
        },
    },
    {
        title: "Compliance & audit trail",
        description:
            "Human-readable certificate with verification badge and full wire JSON for auditors.",
        steps: [
            "Issue or receive a cert",
            "Open print view",
            "Save as PDF from browser",
        ],
        action: {
            type: "audit_print",
            label: "Start this flow",
            variant: "default",
        },
    },
    {
        title: "Multi-chain anchor (API)",
        description:
            "Bind certs to live RPC anchors on EVM, Solana, Cosmos, or XRPL - use the OpenAPI reference for paths.",
        steps: [
            "GET /api/v1/chains for catalog",
            "POST …/chains/evm/issue with rpc_url",
            "See [[/reference]]Reference for all routes",
        ],
        action: {
            type: "multi_chain",
            label: "Open reference",
            variant: "outline",
        },
    },
    {
        title: "Integrate in your app",
        description:
            "Call the same REST endpoints from CI, backends, or agents - store your API key once below.",
        steps: [
            "Save X-API-Key on this page",
            "Copy curl from Reference",
            "Advanced: Swagger",
        ],
        action: {
            type: "focus_key",
            label: "Focus API Key",
            variant: "outline",
        },
    },
] as const;
