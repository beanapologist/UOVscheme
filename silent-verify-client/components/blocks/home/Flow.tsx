import { Container } from "@/components/layout";

const steps = [
    {
        step: "01",
        title: "Issue",
        description: "Agent DID or chain state digest, signed with UOV",
    },
    {
        step: "02",
        title: "Share",
        description: "JSON wire cert or printable PDF",
    },
    {
        step: "03",
        title: "Verify",
        description: "Stateless check — no full node required",
    },
];
export default function Flow() {
    return (
        <section className="section">
            <Container className="flex flex-col gap-4">
                <small className="uppercase text-primary">
                    How it works
                </small>
                <h2>
                    Three Steps <br /> One Result
                </h2>
                <div className="mt-6 flex flex-col ring ring-border divide-y divide-border rounded-xl overflow-hidden md:flex-row md:divide-y-0 md:divide-x">
                    {steps.map((step, index) => (
                        <div
                            className="p-8 flex-1 flex flex-col gap-4"
                            key={`step-${index}`}
                        >
                            <div className="flex">
                                <h4>
                                    <span className="text-primary">
                                        {step.step}.&nbsp;
                                    </span>
                                    {step.title}
                                </h4>
                            </div>
                            <div className="">
                                <p>{step.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </Container>
        </section>
    );
}
