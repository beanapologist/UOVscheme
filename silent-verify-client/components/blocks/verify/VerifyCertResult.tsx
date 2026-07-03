import { CertResult } from "@/types";

export function VerifyCertResult({ data, wire }: CertResult) {
    const ok = data.valid;
    const meta = wire.metadata;
    const info = {
        crypto: ok ? "PASS" : "FAIL",
        type: data.cert_type ?? meta.cert_type ?? "-",
        pubkey: data.pubkey_fp ?? wire.pubkey_fp ?? "-",
        agentDID: meta.agent_did ?? "-",
    };

    return (
        <div
            className="p-4 flex flex-col gap-2 bg-surface border data-[type='pass']:border-success data-[type='fail']:border-warning rounded-xl"
            data-type={info.crypto.toLowerCase()}
        >
            <h3>{ok ? "Valid Certificate" : "Invalid or tampered"}</h3>
            <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-px">
                <dt>Crypto</dt>
                <dd>{info.crypto}</dd>

                <dt>Type</dt>
                <dd>{info.type}</dd>

                <dt>Agent DID</dt>
                <dd>{info.agentDID}</dd>

                <dt>Public Key</dt>
                <dd>{info.pubkey}</dd>

                {data.detail && (
                    <>
                        <dt>Detail</dt>
                        <dd>{data.detail}</dd>
                    </>
                )}
            </dl>
        </div>
    );
}
