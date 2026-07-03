import { api } from "@/lib/api";

export type BillingStatus = {
    stripe_enabled: boolean;
    public_url: string;
    plans: Record<string, unknown>;
};

export async function getBillingStatus(): Promise<BillingStatus> {
    const resp = await api.get("/billing/status");
    return resp.json();
}

export async function verifyApiKey(key: string) {
    const resp = await api.get("/billing/validate-key", {
        headers: { "X-API-Key": key },
    });
    const data = await resp.json();
    return data;
}

export async function fetchFreeKey() {
    const resp = await api.post("/billing/free-key");
    const data = await resp.json();
    return data.api_key as string;
}

export async function startProCheckout() {
    const resp = await api.post("/billing/checkout");
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Stripe checkout is not configured on this deployment."
        );
    }
    return data as { checkout_url: string; session_id: string };
}

export async function redeemCheckoutSession(sessionId: string) {
    const resp = await api.get(
        `/billing/session/${encodeURIComponent(sessionId)}`
    );
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Could not retrieve API key for this checkout session."
        );
    }
    return data.api_key as string;
}

export async function getApiUsage(key: string) {
    const resp = await api.get("/billing/usage", {
        headers: {
            "X-API-Key": key,
        },
    });
    const data = await resp.json();
    return data;
}
