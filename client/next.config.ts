import type { NextConfig } from "next";
import { parse } from "dotenv";
import path from "path";
import fs from "fs";

const envPath = path.join(__dirname, "../.env");
const env = parse(fs.readFileSync(envPath));

const nextConfig: NextConfig = {
  env,
};

export default nextConfig;
