"""Request / response models with OpenAPI examples for Swagger."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .openapi_examples import (
    SAMPLE_CHAIN_VERIFY,
    SAMPLE_VERIFY_FAIL,
    SAMPLE_VERIFY_OK,
    sample_agent_cert_wire,
    sample_chain_issue_response,
    sample_issue_response,
    sample_state_cert_wire,
)

_AGENT_EXAMPLE = {
    "agent_did": "did:example:acme-agent-7",
    "capabilities": {"sign": True, "deploy": True, "network": "acme-cloud"},
    "reputation_hash": "sha256:demo",
    "expires_in_days": 30,
}

_EVM_ISSUE_EXAMPLE = {
    "rpc_url": "https://eth.drpc.org",
    "block": "latest",
    "caip2_chain_id": "eip155:1",
}

_CROSS_L1_LEG_EVM = {
    "kind": "evm",
    "rpc_url": "https://eth.drpc.org",
    "block": "latest",
    "caip2_chain_id": "eip155:1",
}

_CROSS_L1_LEG_SOL = {
    "kind": "solana",
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "cluster_id": "mainnet-beta",
    "commitment": "finalized",
}

_EVM_VERIFY_EXAMPLE = {
    "rpc_url": "https://eth.drpc.org",
    "block": "latest",
    "caip2_chain_id": "eip155:1",
    "cert": sample_agent_cert_wire(),
}


def _schema_example(example: dict) -> dict:
    """OpenAPI 3 default body (Swagger «Example Value»)."""
    return {"example": example, "examples": [example]}


# Exported for FastAPI Body(...)
AGENT_ISSUE_EXAMPLE = _AGENT_EXAMPLE
EVM_ISSUE_EXAMPLE = _EVM_ISSUE_EXAMPLE
STATE_ISSUE_EXAMPLE = {
    "chain_id": "eip155:1",
    "block_height": 19_000_000,
    "state_root_hex": "0x" + "ab" * 32,
}
AGENT_VERIFY_EXAMPLE = {"cert": sample_agent_cert_wire()}
STATE_VERIFY_EXAMPLE = {"cert": sample_state_cert_wire()}


class AgentCertIssueRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra=_schema_example(_AGENT_EXAMPLE))

    agent_did: str = Field(
        default="did:example:acme-agent-7",
        min_length=3,
        max_length=512,
        examples=["did:example:acme-agent-7"],
    )
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    reputation_hash: Optional[str] = Field(default=None, max_length=128)
    anchor: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional chain anchor object (stored in identity, not fetched)",
    )
    expires_in_days: int = Field(default=30, ge=1, le=3650)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StateCertIssueRequest(BaseModel):
    """Issue from a **known** EVM-style anchor (no RPC fetch)."""

    model_config = ConfigDict(json_schema_extra=_schema_example(STATE_ISSUE_EXAMPLE))

    chain_id: str = Field(default="eip155:1", min_length=1, max_length=256)
    block_height: int = Field(default=19_000_000, ge=0)
    state_root_hex: str = Field(default="0x" + "ab" * 32, min_length=2, max_length=128)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CertVerifyRequest(BaseModel):
    """Paste the full ``cert`` object from an issue response (or use the default demo cert)."""

    model_config = ConfigDict(
        json_schema_extra=_schema_example(STATE_VERIFY_EXAMPLE),
        populate_by_name=True,
    )

    cert: Dict[str, Any] = Field(
        default_factory=sample_state_cert_wire,
        validation_alias=AliasChoices("cert", "certificate"),
        description="Entire `cert` object from POST …/certs/state/issue (or agent/issue)",
    )

    def wire(self) -> Dict[str, Any]:
        return self.cert


class AgentCertVerifyRequest(CertVerifyRequest):
    """Verify agent cert — default body is a valid demo agent certificate."""

    model_config = ConfigDict(
        json_schema_extra=_schema_example(AGENT_VERIFY_EXAMPLE),
        populate_by_name=True,
    )

    cert: Dict[str, Any] = Field(
        default_factory=sample_agent_cert_wire,
        validation_alias=AliasChoices("cert", "certificate"),
    )


class CentralMapCompWire(BaseModel):
    """One central-map component in the public key."""

    A: List[List[int]] = Field(description="o×o matrix")
    B: List[List[int]] = Field(description="o×v matrix")
    c: List[int] = Field(description="oil linear term, length o")
    d: List[int] = Field(description="vinegar linear term, length v")
    e: int = Field(description="constant term in GF(q)")


class CentralMapWire(BaseModel):
    comps: List[CentralMapCompWire]


class PublicKeyWire(BaseModel):
    q: int = Field(description="Prime field size")
    o: int = Field(description="Oil variables")
    v: int = Field(description="Vinegar variables")
    central_map: CentralMapWire
    T: List[List[int]] = Field(description="(o+v)×(o+v) change-of-variables matrix")


class StateCertWire(BaseModel):
    """UOV state certificate on the wire (``silentverify.state_cert/v1``)."""

    model_config = ConfigDict(extra="allow")

    schema_version: str = Field(
        default="silentverify.state_cert/v1",
        examples=["silentverify.state_cert/v1"],
    )
    q: int
    o: int
    v: int
    digest_y: List[int] = Field(description="Field digest y ∈ GF(q)^o")
    sigma: List[int] = Field(description="Signature σ ∈ GF(q)^(o+v)")
    public_key: PublicKeyWire
    pubkey_fp: str = Field(description="SHA-256 hex of canonical public key JSON")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Issuer metadata (e.g. cert_type, agent_did, flow)",
    )
    message_sha256_hex: Optional[str] = None


class CertIssueResponse(BaseModel):
    """Successful issuance — copy ``cert`` for verify or on-chain use."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [sample_issue_response()]},
    )

    status: str = Field(default="issued", examples=["issued"])
    cert: StateCertWire
    pubkey_fp: str = Field(
        description="Same as cert.pubkey_fp (convenience)",
        examples=[sample_issue_response()["pubkey_fp"]],
    )


