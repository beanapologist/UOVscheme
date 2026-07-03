"use client";

import * as React from "react";

export function ScrollableTabs({ children }: { children: React.ReactNode }) {
    const ref = React.useRef<HTMLDivElement>(null);

    const [showLeftFade, setShowLeftFade] = React.useState(false);
    const [showRightFade, setShowRightFade] = React.useState(false);

    const updateFades = React.useCallback(() => {
        const el = ref.current;
        if (!el) return;

        const { scrollLeft, scrollWidth, clientWidth } = el;

        setShowLeftFade(scrollLeft > 0);

        setShowRightFade(scrollLeft + clientWidth < scrollWidth - 1);
    }, []);

    React.useEffect(() => {
        updateFades();

        const el = ref.current;
        if (!el) return;

        el.addEventListener("scroll", updateFades);
        window.addEventListener("resize", updateFades);

        return () => {
            el.removeEventListener("scroll", updateFades);
            window.removeEventListener("resize", updateFades);
        };
    }, [updateFades]);

    return (
        <div className="relative">
            {showLeftFade && (
                <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-6 bg-gradient-to-r from-background to-transparent" />
            )}

            {showRightFade && (
                <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-6 bg-gradient-to-l from-background to-transparent" />
            )}

            <div
                ref={ref}
                className="overflow-x-auto py-px scrollbar-hide [-webkit-overflow-scrolling:touch]"
            >
                {children}
            </div>
        </div>
    );
}
