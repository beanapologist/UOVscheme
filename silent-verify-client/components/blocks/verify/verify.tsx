"use client";
import { useEffect, useState } from "react";
import { useWalletStore } from "@/stores";
import { Container } from "@/components/layout";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import { Button } from "@/components/ui/Button";
import { ButtonGroup, ButtonGroupSeparator } from "@/components/ui/ButtonGroup";
import { LinkButton } from "@/components/ui/LinkButton";
import { Field } from "@/components/ui/Field";
import { Textarea } from "@/components/ui/Textarea";
import { CertResult, Wire } from "@/types";
import { toast } from "sonner";
import { getCertHtmlPublic, verifyPublicCert } from "@/services/certsService";
import {
    downloadJSON,
    openHtmlFile,
    stringify,
    toLocalDate,
    toMessage,
} from "@/utils/functions";
import { VerifyCertResult } from "./VerifyCertResult";
import { Input } from "@/components/ui/Input";
import { useQueryParams } from "@/hooks";

type Json = string | null;
type Data = CertResult | null;

export function Verify() {
    const { certId, run } = useQueryParams({ certId: "id", run: "run" });

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

    const updateJson = (cert: Json) => {
        setJson(cert);
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

    const exportCert = (cert: Json) => {
        try {
            const json = decodeCert(cert);
            downloadJSON(json);
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
        updateJson(text);
    };

    const renderHtml = async (cert: Json) => {
        try {
            const wire = decodeCert(cert);
            const html = await getCertHtmlPublic(wire);
            openHtmlFile(html);
        } catch (error) {
            const err = toMessage(error);
            toast.error(err);
        }
    };

    const verifyCert = async (cert: Json) => {
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
        if (!certId) return;
        const exists = certs.find((c) => c.id === certId);
        if (!exists) return;
        const data = stringify(exists);
        queueMicrotask(() => {
            updateJson(data);
            if (Number(run) === 1) {
                void verifyCert(data);
            }
        });
        // Hydrate from URL query params once on mount.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <section className="section-sm flex flex-col">
            <Container className="flex-1 flex flex-col gap-4">
                <h1>Use your certificate</h1>
                <p>
                    Paste JSON from an issuer, upload a .json file, or pick a
                    saved cert. Verification is cryptographic only - no API key
                    required.
                </p>
                {data && <VerifyCertResult data={data.data} wire={data.wire} />}
                <Field>
                    <Textarea
                        value={json ?? ""}
                        onChange={(e) => updateJson(e.target.value)}
                        placeholder="Paste the full cert object from POST .../issue (the cert field)"
                    />
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
                            <div className="flex flex-col">
                                {certs.map((cert) => (
                                    <div
                                        className="py-3 flex items-center justify-between border-b border-b-border"
                                        key={cert.id}
                                    >
                                        <div className="flex flex-col">
                                            <span>{cert.label}</span>
                                            <span>
                                                Saved{" "}
                                                {toLocalDate(cert.savedAt)}
                                            </span>
                                        </div>
                                        <ButtonGroup>
                                            <Button
                                                variant="outline"
                                                size="lg"
                                                onClick={() =>
                                                    updateJson(
                                                        stringify(cert.cert)
                                                    )
                                                }
                                            >
                                                Load
                                            </Button>
                                            <ButtonGroupSeparator />
                                            <Button
                                                variant="outline"
                                                size="lg"
                                                onClick={() =>
                                                    verifyCert(
                                                        stringify(cert.cert)
                                                    )
                                                }
                                            >
                                                Verify
                                            </Button>
                                            <ButtonGroupSeparator />
                                            <Button
                                                variant="outline"
                                                size="lg"
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
                    <TabsContent value="upload_certificates">
                        <Field>
                            <Input type="file" onChange={handleFile} />
                        </Field>
                    </TabsContent>
                </Tabs>
                <div className="flex flex-wrap items-center gap-2">
                    <Button variant="default" onClick={() => verifyCert(json)}>
                        Verify
                    </Button>
                    <Button variant="outline" onClick={() => commitCert(json)}>
                        Save to wallet
                    </Button>
                    <Button variant="outline" onClick={() => renderHtml(json)}>
                        Print / PDF
                    </Button>
                    <Button variant="outline" onClick={() => exportCert(json)}>
                        Download JSON
                    </Button>
                </div>
            </Container>
        </section>
    );
}
