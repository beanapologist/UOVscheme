import dynamic from "next/dynamic";

const Swagger = dynamic(() => import("@/components/blocks/apiRef/ApiRef"), {
    // ssr: false,
    loading: () => <p>Loading API Swagger...</p>,
});

const specUrl = process.env.NEXT_PUBLIC_OPENAPI_URL!;

export default function Page() {
    return <Swagger url={specUrl} />;
}
