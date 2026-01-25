/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_URL 
          ? `${process.env.API_URL}/:path*` 
          : 'http://localhost:8000/:path*',
      },
    ];
  },
  env: {
    APP_NAME: 'xBasis',
    APP_URL: process.env.APP_URL || 'http://localhost:3000',
  },
};

module.exports = nextConfig;
