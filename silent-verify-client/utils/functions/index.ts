import { Wire } from "@/types";
type Result<T> =
    | { success: true; data: T }
    | { success: false; error: unknown };

export function certLabel(wire: Wire) {
    const meta = wire.metadata || {};
    if (meta.agent_did) return String(meta.agent_did);
    if (meta.cert_type === "state" && wire.metadata?.chain_id) {
        return `${wire.metadata.chain_id} @ ${
            wire.metadata.block_height || "?"
        }`;
    }
    const ct = meta.cert_type || "certificate";
    return `${ct} · ${(wire.pubkey_fp || "").slice(0, 12)}…`;
}

export function parseJSON<T>(value: string): Result<T> {
    try {
        return {
            success: true,
            data: JSON.parse(value) as T,
        };
    } catch (error) {
        return {
            success: false,
            error: toMessage(error),
        };
    }
}

export function stringify<T>(value: T) {
    return JSON.stringify(value, null, 2);
}

export function toLocalDate(date: string) {
    return new Date(date).toLocaleString("en-GB");
}
export function toMessage(e: unknown) {
    if (e instanceof Error) {
        return e.message;
    } else {
        return String(e);
    }
}
