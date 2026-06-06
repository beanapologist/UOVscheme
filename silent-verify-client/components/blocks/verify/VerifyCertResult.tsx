import { Wire } from "@/types";

export function VerifyCertResult({ data, wire }: { data: any; wire: Wire }) {
    const ok = data.valid;
    const meta = wire.metadata;
    const info = {
        crypto: ok ? "PASS" : "FAIL",
        type: data.cert_type ?? meta.cert_type ?? "-",
        pubkey: data.pubkey_fp ?? wire.pubkey_fp ?? "-",
        agentDID: meta.agent_did ?? "-",
    };
    return (
        <div>
            <h2>{ok ? "Valid Certificate" : "Invalid or tampered"}</h2>
            <dl>
                <div>
                    <dt>Crypto</dt>
                    <dd>{info.crypto}</dd>
                </div>
                <div>
                    <dt>Type</dt>
                    <dd>{info.type}</dd>
                </div>
                <div>
                    <dt>Agent DID</dt>
                    <dd>{info.agentDID}</dd>
                </div>
                <div>
                    <dt>Public Key</dt>
                    <dd>{info.pubkey}</dd>
                </div>
                {data.detail && (
                    <div>
                        <dt>Detail</dt>
                        <dd>{data.detail}</dd>
                    </div>
                )}
            </dl>
        </div>
    );
}
