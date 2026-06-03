import { create } from "zustand";
import { persist } from "zustand/middleware";

const STORAGE_KEY = process.env.NEXT_PUBLIC_STORAGE_PREFIX ?? "";

type WalletStore = {
    certs: Array<Record<string, string>>
};

export const useWalletStore = create<WalletStore>()(
    persist(
        () => ({
            certs: [] as WalletStore["certs"],
        }),
        {
            name: STORAGE_KEY,
        }
    )
);
