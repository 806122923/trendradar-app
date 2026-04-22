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

        // Same-origin proxy to Tally's submission endpoint.
        // Tally responds with `Access-Control-Allow-Origin: https://tally.so`,
        // which would block any direct browser POST from our domain. Routing
        // through our own /api/tally/* path means the browser sees a
        // same-origin request and never does a CORS preflight.
        //
        // Used by the landing page waitlist form → see `submitWaitlist()` in
        // apps/web/public/landing.html.
        { source: "/api/tally/:path*", destination: "https://api.tally.so/:path*" },
      ],
    };
  },
};

export default nextConfig;
