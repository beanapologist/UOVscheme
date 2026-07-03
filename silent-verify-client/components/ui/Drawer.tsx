"use client";

import * as React from "react";
import { Drawer as DrawerPrimitive } from "@base-ui/react/drawer";

import { cn } from "@/lib/utils";

function Drawer({
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Root>) {
    return <DrawerPrimitive.Root data-slot="drawer" {...props} />;
}

function DrawerTrigger({
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Trigger>) {
    return <DrawerPrimitive.Trigger data-slot="drawer-trigger" {...props} />;
}

function DrawerPortal({
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Portal>) {
    return <DrawerPrimitive.Portal data-slot="drawer-portal" {...props} />;
}

function DrawerClose({
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Close>) {
    return <DrawerPrimitive.Close data-slot="drawer-close" {...props} />;
}

function DrawerPopup({
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Popup>) {
    return <DrawerPrimitive.Popup data-slot="drawer-popup" {...props} />;
}

function DrawerBackdrop({
    className,
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Backdrop>) {
    return (
        <DrawerPrimitive.Backdrop
            data-slot="drawer-overlay"
            className={cn(
                "fixed inset-0 z-50 bg-black/10 supports-backdrop-filter:backdrop-blur-xs data-open:animate-in data-open:fade-in-0 data-closed:animate-out data-closed:fade-out-0",
                className
            )}
            {...props}
        />
    );
}

function DrawerViewport({
    className,
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Viewport>) {
    return (
        <DrawerPrimitive.Viewport
            data-slot="drawer-viewport"
            className={cn(className)}
            {...props}
        />
    );
}

function DrawerContent({
    className,
    children,
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Content>) {
    return (
        <DrawerPortal data-slot="drawer-portal">
            <DrawerBackdrop />
            <DrawerViewport>
                <DrawerPopup
                    className={cn(
                        className,
                        "group/drawer-content fixed z-50 overflow-hidden flex h-auto flex-col bg-popover text-popover-foreground border-transparent data-[swipe-direction=down]:inset-x-0 data-[swipe-direction=down]:bottom-0 data-[swipe-direction=down]:mt-24 data-[swipe-direction=down]:max-h-[80vh] data-[swipe-direction=down]:rounded-t-xl data-[swipe-direction=down]:border-t data-[swipe-direction=left]:inset-y-0 data-[swipe-direction=left]:left-0 data-[swipe-direction=left]:w-3/4 data-[swipe-direction=left]:rounded-r-xl data-[swipe-direction=left]:border-r data-[swipe-direction=right]:inset-y-0 data-[swipe-direction=right]:right-0 data-[swipe-direction=right]:w-3/4 data-[swipe-direction=right]:rounded-l-xl data-[swipe-direction=right]:border-l data-[swipe-direction=up]:inset-x-0 data-[swipe-direction=up]:top-0 data-[swipe-direction=up]:mb-24 data-[swipe-direction=up]:max-h-[80vh] data-[swipe-direction=up]:rounded-b-xl data-[swipe-direction=up]:border-b data-[swipe-direction=left]:sm:max-w-sm data-[swipe-direction=right]:sm:max-w-sm"
                    )}
                >
                    <DrawerPrimitive.Content
                        data-slot="drawer-content"
                        // className={cn(className)}
                        {...props}
                    >
                        {children}
                    </DrawerPrimitive.Content>
                </DrawerPopup>
            </DrawerViewport>
        </DrawerPortal>
    );
}

function DrawerHeader({ className, ...props }: React.ComponentProps<"div">) {
    return (
        <div
            data-slot="drawer-header"
            className={cn(
                "flex flex-col gap-0.5 p-4 group-data-[swipe-direction=down]/drawer-content:text-center group-data-[swipe-direction=up]/drawer-content:text-center md:gap-0.5 md:text-left",
                className
            )}
            {...props}
        />
    );
}

function DrawerFooter({ className, ...props }: React.ComponentProps<"div">) {
    return (
        <div
            data-slot="drawer-footer"
            className={cn("mt-auto flex flex-col gap-2 p-4", className)}
            {...props}
        />
    );
}

function DrawerTitle({
    className,
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Title>) {
    return (
        <DrawerPrimitive.Title
            data-slot="drawer-title"
            className={cn(
                "cn-font-heading text-base font-medium text-foreground",
                className
            )}
            {...props}
        />
    );
}

function DrawerDescription({
    className,
    ...props
}: React.ComponentProps<typeof DrawerPrimitive.Description>) {
    return (
        <DrawerPrimitive.Description
            data-slot="drawer-description"
            className={cn("text-sm text-muted-foreground", className)}
            {...props}
        />
    );
}

export {
    Drawer,
    DrawerPortal,
    DrawerBackdrop,
    DrawerTrigger,
    DrawerClose,
    DrawerContent,
    DrawerHeader,
    DrawerFooter,
    DrawerTitle,
    DrawerDescription,
};
