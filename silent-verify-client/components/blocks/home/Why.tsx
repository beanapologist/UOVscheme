import { Container } from "@/components/layout";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import { Braces, Cpu, Network } from "lucide-react";

const features = [
    {
        icon: Network,
        title: "Cross-chain trust",
        body: "Verify cross-chain or off-chain state without multisigs or running your own archive node.",
        accent: "bg-cyan-950/10 text-cyan-100 border-cyan-500/90",
    },
    {
        icon: Cpu,
        title: "Agent identity",
        body: "Post-quantum agent identity for MCP, serverless, and payout gating — built for the agentic era.",
        accent: "bg-teal-950/10 text-teal-100 border-teal-600/90",
    },
    {
        icon: Braces,
        title: "One REST API",
        body: "Same endpoint for EVM, Solana, Cosmos, and XRPL anchors — no per-chain integration work.",
        accent: "bg-mist-950/10 text-mist-100 border-mist-500/90",
    },
];

export default function Why() {
    return (
        <section className="section">
            <Container className="flex flex-col gap-6 relative">
                <h2>Why UOV + SilentVerify?</h2>
                <p>
                    Unbalanced Oil and Vinegar (UOV) gives fast signing and
                    verification on prime fields — practical for agents and
                    APIs. Our production profile (<code>I_MIN</code>: q=251,
                    o=8, v=24) targets NIST-style security levels; core
                    algorithms are
                    <a
                        href="https://github.com/beanapologist/UOVscheme/tree/main/formal"
                        target="_blank"
                        rel="noopener"
                    >
                        formally specified in Lean 4
                    </a>
                    .
                </p>
                <div className="flex flex-col gap-9 md:flex-row">
                    {features.map((feature) => (
                        <Card key={feature.title}>
                            <CardHeader>
                                <Badge
                                    className={cn(
                                        "[&>svg]:size-5! size-10 rounded-lg mb-2",
                                        feature.accent
                                    )}
                                    variant="outline"
                                >
                                    <feature.icon />
                                </Badge>
                                <CardTitle>{feature.title}</CardTitle>
                            </CardHeader>
                            <CardContent>{feature.body}</CardContent>
                        </Card>
                    ))}
                </div>
                {/* 
                <a
                    href="https://csrc.nist.gov/projects/post-quantum-cryptography"
                    target="_blank"
                    rel="noopener"
                    className="absolute top-0 right-0"
                >
                    NIST PQC program
                </a>
                 */}
            </Container>
        </section>
    );
}
