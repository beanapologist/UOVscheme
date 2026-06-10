"use client";

import { CopyButton } from "@/components/ui/CopyButton";
import { cn } from "@/lib/utils";
import React from "react";

type CodeBlockContentProps =
    | { children: string }
    | { children: React.ReactNode; renderHtml?: boolean };

function CodeBlock({
    className,
    code,
    ...props
}: React.ComponentProps<"div"> & {
    code?: string;
}) {
    return <div className={cn("flex flex-col", className)} {...props} />;
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
        <div className={cn("flex items-center gap-px", className)} {...props} />
    );
}

function CodeBlockContent({
    className,
    html,
    ...props
}: React.ComponentProps<"div"> & {
    html: string
}) {
    return (
        <div
            className={cn("relative overflow-x-auto", className)}
            {...props}
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
}

export {
    CodeBlock,
    CodeBlockHeader,
    CodeBlockTitle,
    CodeBlockToolbar,
    CodeBlockContent,
};
