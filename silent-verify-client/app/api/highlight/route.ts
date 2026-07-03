import { highlight } from "@/lib/shiki";
import { stringify } from "@/utils/functions";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
    try {
        const body = await request.json();
        if (!body.code) {
            return NextResponse.json(
                { error: "Code is required" },
                { status: 400 }
            );
        }
        const code = body.code === "string" ? body.code : stringify(body.code);

        // Generate HTML on the server
        const html = await highlight(code, "json");

        return NextResponse.json({ html });
    } catch (error) {
        console.error(error);
        return NextResponse.json(
            { error: "Failed to highlight code" },
            { status: 500 }
        );
    }
}
