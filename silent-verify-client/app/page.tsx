import { Suspense } from "react";
import { Hero, Flow, Why, Plans, SupportedChains } from "@/components/blocks/home";
import { CheckoutReturn } from "@/components/blocks/home/CheckoutReturn";

export default function Page() {
    return (
        <>
            <Suspense fallback={null}>
                <CheckoutReturn />
            </Suspense>
            <Hero />
            <Flow />
            <Why />
            <Plans />
            <SupportedChains />
        </>
    );
}
