import { Suspense } from "react";
import { Verify } from "@/components/blocks/verify/verify";

export default function Page() {
    return (
        <Suspense fallback={null}>
            <Verify />
        </Suspense>
    );
}
