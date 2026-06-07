import { useSearchParams } from "next/navigation";

export function useQueryParams(input: string): string | null;
export function useQueryParams<T extends string[]>(
    input: [...T]
): Record<T[number], string | null>;
export function useQueryParams<T extends Record<string, string>>(
    input: T
): Record<keyof T, string>;

export function useQueryParams<T extends string[] | Record<string, string>>(
    input: string | T
): string | null | Record<string, string | null> {
    const searchParams = useSearchParams();

    if (typeof input === "string") {
        return searchParams.get(input);
    }

    if (Array.isArray(input)) {
        return input.reduce((acc, key) => {
            acc[key] = searchParams.get(key);
            return acc;
        }, {} as Record<string, string | null>);
    }

    return Object.keys(input).reduce((acc, key) => {
        acc[key] =
            searchParams.get(key) ?? (input as Record<string, string>)[key];
        return acc;
    }, {} as Record<string, string>);
}
