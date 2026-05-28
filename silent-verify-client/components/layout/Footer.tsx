import { Container } from "@/components/layout";

export default function Footer() {
    return (
        <footer className="py-6 border-t border-t-border">
            <Container className="flex flex-col items-center">
                SilentVerify · UOV prime-field reference
                <span>A product of COINjecture Network LLC</span>
            </Container>
        </footer>
    );
}
