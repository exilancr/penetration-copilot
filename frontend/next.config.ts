import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    apiUrl: `${process.env.NEXT_PUBLIC_API_URL}`,
  }
};

export default nextConfig;
