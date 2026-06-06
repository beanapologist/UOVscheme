"use client";

import { useState, useRef, useCallback } from "react";
import { toast } from "sonner";

type TimeoutRef = ReturnType<typeof setTimeout> | null;
type MessageType = "success" | "failure";
type CopyOptions = {
    onSuccess?: () => void;
    onFailure?: (err: unknown) => void;
};

const ToastMessage = ({
    type,
    message,
}: {
    type: MessageType;
    message: string;
}) => {
    return (
        <div
            className="w-fit px-5 py-3 bg-popover text-popover-foreground text-sm rounded-full"
            role="status"
            aria-live="polite"
            aria-atomic="true"
            data-type={type}
        >
            {message}
        </div>
    );
};

const notifyCopied = ({
    type = "success",
    message,
}: {
    type?: MessageType;
    message: string;
}) => {
    const options: Parameters<typeof toast>[1] = {
        unstyled: true,
        position: "bottom-center",
        className: "flex items-center justify-center",
    };
    return toast(<ToastMessage type={type} message={message} />, options);
};

export function useCopyToClipboard(notify = false, timeout = 1500) {
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
                if (notify) {
                    notifyCopied({ message: "Copied to clipboard" });
                }
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
