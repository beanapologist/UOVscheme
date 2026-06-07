import { api } from "@/api/client";
import { Container } from "@/components/layout";
import { Badge } from "@/components/ui/Badge";

type Chains = Record<"chains", Array<{ id: string; label: string }>>;

const FALLBACK_CHAINS = [
    { id: "evm", label: "EVM" },
    { id: "solana", label: "Solana" },
    { id: "cosmos", label: "Cosmos" },
    { id: "xrpl", label: "XRPL" },
];

export default async function SupportedChains() {
    let chains = FALLBACK_CHAINS;

    try {
        const resp = await api.get("/chains");
        if (resp.ok) {
            const data = (await resp.json()) as Chains;
            chains = data.chains;
        }
    } catch {
        // API may be unavailable during static build — use fallback catalog
    }

    return (
        <section className="section">
            <Container className="flex flex-col gap-8">
                <h2>Supported chains</h2>
                <div className="flex flex-wrap items-center gap-2">
                    {chains.map((chain) => (
                        <Badge
                            className="rounded-lg"
                            key={chain.id}
                            variant="outline"
                            size="lg"
                        >
                            {chain.label}
                        </Badge>
                    ))}
                </div>
            </Container>
        </section>
    );
}
