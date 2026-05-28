import { Container } from "@/components/layout";
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
        <section>
            <Container className="flex flex-col gap-4">
                <h2>Plans & Pricing</h2>
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Architecto sunt molestias a voluptates, doloremque ut.</p>
                <div className="flex flex-col items-center justify-between gap-8 mt-8 md:flex-row">
                    {plans.map((plan, index) => (
                        <article
                            className="w-full p-6 flex flex-col gap-4 border border-border bg-surface rounded-2xl"
                            key={`plan-${index}`}
                        >
                            <h3>{plan.title}</h3>
                            {typeof plan.price === "string" ? (
                                <div className="">{plan.price}</div>
                            ) : (
                                <div className="">
                                    <span>
                                        {plan.price.currency}/
                                        {plan.price.amount}
                                    </span>
                                    <small>{plan.price.interval}</small>
                                </div>
                            )}
                            <ul className="flex flex-col gap-2">
                                {plan.features.map((feature, index) => (
                                    <li className="" key={`feature-${index}`}>
                                        <span className="text-green-500 mr-2">
                                            ✓
                                        </span>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                            <Button size="lg">{plan.action}</Button>
                        </article>
                    ))}
                </div>
            </Container>
        </section>
    );
}
