import { useSearchParams } from "next/navigation";

type QueryResult<T extends string | string[]> = T extends string[]
    ? Record<T[number], string | null>
    : string | null;

export function useQueryParams<T extends string | string[]>(
    input: T
): QueryResult<T> {
    const searchParams = useSearchParams();

    if (Array.isArray(input)) {
        return input.reduce((acc, key) => {
            acc[key] = searchParams.get(key);
            return acc;
        }, {} as Record<string, string | null>) as QueryResult<T>;
    } else {
        return searchParams.get(input as string) as QueryResult<T>;
    }
}
