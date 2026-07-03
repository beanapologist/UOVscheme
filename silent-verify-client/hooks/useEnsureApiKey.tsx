import { useMutation } from "@tanstack/react-query";
import { useApiKeyStore } from "@/stores";
// import { useShallow } from "zustand/react/shallow";
import { verifyApiKey, fetchFreeKey } from "@/services/billingService";

export const useEnsureApiKey = () => {
    const { apiKey, setApiKey, clearApiKey } = useApiKeyStore();

    return useMutation({
        mutationFn: async () => {
            if (apiKey) {
                const result = await verifyApiKey(apiKey);
                if (result.valid) return apiKey;
                clearApiKey();
            }
            const newApiKey = await fetchFreeKey();
            setApiKey(newApiKey);
            return newApiKey;
        },
    });
};
