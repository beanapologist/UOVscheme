"use client";

import { Container } from "@/components/layout";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useEnsureApiKey } from "@/hooks/useEnsureApiKey";
import { toMessage } from "@/utils/functions";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function Hero() {
    const router = useRouter();
    const { mutateAsync: ensureApiKey } = useEnsureApiKey();

    const handleConsole = async () => {
        try {
            router.push("/docs");
        } catch (error) {
            const err = toMessage(error);
            toast.error(err);
        }
    };

    const handleApiDemo = async () => {
        try {
            await ensureApiKey();
            router.push("/docs?demo=agent&run=1");
        } catch (error) {
            const err = toMessage(error);
            toast.error(err);
        }
    };
    return (
        <section className="section">
            <Container className="flex flex-col gap-4">
                <h1>
                    Post-quantum certificates <br /> for agents &amp; chain
                    state
                </h1>
                <p>
                    Issue and verify UOV-backed agent identity certs and
                    live-anchored state proofs across EVM, Solana, Cosmos, and
                    XRPL.
                </p>
                <div className="flex flex-wrap items-center gap-2 mb-4">
                    <Badge variant="outline" size="lg">
                        Agent KPI
                    </Badge>
                    <Badge variant="outline" size="lg">
                        Multi-chain anchors
                    </Badge>
                    <Badge variant="outline" size="lg">
                        Lean 4 verified core
                    </Badge>
                </div>
                <div className="flex flex-wrap items-center gap-4 mb-0">
                    <Button
                        variant="default"
                        size="lg"
                        onClick={() => handleApiDemo()}
                    >
                        Try live demo
                    </Button>
                    <Button
                        variant="outline"
                        size="lg"
                        onClick={() => handleConsole()}
                    >
                        Open API console
                    </Button>
                </div>
            </Container>
        </section>
    );
}
