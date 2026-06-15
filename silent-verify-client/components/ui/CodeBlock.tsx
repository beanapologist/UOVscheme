"use client";

import { CopyButton } from "@/components/ui/CopyButton";
import { cn } from "@/lib/utils";
import React from "react";

function CodeBlock({
    className,
    ...props
}: React.ComponentProps<"div">) {
    return <div className={cn("[--px:--spacing(4)] flex flex-col", className)} {...props} />;
}

function CodeBlockHeader({ className, ...props }: React.ComponentProps<"div">) {
    return (
        <div
            className={cn("px-(--px) py-4 flex items-center justify-between", className)}
            {...props}
        />
    );
}

function CodeBlockTitle({ className, ...props }: React.ComponentProps<"div">) {
    return <div className={cn(className)} {...props} />;
}

function CodeBlockCopybar({
    className,
    ...props
}: React.ComponentProps<typeof CopyButton>) {
    return <CopyButton className={cn(className)} {...props} />;
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
    html: string;
}) {
    return (
        <div
            className={cn("relative rounded-lg overflow-x-auto", className)}
            {...props}
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
}

export {
    CodeBlock,
    CodeBlockHeader,
    CodeBlockTitle,
    CodeBlockCopybar,
    CodeBlockToolbar,
    CodeBlockContent,
};
