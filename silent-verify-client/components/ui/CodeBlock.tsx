"use client";

import { CopyButton } from "@/components/ui/CopyButton";
import { cn } from "@/lib/utils";
import React from "react";

function CodeBlock({ html, code }: { html: string; code: string }) {
    return (
        <div className="[--space:--spacing(4)] w-full h-full relative rounded-lg overflow-hidden">
            <CopyButton
                className="absolute top-2 right-2 bg-transparent!"
                value={code}
            />
            <div
                className="h-full [&>*]:w-full [&>*]:h-fit [&>*]:p-(--space) [&>*]:overflow-x-auto"
                dangerouslySetInnerHTML={{ __html: html }}
            />
        </div>
    );
}

function CodeBlockHeader({ className, ...props }: React.ComponentProps<"div">) {
    return (
        <div
            className={cn("flex items-center justify-between", className)}
            {...props}
        />
    );
}

function CodeBlockTitle({ className, ...props }: React.ComponentProps<"div">) {
    return <div className={cn("", className)} {...props} />;
}

function CodeBlockToolbar({
    className,
    ...props
}: React.ComponentProps<"div">) {
    return (
        <div className={cn("flex items-center gap-1", className)} {...props} />
    );
}

function CodeBlockContent({
    className,
    ...props
}: React.ComponentProps<"div">) {
    return (
        <div className={cn("relative overflow-x-auto", className)} {...props} />
    );
}

export {
    CodeBlock,
    CodeBlockHeader,
    CodeBlockTitle,
    CodeBlockToolbar,
    CodeBlockContent,
};
