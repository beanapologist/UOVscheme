"use client";

import { Container } from "@/components/layout";
import { Logo } from "@/components/ui/Logo";
import Link from "next/link";
// import { SiGithub } from "@icons-pack/react-simple-icons";
import { Button } from "@/components/ui/Button";
// import { Menu, X } from "lucide-react";
import { useState } from "react";

const links = [
    { name: "Verify", href: "/verify" },
    { name: "Try API", href: "/docs" },
    { name: "Reference", href: "/redoc" },
    { name: "Swagger", href: "/swagger" },
];

export default function Header() {
    const [open, setOpen] = useState(false);
    return (
        <header
            className="group/header h-(--header-height) sticky top-0 left-0 z-2000 shadow-[0_1px_0_0_var(--border)] bg-background"
            data-open={open ? "" : undefined}
        >
            <Container className="h-full flex items-center justify-between">
                <Logo />
                <Button
                    className="w-5 h-4 flex flex-col justify-between md:hidden"
                    size="icon"
                    variant="ghost"
                    onClick={() => setOpen(!open)}
                >
                    <span className="w-full h-0.5 bg-foreground group-data-open/header:rotate-0" />
                    <span className="w-full h-0.5 bg-foreground" />
                    <span className="w-full h-0.5 bg-foreground group-data-open/header:rotate-0" />
                </Button>
                <nav className="hidden md:flex">
                    <ul className="flex flex-row items-center gap-6">
                        {links.map(({ name, href }) => (
                            <li className="hover:text-primary" key={name}>
                                <Link href={href}>{name}</Link>
                            </li>
                        ))}
                    </ul>
                </nav>
                <nav className="w-full h-0 fixed bottom-0 left-0 -z-1000 origin-top-left bg-background group-data-open/header:h-[calc(100%-var(--header-height))] md:hidden">
                    <ul className="flex flex-col gap-4">
                        {links.map(({ name, href }) => (
                            <li key={name}>
                                <Link href={href}>{name}</Link>
                            </li>
                        ))}
                    </ul>
                </nav>
            </Container>
        </header>
    );
}
