"use client";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useWalletStore } from "@/stores";
import { Container } from "@/components/layout";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import { Button } from "@/components/ui/Button";
import { ButtonGroup, ButtonGroupSeparator } from "@/components/ui/ButtonGroup";
import { LinkButton } from "@/components/ui/LinkButton";
import { Field } from "@/components/ui/Field";
import { Textarea } from "@/components/ui/Textarea";
import { Wire } from "@/types";
import { toast } from "sonner";
import { verifyPublicCert } from "@/services/certsService";
import { toMessage } from "@/utils/functions";
import { VerifyCertResult } from "./VerifyCertResult";

type Json = string | null;
type Data = {
    data: any;
    wire: Wire;
} | null;

export function Verify() {
    const searchParams = useSearchParams();
    const walletId = searchParams.get("id");
    const runQuery = searchParams.get("run");

    const [json, setJson] = useState<Json>(null);
    const [data, setData] = useState<Data>(null);

    const { certs, saveCert, removeCert } = useWalletStore();

    const decodeCert = (cert: Json) => {
        const rawCert = cert?.trim();
        if (!rawCert) {
            throw new Error("Paste or upload a certificate JSON");
        }
        const rawData = JSON.parse(rawCert);
        return (rawData.cert ?? rawData) as Wire;
    };

    const updateJson = (cert: Wire) => {
        const data = JSON.stringify(cert, null, 2);
        setJson(data);
        return data;
    };

    const commitCert = (cert: Json) => {
        try {
            const wire = decodeCert(cert);
            saveCert(wire);
        } catch (error) {
            const err = toMessage(error);
            toast.error(err);
        }
    };

    const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];

        if (!file) return;
        if (!file.name.endsWith(".json")) return;
        if (!file.type.endsWith("/json")) return;

        const text = await file.text();
        setJson(text);
    };

    const verifyCert = async (c) => {
        const cert = c ? updateJson(c) : json;
        try {
            const wire = decodeCert(cert);
            const data = await verifyPublicCert(wire);
            setData({ data, wire });
        } catch (error) {
            const err = toMessage(error);
            toast.error(err);
        }
    };

    useEffect(() => {
        if (!walletId) return;
        const existing = certs.find((c) => c.id === walletId);
        if (!existing) return;
        updateJson(existing.cert);
    }, [walletId, certs]);

    useEffect(() => {
        if (!walletId) return;
        if (!runQuery) return;
        verifyCert(json);
    }, [walletId, runQuery, json, verifyCert]);

    return (
        <section className="section-sm flex flex-col">
            <Container className="flex-1 flex flex-col gap-4">
                <h1>Use your certificate</h1>
                <p>
                    Paste JSON from an issuer, upload a .json file, or pick a
                    saved cert. Verification is cryptographic only - no API key
                    required.
                </p>
                {data && (
                    <VerifyCertResult data={data.data} wire={data.wire} />
                )}
                <Field>
                    <Textarea placeholder="Paste the full cert object from POST .../issue (the cert field)" />
                </Field>
                <Tabs
                    className="flex-1 gap-8"
                    defaultValue="stored_certificates"
                >
                    <TabsList variant="outline">
                        <TabsTrigger value="stored_certificates">
                            Saved certificates
                        </TabsTrigger>
                        <TabsTrigger value="upload_certificates">
                            Upload JSON
                        </TabsTrigger>
                    </TabsList>
                    <TabsContent value="stored_certificates">
                        <p>
                            Certs you issue at&nbsp;
                            <LinkButton href="/docs">Try API</LinkButton> can be
                            saved here for quick verify and print.
                        </p>
                        {certs.length ? (
                            <div>
                                {certs.map((cert) => (
                                    <div className="" key={cert.id}>
                                        <div>
                                            <span>{cert.label}</span>
                                            <span>{cert.savedAt}</span>
                                        </div>
                                        <ButtonGroup>
                                            <Button
                                                onClick={() =>
                                                    updateJson(cert.cert)
                                                }
                                            >
                                                Load
                                            </Button>
                                            <ButtonGroupSeparator />
                                            <Button
                                                onClick={() =>
                                                    verifyCert(cert.cert)
                                                }
                                            >
                                                Verify
                                            </Button>
                                            <ButtonGroupSeparator />
                                            <Button
                                                onClick={() =>
                                                    removeCert(cert.id)
                                                }
                                            >
                                                Remove
                                            </Button>
                                        </ButtonGroup>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div>No saved certs</div>
                        )}
                    </TabsContent>
                    <TabsContent value="upload_certificates"></TabsContent>
                </Tabs>
                <div className="flex flex-wrap items-center gap-2">
                    <Button variant="default" onClick={() => verifyCert(json)}>
                        Verify
                    </Button>
                    <Button variant="outline" onClick={() => commitCert(json)}>
                        Save to wallet
                    </Button>
                    <Button variant="outline">Print / PDF</Button>
                    <Button variant="outline">Download JSON</Button>
                </div>
            </Container>
        </section>
    );
}
