"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { redeemCheckoutSession } from "@/services/billingService";
import { useApiKeyStore } from "@/stores";
import { ApiKeyDialog } from "@/components/shared/dialog";
import { toMessage } from "@/utils/functions";

export function CheckoutReturn() {
    const searchParams = useSearchParams();
    const setApiKey = useApiKeyStore((state) => state.setApiKey);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        if (searchParams.get("checkout") !== "success") return;
        const sessionId = searchParams.get("session_id");
        if (!sessionId) return;

        let cancelled = false;

        const redeem = async () => {
            try {
                const key = await redeemCheckoutSession(sessionId);
                if (cancelled) return;
                setApiKey(key);
                setOpen(true);
                toast.success("Pro subscription active — save your API key.");
                window.history.replaceState({}, "", "/");
            } catch (error) {
                if (cancelled) return;
                toast.error(toMessage(error));
            }
        };

        void redeem();

        return () => {
            cancelled = true;
        };
    }, [searchParams, setApiKey]);

    return <ApiKeyDialog open={open} onOpenChange={setOpen} />;
}
