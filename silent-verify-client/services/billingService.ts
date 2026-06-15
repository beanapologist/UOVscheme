import { api } from "@/lib/api";

export async function verifyApiKey(key: string) {
    const resp = await api.get("/billing/validate-key", {
        headers: { "X-API-key": key },
    });
    const data = await resp.json();
    return data;
}

export async function fetchFreeKey() {
    const resp = await api.post("/billing/free-key");
    const data = await resp.json();
    return data.api_key;
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
