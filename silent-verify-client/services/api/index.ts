import { api } from "@/lib/api";

export async function getApiBlock({ code }: { code: unknown }) {
    const resp = await api.post("/api/highlight", {
        body: JSON.stringify({ code }),
    });
    const data = await resp.json();
    return data;
}
