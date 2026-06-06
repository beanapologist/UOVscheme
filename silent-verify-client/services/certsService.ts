import { api } from "@/api/client";
import { Flow, Wire } from "@/types";
import { parseJSON } from "@/utils/functions";

type AgentCert = {
    agent_did: Flow["agent_did"];
    capabilities: Flow["agent_caps"];
    expires_in_days: number;
};

type StateCert = {
    chain_id: Flow["chain_id"];
    block_height: Flow["block_height"];
    state_root_hex: Flow["state_root_hex"];
};

type ResultCert = {
    status: string;
    cert: Wire;
    pubkey_fp: string;
};

export async function verifyPublicCert(wire: Wire) {
    const resp = await api.post("/certs/verify", {
        body: JSON.stringify({ cert: wire }),
    });
    const data = await resp.json();
    return data;
}

export async function getStateCert(key: string, body: StateCert) {
    const resp = await api.post("/certs/state/issue", {
        body: JSON.stringify(body),
        headers: {
            "X-API-Key": key,
        },
    });
    const text = await resp.text();
    const json = parseJSON(text);
    const data = json.success ? json.data : text;
    return data as ResultCert;
}

export async function getAgentCert(key: string, body: AgentCert) {
    const resp = await api.post("/certs/agent/issue", {
        body: JSON.stringify(body),
        headers: {
            "X-API-Key": key,
        },
    });
    const text = await resp.text();
    const json = parseJSON(text);
    const data = json.success ? json.data : text;
    return data as ResultCert;
}

export async function verifyStateCert(key: string, cert: Wire) {
    const resp = await api.post("/certs/state/verify", {
        body: JSON.stringify(cert),
        headers: {
            "X-API-Key": key,
        },
    });
    const text = await resp.text();
    const json = parseJSON(text);
    return json.success ? json.data : text;
}

export async function verifyAgentCert(key: string, cert: Wire) {
    const resp = await api.post("/certs/agent/verify", {
        body: JSON.stringify(cert),
        headers: {
            "X-API-Key": key,
        },
    });
    const text = await resp.text();
    const json = parseJSON(text);
    return json.success ? json.data : text;
}

export async function getPrintCert(wire: Wire) {
    const resp = await api.post("/certs/print/public", {
        body: JSON.stringify({ cert: wire }),
    });
    const html = await resp.text();
    return html;
}
