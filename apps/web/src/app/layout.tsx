import type { Metadata, Viewport } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// Match the orange landing page's typography. Latin subset is fine —
// Chinese glyphs fall back to PingFang SC / Microsoft YaHei via CSS.
const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-display",
  weight: ["400", "500", "600", "700"],
});
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
  weight: ["400", "500", "600"],
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
  weight: ["400", "500"],
});

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
    <html
      lang="zh-CN"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body className="bg-white text-black antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
