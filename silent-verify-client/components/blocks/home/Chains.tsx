import { api } from "@/api/client";
import { Container } from "@/components/layout";
import { Badge } from "@/components/ui/Badge";

type Chains = Record<"chains", Array<{ id: string; label: string }>>;

export default async function SupportedChains() {
    const resp = await api.get("/chains");
    const data = (await resp.json()) as Chains;

    return (
        <section className="section">
            <Container className="flex flex-col gap-8">
                <h2>Supported chains</h2>
                <div className="flex flex-wrap items-center gap-2">
                    {data.chains.map((chain) => (
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
