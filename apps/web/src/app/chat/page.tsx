"use client";

/**
 * TrendRadar chat page — conversational product picker.
 *
 * Visual language mirrors the orange landing page:
 *   - Pure B/W + single acid accent (#FF4F1A)
 *   - Sharp 2px corners, no soft shadows, no gradients
 *   - Space Grotesk display, Inter body, JetBrains Mono labels
 *
 * While the LLM streams, we show a skeleton plus collapsible raw output.
 * When streaming completes we try to parse the JSON picks and render
 * them as structured cards with an inline SVG score chart; if parsing
 * fails we fall back to the raw text.
 */

import { Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { streamPickerQuery } from "@/lib/api";
import { ProductCards, tryParsePicks } from "@/components/ProductCards";

const PRESETS = [
  "给我 3 个美区 30 美金以内、宠物类、增速最快的品",
  "最近 14 天家居类增速 Top 3，竞争不能太激烈",
  "厨房小工具里单价 15 美金左右、复购率高的品",
  "美妆个护里近期 GMV 飙升、达人合作热的品",
];

function ChatInner() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const [response, setResponse] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [model, setModel] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const autoRan = useRef(false);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Auto-fill + auto-submit when URL has ?q=
  useEffect(() => {
    const q = searchParams.get("q");
    if (q && !autoRan.current) {
      autoRan.current = true;
      setQuery(q);
      setTimeout(() => run(q), 50);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // Elapsed-time counter while streaming
  useEffect(() => {
    if (busy) {
      setElapsed(0);
      const started = Date.now();
      tickRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - started) / 100) / 10);
      }, 100);
    } else if (tickRef.current) {
      clearInterval(tickRef.current);
      tickRef.current = null;
    }
    return () => {
      if (tickRef.current) clearInterval(tickRef.current);
    };
  }, [busy]);

  async function run(q: string) {
    if (!q.trim() || busy) return;
    setBusy(true);
    setErr(null);
    setResponse("");
    setModel(null);
    setDone(false);
    setSubmittedQuery(q);

    try {
      for await (const ev of streamPickerQuery({ query: q })) {
        if (ev.event === "start") setModel(ev.model);
        else if (ev.event === "delta") setResponse((p) => p + ev.text);
        else if (ev.event === "error") {
          setErr(ev.message);
          break;
        } else if (ev.event === "done") {
          setDone(true);
          break;
        }
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (searchParams.get("q")) router.replace("/chat");
    run(query);
  }

  function usePreset(p: string) {
    setQuery(p);
    run(p);
  }

  function reset() {
    setQuery("");
    setResponse("");
    setSubmittedQuery(null);
    setDone(false);
    setErr(null);
    setModel(null);
    if (searchParams.get("q")) router.replace("/chat");
  }

  const parsed = done && !err ? tryParsePicks(response) : null;

  return (
    <div className="min-h-screen bg-paper text-ink">
      {/* ============ NAV ============ */}
      <nav className="sticky top-0 z-20 bg-paper border-b border-ink">
        <div className="mx-auto max-w-6xl px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <span
              aria-hidden
              className="inline-flex items-center justify-center h-6 w-6 bg-ink text-acid font-display text-lg leading-none"
              style={{ borderRadius: 2 }}
            >
              ▲
            </span>
            <span className="font-display font-semibold text-[15px] tracking-tight">
              TrendRadar
            </span>
            <span className="font-mono text-[10px] tracking-label text-muted ml-1">
              / CONSOLE
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="font-mono text-[11px] tracking-label text-muted hover:text-ink focus-visible:text-ink transition-colors"
            >
              ← 首页
            </Link>
            {submittedQuery && (
              <button onClick={reset} className="btn-tr-ghost !py-2 !px-3 text-xs">
                新查询
              </button>
            )}
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-6 py-10 pb-24">
        {/* ============ HERO (pre-submit) ============ */}
        {!submittedQuery && (
          <section className="max-w-3xl">
            <div className="tr-label text-muted mb-4">
              00 · <span className="text-ink">AI PRODUCT PICKER</span>
            </div>
            <h1 className="tr-display text-[44px] md:text-[56px] leading-[1.05] mb-5">
              说说你想找<span className="tr-acid-u">什么品</span>
              <span style={{ color: "#FF4F1A" }}>.</span>
            </h1>
            <p className="text-[15px] leading-relaxed text-muted max-w-xl">
              用一句话描述类目 / 价格 / 增速 / 竞争度。AI 返回 Top 3
              推荐，附带综合评分、推理、风险与下一步动作。
            </p>
          </section>
        )}

        {/* ============ INPUT (pre-submit) ============ */}
        {!submittedQuery && (
          <section className="mt-10 max-w-3xl">
            <div className="tr-label text-muted mb-3">01 · QUERY</div>
            <form onSubmit={submit}>
              <div
                className="relative border border-ink transition-colors focus-within:border-acid"
                style={{ borderRadius: 2 }}
              >
                <textarea
                  className="block w-full min-h-[140px] p-5 pr-4 pb-16 text-[15px] leading-relaxed text-ink placeholder:text-muted bg-paper focus:outline-none focus-visible:outline-none resize-none"
                  style={{ borderRadius: 2 }}
                  placeholder="例：给我 3 个美区 50 美金以内、家居类、最近 7 天增速最快的品"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={busy}
                  onKeyDown={(e) => {
                    if (
                      (e.metaKey || e.ctrlKey) &&
                      e.key === "Enter" &&
                      query.trim()
                    ) {
                      e.preventDefault();
                      submit(e as unknown as React.FormEvent);
                    }
                  }}
                />
                <div className="absolute left-5 bottom-5 font-mono text-[11px] tracking-label">
                  {busy ? (
                    <span className="text-acid">ANALYZING · {elapsed.toFixed(1)}s</span>
                  ) : (
                    <span className="text-muted">按 ⌘/CTRL + ENTER 快速提交</span>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={busy || !query.trim()}
                  className="absolute right-3 bottom-3 btn-tr-acid !py-2.5 !px-4 text-sm"
                >
                  {busy ? "分析中…" : "提交 →"}
                </button>
              </div>
            </form>
          </section>
        )}

        {/* ============ PRESETS (pre-submit) ============ */}
        {!submittedQuery && (
          <section className="mt-8 max-w-3xl">
            <div className="tr-label text-muted mb-3">
              02 · <span className="text-ink">QUICK QUERIES</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p, i) => (
                <button
                  key={i}
                  onClick={() => usePreset(p)}
                  disabled={busy}
                  className="tr-chip disabled:opacity-40"
                >
                  <span className="font-mono text-[10px] tracking-label text-muted mr-1">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  {p}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* ============ QUERY DISPLAY (post-submit) ============ */}
        {submittedQuery && (
          <section className="mb-8 tr-card p-5">
            <div className="flex items-start gap-5">
              <div className="tr-label text-muted">01 · QUERY</div>
              <div className="flex-1">
                <p className="text-[15px] leading-relaxed text-ink">
                  {submittedQuery}
                </p>
              </div>
            </div>
            {(model || busy || done) && (
              <div className="mt-4 pt-4 border-t border-line flex items-center gap-4 font-mono text-[11px] tracking-label">
                {model && (
                  <span className="flex items-center gap-2 text-muted">
                    <span
                      className="inline-block h-1.5 w-1.5 rounded-full"
                      style={{
                        background: done
                          ? "#00C853"
                          : busy
                          ? "#FF4F1A"
                          : "#8a8a8a",
                      }}
                    />
                    MODEL · <span className="text-ink">{model}</span>
                  </span>
                )}
                {busy && (
                  <span className="text-acid">ELAPSED · {elapsed.toFixed(1)}s</span>
                )}
                {done && <span className="text-pos">✓ COMPLETE</span>}
              </div>
            )}
          </section>
        )}

        {/* ============ ERROR ============ */}
        {err && (
          <section
            className="mb-6 tr-card p-5 border-t-2 border-acid"
            style={{ borderRadius: 2 }}
          >
            <div className="tr-label text-acid mb-2">! ERROR</div>
            <pre className="font-mono text-[12px] text-ink whitespace-pre-wrap break-words">
              {err}
            </pre>
          </section>
        )}

        {/* ============ STREAMING SKELETON ============ */}
        {busy && !err && (
          <section className="space-y-4">
            <StreamingSkeleton />
            {response && (
              <details className="tr-card">
                <summary className="cursor-pointer select-none px-5 py-3 text-[11px] font-mono tracking-label text-muted hover:text-ink">
                  ▸ 查看原始流式输出 (DEBUG)
                </summary>
                <pre className="px-5 pb-4 text-[12px] font-mono text-ink whitespace-pre-wrap break-words max-h-64 overflow-y-auto">
                  {response}
                </pre>
              </details>
            )}
          </section>
        )}

        {/* ============ RESULTS ============ */}
        {done && parsed && <ProductCards result={parsed} />}

        {/* ============ RESULTS (parse failed) ============ */}
        {done && !parsed && response && (
          <section
            className="tr-card p-5 border-t-2 border-acid"
            style={{ borderRadius: 2 }}
          >
            <div className="tr-label text-acid mb-2">
              ! RAW OUTPUT · 无法解析为结构化卡片
            </div>
            <pre className="text-[14px] text-ink whitespace-pre-wrap break-words font-mono">
              {response}
            </pre>
          </section>
        )}

        {/* ============ FOOTER CTA ============ */}
        {submittedQuery && done && (
          <section className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-3">
            <button onClick={reset} className="btn-tr-acid">
              开始新查询 →
            </button>
            <Link href="/" className="btn-tr-ghost">
              ← 返回首页
            </Link>
          </section>
        )}
      </main>
    </div>
  );
}

/* =====================================================================
   Streaming skeleton — 3 sharp-cornered bar placeholders
===================================================================== */
function StreamingSkeleton() {
  return (
    <div className="space-y-4">
      {/* Metrics strip placeholder */}
      <div className="grid grid-cols-4 border border-ink tr-breathe">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={`px-5 py-4 ${i > 0 ? "border-l border-ink" : ""}`}
          >
            <div className="h-8 w-16 bg-line mb-2" />
            <div className="h-2 w-12 bg-line" />
          </div>
        ))}
      </div>
      {/* Chart placeholder */}
      <div className="tr-card p-6 tr-breathe">
        <div className="h-2 w-24 bg-line mb-4" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="h-6 w-6 bg-line" />
              <div
                className="h-6 bg-line"
                style={{ width: `${80 - i * 15}%` }}
              />
            </div>
          ))}
        </div>
      </div>
      {/* Card placeholders */}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="tr-card tr-breathe"
          style={{ animationDelay: `${i * 150}ms` }}
        >
          <div className="flex items-stretch border-b border-ink">
            <div className="w-[88px] bg-line" />
            <div className="flex-1 px-5 py-4 space-y-2">
              <div className="h-2 w-24 bg-line" />
              <div className="h-5 w-2/3 bg-line" />
            </div>
          </div>
          <div className="p-5 space-y-3">
            <div className="h-2 bg-line w-full" />
            <div className="h-2 bg-line w-11/12" />
            <div className="h-2 bg-line w-3/4" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-paper flex items-center justify-center font-mono text-[11px] tracking-label text-muted">
          LOADING · CONSOLE
        </div>
      }
    >
      <ChatInner />
    </Suspense>
  );
}
