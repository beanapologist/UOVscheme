"use client";

import { useApiKeyStore, useWalletStore } from "@/stores";
import { Button } from "@/components/ui/Button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
} from "@/components/ui/Card";
import { Field, FieldLabel } from "@/components/ui/Field";
import { Flow, Wire } from "@/types";
import { Textarea } from "@/components/ui/Textarea";
import { Label } from "@/components/ui/Label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/RadioGroup";
import { stringify, toMessage } from "@/utils/functions";
import { verifyAgentCert, verifyStateCert } from "@/services/certsService";
import type { HandleChange } from "./types";

type Load = {
    cert: Flow["certificate"];
    type?: Flow["type"];
    lastCert: Flow["certificate"];
};

export default function TryApiVerifyTab({
    flow,
    handleChange,
    resolveCert
}: {
    flow: Flow;
    resolveCert: (cert: string, lastCert: string) => Wire | null;
    handleChange: (e: HandleChange) => void;
}) {
    const apiKey = useApiKeyStore((state) => state.apiKey);
    const lastCert = useWalletStore((state) => state.lastCert);

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
    return (
        <Card>
            <CardHeader>
                <CardDescription>
                    Paste the cert object from a previous issue response, or use
                    the last result automatically.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Field>
                    <FieldLabel>Certificate JSON</FieldLabel>
                    <Textarea
                        name="certificate"
                        value={flow.certificate}
                        placeholder='{"schema_version": ...}'
                        onChange={handleChange}
                    />
                </Field>
                <RadioGroup
                    name="type"
                    value={flow.type}
                    onValueChange={handleChange}
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
                            lastCert: lastCert ? stringify(lastCert) : "",
                        })
                    }
                >
                    Verify
                </Button>
            </CardFooter>
        </Card>
    );
}
