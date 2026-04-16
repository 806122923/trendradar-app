"use client";

/**
 * Chat page — minimal MVP version of the conversational picker.
 * Streams text chunks from the API and appends them live.
 */
import { useState } from "react";
import { streamPickerQuery } from "@/lib/api";

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [model, setModel] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setBusy(true);
    setErr(null);
    setResponse("");
    setModel(null);
    try {
      for await (const ev of streamPickerQuery({ query })) {
        if (ev.event === "start") setModel(ev.model);
        else if (ev.event === "delta") setResponse((p) => p + ev.text);
        else if (ev.event === "error") {
          setErr(ev.message);
          break;
        } else if (ev.event === "done") break;
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="text-3xl font-bold tracking-tight mb-2">
        TrendRadar · 选品
      </h1>
      <p className="text-sm text-muted-foreground mb-8">
        用一句话描述你想找的品，AI 会返回 Top 3 推荐 + 推理。
      </p>

      <form onSubmit={submit} className="space-y-3 mb-6">
        <textarea
          className="w-full min-h-[120px] p-3 border rounded-md text-base"
          placeholder="例：给我 3 个美区 50 美金以内、家居类、最近 7 天增速最快的品"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={busy}
        />
        <button
          type="submit"
          disabled={busy || !query.trim()}
          className="px-6 py-2 rounded-md bg-black text-white font-medium disabled:opacity-50"
        >
          {busy ? "分析中…" : "提交查询"}
        </button>
      </form>

      {model && (
        <div className="text-xs text-muted-foreground mb-2 font-mono">
          · MODEL {model}
        </div>
      )}

      {err && (
        <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm mb-4">
          {err}
        </div>
      )}

      {response && (
        <article className="whitespace-pre-wrap rounded-md border p-4 font-mono text-sm leading-relaxed">
          {response}
        </article>
      )}
    </main>
  );
}
