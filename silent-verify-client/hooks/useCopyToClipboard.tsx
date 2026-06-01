"use client";

import { useState, useRef, useCallback } from "react";

type TimeoutRef = ReturnType<typeof setTimeout> | null;
type CopyOptions = {
    onSuccess?: () => void;
    onFailure?: (err: unknown) => void;
};

export function useCopyToClipboard(timeout = 1500) {
    const [copied, setCopied] = useState(false);
    const blockedRef = useRef(false);
    const timeoutRef = useRef<TimeoutRef>(null);

    const copy = useCallback(
        async (text: string, options?: CopyOptions) => {
            if (blockedRef.current) return;
            blockedRef.current = true;

            try {
                await navigator.clipboard.writeText(text);

                setCopied(true);
                options?.onSuccess?.();

                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }

                timeoutRef.current = setTimeout(() => {
                    blockedRef.current = false;
                    setCopied(false);
                }, timeout);
            } catch (err) {
                blockedRef.current = false;
                setCopied(false);
                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }
                options?.onFailure?.(err);
            }
        },
        [timeout]
    );

    return { copied, copy };
}
