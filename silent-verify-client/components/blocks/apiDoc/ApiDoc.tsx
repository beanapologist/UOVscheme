"use client";

import { RedocStandalone } from "redoc";

/*
const REDOC_OPTIONS = {
    scrollYOffset: "",
    theme: {
        colors: {
            primary: { main: "" },
            success: { main: "" },
            text: { primary: "", secondary: "" },
            http: { get: "", post: "", put: "", delete: "" },
        },
        typography: {
            fontFamily: "",
            code: { fontFamily: "" },
            headings: { fontFamily: "" },
        },
        sidebar: { backgroundColor: "", textColor: "", activeTextColor: "" },
        rightPanel: { backgroundColor: "" },
    },
};
*/

const REDOC_OPTIONS = {
    scrollYOffset: 60,
    theme: {
        colors: {
            primary: {
                main: "#0ea5e9",
            },
            success: {
                main: "#22c55e",
            },
            text: {
                primary: "#e2e8f0",
                secondary: "#94a3b8",
            },
            http: {
                get: "#0ea5e9",
                post: "#22c55e",
                put: "#f59e0b",
                delete: "#ef4444",
            },
        },

        typography: {
            fontFamily:
                "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            headings: {
                fontFamily:
                    "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
                color: "#e2e8f0",
            },
            code: {
                fontFamily:
                    "JetBrains Mono, Menlo, Monaco, Consolas, monospace",
            },
        },

        sidebar: {
            backgroundColor: "#0b1220",
            textColor: "#cbd5e1",
            activeTextColor: "#0ea5e9",
        },

        rightPanel: {
            backgroundColor: "#0f172a",
        },

        components: {
            ApiInfo: {
                backgroundColor: "#0f172a",
            },
            ApiContent: {
                backgroundColor: "#0f172a",
            },
            Operation: {
                backgroundColor: "#0b1220",
            },
            responses: {
                backgroundColor: "#0b1220",
            },
            schema: {
                backgroundColor: "#0b1220",
            },
        },
    },
};

export default function APIDocumentation({ specUrl }: { specUrl: string }) {
    return <RedocStandalone specUrl={specUrl} options={REDOC_OPTIONS} />;
}
