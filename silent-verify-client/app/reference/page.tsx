import dynamic from "next/dynamic";

const Redoc = dynamic(() => import("@/components/blocks/apiDoc/ApiDoc"), {
    // ssr: false,
    loading: () => <p>Loading API Documentation...</p>,
});

const specUrl = process.env.NEXT_PUBLIC_OPENAPI_URL!;

export default function Page() {
    return <Redoc specUrl={specUrl} />;
}
