/** @type {import('next').NextConfig} */
const backendUrl =
  process.env.API_PROXY_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl.replace(/\/$/, "")}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${backendUrl.replace(/\/$/, "")}/health`,
      },
    ];
  },
};

module.exports = nextConfig;
