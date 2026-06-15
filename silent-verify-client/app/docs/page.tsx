import { Suspense } from "react";
import { TryApi } from "@/components/blocks/tryApi/TryApi";
import { CodeBlock, CodeError } from "@/types";
import { getParams } from "@/services/paramsService";
import { highlight } from "@/lib/shiki";

const BASE = process.env.NEXT_PUBLIC_APP_URL!;

const codeBlocks = [
    { title: "Health", block: `curl -s "${BASE}/api/v1/health"` },
    {
        title: "Issue agent cert",
        block:
            `curl -s -X POST "${BASE}/api/v1/certs/agent/issue" \\\n` +
            `  -H "Content-Type: application/json" \\\n` +
            `  -H "X-API-Key: $SV_API_KEY" \\\n` +
            `  -d '{"agent_did":"did:example:bot","capabilities":{"sign":true}}'`,
    },
    {
        title: "Check quota",
        block: `curl -s "${BASE}/api/v1/billing/usage" -H "X-API-Key: $SV_API_KEY"`,
    },
];

const codeErrors = [
    { title: "401 / missing_api_key", error: "add X-API-Key header" },
    {
        title: "429 / quota_exceeded",
        error: "free tier is 100 issuances/month; upgrade on HOME",
    },
    {
        title: "502 / rpc_or_schema",
        error: "RPC blocked or stale block try public HTTPS URL + higher depth policy",
    },
    {
        title: "valid : false ",
        error: "re-run issue or check cert JSON was not edited",
    },
];

export default async function Page() {
    const params = await getParams();
    const blocks = (await Promise.all(
        codeBlocks.map(async (item) => ({
            title: item.title,
            block: {
                code: item.block,
                html: await highlight(item.block, "bash"),
            },
        }))
    )) as CodeBlock[];
    const errors = codeErrors as CodeError[];

    return (
        <Suspense fallback={null}>
            <TryApi
                codeBlocks={blocks}
                codeErrors={errors}
                devKeyAllowed={params.auth.dev_key_enabled}
            />
        </Suspense>
    );
}
