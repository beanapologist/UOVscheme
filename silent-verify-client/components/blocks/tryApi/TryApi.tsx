"use client";

import { useCallback, useState } from "react";
import { BASE } from "@/config";
import { useWalletStore, useApiKeyStore } from "@/stores";
import { Container } from "@/components/layout";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import { CodeBlock } from "@/components/ui/CodeBlock";
import { LinkButton } from "@/components/ui/LinkButton";
import {
    Collapsible,
    CollapsibleTrigger,
    CollapsibleContent,
} from "@/components/ui/Collapsible";
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    CardFooter,
} from "@/components/ui/Card";
import { Field, FieldLabel } from "@/components/ui/Field";
import { Button, type ButtonVariantProps } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import { ChevronRight } from "lucide-react";
import type { CodeBlock as TCodeBlock, CodeError as TCodeError } from "@/types";

const TAB_ACTIONS = {
    USE_CASES: "use_cases",
    ISSUE_AGENT_CERT: "issue_agent_cert",
    ISSUE_STATE_CERT: "issue_state_cert",
    VERIFY_CERT: "verify_cert",
    PRINT_CERT: "print_cert",
    MY_CERTS: "my_certs",
};

const useFlows = [
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
            type: "agent-pki",
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
            type: "state-proof",
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
            type: "gate-verify",
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
            type: "audit-print",
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
            type: "multi-chain",
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
            type: "focus-key",
            label: "Focus API Key",
            variant: "outline",
        },
    },
] as {
    title: string;
    description: string;
    steps: string[];
    action: {
        type: string;
        label: string;
        variant: ButtonVariantProps["variant"];
    };
}[];

