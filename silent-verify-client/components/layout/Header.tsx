"use client";

import { Container } from "@/components/layout";
import { Logo } from "@/components/ui/Logo";
import Link from "next/link";
import { SiGithub } from "@icons-pack/react-simple-icons";
import { Button } from "@/components/ui/Button";
import { Menu } from "lucide-react";
import { useState } from "react";

export default function Header() {
    const [open, setOpen] = useState(false);
    return (
        <header
            className="group/header h-(--header-height)"
            data-open={open ? "" : undefined}
        >
            <Container className="h-full flex items-center justify-between">
                <Logo />
                <div className="flex items-center">
                    <nav className="">
                        <ul className="hidden items-center gap-8 md:flex">
                            <li>
                                <Link href="/verify">Verify</Link>
                            </li>
                            <li>
                                <Link href="/docs">Try API</Link>
                            </li>
                            <li>
                                <Link href="/redoc">Reference</Link>
                            </li>
                            <li>
                                <Link href="/swagger">Swagger</Link>
                            </li>
                            <li>
                                <a
                                    href="https://github.com/beanapologist/UOVscheme"
                                    target="_blank"
                                    rel="noopener"
                                >
                                    {/* GitHub */}
                                    <SiGithub />
                                </a>
                            </li>
                        </ul>
                        {/* 
                        <div className="w-full h-full px-4 fixed top-0 left-0 z-1000 bg-background overflow-hidden transform transition-transform duration-300 ease-in-out translate-x-full group-data-open/header:translate-x-0 sm:px-6">
                            <div className="h-(--header-height) flex items-center justify-between">
                                <Logo />
                                <Button
                                    variant="outline"
                                    size="icon-lg"
                                    onClick={() => setOpen(false)}
                                >
                                    <X />
                                </Button>
                            </div>
                            <ul className="flex-1 flex flex-col gap-8 md:items-center">
                                <li>
                                    <Link href="/verify">Verify</Link>
                                </li>
                                <li>
                                    <Link href="/docs">Try API</Link>
                                </li>
                                <li>
                                    <Link href="/redoc">Reference</Link>
                                </li>
                                <li>
                                    <Link href="/swagger">Swagger</Link>
                                </li>
                                <li>
                                    <a
                                        href="https://github.com/beanapologist/UOVscheme"
                                        target="_blank"
                                        rel="noopener"
                                    >
                                        // GitHub
                                        <SiGithub />
                                    </a>
                                </li>
                            </ul>
                        </div>
                        */}
                    </nav>
                    <div className="flex md:hidden">
                        <Button
                            variant="outline"
                            size="icon"
                            onClick={() => setOpen(true)}
                        >
                            <Menu />
                        </Button>
                    </div>
                </div>
            </Container>
        </header>
    );
}
