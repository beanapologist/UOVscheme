import { create } from "zustand";
import { persist } from "zustand/middleware";

const STORAGE_KEY = process.env.NEXT_PUBLIC_STORAGE_PREFIX ?? "";

type ApiKeyStore = Record<string, never>;

export const useApiKeyStore = create<ApiKeyStore>()(
    persist(() => ({}), {
        name: STORAGE_KEY,
    })
);
