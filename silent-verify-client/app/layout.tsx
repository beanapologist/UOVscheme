import type { Metadata } from "next";
import { DM_Sans } from "next/font/google";
import "@/styles/globals.css";
import { Footer, Header } from "@/components/layout";
import { Toaster } from "sonner";
import { QueryProvider } from "@/providers";

const dmSans = DM_Sans({
    variable: "--font-dm",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "SilentVerify - Agent PKI & Chain State Certificates",
    description: "",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className={`${dmSans.variable} h-full antialiase`}>
            <body className="min-h-full flex flex-col">
                <QueryProvider>
                    <Header />
                    <main className="flex-1 flex flex-col">{children}</main>
                    <Footer />
                    <Toaster
                        theme="dark"
                        visibleToasts={1}
                        toastOptions={{
                            classNames: {
                                toast: "flex items-start!",
                                title: "p-0! m-0!",
                                description: "p-0! m-0!"
                            },
                        }}
                    />
                </QueryProvider>
            </body>
        </html>
    );
}
