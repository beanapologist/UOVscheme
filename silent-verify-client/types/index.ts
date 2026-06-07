export type CodeBlock = {
    title: string;
    block: {
        html: string;
        code: string;
    };
};

export type CodeError = {
    title: string;
    error: string;
};

export type Flow = {
    agent_did: string;
    agent_caps: {
        sign: boolean;
        deploy: boolean;
        mcp?: boolean;
    };
    chain_id: string;
    block_height: number;
    state_root_hex: string;
    certificate: string;
    certificate_optional: string;
    type: "agent" | "state";
};

export type Wire = {
    metadata: {
        chain_id?: string;
        block_height: string;
        agent_did: string;
        cert_type: string;
    };
    pubkey_fp: string;
    sigma: string;
};

export type Cert = {
    id: string;
    label: string;
    savedAt: string;
    cert: Wire;
};

export type CertResult = {
    wire: Wire;
    data: {
        valid: boolean;
        cert_type: string;
        pubkey_fp: string;
        detail: string;
    };
};
