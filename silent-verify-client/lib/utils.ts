import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// FUNCTIONS
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// CONSTANTS
