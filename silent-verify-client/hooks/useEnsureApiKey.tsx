import { useMutation } from "@tanstack/react-query";
import { useApiKeyStore } from "@/stores";
// import { useShallow } from "zustand/react/shallow";
import { validateKey, fetchNewKey } from "@/services/apiKeyService";

export const useEnsureApiKey = () => {
    const { apiKey, setApiKey, clearApiKey } = useApiKeyStore();

    return useMutation({
        mutationFn: async () => {
            if (apiKey) {
                const isValid = await validateKey(apiKey);
                if (isValid) return apiKey;
                clearApiKey();
            }
            const newApiKey = await fetchNewKey();
            setApiKey(newApiKey);
            return newApiKey;
        },
    });
};
