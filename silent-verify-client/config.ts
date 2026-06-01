export const BASE =
    typeof window === "undefined"
        ? "http://localhost:3000" ?? ""
        : window.location.origin;