export function TryApi({
    codeBlocks,
    codeErrors,
}: {
    codeBlocks: TCodeBlock[];
    codeErrors: TCodeError[];
}) {
    // const [tab, setTab] = useState(TAB_ACTIONS.USE_CASES);
    // const { certs } = useWalletStore((state) => state.certs);

    return (
        <section className="section-sm flex flex-col">
            <Container className="flex-1 flex flex-col gap-4">
                <h1>Issue, verify & print certificates</h1>
                <p>
                    Step-by-step console for agent PKI and chain state certs. No
                    Swagger maze — pick a flow, run it, then print a signed
                    summary for your records.
                </p>
                <Tabs
                    className="flex-1 gap-8"
                    defaultValue="use_cases"
                    // value={tab}
                    // onValueChange={setTab}
                >
                    <TabsList variant="outline">
                        <TabsTrigger value={TAB_ACTIONS.USE_CASES}>
                            Use cases
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.ISSUE_AGENT_CERT}>
                            Issue agent cert
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.ISSUE_STATE_CERT}>
                            Issue state cert
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.VERIFY_CERT}>
                            Verify cert
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.PRINT_CERT}>
                            Print certificate
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.MY_CERTS}>
                            My certs
                        </TabsTrigger>
                    </TabsList>
                    <TabsContent
                        className="flex flex-col gap-6"
                        value={TAB_ACTIONS.USE_CASES}
                    >
                        <div className="flex flex-col gap-6">
                            <div>
                                <h3>Quickstart (curl)</h3>
                                <p>
                                    Set BASE to this host and SV_API_KEY from
                                    your key above (or get one at&nbsp;
                                    <LinkButton href="/">Home</LinkButton>
                                    ).
                                </p>
                                <div className="flex flex-col gap-4">
                                    {codeBlocks.map(({ title, block }) => (
                                        <div className="flex flex-col gap-2" key={title}>
                                            <h4>{title}</h4>
                                            <CodeBlock
                                                html={block.html}
                                                code={block.code}
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <Collapsible className="flex flex-col items-start gap-4">
                                <CollapsibleTrigger className="group/trigger flex flex-row items-center gap-px text-left">
                                    <span className="transition-rotate duration-150 ease-in-out group-data-[panel-open]/trigger:rotate-90">
                                        <ChevronRight size={20} />
                                    </span>
                                    Common errors
                                </CollapsibleTrigger>
                                <CollapsibleContent>
                                    {codeErrors.map(({ title, error }) => (
                                        <div key={title}>
                                            {title} <span>- {error}</span>
                                        </div>
                                    ))}
                                </CollapsibleContent>
                            </Collapsible>
                        </div>
                        <div className="flex flex-col gap-6">
                            <p>
                                Pick a real-world flow — we pre-fill the right
                                tab and you run one click at a time.
                            </p>
                            <div className="grid grid-cols-1 items-stretch gap-8 md:grid-cols-3">
                                {useFlows.map((flow) => (
                                    <Card key={flow.title}>
                                        <CardHeader>
                                            <CardTitle>{flow.title}</CardTitle>
                                            <CardDescription>
                                                {flow.description}
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            {flow.steps.map((step, i) => (
                                                <li key={i}>{step}</li>
                                            ))}
                                        </CardContent>
                                        <CardFooter>
                                            <Button
                                                variant={flow.action.variant}
                                                onClick={() => null}
                                            >
                                                {flow.action.label}
                                            </Button>
                                        </CardFooter>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.ISSUE_AGENT_CERT}>
                        <Card>
                            <CardHeader>
                                <CardDescription>
                                    Creates a post-quantum agent identity
                                    certificate (DID + capabilities).
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Field>
                                    <FieldLabel>Agent DID</FieldLabel>
                                    <Input />
                                </Field>
                                <Field>
                                    <FieldLabel>Capabilities (JSON)</FieldLabel>
                                    <Input />
                                </Field>
                            </CardContent>
                            <CardFooter>
                                <Button>Issue agent certificate</Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.ISSUE_STATE_CERT}>
                        <Card>
                            <CardHeader>
                                <CardDescription>
                                    Anchors a live chain state snapshot into a
                                    UOV certificate. Chain ID
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Field>
                                    <FieldLabel>Chain ID</FieldLabel>
                                    <Input />
                                </Field>
                                <Field>
                                    <FieldLabel>Block height</FieldLabel>
                                    <Input />
                                </Field>
                                <Field>
                                    <FieldLabel>State root (hex)</FieldLabel>
                                    <Input />
                                </Field>
                            </CardContent>
                            <CardFooter>
                                <Button>Issue state certificate</Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.VERIFY_CERT}>
                        <Card>
                            <CardHeader>
                                <CardDescription>
                                    Paste the cert object from a previous issue
                                    response, or use the last result
                                    automatically.
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Field>
                                    <FieldLabel>Certificate JSON</FieldLabel>
                                    <Textarea />
                                </Field>
                                <Field></Field>
                            </CardContent>
                            <CardFooter>
                                <Button>Verify</Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.PRINT_CERT}>
                        <Card>
                            <CardHeader>
                                <CardDescription>
                                    Opens a print-friendly page with identity,
                                    crypto fields, and full wire JSON. Uses the
                                    certificate from your last issue or the JSON
                                    below
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Field>
                                    <FieldLabel>
                                        Certificate JSON (optional)
                                    </FieldLabel>
                                    <Textarea />
                                </Field>
                            </CardContent>
                            <CardFooter>
                                <Button variant="default">
                                    Print certificate
                                </Button>
                                <Button variant="outline">
                                    Demo print (no key)
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.MY_CERTS}>
                        <Card>
                            <CardHeader>
                                <CardDescription>
                                    Certificates saved in this browser.
                                    Open&nbsp;
                                    <LinkButton href="/">verify</LinkButton>
                                    &nbsp; to check or print without an API key.
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {[].length ? (
                                    <div>
                                        {[].map((cert, i) => (
                                            <div key={i}></div>
                                        ))}
                                    </div>
                                ) : (
                                    <div>
                                        Issue a cert above — it will appear here
                                        automatically.
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </Container>
        </section>
    );
}
