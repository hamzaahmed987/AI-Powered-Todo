/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  typescript: {
    // Allows production builds to complete even with type errors
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;