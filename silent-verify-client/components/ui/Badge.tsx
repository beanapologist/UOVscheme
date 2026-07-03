import { cn } from "@/lib/utils";
import { VariantProps, cva } from "class-variance-authority";

const badgeVariants = cva(
    "group/badge inline-flex w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-4xl border border-transparent px-2 py-0.5 text-sm font-medium whitespace-nowrap transition-all focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 aria-invalid:border-error aria-invalid:ring-error/20 [&>svg]:pointer-events-none [&>svg]:size-3!",
    {
        variants: {
            variant: {
                default:
                    "bg-primary text-primary-foreground [a]:hover:bg-primary/80",
                support:
                    "bg-support text-support-foreground [a]:hover:bg-support/80",
                error: "bg-error/10 text-error focus-visible:ring-error/20 [a]:hover:bg-error/20",
                outline:
                    "bg-surface border-border text-foreground [a]:hover:bg-muted [a]:hover:text-muted-foreground",
                ghost: "hover:bg-muted hover:text-muted-foreground",
                link: "text-primary underline-offset-4 hover:underline",
            },
            size: {
                default: "h-8 px-2.5",
                sm: "h-6 px-3",
                lg: "h-9 px-3.5",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
);

export function Badge({
    children,
    className,
    variant = "default",
    size = "default",
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
    return (
        <span className={cn(badgeVariants({ variant, size }), className)}>
            {children}
        </span>
    );
}
