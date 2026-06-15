"use client";

import { useApiKeyStore } from "@/stores";
import { Button } from "@/components/ui/Button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
} from "@/components/ui/Card";
import { Field, FieldLabel } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import type { Flow } from "@/types";
import type { HandleChange } from "./types";
import { stringify } from "@/utils/functions";

type Format = Flow["agent_caps"] | string;
export default function TryApiAgentTab({
    flow,
    handleChange,
    handleAgent,
}: {
    flow: Flow;
    handleChange: (e: HandleChange) => void;
    handleAgent: (apiKey: string, flow: Flow) => void;
}) {
    const apiKey = useApiKeyStore((state) => state.apiKey);
    const format = (v: Format) => (typeof v === "string" ? v : stringify(v));

    return (
        <Card>
            <CardHeader>
                <CardDescription>
                    Creates a post-quantum agent identity certificate (DID +
                    capabilities).
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Field>
                    <FieldLabel>Agent DID</FieldLabel>
                    <Input
                        name="agent_did"
                        value={flow.agent_did}
                        onChange={handleChange}
                    />
                </Field>
                <Field>
                    <FieldLabel>Capabilities (JSON)</FieldLabel>
                    <Input
                        name="agent_caps"
                        value={format(flow.agent_caps)}
                        onChange={handleChange}
                    />
                </Field>
            </CardContent>
            <CardFooter>
                <Button onClick={() => handleAgent(apiKey, flow)}>
                    Issue agent certificate
                </Button>
            </CardFooter>
        </Card>
    );
}
