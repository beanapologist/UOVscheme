"use client";

import { Container } from "@/components/layout";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/Tabs";
import { Button } from "@/components/ui/Button";
import { ButtonGroup, ButtonGroupSeparator } from "@/components/ui/ButtonGroup";
import { LinkButton } from "@/components/ui/LinkButton";
import { Field } from "@/components/ui/Field";
import { Textarea } from "@/components/ui/Textarea";

export function Verify() {
    const certs: Array<{ id: string }> = [];
    // const { certs } = useWalletStore((state) => state.certs);
    return (
        <section className="section-sm flex flex-col">
            <Container className="flex-1 flex flex-col gap-4">
                <h1>Use your certificate</h1>
                <p>
                    Paste JSON from an issuer, upload a .json file, or pick a
                    saved cert. Verification is cryptographic only - no API key
                    required.
                </p>
                <Tabs
                    className="flex-1 gap-8"
                    defaultValue="saved_certificates"
                >
                    <TabsList variant="outline">
                        <TabsTrigger value="saved_certificates">
                            Saved certificates
                        </TabsTrigger>
                        <TabsTrigger value="paste_certificates">
                            Paste certificates
                        </TabsTrigger>
                        <TabsTrigger value="upload_json">
                            Upload JSON
                        </TabsTrigger>
                    </TabsList>
                    <TabsContent value="saved_certificates">
                        <p>
                            Certs you issue at&nbsp;
                            <LinkButton href="/docs">Try API</LinkButton> can be
                            saved here for quick verify and print.
                        </p>
                        {certs.length ? (
                            <div>
                                {certs.map((cert) => (
                                    <div key={cert.id}>
                                        <div>
                                            <span>Lorem ipsum</span>
                                            <span>Saved 28/06/2026</span>
                                        </div>
                                        <ButtonGroup>
                                            <Button>Load</Button>
                                            <ButtonGroupSeparator />
                                            <Button>Verify</Button>
                                            <ButtonGroupSeparator />
                                            <Button>Remove</Button>
                                        </ButtonGroup>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div>No saved certs</div>
                        )}
                    </TabsContent>
                    <TabsContent value="paste_certificates">
                        <Field>
                            <Textarea placeholder="Paste the full cert object from POST .../issue (the cert field)" />
                        </Field>
                    </TabsContent>
                    <TabsContent value="upload_json"></TabsContent>
                </Tabs>
                <div className="flex flex-wrap items-center gap-2">
                    <Button variant="default">Verify</Button>
                    <Button variant="outline">Save to wallet</Button>
                    <Button variant="outline">Print / PDF</Button>
                    <Button variant="outline">Download JSON</Button>
                </div>
            </Container>
        </section>
    );
}
