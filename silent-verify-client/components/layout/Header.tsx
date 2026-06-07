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
                    className="md:hidden"
                    variant="outline"
                    onClick={() => setOpen(!open)}
                >
                    <span className="w-full h-px" />
                </Button>
                <nav className="hidden md:flex">
                    <ul className="flex flex-row items-center gap-5">
                        {links.map(({ name, href }) => (
                            <li key={name}>
                                <Link href={href}>{name}</Link>
                            </li>
                        ))}
                    </ul>
                </nav>
                <nav className="w-full h-full fixed top-(--header-height) left-0 z-1000 -translate-x-full bg-background md:hidden">

                    <ul className="flex flex-col">
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
