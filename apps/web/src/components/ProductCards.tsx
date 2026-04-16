"use client";

/**
 * Render the LLM's structured picks as a clean product-card list.
 *
 * The LLM returns a JSON object of the form:
 * {
 *   picks: [{ product_id, rank, score, why_now, rationale, risks[], action }],
 *   summary: string
 * }
 *
 * The JSON is often wrapped in a ```json code fence, and while streaming
 * may be incomplete. We best-effort extract + parse; if that fails we fall
 * back to showing the raw text.
 */

export type Pick = {
  product_id: string;
  rank: number;
  score: number;
  why_now: string;
  rationale: string;
  risks: string[];
  action: string;
  title?: string;  // optional, enriched client-side from candidate list later
};

export type PickerResult = {
  picks: Pick[];
  summary: string;
};

/** Try to pull a JSON object out of a possibly-fenced string. Returns null on failure. */
export function tryParsePicks(raw: string): PickerResult | null {
  if (!raw) return null;
  // Strip ```json … ``` fence if present
  const fenced = raw.match(/```(?:json)?\s*([\s\S]*?)```/);
  const candidate = (fenced ? fenced[1] : raw).trim();
  // Find outermost { … } — LLM sometimes prefixes/suffixes prose
  const start = candidate.indexOf("{");
  const end = candidate.lastIndexOf("}");
  if (start === -1 || end === -1 || end <= start) return null;
  const jsonStr = candidate.slice(start, end + 1);
  try {
    const parsed = JSON.parse(jsonStr) as PickerResult;
    if (!parsed || !Array.isArray(parsed.picks)) return null;
    return parsed;
  } catch {
    return null;
  }
}

const RANK_GRADIENTS = [
  "from-amber-400 to-orange-500",
  "from-zinc-300 to-zinc-500",
  "from-orange-700 to-amber-800",
];

export function ProductCards({ result }: { result: PickerResult }) {
  const sorted = [...result.picks].sort((a, b) => a.rank - b.rank);
  return (
    <div className="space-y-4">
      {/* Summary banner */}
      {result.summary && (
        <div className="rounded-xl bg-gradient-to-br from-orange-50 to-rose-50 border border-orange-100 p-4">
          <div className="text-xs font-medium text-orange-700 uppercase tracking-wider mb-1.5">
            一句话总结
          </div>
          <p className="text-sm text-zinc-800 leading-relaxed">
            {result.summary}
          </p>
        </div>
      )}

      {/* Pick cards */}
      {sorted.map((pick) => {
        const g = RANK_GRADIENTS[pick.rank - 1] ?? "from-zinc-300 to-zinc-500";
        return (
          <article
            key={pick.product_id}
            className="rounded-xl border border-zinc-200 bg-white overflow-hidden hover:border-zinc-300 transition-colors"
          >
            {/* Header row */}
            <div className="flex items-start gap-4 p-5 border-b border-zinc-100">
              <div
                className={`h-10 w-10 flex-shrink-0 rounded-lg bg-gradient-to-br ${g} flex items-center justify-center text-white font-bold text-lg shadow-sm`}
              >
                {pick.rank}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-mono text-zinc-400 mb-1 truncate">
                  {pick.product_id}
                </div>
                <div className="text-sm font-medium text-zinc-900 leading-snug">
                  {pick.why_now}
                </div>
              </div>
              <div className="flex-shrink-0 text-right">
                <div className="text-2xl font-bold tabular-nums text-zinc-900">
                  {pick.score}
                </div>
                <div className="text-xs text-zinc-500">综合分</div>
              </div>
            </div>

            {/* Body */}
            <div className="p-5 space-y-4">
              <div>
                <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1.5">
                  推理
                </div>
                <p className="text-sm text-zinc-700 leading-relaxed">
                  {pick.rationale}
                </p>
              </div>

              {pick.risks && pick.risks.length > 0 && (
                <div>
                  <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1.5">
                    风险
                  </div>
                  <ul className="space-y-1">
                    {pick.risks.map((r, i) => (
                      <li
                        key={i}
                        className="text-sm text-zinc-700 leading-relaxed flex items-start gap-2"
                      >
                        <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-rose-500" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {pick.action && (
                <div className="rounded-lg bg-zinc-50 p-3 border border-zinc-100">
                  <div className="text-xs font-medium text-orange-600 uppercase tracking-wider mb-1">
                    下一步动作
                  </div>
                  <p className="text-sm text-zinc-800 leading-relaxed">
                    {pick.action}
                  </p>
                </div>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}
