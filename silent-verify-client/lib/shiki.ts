import { codeToHtml } from "shiki";

export async function highlight(code: string, lang: string) {
    return codeToHtml(code, {
        lang,
        theme: "github-dark",
    });
}
