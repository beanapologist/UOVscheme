"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Container } from "@/components/layout";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
    fetchFreeKey,
    getBillingStatus,
    startProCheckout,
} from "@/services/billingService";
import { useApiKeyStore } from "@/stores";
import { ApiKeyDialog } from "@/components/shared/dialog";
import { toMessage } from "@/utils/functions";

const plans = [
    {
        id: "free",
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
        id: "pro",
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
        id: "developers",
        title: "Developers",
        price: "Self-Host",
        features: [
            "Open source Lean + Python",
            "Railway-ready deploy",
            "Bring your own RPC keys",
        ],
        action: "Try API",
    },
] as const;

export default function Plans() {
    const router = useRouter();
    const setApiKey = useApiKeyStore((state) => state.setApiKey);
    const [stripeEnabled, setStripeEnabled] = useState(false);
    const [loading, setLoading] = useState<string | null>(null);
    const [keyDialogOpen, setKeyDialogOpen] = useState(false);

    useEffect(() => {
        getBillingStatus()
            .then((status) => setStripeEnabled(status.stripe_enabled))
            .catch(() => setStripeEnabled(false));
    }, []);

    const handlePlan = async (planId: (typeof plans)[number]["id"]) => {
        setLoading(planId);
        try {
            if (planId === "free") {
                const key = await fetchFreeKey();
                setApiKey(key);
                setKeyDialogOpen(true);
                toast.success("Free API key created.");
                return;
            }
            if (planId === "pro") {
                if (!stripeEnabled) {
                    toast.error(
                        "Stripe is not configured on the API yet. Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID on the backend."
                    );
                    return;
                }
                const { checkout_url } = await startProCheckout();
                window.location.assign(checkout_url);
                return;
            }
            router.push("/docs");
        } catch (error) {
            toast.error(toMessage(error));
        } finally {
            setLoading(null);
        }
    };

    return (
        <section className="section">
            <Container className="flex flex-col gap-4">
                <h2>Plans & Pricing</h2>
                <p>
                    Start free, upgrade to Pro for production volume, or
                    self-host the open-source stack.
                </p>
                <div className="flex flex-col items-stretch justify-between gap-8 mt-8 md:flex-row">
                    {plans.map((plan) => (
                        <article
                            className="w-full p-6 flex flex-col justify-between gap-8 border border-border bg-surface rounded-2xl"
                            key={plan.id}
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
                                {plan.features.map((feature) => (
                                    <li
                                        className="flex items-start"
                                        key={feature}
                                    >
                                        <span className="text-green-500 mr-2">
                                            ✓
                                        </span>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                            <Button
                                disabled={loading === plan.id}
                                onClick={() => handlePlan(plan.id)}
                            >
                                {loading === plan.id
                                    ? "Please wait…"
                                    : plan.action}
                            </Button>
                        </article>
                    ))}
                </div>
            </Container>
            <ApiKeyDialog
                open={keyDialogOpen}
                onOpenChange={setKeyDialogOpen}
            />
        </section>
    );
}
