import { redirect } from "next/navigation";

/**
 * Fallback for `/`.
 *
 * The real landing page is the static designer-grade `public/landing.html`,
 * served via a `beforeFiles` rewrite in `next.config.mjs`. This component
 * should never actually render in production — if it does, the rewrite is
 * misconfigured and we want the user to still land on the real page.
 */
export default function Home() {
  redirect("/landing.html");
}
