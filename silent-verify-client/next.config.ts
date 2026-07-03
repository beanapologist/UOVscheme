import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    allowedDevOrigins: ["local-origin.dev", "*.local-origin.dev"],
    turbopack: {
        root: path.join(__dirname),
    },
};

export default nextConfig;
