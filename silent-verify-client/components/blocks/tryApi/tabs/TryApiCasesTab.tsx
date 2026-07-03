"use client";

import { useApiKeyStore } from "@/stores";
import { LinkButton } from "@/components/ui/LinkButton";
import { CodeBlock, CodeBlockContent } from "@/components/ui/CodeBlock";
import { Button } from "@/components/ui/Button";
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/Collapsible";
import { USE_PROCESS } from "../tryApi.constants";
import { ChevronRight } from "lucide-react";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/Card";
import type { CodeBlock as TCodeBlock, CodeError as TCodeError } from "@/types";
import { getApiUsage } from "@/services/billingService";
import { toMessage } from "@/utils/functions";
import type { HandleAction } from "./types";
import { getApiBlock } from "@/services/api";

export default function TryApiCasesTab({
    codeBlocks,
    codeErrors,
    handleAction,
    updateHtml,
}: {
    codeBlocks: TCodeBlock[];
    codeErrors: TCodeError[];
    handleAction: (t: HandleAction) => void;
    updateHtml: (c: string | null) => void;
}) {
    const apiKey = useApiKeyStore((state) => state.apiKey);

    const handleQuotas = async (apiKey: string) => {
        try {
            const data = await getApiUsage(apiKey);
            const html = await getApiBlock({ code: data });
            console.log(html)
            updateHtml(html.html);
            // show in code block
        } catch (error) {
            const err = toMessage(error);
            console.error(err);
            // show in code block
        }
    };
    return (
        <>
            <div className="flex flex-col gap-6">
                <div className="flex flex-col gap-3 p-8 rounded-xl bg-surface">
                    <h3>Quickstart (curl)</h3>
                    <p>
                        Set BASE to this host and SV_API_KEY from your key above
                        (or get one at&nbsp;
                        <LinkButton href="/">Home</LinkButton>
                        ).
                    </p>
                    <ol className="flex flex-col gap-4">
                        {codeBlocks.map(({ title, block }) => (
                            <li className="flex flex-col gap-2" key={title}>
                                <h4>{title}</h4>
                                <CodeBlock>
                                    <CodeBlockContent html={block.html} />
                                </CodeBlock>
                            </li>
                        ))}
                    </ol>
                    <Button
                        className="w-fit"
                        variant="outline"
                        onClick={() => handleQuotas(apiKey)}
                    >
                        Show my usage in result
                    </Button>
                </div>
                <Collapsible className="flex flex-col items-start gap-4">
                    <CollapsibleTrigger className="group/trigger flex flex-row items-center gap-px text-left">
                        <span className="transition-rotate duration-150 ease-in-out group-data-[panel-open]/trigger:rotate-90">
                            <ChevronRight size={20} />
                        </span>
                        Common errors
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                        {codeErrors.map(({ title, error }) => (
                            <div key={title}>
                                {title} <span>- {error}</span>
                            </div>
                        ))}
                    </CollapsibleContent>
                </Collapsible>
            </div>
            <div className="flex flex-col gap-6">
                <p>
                    Pick a real-world flow — we pre-fill the right tab and you
                    run one click at a time.
                </p>
                <div className="grid grid-cols-1 items-stretch gap-8 md:grid-cols-3">
                    {USE_PROCESS.map((flow) => (
                        <Card key={flow.title}>
                            <CardHeader>
                                <CardTitle>{flow.title}</CardTitle>
                                <CardDescription>
                                    {flow.description}
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ol className="list-decimal list-inside">
                                    {flow.steps.map((step, i) => (
                                        <li key={i}>{step}</li>
                                    ))}
                                </ol>
                            </CardContent>
                            <CardFooter>
                                <Button
                                    variant={flow.action.variant}
                                    onClick={() =>
                                        handleAction(flow.action.type)
                                    }
                                >
                                    {flow.action.label}
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            </div>
        </>
    );
}
