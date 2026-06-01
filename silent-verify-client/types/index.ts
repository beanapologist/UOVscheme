export type CodeBlock = {
    title: string;
    block: {
        html: string;
        code: string;
    };
};

export type CodeError = {
    title: string;
    error: string;
};
