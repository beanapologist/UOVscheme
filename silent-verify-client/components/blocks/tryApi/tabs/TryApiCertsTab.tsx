"use client";

import { useWalletStore } from "@/stores";
import { Button } from "@/components/ui/Button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
} from "@/components/ui/Card";
import { Cert, Wire } from "@/types";
import { LinkButton } from "@/components/ui/LinkButton";
import { Badge } from "@/components/ui/Badge";
import { toLocalDate } from "@/utils/functions";
import Link from "next/link";
import { Binary, Fingerprint } from "lucide-react";
import { toast } from "sonner";

export default function TryApiCertsTab() {
    const { certs, setLastCert } = useWalletStore();
    
    const encodeCert = (cert: Cert) => {
        return `/verify?id=${encodeURIComponent(cert.id)}&run=1`;
    };
    const loadInTabs = (cert: Wire) => {
        setLastCert(cert);
        toast("Loaded into Verify / Print tabs");
    };
    return (
        <Card>
            <CardHeader>
                <CardDescription>
                    Certificates saved in this browser. Open&nbsp;
                    <LinkButton href="/">verify</LinkButton>
                    &nbsp; to check or print without an API key.
                </CardDescription>
            </CardHeader>
            <CardContent>
                {certs.length ? (
                    <div className="flex flex-col gap-4">
                        {certs.map((cert, i) => (
                            <div
                                className="p-4 flex items-center gap-4 justify-between border border-border rounded-lg"
                                key={i}
                            >
                                <Badge
                                    className="size-10 rounded-lg [&>svg]:size-5!"
                                    variant="outline"
                                >
                                    {i % 2 === 0 ? <Fingerprint /> : <Binary />}
                                </Badge>
                                <div className="inline-flex flex-col gap-1 flex-1">
                                    <div>{cert.label}</div>
                                    <div>{toLocalDate(cert.savedAt)}</div>
                                </div>
                                <div className="inline-flex flex-row gap-2 flex-0">
                                    <Button
                                        variant="link"
                                        nativeButton={false}
                                        render={
                                            <Link href={encodeCert(cert)}>
                                                Verify
                                            </Link>
                                        }
                                    />
                                    <Button
                                        onClick={() => loadInTabs(cert.cert)}
                                    >
                                        Load in tabs
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div>
                        Issue a cert above — it will appear here automatically.
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
