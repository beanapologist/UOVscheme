import { create } from "zustand";
import { persist } from "zustand/middleware";
import { certLabel } from "@/utils/functions";
import { Cert, Wire } from "@/types";

const STORAGE_KEY = "sv_cert_wallet";

type WalletStore = {
    certs: Cert[] | [];
    lastCert: Wire | null;
    saveCert: (wire: Wire, label?: string) => Cert;
    saveLastCert: (wire: Wire) => void;
    removeCert: (certId: Cert["id"]) => void;
};

export const useWalletStore = create<WalletStore>()(
    persist(
        (set) => ({
            certs: [],
            lastCert: null,
            saveCert: (wire, label) => {
                const id = `sv-${
                    crypto.randomUUID ? crypto.randomUUID() : Date.now()
                }`;
                const item = {
                    id,
                    label: label ?? certLabel(wire),
                    savedAt: new Date().toString(),
                    cert: wire,
                };
                set((state) => {
                    const existing = state.certs.find(
                        (c) =>
                            c.cert &&
                            c.cert.pubkey_fp === wire.pubkey_fp &&
                            JSON.stringify(c.cert.sigma) ===
                                JSON.stringify(wire.sigma)
                    );
                    const certList = existing
                        ? state.certs.map((cert) =>
                              cert.id === item.id
                                  ? { ...cert, ...item, id: cert.id }
                                  : item
                          )
                        : [item, ...state.certs];

                    return {
                        ...state,
                        certs: certList.slice(0, 50),
                    };
                });
                return item;
            },
            removeCert: (id) =>
                set((state) => ({
                    ...state,
                    certs: state.certs.filter((c) => c.id !== id),
                })),
            saveLastCert: (wire) => {
                set((state) => ({
                    ...state,
                    lastCert: wire,
                }));
            },
        }),
        {
            name: STORAGE_KEY,
        }
    )
);
