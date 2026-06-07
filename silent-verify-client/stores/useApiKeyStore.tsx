import { create } from "zustand";
import { persist } from "zustand/middleware";

const STORAGE_KEY = "sv_api_key";

type ApiKeyStore = {
    apiKey: string;
    setApiKey: (apiKey: string) => void;
    clearApiKey: () => void;
};

export const useApiKeyStore = create<ApiKeyStore>()(
    persist(
        (set) => ({
            apiKey: "",
            setApiKey: (key) =>
                set({
                    apiKey: key,
                }),
            clearApiKey: () =>
                set({
                    apiKey: "",
                }),
        }),
        {
            name: STORAGE_KEY,
        }
    )
);
