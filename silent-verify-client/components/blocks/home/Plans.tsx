import { Container } from "@/components/layout";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

const plans = [
    {
        title: "Free",
        price: {
            amount: 0,
            currency: "$",
            interval: "month",
        },
        features: [
            "100 issuances / month",
            "Agent + state certificates",
            "All chain verify routes",
        ],
        action: "Get free API key",
    },
    {
        title: "Pro",
        price: {
            amount: 9,
            currency: "$",
            interval: "month",
        },
        features: [
            "High volume quota",
            "Production UOV profile on Railway",
            "Stripe billing",
        ],
        action: "Subscribe with Stripe",
    },
    {
        title: "Developers",
        price: "Self-Host",
        features: [
            "Open source Lean + Python",
            "Railway-ready deploy",
            "Bring your own RPC keys",
        ],
        action: "Try API",
    },
];

export default function Plans() {
    return (
        <section className="section">
            <Container className="flex flex-col gap-4">
                <h2>Plans & Pricing</h2>
                <p>
                    Lorem ipsum dolor sit amet consectetur adipisicing elit.
                    Architecto sunt molestias a voluptates, doloremque ut.
                </p>
                <div className="flex flex-col items-stretch justify-between gap-8 mt-8 md:flex-row">
                    {plans.map((plan, index) => (
                        <article
                            className="w-full p-6 flex flex-col justify-between gap-8 border border-border bg-surface rounded-2xl"
                            key={`plan-${index}`}
                        >
                            <Badge variant="outline">{plan.title}</Badge>
                            {typeof plan.price === "string" ? (
                                <div className="text-2xl font-bold">
                                    {plan.price}
                                </div>
                            ) : (
                                <div className="text-4xl font-bold">
                                    {plan.price.currency}
                                    {plan.price.amount}
                                    <small className="text-base text-muted-foreground font-medium">
                                        &nbsp;/&nbsp;{plan.price.interval}
                                    </small>
                                </div>
                            )}
                            <ul className="flex flex-1 flex-col gap-2">
                                {plan.features.map((feature, index) => (
                                    <li
                                        className="flex items-start"
                                        key={`feature-${index}`}
                                    >
                                        <span className="text-green-500 mr-2">
                                            ✓
                                        </span>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                            <Button>{plan.action}</Button>
                        </article>
                    ))}
                </div>
            </Container>
        </section>
    );
}
