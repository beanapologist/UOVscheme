import { Container } from "@/components/layout";
import { Logo } from "@/components/ui/Logo";

export default function Header() {
    return (
        <header className="h-(--header-height)">
            <Container className="h-full flex items-center">
                <Logo />
                <nav></nav>
            </Container>
        </header>
    );
}