class ChainAnchorWire(BaseModel):
    """Canonical anchor object (shape depends on chain)."""

    model_config = ConfigDict(extra="allow")

    kind: str = Field(examples=["ChainState", "SolanaCommitment"])
    chain_id: Optional[str] = None
    block_height: Optional[int] = None
    state_root_hex: Optional[str] = None


class ChainBindingResponse(CertIssueResponse):
    model_config = ConfigDict(
        json_schema_extra={"examples": [sample_chain_issue_response()]},
    )

    anchor: ChainAnchorWire = Field(
        description="Anchor fetched from RPC when issuing on-chain",
    )


class CertVerifyResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [SAMPLE_VERIFY_OK, SAMPLE_VERIFY_FAIL],
        },
    )

    valid: bool
    pubkey_fp: Optional[str] = None
    cert_type: Optional[str] = Field(default=None, examples=["agent", "state"])
    detail: Optional[str] = Field(
        default=None,
        description="Error hint when valid=false",
    )


class ChainVerifyBinding(BaseModel):
    """Inner ``result`` object from chain verify endpoints."""

    model_config = ConfigDict(extra="allow")

    ok: bool
    digest_binds_to_anchor: bool
    certificate_crypto_ok: bool
    certificate_full_ok: bool
    computed_digest_y: List[int]


class ChainVerifyResult(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [SAMPLE_CHAIN_VERIFY]},
    )

    result: ChainVerifyBinding


class EvmChainRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra=_schema_example(_EVM_ISSUE_EXAMPLE))

    rpc_url: str = Field(
        default="https://eth.drpc.org",
        min_length=8,
        description="Public HTTPS JSON-RPC URL (see GET /api/v1/chains/evm/hints)",
    )
    block: Any = Field(default="latest", description='Height int, "latest", or "0x…" hex')
    caip2_chain_id: Optional[str] = Field(default=None, examples=["eip155:1"])
    rpc_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description='Optional HTTP headers, e.g. {"Authorization":"Bearer INFURA_KEY"}',
    )
    policy: Optional[Dict[str, Any]] = Field(
        default=None,
        description='e.g. {"min_confirmations_behind_tip": 32}',
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)


