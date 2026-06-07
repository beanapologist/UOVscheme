import "server-only";
import { z } from "zod";
import { createHighlighter, type Highlighter } from "shiki";

const THEMES = ["github-dark", "github-light"] as const;
const LANGS = ["json", "bash", "typescript", "javascript"] as const;

const HighlightSchema = z.object({
    code: z.string(),
    lang: z.enum([...LANGS]),
    theme: z.enum([...THEMES]),
});

type HighlightInput = z.infer<typeof HighlightSchema>;

const g = globalThis as typeof globalThis & {
    __shikiHighlighter?: Promise<Highlighter>;
};

function getHighlighter() {
    g.__shikiHighlighter ??= createHighlighter({
        themes: [...THEMES],
        langs: [...LANGS],
    });
    return g.__shikiHighlighter;
}

export async function highlight(input: HighlightInput) {
    const { code, lang, theme } = HighlightSchema.parse(input);
    const h = await getHighlighter();
    return h.codeToHtml(code, { lang, theme });
}
