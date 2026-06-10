"use client";

import { Container } from "@/components/layout";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import { CodeBlock, CodeBlockContent } from "@/components/ui/CodeBlock";
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
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import {
    Binary,
    ChevronRight,
    Fingerprint,
    // Grid3X3,
    TriangleAlert,
} from "lucide-react";
import type {
    Cert,
    Flow,
    CodeBlock as TCodeBlock,
    CodeError as TCodeError,
    Wire,
} from "@/types";
import { TAB_ACTIONS, USE_PROCESS } from "./tryApi.constants";
import {
    parseJSON,
    stringify,
    toLocalDate,
    toMessage,
} from "@/utils/functions";
import {
    getAgentCert,
    getStateCert,
    verifyAgentCert,
    verifyStateCert,
} from "@/services/certsService";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import {
    fetchFreeKey,
    getApiUsage,
    verifyApiKey as verifyApiKeyApi,
} from "@/services/billingService";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/Alert";
import { useQueryParams } from "@/hooks";
import { Badge } from "@/components/ui/Badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/RadioGroup";
import { Label } from "@/components/ui/Label";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useApiKeyStore, useWalletStore } from "@/stores";

type Tabs = (typeof TAB_ACTIONS)[keyof typeof TAB_ACTIONS];
type Load = {
    cert: Flow["certificate"];
    type: Flow["type"];
    lastCert: Flow["certificate"];
};

type FormatCapsChange = Flow["agent_caps"];
type HandleTypeChange = Flow["type"];
type HandleFlowChange = React.ChangeEvent<
    HTMLInputElement | HTMLTextAreaElement
>;
type HandleFlowAction = (typeof USE_PROCESS)[number]["action"]["type"];

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const isLocalhost =
    typeof window !== "undefined" &&
    ["localhost", "127.0.0.1"].includes(window.location.hostname);

