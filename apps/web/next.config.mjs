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
        // Clean URLs for /alternatives/* — no .html suffix needed
        { source: "/alternatives", destination: "/alternatives/index.html" },
        { source: "/alternatives/", destination: "/alternatives/index.html" },
        { source: "/alternatives/kalodata", destination: "/alternatives/kalodata.html" },
        { source: "/alternatives/didadog", destination: "/alternatives/didadog.html" },
        { source: "/alternatives/echotik", destination: "/alternatives/echotik.html" },
      ],
    };
  },
};

export default nextConfig;
