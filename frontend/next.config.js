/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true,
  },
  // This disables Next.js analytics which helps reduce JavaScript bundle size
  experimental: {
    instrumentationHook: false,
  }
}

module.exports = nextConfig
