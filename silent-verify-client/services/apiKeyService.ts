import { api } from "@/api/client";

export async function validateKey(key: string) {
    const resp = await api.post("/billing/validate-key", {
        headers: { "X-API-key": key },
    });
    const data = await resp.json();
    return data.valid;
}

export async function fetchNewKey() {
    const resp = await api.post("/billing/free-key");
    const data = await resp.json();
    return data.api_key;
}
