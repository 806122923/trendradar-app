/**
 * copy-fonts.mjs — also copies Chart.js (despite the name)
 *
 * Stage 1: Fontsource WOFF2 files → public/fonts/
 * Stage 2: Chart.js UMD build     → public/vendor/
 *
 * Why this exists:
 *   - apps/web/src/app/**  is a Next.js app. next/font/google *could* serve fonts,
 *     but next/font bundles are only available to Webpack-processed pages — they
 *     are not referenceable by plain static HTML in /public.
 *   - landing.html is intentionally a static, designer-owned file and should
 *     NOT be migrated to JSX. So we mirror the assets into /public/
 *     where both the static HTML and Next pages can agree on the same URLs.
 *   - CN egress: fonts.gstatic.com / unpkg / jsdelivr are slow/blocked for our
 *     target audience (mainland TikTok Shop sellers without VPN). Self-hosting
 *     through Vercel's edge network is 3-5× faster.
 *
 * Runs automatically via `npm run dev` and `npm run build` (see package.json).
 */

import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "..");
const nodeModules = join(root, "node_modules");

/* ------------------------------------------------------------------ *
 * Stage 1 — Fonts (WOFF2 only, `latin` subset, `normal` style).
 * ------------------------------------------------------------------ */
const fontOut = join(root, "public", "fonts");
const fontFamilies = [
  { pkg: "space-grotesk", weights: ["400", "500", "600", "700"] },
  { pkg: "inter", weights: ["400", "500", "600"] },
  { pkg: "jetbrains-mono", weights: ["400", "500"] },
];

const fontsourceRoot = join(nodeModules, "@fontsource");
if (!existsSync(fontsourceRoot)) {
  console.error("[copy-fonts] node_modules/@fontsource not found. Run `npm install` first.");
  process.exit(1);
}

// Purge stale WOFF2 files so we don't leave behind files for weights we no longer ship.
if (existsSync(fontOut)) {
  for (const entry of readdirSync(fontOut)) {
    if (entry.endsWith(".woff2")) rmSync(join(fontOut, entry));
  }
} else {
  mkdirSync(fontOut, { recursive: true });
}

let fontCount = 0;
for (const { pkg, weights } of fontFamilies) {
  const srcFiles = join(fontsourceRoot, pkg, "files");
  if (!existsSync(srcFiles)) {
    console.error(`[copy-fonts] missing package: @fontsource/${pkg} (did npm install fail?)`);
    process.exit(1);
  }
  for (const weight of weights) {
    // Fontsource naming: <family>-<subset>-<weight>-<style>.woff2
    const filename = `${pkg}-latin-${weight}-normal.woff2`;
    const src = join(srcFiles, filename);
    const dst = join(fontOut, filename);
    if (!existsSync(src)) {
      console.error(`[copy-fonts] expected font file not found: ${src}`);
      process.exit(1);
    }
    copyFileSync(src, dst);
    fontCount++;
  }
}

/* ------------------------------------------------------------------ *
 * Stage 2 — Chart.js UMD build, used only by public/landing.html.
 * (The React app doesn't use Chart.js.)
 * ------------------------------------------------------------------ */
const vendorOut = join(root, "public", "vendor");
mkdirSync(vendorOut, { recursive: true });

const chartSrc = join(nodeModules, "chart.js", "dist", "chart.umd.js");
const chartDst = join(vendorOut, "chart.umd.js");
if (!existsSync(chartSrc)) {
  console.error("[copy-fonts] chart.js not found at node_modules/chart.js/dist/chart.umd.js");
  process.exit(1);
}
copyFileSync(chartSrc, chartDst);

console.log(
  `[copy-fonts] copied ${fontCount} font files → public/fonts/ · Chart.js → public/vendor/`,
);