export function TryApi({
    codeBlocks,
    codeErrors,
    devKeyAllowed,
}: {
    codeBlocks: TCodeBlock[];
    codeErrors: TCodeError[];
    devKeyAllowed: boolean;
}) {
    const router = useRouter();
    const keyRef = useRef<HTMLInputElement>(null);

    const { apiKey, setApiKey, clearApiKey } = useApiKeyStore();
    const { certs, lastCert, saveCert, saveLastCert } = useWalletStore();
    const { demo, run } = useQueryParams(["demo", "run"]);

    const isDevKeyAllowed = devKeyAllowed ?? isLocalhost;
    const [tabs, setTabs] = useState<Tabs>(TAB_ACTIONS.CASES);
    const [flow, setFlow] = useState<Flow>({
        agent_did: "did:example:acme-agent-7",
        agent_caps: { deploy: true, sign: true },
        chain_id: "eip155:1",
        block_height: 19000000,
        state_root_hex:
            "0xabababababababababababababababababababababababababababababababab",
        certificate: "",
        certificate_optional: "",
        type: "agent",
    });

    const encodeCert = (cert: Cert) => {
        return `/verify?id=${encodeURIComponent(cert.id)}`;
    };

    const updateCert = (cert: Wire) => {
        const entry = saveCert(cert);
        saveLastCert(cert);
        toast("Saved to My certs — verify at /verify?id=" + entry.id);
    };

    const loadInTabs = (cert: Wire) => {
        saveLastCert(cert);
        toast("Loaded into Verify / Print tabs");
    };

    const previewCert = () => {
        const url = `${API_URL}/api/v1/certs/print/demo?autoprint=1`;
        window.open(url, "_blank");
    };

    const resolveCert = (cert: string, lastCert: string) => {
        const wire = cert ? cert : lastCert;
        try {
            if (!wire) {
                throw new Error("Issue a cert first or paste JSON");
            }
            const json = parseJSON(wire);
            const pass = json.success;
            if (!pass) {
                throw new Error("Invalid certificate JSON");
            }
            return json.data as Wire;
        } catch (error) {
            const err = toMessage(error);
            toast(err);
            return null;
        }
    };

    const claimFreeKey = async () => {
        try {
            const apiKey = await fetchFreeKey();
            setApiKey(apiKey);
            toast("New API key saved ");
        } catch (error) {
            const err = toMessage(error);
            toast(err);
        }
    };

    const handleQuotas = async (apiKey: string) => {
        try {
            const data = await getApiUsage(apiKey);
            prompt(stringify(data));
            // show in code block
        } catch (error) {
            const err = toMessage(error);
            console.error(err);
            // show in code block
        }
    };

    const handleAgent = async (apiKey: string, flow: Flow) => {
        try {
            const caps = parseJSON<FormatCapsChange>(
                formatCapsChange(flow.agent_caps)
            );
            if (!caps.success) {
                throw new Error("Invalid JSON capabilities");
            }
            const data = await getAgentCert(apiKey, {
                agent_did: flow.agent_did,
                capabilities: caps.data,
                expires_in_days: 30,
            });
            if (!data.cert) return;
            updateCert(data.cert);
        } catch (error) {
            const err = toMessage(error);
            toast(err);
            // show in code block
        }
    };

    const handleState = async (apiKey: string, flow: Flow) => {
        try {
            const data = await getStateCert(apiKey, {
                chain_id: flow.chain_id,
                block_height: flow.block_height,
                state_root_hex: flow.state_root_hex,
            });
            if (!data.cert) return;
            updateCert(data.cert);
        } catch (error) {
            const err = toMessage(error);
            console.error(err);
            // show in code block
        }
    };

    const handleVerify = async (apiKey: string, flow: Load) => {
        try {
            const cert = resolveCert(flow.cert, flow.lastCert);
            if (!cert) return;
            const data =
                flow.type === "agent"
                    ? await verifyAgentCert(apiKey, cert)
                    : await verifyStateCert(apiKey, cert);
            console.log(data);
        } catch (error) {
            const err = toMessage(error);
            // show in code block
            console.error(err);
        }
    };

    const commitApiKey = async (apiKey: string, devKeyAllowed: boolean) => {
        if (!apiKey) return;
        setApiKey(apiKey);
        const isValid = await verifyApiKey(apiKey, devKeyAllowed);
        toast.info(
            isValid
                ? "API key saved and verified"
                : "Key saved but not valid on the server - use Get free key"
        );
    };

    const verifyApiKey = async (apiKey: string, devKeyAllowed: boolean) => {
        try {
            if (!apiKey) {
                if (!devKeyAllowed) {
                    throw new Error("No API key set.");
                }
                return false;
            }
            const data = await verifyApiKeyApi(apiKey);
            if (data.valid) return true;
            clearApiKey();
            throw new Error(
                data.hint ?? "This key is not registered on the server"
            );
        } catch (error) {
            const err = toMessage(error);
            toast.error(err);
            return false;
        }
    };

    const assignApiKey = async (apiKey: string, devKeyAllowed: boolean) => {
        if (apiKey) {
            await verifyApiKey(apiKey, devKeyAllowed);
        } else {
            if (devKeyAllowed) {
                const devKey = "sv_dev_test_key";
                keyRef.current!.placeholder = "sv_dev_test_key (local data)";
                setApiKey(devKey);
                await verifyApiKey(devKey, devKeyAllowed);
            } else {
                toast.info("Click Get free API key to call issue endpoints.");
            }
        }
    };

    const formatCapsChange = (c: FormatCapsChange) => {
        return typeof c === "string" ? c : stringify(c);
    };

    const handleTypeChange = (v: HandleTypeChange) => {
        setFlow((prev) => ({
            ...prev,
            type: v,
        }));
    };

    const handleFlowChange = (e: HandleFlowChange) => {
        const { name, value } = e.target;
        setFlow((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleFlowAction = (t: HandleFlowAction) => {
        switch (t) {
            case "agent_pki":
                setFlow((prev) => ({
                    ...prev,
                    agent_did: "did:example:acme-deploy-bot",
                    agent_caps: {
                        sign: true,
                        deploy: true,
                        mcp: true,
                    },
                }));
                setTabs(TAB_ACTIONS.AGENT);
                toast.info("Agent PKI flow - click Issue agent certificate");
                return;
            case "state_proof":
                setFlow((prev) => ({
                    ...prev,
                    chain_id: "eip155:1",
                    block_height: 19000000,
                }));
                setTabs(TAB_ACTIONS.STATE);
                toast.info(
                    "State proof flow - set your real state root, then Issue state certificate"
                );
                return;
            case "gate_verify":
                setTabs(TAB_ACTIONS.VERIFY);
                toast.info("Paste the cert you received, then Verify");
                return;
            case "audit_print":
                setTabs(TAB_ACTIONS.PRINT);
                if (lastCert) {
                    toast.info(
                        "Print flow - click Print certificate (or Demo print)"
                    );
                } else {
                    toast.info("Issue a cert first, or use Demo print");
                }
                return;
            case "multi_chain":
                router.push("/redoc");
                return;
            case "focus_key":
                toast.info("Paste your API key and click Save key");
                keyRef.current?.focus();
                return;
            default:
                throw new Error("Unsupported flow type");
        }
    };

    useEffect(() => {
        if (!lastCert) return;
        const cert = stringify(lastCert);
        queueMicrotask(() => {
            setFlow((prev) => ({
                ...prev,
                certificate: cert,
                certificate_optional: cert,
            }));
        });
    }, [lastCert]);

    useEffect(() => {
        queueMicrotask(() => {
            if (demo === "agent") {
                handleFlowAction("agent_pki");
            }
            if (Number(run) === 1) {
                void handleAgent(apiKey, flow);
            }
            assignApiKey(apiKey, isDevKeyAllowed);
        });
        // Hydrate from URL query params once on mount.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    return (
        <section className="section-sm flex flex-col">
            <Container className="flex-1 flex flex-col gap-8">
                <h1>Issue, verify & print certificates</h1>
                <p>
                    Step-by-step console for agent PKI and chain state certs. No
                    Swagger maze — pick a flow, run it, then print a signed
                    summary for your records.
                </p>
                {!apiKey && (
                    <Alert variant="warning">
                        <TriangleAlert />
                        <AlertTitle>API Key not accepted.</AlertTitle>
                        <AlertDescription>
                            Unknown API Key. Use the key from Home (get free API
                            Key) or check SILENTVERIFY_API_KEYS on the server.
                        </AlertDescription>
                    </Alert>
                )}
                <Field className="p-4 gap-4 ring ring-border rounded-xl bg-surface">
                    <FieldLabel>X-API-Key</FieldLabel>
                    <div className="flex items-center justify-between">
                        <Input
                            className="w-full md:max-w-lg"
                            ref={keyRef}
                            value={apiKey}
                            type="password"
                        />
                        <div className="flex items-center gap-4">
                            <Button
                                variant="outline"
                                onClick={() =>
                                    commitApiKey(apiKey, isDevKeyAllowed)
                                }
                            >
                                Save key
                            </Button>
                            <Button
                                variant="default"
                                onClick={() => claimFreeKey()}
                            >
                                Get free key
                            </Button>
                        </div>
                    </div>
                </Field>
                <Tabs
                    className="flex-1 gap-8"
                    value={tabs}
                    onValueChange={setTabs}
                >
                    <TabsList variant="outline">
                        <TabsTrigger value={TAB_ACTIONS.CASES}>
                            Use cases
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.AGENT}>
                            Issue agent cert
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.STATE}>
                            Issue state cert
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.VERIFY}>
                            Verify cert
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.PRINT}>
                            Print certificate
                        </TabsTrigger>
                        <TabsTrigger value={TAB_ACTIONS.CERTS}>
                            My certs
                        </TabsTrigger>
                    </TabsList>
                    <TabsContent
                        className="flex flex-col gap-6"
                        value={TAB_ACTIONS.CASES}
                    >
                        <div className="flex flex-col gap-6">
                            <div className="flex flex-col p-8 rounded-xl bg-surface">
                                <h3>Quickstart (curl)</h3>
                                <p>
                                    Set BASE to this host and SV_API_KEY from
                                    your key above (or get one at&nbsp;
                                    <LinkButton href="/">Home</LinkButton>
                                    ).
                                </p>
                                <ol className="flex flex-col gap-4">
                                    {codeBlocks.map(({ title, block }) => (
                                        <li
                                            className="flex flex-col gap-2"
                                            key={title}
                                        >
                                            <h4>{title}</h4>
                                            <CodeBlock>
                                                <CodeBlockContent
                                                    html={block.html}
                                                />
                                            </CodeBlock>
                                        </li>
                                    ))}
                                </ol>
                                <Button
                                    className="w-fit"
                                    variant="outline"
                                    onClick={() => handleQuotas(apiKey)}
                                >
                                    Show my usage in result
                                </Button>
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
                                {USE_PROCESS.map((flow) => (
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
                                                onClick={() =>
                                                    handleFlowAction(
                                                        flow.action.type
                                                    )
                                                }
                                            >
                                                {flow.action.label}
                                            </Button>
                                        </CardFooter>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.AGENT}>
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
                                    <Input
                                        name="agent_did"
                                        value={flow.agent_did}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                                <Field>
                                    <FieldLabel>Capabilities (JSON)</FieldLabel>
                                    <Input
                                        name="agent_caps"
                                        value={formatCapsChange(
                                            flow.agent_caps
                                        )}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                            </CardContent>
                            <CardFooter>
                                <Button
                                    onClick={() => handleAgent(apiKey, flow)}
                                >
                                    Issue agent certificate
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.STATE}>
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
                                    <Input
                                        name="chain_id"
                                        value={flow.chain_id}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                                <Field>
                                    <FieldLabel>Block height</FieldLabel>
                                    <Input
                                        name="block_height"
                                        value={flow.block_height}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                                <Field>
                                    <FieldLabel>State root (hex)</FieldLabel>
                                    <Input
                                        name="state_root_hex"
                                        value={flow.state_root_hex}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                            </CardContent>
                            <CardFooter>
                                <Button
                                    onClick={() => handleState(apiKey, flow)}
                                >
                                    Issue state certificate
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.VERIFY}>
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
                                    <Textarea
                                        name="certificate"
                                        value={flow.certificate}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                                <RadioGroup
                                    name="type"
                                    value={flow.type}
                                    onValueChange={handleTypeChange}
                                >
                                    <Label>
                                        <RadioGroupItem value="agent" />
                                        Agent Verify
                                    </Label>
                                    <Label>
                                        <RadioGroupItem value="state" />
                                        State Verify
                                    </Label>
                                </RadioGroup>
                            </CardContent>
                            <CardFooter>
                                <Button
                                    onClick={() =>
                                        handleVerify(apiKey, {
                                            type: flow.type,
                                            cert: flow.certificate,
                                            lastCert: lastCert
                                                ? stringify(lastCert)
                                                : "",
                                        })
                                    }
                                >
                                    Verify
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.PRINT}>
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
                                    <Textarea
                                        name="certificate_optional"
                                        value={flow.certificate_optional}
                                        onChange={handleFlowChange}
                                    />
                                </Field>
                            </CardContent>
                            <CardFooter>
                                <Button
                                    variant="default"
                                    onClick={() => previewCert()}
                                >
                                    Print certificate
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => previewCert()}
                                >
                                    Demo print (no key)
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.CERTS}>
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
                                {certs.length ? (
                                    <div className="flex flex-col gap-4">
                                        {certs.map((cert, i) => (
                                            <div
                                                className="p-4 flex items-center gap-4 justify-between border border-border rounded-xl bg-support"
                                                key={i}
                                            >
                                                <Badge
                                                    className="size-10 rounded-lg [&>svg]:size-5!"
                                                    variant="outline"
                                                >
                                                    {i % 2 === 0 ? (
                                                        <Fingerprint />
                                                    ) : (
                                                        <Binary />
                                                    )}
                                                </Badge>
                                                <div className="inline-flex flex-col gap-1 flex-1">
                                                    <div>{cert.label}</div>
                                                    <div>
                                                        {toLocalDate(
                                                            cert.savedAt
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="inline-flex flex-row gap-2 flex-0">
                                                    <Button
                                                        variant="link"
                                                        nativeButton={false}
                                                        render={
                                                            <Link
                                                                href={encodeCert(
                                                                    cert
                                                                )}
                                                            >
                                                                Verify
                                                            </Link>
                                                        }
                                                    />
                                                    <Button
                                                        onClick={() =>
                                                            loadInTabs(
                                                                cert.cert
                                                            )
                                                        }
                                                    >
                                                        Load in tabs
                                                    </Button>
                                                </div>
                                            </div>
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
