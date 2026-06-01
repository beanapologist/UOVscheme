import { create } from "zustand";
import { persist } from "zustand/middleware";

const STORAGE_KEY = process.env.NEXT_PUBLIC_STORAGE_PREFIX ?? "";

type ApiKeyStore = {};

export const useApiKeyStore = create<ApiKeyStore>()(
    persist((set, get) => ({}), {
        name: STORAGE_KEY,
    })
);
