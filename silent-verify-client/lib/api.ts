const BASE_URL = `${process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8765"}/api/v1`;

async function request(
    path: string,
    options?: RequestInit
): Promise<Response> {
    const url = path.startsWith("/api") ? path : `${BASE_URL}${path}`;
    return fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options?.headers || {}),
        },
    });
}

export const api = {
    get: (path: string, options?: RequestInit) =>
        request(path, {
            ...options,
            method: "GET",
        }),

    post: (path: string, options?: RequestInit) =>
        request(path, {
            ...options,
            method: "POST",
        }),

    put: (path: string, options?: RequestInit) =>
        request(path, {
            ...options,
            method: "PUT",
        }),
    delete: (path: string, options?: RequestInit) =>
        request(path, {
            ...options,
            method: "DELETE",
        }),
};
