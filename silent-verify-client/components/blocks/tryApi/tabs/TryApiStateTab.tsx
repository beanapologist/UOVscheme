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
import { Flow, Wire } from "@/types";
import type { HandleChange } from "./types";
import { getStateCert } from "@/services/certsService";
import { toMessage } from "@/utils/functions";

export default function TryApiStateTab({
    flow,
    updateCert,
    handleChange,
}: {
    flow: Flow;
    updateCert: (cert: Wire) => void;
    handleChange: (e: HandleChange) => void;
}) {
    const apiKey = useApiKeyStore((state) => state.apiKey);

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
    return (
        <Card>
            <CardHeader>
                <CardDescription>
                    Anchors a live chain state snapshot into a UOV certificate.
                    Chain ID
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Field>
                    <FieldLabel>Chain ID</FieldLabel>
                    <Input
                        name="chain_id"
                        value={flow.chain_id}
                        onChange={handleChange}
                    />
                </Field>
                <Field>
                    <FieldLabel>Block height</FieldLabel>
                    <Input
                        name="block_height"
                        value={flow.block_height}
                        onChange={handleChange}
                    />
                </Field>
                <Field>
                    <FieldLabel>State root (hex)</FieldLabel>
                    <Input
                        name="state_root_hex"
                        value={flow.state_root_hex}
                        onChange={handleChange}
                    />
                </Field>
            </CardContent>
            <CardFooter>
                <Button onClick={() => handleState(apiKey, flow)}>
                    Issue state certificate
                </Button>
            </CardFooter>
        </Card>
    );
}
