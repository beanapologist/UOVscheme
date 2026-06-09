import { api } from "@/api/client";

const FALLBACK_PARAMS = {
    auth: {
        dev_key_enabled: true,
    },
};

export async function getParams() {
    try {
        const resp = await api.get("/params");
        if (!resp.ok) return FALLBACK_PARAMS;
        return await resp.json();
    } catch {
        return FALLBACK_PARAMS;
    }
}
