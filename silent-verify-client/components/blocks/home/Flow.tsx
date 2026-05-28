import { Container } from "@/components/layout";
import { Button } from "@/components/ui/Button";

const steps = [
    {
        title: "Issue",
        description: "Agent DID or chain state digest, signed with UOV",
    },
    { title: "Share", description: "JSON wire cert or printable PDF" },
    { title: "Verify", description: "Stateless check — no full node required" },
];
export default function Flow() {
    return (
        <section>
            <Container className="flex flex-col gap-8">
                <h2>How it works</h2>
                <div className="flex flex-col gap-8 md:flex-row">
                    {steps.map((step, index) => (
                        <div
                            className="p-4 flex-1 flex flex-row gap-4 border border-border rounded-xl"
                            key={`step-${index}`}
                        >
                            <div className="text-4xl font-semibold">
                                0{index + 1}.
                            </div>
                            <div className="flex flex-col gap-2">
                                <h4>{step.title}</h4>
                                <p>{step.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="p-8 flex flex-col gap-4 border border-border rounded-2xl">
                    <h4>Why UOV + SilentVerify?</h4>
                    <p>
                        Unbalanced Oil and Vinegar (UOV) gives fast signing and
                        verification on prime fields — practical for agents and
                        APIs. Our production profile (<code>I_MIN</code>: q=251,
                        o=8, v=24) targets NIST-style security levels; core
                        algorithms are&nbsp;
                        <a
                            className="text-primary underline underline-offset-4"
                            href="https://github.com/beanapologist/UOVscheme/tree/main/formal"
                            target="_blank"
                            rel="noopener"
                        >
                            formally specified in Lean 4
                        </a>
                        .
                    </p>
                    <ul>
                        <li>
                            Trust cross-chain or off-chain state without
                            multisigs or running your own archive node
                        </li>
                        <li>
                            Post-quantum agent identity for MCP, serverless, and
                            payout gating
                        </li>
                        <li>
                            Same REST API for EVM, Solana, Cosmos, and XRPL
                            anchors
                        </li>
                    </ul>
                    <Button
                        className="w-fit"
                        variant="link"
                        nativeButton={false}
                        render={
                            <a
                                href="https://csrc.nist.gov/projects/post-quantum-cryptography"
                                target="_blank"
                                rel="noopener"
                            >
                                NIST PQC program
                            </a>
                        }
                    />
                </div>
            </Container>
        </section>
    );
}
