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
import { openHtmlFile, stringify, toMessage } from "@/utils/functions";
import type { HandleChange } from "./types";
import { getCertHtml } from "@/services/certsService";

type Load = {
    cert: Flow["certificate"];
    type?: Flow["type"];
    lastCert: Flow["certificate"];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;
export default function TryApiPrintTab({
    flow,
    handleChange,
    resolveCert,
}: {
    flow: Flow;
    resolveCert: (cert: string, lastCert: string) => Wire | null;
    handleChange: (e: HandleChange) => void;
}) {
    const apiKey = useApiKeyStore((state) => state.apiKey);
    const lastCert = useWalletStore((state) => state.lastCert);

    const openCertHtml = async (apiKey: string, flow: Load) => {
        try {
            const cert = resolveCert(flow.cert, flow.lastCert);
            if (!cert) return;
            const html = await getCertHtml(apiKey, { wire: cert });
            openHtmlFile(html);
        } catch (error) {
            const err = toMessage(error);
            // show in code block
            console.error(err);
        }
    };
    const previewCert = () => {
        const url = `${API_URL}/api/v1/certs/print/demo?autoprint=1`;
        window.open(url, "_blank");
    };
    return (
        <Card>
            <CardHeader>
                <CardDescription>
                    Opens a print-friendly page with identity, crypto fields,
                    and full wire JSON. Uses the certificate from your last
                    issue or the JSON below
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Field>
                    <FieldLabel>Certificate JSON (optional)</FieldLabel>
                    <Textarea
                        name="certificate_optional"
                        value={flow.certificate_optional}
                        placeholder="Leave empty to use last issued cert"
                        onChange={handleChange}
                    />
                </Field>
            </CardContent>
            <CardFooter>
                <Button
                    variant="default"
                    onClick={() =>
                        openCertHtml(apiKey, {
                            cert: flow.certificate_optional,
                            lastCert: lastCert ? stringify(lastCert) : "",
                        })
                    }
                >
                    Print certificate
                </Button>
                <Button variant="outline" onClick={() => previewCert()}>
                    Demo print (no key)
                </Button>
            </CardFooter>
        </Card>
    );
}
