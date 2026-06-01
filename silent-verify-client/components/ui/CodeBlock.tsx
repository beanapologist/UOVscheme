"use client";

import { CopyButton } from "@/components/ui/CopyButton";

export function CodeBlock({ html, code }: { html: string; code: string }) {
    return (
        <div className="[--space:--spacing(4)] w-full h-full relative rounded-lg overflow-hidden">
            <CopyButton className="absolute top-2 right-2" value={code} />
            <div
                className="h-full [&>*]:w-full [&>*]:h-fit [&>*]:p-(--space) [&>*]:overflow-x-auto"
                dangerouslySetInnerHTML={{ __html: html }}
            />
        </div>
    );
}
