"use client";

import { Container } from "@/components/layout";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import {
    CodeBlock,
    CodeBlockContent,
    CodeBlockHeader,
    CodeBlockTitle,
} from "@/components/ui/CodeBlock";
import { Field, FieldLabel } from "@/components/ui/Field";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type {
    Flow,
    CodeBlock as TCodeBlock,
    CodeError as TCodeError,
    Wire,
} from "@/types";
import { TAB_ACTIONS } from "./tryApi.constants";
import { parseJSON, stringify, toMessage } from "@/utils/functions";
import { getAgentCert } from "@/services/certsService";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import {
    fetchFreeKey,
    verifyApiKey as verifyApiKeyApi,
} from "@/services/billingService";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/Alert";
import { useQueryParams } from "@/hooks";
import { useEffect, useRef, useState } from "react";
import { useApiKeyStore, useWalletStore } from "@/stores";
import { Drawer, DrawerContent } from "@/components/ui/Drawer";
import {
    TryApiAgentTab,
    TryApiCasesTab,
    TryApiCertsTab,
    TryApiPrintTab,
    TryApiStateTab,
    TryApiVerifyTab,
} from "./tabs";
import { TriangleAlert } from "lucide-react";
import type { HandleAction, HandleChange } from "./tabs/types";

type Html = string | null;
type Tabs = (typeof TAB_ACTIONS)[keyof typeof TAB_ACTIONS];

// type FormatCapsChange = Flow["agent_caps"];

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
    const { lastCert, setCert, setLastCert } = useWalletStore();
    const { demo, run } = useQueryParams(["demo", "run"]);

    const isDevKeyAllowed = devKeyAllowed ?? isLocalhost;
    const [html, setHtml] = useState<Html>(null);
    const [open, setOpen] = useState(false);
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

    const updateHtml = (html: Html) => {
        setOpen(true);
        setHtml(html);
    };
    const updateCert = (cert: Wire) => {
        const entry = setCert(cert);
        setLastCert(cert);
        toast("Saved to My certs — verify at /verify?id=" + entry.id);
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
            toast("New API key saved");
        } catch (error) {
            const err = toMessage(error);
            toast(err);
        }
    };

    const handleAgent = async (apiKey: string, flow: Flow) => {
        try {
            const text = stringify(flow.agent_caps);
            const caps = parseJSON<Flow["agent_caps"]>(text);
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

    const handleChange = (e: HandleChange) => {
        if (typeof e === "string") {
            setFlow((prev) => ({
                ...prev,
                type: e,
            }));
        } else {
            const { name, value } = e.target;
            setFlow((prev) => ({
                ...prev,
                [name]: value,
            }));
        }
    };

    const handleAction = (t: HandleAction) => {
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
        setFlow((prev) => ({
            ...prev,
            certificate: cert,
            certificate_optional: cert,
        }));
    }, [lastCert]);

    useEffect(() => {
        if (demo === "agent") {
            handleAction("agent_pki");
        }
        if (Number(run) === 1) {
            handleAgent(apiKey, flow);
        }
        assignApiKey(apiKey, isDevKeyAllowed);
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
                {/* 
                <Button variant="link" onClick={() => setOpen(true)}>
                    View API response
                </Button>
                */}
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
                    <div className="flex flex-col gap-4 md:flex-row md:justify-between">
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
                    className="flex-1 gap-8 **:data-[slot=card-content]:has-data-[slot=field]:flex **:data-[slot=card-content]:has-data-[slot=field]:flex-col **:data-[slot=card-content]:has-data-[slot=field]:gap-4"
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
                    <TabsContent value={TAB_ACTIONS.CASES}>
                        <TryApiCasesTab
                            codeBlocks={codeBlocks}
                            codeErrors={codeErrors}
                            handleAction={handleAction}
                            updateHtml={updateHtml}
                        />
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.AGENT}>
                        <TryApiAgentTab
                            flow={flow}
                            handleChange={handleChange}
                            handleAgent={handleAgent}
                        />
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.STATE}>
                        <TryApiStateTab
                            flow={flow}
                            handleChange={handleChange}
                            updateCert={updateCert}
                        />
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.VERIFY}>
                        <TryApiVerifyTab
                            flow={flow}
                            handleChange={handleChange}
                            resolveCert={resolveCert}
                        />
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.PRINT}>
                        <TryApiPrintTab
                            flow={flow}
                            handleChange={handleChange}
                            resolveCert={resolveCert}
                        />
                    </TabsContent>
                    <TabsContent value={TAB_ACTIONS.CERTS}>
                        <TryApiCertsTab />
                    </TabsContent>
                </Tabs>
                <Drawer open={open} onOpenChange={setOpen}>
                    <DrawerContent className="border-border rounded-t-none!">
                        <CodeBlock>
                            <CodeBlockHeader>
                                <CodeBlockTitle>JSON</CodeBlockTitle>
                            </CodeBlockHeader>
                            <CodeBlockContent html={html ?? ""} />
                        </CodeBlock>
                    </DrawerContent>
                </Drawer>
            </Container>
        </section>
    );
}
