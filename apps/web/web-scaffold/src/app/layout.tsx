import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TrendRadar · 爆品雷达",
  description: "AI product-research agent for TikTok Shop US sellers.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-white text-zinc-900 antialiased">{children}</body>
    </html>
  );
}
