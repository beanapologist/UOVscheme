import { api } from "@/api/client";

async function validateKey(key) {
    const resp = await api.post("/billing/validate-key", {
        headers: { "X-API-key": key },
    });
    const data = await resp.json();
    return data.valid;
}

async function fetchNewKey() {
    const resp = await api.post("/billing/free-key");
    const data = resp.key;
}
