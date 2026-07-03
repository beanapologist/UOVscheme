export const BASE =
    typeof window === "undefined"
        ? (process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000")
        : window.location.origin;
