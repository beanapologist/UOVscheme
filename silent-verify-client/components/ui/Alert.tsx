import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";
import { Button } from "@base-ui/react";

const alertVariants = cva(
    "relative grid w-full grid-cols-[0_1fr] items-start gap-y-0.5 rounded-lg border border-border px-4 py-3 has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] has-[>svg]:gap-x-5 [&>svg]:w-5 [&>svg]:h-1lh [&>svg]:translate-y-0.5 [&>svg]:text-current",
    {
        variants: {
            variant: {
                default: "bg-surface text-card-foreground",
                danger: "bg-surface text-destructive *:data-[slot=alert-description]:text-warning/90 [&>svg]:text-current",
                success: "",
                warning:
                    "bg-warning text-warning-foreground border-warning",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
);

function Alert({
    className,
    variant,
    ...props
}: React.ComponentProps<"div"> & VariantProps<typeof alertVariants>) {
    return (
        <div
            data-slot="alert"
            role="alert"
            className={cn(alertVariants({ variant }), className)}
            {...props}
        />
    );
}

function AlertClose({ className, ...props }: React.ComponentProps<"button">) {
    return (
        <Button data-slot="alert-close" className={cn("", className)} {...props} />
    );
}

function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
    return (
        <div
            data-slot="alert-title"
            className={cn(
                "col-start-2 line-clamp-1 min-h-4 font-medium tracking-tight",
                className
            )}
            {...props}
        />
    );
}

function AlertDescription({
    className,
    ...props
}: React.ComponentProps<"div">) {
    return (
        <div
            data-slot="alert-description"
            className={cn(
                "col-start-2 grid justify-items-start gap-1 text-muted-foreground [&_p]:leading-relaxed",
                className
            )}
            {...props}
        />
    );
}

export { Alert, AlertTitle, AlertClose, AlertDescription };
