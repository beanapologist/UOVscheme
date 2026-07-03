"use client";

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogFooter,
    DialogTitle,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { useCopyToClipboard } from "@/hooks";
import { useApiKeyStore } from "@/stores";

export function ApiKeyDialog({
    open,
    onOpenChange,
}: // apiKey
{
    open: boolean;
    onOpenChange: (open: boolean) => void;
    // apiKey: string;
}) {
    const apiKey = useApiKeyStore((state) => state.apiKey);
    const { copy } = useCopyToClipboard(true);

    if (!apiKey) return;
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Your API key</DialogTitle>
                    <DialogDescription>
                        Keep this API key secure. Anyone with access to it can
                        make requests on your behalf.
                        {/* Copy and store this API key securely. Do not share it publicly. */}
                    </DialogDescription>
                </DialogHeader>
                <div className="p-3 rounded-lg border border-border bg-background text-foreground">
                    <span>{apiKey}</span>
                </div>
                <DialogFooter>
                    <Button
                        className=""
                        variant="default"
                        onClick={() => copy(apiKey)}
                    >
                        Copy to Clipboard
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                    >
                        Close
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
