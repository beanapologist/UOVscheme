import { api } from "@/api/client";

export async function getParams() {
    const resp = await api.get("/params");
    const data = await resp.json();
    return data;
}