"use client";

/**
 * Chat page — conversational product picker.
 *
 * While the LLM streams, we show a lightweight "typing" indicator + partial
 * text. When streaming completes we try to parse the JSON picks and render
 * them as product cards; if parsing fails we fall back to the raw text.
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
  const autoRan = useRef(false);

  // Auto-fill + auto-submit when URL has ?q=
  useEffect(() => {
    const q = searchParams.get("q");
    if (q && !autoRan.current) {
      autoRan.current = true;
      setQuery(q);
      // run after state settles
      setTimeout(() => run(q), 50);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

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
    // Clear ?q= from URL so a refresh doesn't re-run the preset
    if (searchParams.get("q")) {
      router.replace("/chat");
    }
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
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b border-zinc-100">
        <div className="mx-auto max-w-3xl px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-white font-bold text-xs">
              T
            </div>
            <span className="font-semibold tracking-tight text-sm">
              TrendRadar
            </span>
          </Link>
          {submittedQuery && (
            <button
              onClick={reset}
              className="text-xs font-medium text-zinc-500 hover:text-black transition"
            >
              新查询
            </button>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8 pb-24">
        {/* Hero text (only before first submit) */}
        {!submittedQuery && (
          <div className="mb-6">
            <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-2">
              说说你想找什么品
            </h1>
            <p className="text-sm text-zinc-600">
              用一句话描述类目 / 价格 / 增速 / 竞争度，AI 会给你 Top 3
              推荐和推理。
            </p>
          </div>
        )}

        {/* Submitted query display */}
        {submittedQuery && (
          <div className="mb-6 rounded-xl bg-white border border-zinc-200 p-4">
            <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1.5">
              你的查询
            </div>
            <p className="text-sm text-zinc-800 leading-relaxed">
              {submittedQuery}
            </p>
          </div>
        )}

        {/* Input form */}
        {!submittedQuery && (
          <form onSubmit={submit} className="space-y-3 mb-6">
            <div className="relative">
              <textarea
                className="w-full min-h-[120px] p-4 pr-14 rounded-xl border border-zinc-200 bg-white text-base text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:border-zinc-400 focus:ring-4 focus:ring-zinc-100 transition resize-none"
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
              <button
                type="submit"
                disabled={busy || !query.trim()}
                className="absolute right-3 bottom-3 h-9 px-4 rounded-lg bg-black text-white text-sm font-medium hover:bg-zinc-800 disabled:opacity-30 disabled:cursor-not-allowed transition"
              >
                {busy ? "分析中…" : "提交 ↵"}
              </button>
            </div>
            <div className="text-xs text-zinc-400 pl-1">
              按 ⌘/Ctrl + Enter 快速提交
            </div>
          </form>
        )}

        {/* Preset chips (only before submit) */}
        {!submittedQuery && (
          <div>
            <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3 pl-1">
              或者直接试试
            </div>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p, i) => (
                <button
                  key={i}
                  onClick={() => usePreset(p)}
                  disabled={busy}
                  className="px-3 py-2 rounded-full bg-white border border-zinc-200 text-sm text-zinc-700 hover:border-zinc-400 hover:bg-zinc-50 disabled:opacity-50 transition"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Model badge */}
        {model && submittedQuery && (
          <div className="mb-3 text-xs text-zinc-400 font-mono flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            MODEL · {model}
            {busy && <span className="text-orange-500">· 分析中</span>}
          </div>
        )}

        {/* Error */}
        {err && (
          <div className="rounded-xl bg-rose-50 border border-rose-200 p-4 text-sm text-rose-800 mb-4">
            <div className="font-medium mb-1">出错了</div>
            <div className="font-mono text-xs">{err}</div>
          </div>
        )}

        {/* Streaming state — show skeleton + raw partial */}
        {busy && !err && (
          <div className="space-y-3">
            <StreamingSkeleton />
            {response && (
              <details className="rounded-lg border border-zinc-200 bg-white">
                <summary className="cursor-pointer select-none px-4 py-2 text-xs font-medium text-zinc-500 hover:text-zinc-900">
                  查看原始流式输出
                </summary>
                <pre className="px-4 pb-3 text-xs font-mono text-zinc-600 whitespace-pre-wrap break-words max-h-60 overflow-y-auto">
                  {response}
                </pre>
              </details>
            )}
          </div>
        )}

        {/* Done — parsed cards */}
        {done && parsed && <ProductCards result={parsed} />}

        {/* Done — parse failed, show raw */}
        {done && !parsed && response && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
            <div className="text-xs font-medium text-amber-800 mb-2">
              无法解析为结构化卡片，显示原文：
            </div>
            <pre className="text-sm text-zinc-800 whitespace-pre-wrap break-words font-mono">
              {response}
            </pre>
          </div>
        )}

        {/* Retry / new query button when done */}
        {submittedQuery && done && (
          <div className="mt-8 flex justify-center">
            <button
              onClick={reset}
              className="px-5 py-2.5 rounded-lg bg-black text-white text-sm font-medium hover:bg-zinc-800 transition"
            >
              开始新查询
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

function StreamingSkeleton() {
  return (
    <div className="space-y-3">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="rounded-xl border border-zinc-200 bg-white p-5 animate-pulse"
          style={{ animationDelay: `${i * 150}ms` }}
        >
          <div className="flex items-start gap-4 mb-4">
            <div className="h-10 w-10 rounded-lg bg-zinc-100" />
            <div className="flex-1 space-y-2">
              <div className="h-3 bg-zinc-100 rounded w-1/3" />
              <div className="h-4 bg-zinc-100 rounded w-2/3" />
            </div>
            <div className="h-10 w-12 rounded bg-zinc-100" />
          </div>
          <div className="space-y-2">
            <div className="h-3 bg-zinc-100 rounded" />
            <div className="h-3 bg-zinc-100 rounded w-5/6" />
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
        <div className="min-h-screen bg-zinc-50 flex items-center justify-center text-sm text-zinc-400">
          加载中…
        </div>
      }
    >
      <ChatInner />
    </Suspense>
  );
}
