"use client";

import { useCopyToClipboard } from "@/hooks";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Button } from "@/components/ui/Button";
import { Clipboard, Copy } from "lucide-react";

export function CopyButton({
    value,
    className,
}: {
    value: string;
    className?: string;
}) {
    const { copy } = useCopyToClipboard();
    const copyNode = <div className="">Copied to clipboard</div>;

    return (
        <Button
            className={cn(className)}
            size="icon"
            variant="support"
            onClick={() =>
                copy(value, {
                    onSuccess: () => {
                        toast(copyNode);
                    },
                })
            }
        >
            <Clipboard />
            {/* <Copy /> */}
        </Button>
    );
}
