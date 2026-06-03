import { api } from "@/api/client";

export async function validateKey(key: string): Promise<boolean> {
    const resp = await api.post("/billing/validate-key", {
        headers: { "X-API-Key": key },
    });
    const data = await resp.json();
    return Boolean(data.valid);
}

export async function fetchNewKey(): Promise<string> {
    const resp = await api.post("/billing/free-key");
    const data = await resp.json();
    return data.key as string;
}
