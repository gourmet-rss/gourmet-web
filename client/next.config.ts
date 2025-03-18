import type { NextConfig } from "next";
import { parse } from "dotenv";
import path from "path";
import fs from "fs";

const nextConfig: NextConfig = {};

if (process.env.NODE_ENV === "development") {
  const devEnvPath = path.join(__dirname, "../.env");
  if (!fs.existsSync(devEnvPath)) {
    throw new Error("Development environment variables not found");
  }

  nextConfig.env = parse(fs.readFileSync(devEnvPath, "utf-8"));
  nextConfig.images = {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
        port: "",
        pathname: "**",
      },
    ],
  };
}

export default nextConfig;
