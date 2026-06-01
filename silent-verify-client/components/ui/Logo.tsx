import Link from "next/link";
import Image from "next/image";

export function Logo() {
    return (
        <Link className="inline-flex items-center gap-2" href="/">
            <div className="size-9 relative rounded-full overflow-hidden">
                <Image
                    src="/img/silentverify-logo.png"
                    alt="Silent Verify"
                    sizes=""
                    className="object-cover"
                    fill={true}
                />
            </div>
            <div>
                Silent<span>Verify</span>
            </div>
        </Link>
    );
}
