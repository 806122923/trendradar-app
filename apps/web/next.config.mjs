/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Serve the static designer-grade landing page at `/` before the App Router
  // picks up page.tsx. `beforeFiles` makes the rewrite win over framework pages
  // while still letting /_next/*, /chat, /og-image.png, etc. route normally.
  async rewrites() {
    return {
      beforeFiles: [
        { source: "/", destination: "/landing.html" },
      ],
    };
  },
};

export default nextConfig;
