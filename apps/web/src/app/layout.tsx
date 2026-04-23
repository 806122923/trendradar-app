import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";

// Plausible Analytics — privacy-friendly, no cookies.
// Also injected into the static landing + alternatives HTML pages so every
// route reports to the same `data-domain`.
const PLAUSIBLE_DOMAIN = "trendradar-app-sigma.vercel.app";

// Typography: Space Grotesk / Inter / JetBrains Mono are self-hosted from
// /public/fonts/ (copied from @fontsource/* at build time — see
// scripts/copy-fonts.mjs). The actual @font-face declarations live in
// /public/fonts/fonts.css, loaded via a <link> in the <head> below so the
// same file is shared between the static landing + alternatives HTML pages
// and the Next.js-rendered app.
//
// Rationale for not using next/font/google: fonts.gstatic.com is blocked/slow
// in mainland China, where our TikTok Shop seller audience lives. Self-hosting
// through Vercel's edge CDN (HK/Tokyo PoPs) is 3-5x faster for CN visitors
// and keeps React + static pages on exactly the same font files.

// NOTE: `/` is served from the static `public/landing.html` via a
// `beforeFiles` rewrite in `next.config.mjs`. That file has its own full
// `<head>` with Open Graph, Twitter, and canonical tags — so this metadata
// only applies to App Router pages like `/chat`.
export const metadata: Metadata = {
  title: "TrendRadar · AI 选品 Agent for TikTok Shop",
  description:
    "面向 TikTok Shop 美区卖家的 AI 选品 Agent。对话式选品、竞品痛点、利润测算、1688 反搜。中文原生，比 Kalodata 便宜三分之二。",
  keywords: [
    "TikTok Shop",
    "AI 选品",
    "跨境电商",
    "爆品",
    "Kalodata",
    "FastMoss",
    "1688",
  ],
  authors: [{ name: "TrendRadar" }],
  openGraph: {
    title: "TrendRadar · AI 选品 Agent for TikTok Shop",
    description:
      "面向 TikTok Shop 美区卖家的 AI 选品 Agent。一句话输入，返回推荐、痛点、利润、货源。比 Kalodata 便宜三分之二。",
    url: "https://trendradar-app-sigma.vercel.app/",
    siteName: "TrendRadar",
    locale: "zh_CN",
    type: "website",
    images: [
      {
        url: "https://trendradar-app-sigma.vercel.app/og-image.png",
        width: 1200,
        height: 630,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "TrendRadar · AI Product Research Agent for TikTok Shop",
    description:
      "AI product research agent for TikTok Shop US sellers. One prompt, get picks + competitor pain + margin + 1688 sourcing.",
    images: ["https://trendradar-app-sigma.vercel.app/og-image.png"],
  },
};

export const viewport: Viewport = {
  themeColor: "#000000",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <head>
        {/* Self-hosted fonts — see /public/fonts/fonts.css.
            Preload the two weights used above the fold so the paint is crisp
            on first load (hero headline + body copy). */}
        <link
          rel="preload"
          href="/fonts/space-grotesk-latin-600-normal.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href="/fonts/inter-latin-400-normal.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link rel="stylesheet" href="/fonts/fonts.css" />
      </head>
      <body className="bg-white text-black antialiased font-sans">
        {children}
        {/* Plausible pageviews + outbound links + file downloads.
            `afterInteractive` so it runs after hydration without blocking first paint. */}
        <Script
          defer
          data-domain={PLAUSIBLE_DOMAIN}
          src="https://plausible.io/js/script.outbound-links.file-downloads.js"
          strategy="afterInteractive"
        />
        <Script id="plausible-queue" strategy="afterInteractive">
          {`window.plausible = window.plausible || function() { (window.plausible.q = window.plausible.q || []).push(arguments); };`}
        </Script>
      </body>
    </html>
  );
}