class EvmVerifyRequest(EvmChainRequest):
    model_config = ConfigDict(
        json_schema_extra=_schema_example(_EVM_VERIFY_EXAMPLE),
        populate_by_name=True,
    )

    cert: Dict[str, Any] = Field(
        default_factory=sample_state_cert_wire,
        validation_alias=AliasChoices("cert", "certificate"),
        description="Certificate from a prior issue call",
    )

    def wire(self) -> Dict[str, Any]:
        return self.cert


class SolanaChainRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "rpc_url": "https://api.mainnet-beta.solana.com",
                    "cluster_id": "mainnet-beta",
                    "commitment": "finalized",
                }
            ]
        },
    )

    rpc_url: str = Field(default="https://api.mainnet-beta.solana.com")
    cluster_id: str = "mainnet-beta"
    slot: Optional[int] = None
    commitment: str = "finalized"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)


class SolanaVerifyRequest(SolanaChainRequest):
    cert: Dict[str, Any] = Field(..., validation_alias=AliasChoices("cert", "certificate"))

    def wire(self) -> Dict[str, Any]:
        return self.cert


class CosmosChainRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "rest_base": "https://cosmos-rest.publicnode.com",
                    "chain_id": "cosmoshub-4",
                }
            ]
        },
    )

    rest_base: str = Field(
        default="https://cosmos-rest.publicnode.com",
        description="Cosmos LCD / REST base URL",
    )
    chain_id: str = Field(default="cosmoshub-4")
    height: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)


class CosmosVerifyRequest(CosmosChainRequest):
    cert: Dict[str, Any] = Field(..., validation_alias=AliasChoices("cert", "certificate"))

    def wire(self) -> Dict[str, Any]:
        return self.cert


class XrpChainRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "rpc_url": "https://xrplcluster.com",
                    "network_id": "mainnet",
                    "ledger_index": "validated",
                }
            ]
        },
    )

    rpc_url: str = Field(default="https://xrplcluster.com")
    network_id: str = Field(default="mainnet")
    ledger_index: Any = "validated"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)


class XrpVerifyRequest(XrpChainRequest):
    cert: Dict[str, Any] = Field(..., validation_alias=AliasChoices("cert", "certificate"))

    def wire(self) -> Dict[str, Any]:
        return self.cert


class TwoLegRequest(BaseModel):
    src: Dict[str, Any]
    dst: Dict[str, Any]
    policy: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)


class EvmCrossIssueRequest(TwoLegRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "src": {
                        "rpc_url": "https://ethereum.publicnode.com",
                        "block": "latest",
                        "caip2_chain_id": "eip155:1",
                    },
                    "dst": {
                        "rpc_url": "https://rpc.ankr.com/arbitrum",
                        "block": "latest",
                    },
                }
            ]
        },
    )


class EvmCrossVerifyRequest(EvmCrossIssueRequest):
    cert: Dict[str, Any] = Field(..., validation_alias=AliasChoices("cert", "certificate"))

    def wire(self) -> Dict[str, Any]:
        return self.cert


class CrossL1IssueRequest(TwoLegRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"src": _CROSS_L1_LEG_EVM, "dst": _CROSS_L1_LEG_SOL}]
        },
    )


class CrossL1VerifyRequest(CrossL1IssueRequest):
    cert: Dict[str, Any] = Field(..., validation_alias=AliasChoices("cert", "certificate"))

    def wire(self) -> Dict[str, Any]:
        return self.cert


class ChainCatalogResponse(BaseModel):
    chains: List[Dict[str, Any]]
    hint: str = "Use POST …/issue to fetch anchor + sign; POST …/verify to bind cert to live chain"
