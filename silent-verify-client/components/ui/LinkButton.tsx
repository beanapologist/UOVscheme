import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

export function LinkButton({
    href,
    children,
    className,
    external = false,
}: {
    href: string;
    children: React.ReactNode;
    className?: string;
    external?: boolean;
}) {
    return (
        <Button
            className={cn("p-0 m-0", className)}
            variant="link"
            nativeButton={false}
            render={
                external ? (
                    <a href={href} target="_blank" rel="noreferrer noopener">
                        {children}
                    </a>
                ) : (
                    <Link href={href}>{children}</Link>
                )
            }
        />
    );
}
