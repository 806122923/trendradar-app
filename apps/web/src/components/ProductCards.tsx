"use client";

/**
 * Render the LLM's structured picks with the TrendRadar orange aesthetic.
 *
 * Stack:
 *   1. SummaryStats     — mono-typed metric strip (# picks, avg score, risks)
 *   2. ScoreBarChart    — inline SVG horizontal bar chart comparing picks
 *   3. <Summary>        — LLM one-liner (acid-accented)
 *   4. Per-pick cards   — rank + score gauge + rationale + risks + action
 *
 * The LLM returns JSON of the form:
 * {
 *   picks: [{ product_id, rank, score, why_now, rationale, risks[], action }],
 *   summary: string
 * }
 *
 * The JSON is often fenced with ```json … ```; we best-effort extract + parse.
 */

export type Pick = {
  product_id: string;
  rank: number;
  score: number;
  why_now: string;
  rationale: string;
  risks: string[];
  action: string;
  title?: string;
};

export type PickerResult = {
  picks: Pick[];
  summary: string;
};

/** Try to pull a JSON object out of a possibly-fenced string. */
export function tryParsePicks(raw: string): PickerResult | null {
  if (!raw) return null;
  const fenced = raw.match(/```(?:json)?\s*([\s\S]*?)```/);
  const candidate = (fenced ? fenced[1] : raw).trim();
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

/* =====================================================================
   SummaryStats — mono-typed metric strip, e.g.
   ┌──────────────┬──────────────┬──────────────┐
   │ 03 · PICKS   │ 87 · AVG     │ 04 · RISKS   │
   └──────────────┴──────────────┴──────────────┘
===================================================================== */
function SummaryStats({ picks }: { picks: Pick[] }) {
  const n = picks.length;
  const avg = n
    ? Math.round(picks.reduce((s, p) => s + (p.score || 0), 0) / n)
    : 0;
  const topScore = n ? Math.max(...picks.map((p) => p.score || 0)) : 0;
  const totalRisks = picks.reduce((s, p) => s + (p.risks?.length ?? 0), 0);

  const cells: { value: string; label: string; acid?: boolean }[] = [
    { value: String(n).padStart(2, "0"), label: "PICKS" },
    { value: String(topScore), label: "TOP SCORE", acid: true },
    { value: String(avg), label: "AVG SCORE" },
    { value: String(totalRisks).padStart(2, "0"), label: "TOTAL RISKS" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 border border-ink">
      {cells.map((c, i) => (
        <div
          key={c.label}
          className={`px-5 py-4 ${
            i > 0 ? "border-t md:border-t-0 md:border-l border-ink" : ""
          } ${i >= 2 ? "border-t md:border-t-0" : ""}`}
        >
          <div
            className={`font-display text-3xl font-semibold tabular-nums leading-none ${
              c.acid ? "text-acid" : "text-ink"
            }`}
          >
            {c.value}
          </div>
          <div className="mt-2 font-mono text-[11px] tracking-label text-muted">
            {c.label}
          </div>
        </div>
      ))}
    </div>
  );
}

/* =====================================================================
   ScoreBarChart — inline SVG horizontal bar chart.
   - Rank 1 bar is filled acid (solid)
   - Rank 2+ bars are solid black
   - Axis: 0 → 100 with subtle 25/50/75 dashed guides
===================================================================== */
function ScoreBarChart({ picks }: { picks: Pick[] }) {
  const sorted = [...picks].sort((a, b) => a.rank - b.rank);
  const W = 800;
  const H = Math.max(140, sorted.length * 56 + 40);
  const LEFT = 120; // room for rank+id labels
  const RIGHT = 56; // room for trailing score number
  const innerW = W - LEFT - RIGHT;
  const rowH = 36;
  const gap = 20;
  const topY = 16;

  return (
    <figure className="tr-card p-6">
      <figcaption className="tr-label mb-4">
        03 · <span className="text-muted">SCORE DISTRIBUTION</span>
      </figcaption>

      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          width="100%"
          preserveAspectRatio="xMinYMid meet"
          className="block"
          role="img"
          aria-label="Score comparison across top picks"
        >
          {/* Axis baseline */}
          <line
            x1={LEFT}
            x2={LEFT + innerW}
            y1={H - 22}
            y2={H - 22}
            stroke="#000"
            strokeWidth="1"
          />

          {/* Gridlines at 25/50/75/100 */}
          {[25, 50, 75, 100].map((tick) => {
            const x = LEFT + (innerW * tick) / 100;
            return (
              <g key={tick}>
                <line
                  x1={x}
                  x2={x}
                  y1={topY}
                  y2={H - 22}
                  stroke="#e5e5e5"
                  strokeDasharray="3 4"
                  strokeWidth="1"
                />
                <text
                  x={x}
                  y={H - 6}
                  textAnchor="middle"
                  fontFamily="var(--font-mono), monospace"
                  fontSize="10"
                  fill="#8a8a8a"
                >
                  {tick}
                </text>
              </g>
            );
          })}

          {/* Bars */}
          {sorted.map((p, i) => {
            const y = topY + i * (rowH + gap);
            const w = Math.max(2, (innerW * Math.min(100, p.score || 0)) / 100);
            const isTop = i === 0;
            return (
              <g key={p.product_id}>
                {/* Rank number */}
                <text
                  x={8}
                  y={y + rowH / 2 + 10}
                  fontFamily="var(--font-display), system-ui"
                  fontSize="26"
                  fontWeight="600"
                  fill={isTop ? "#FF4F1A" : "#000"}
                >
                  {String(p.rank).padStart(2, "0")}
                </text>

                {/* Product id */}
                <text
                  x={52}
                  y={y + rowH / 2 + 5}
                  fontFamily="var(--font-mono), monospace"
                  fontSize="11"
                  fill="#000"
                >
                  {truncate(p.product_id, 11)}
                </text>

                {/* Bar background track */}
                <rect
                  x={LEFT}
                  y={y}
                  width={innerW}
                  height={rowH}
                  fill="none"
                  stroke="#000"
                  strokeWidth="1"
                />
                {/* Filled bar */}
                <rect
                  x={LEFT}
                  y={y}
                  width={w}
                  height={rowH}
                  fill={isTop ? "#FF4F1A" : "#000"}
                />

                {/* Score label trailing the bar */}
                <text
                  x={LEFT + w + 10}
                  y={y + rowH / 2 + 6}
                  fontFamily="var(--font-display), system-ui"
                  fontSize="18"
                  fontWeight="600"
                  fill="#000"
                >
                  {p.score ?? "—"}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="mt-3 flex items-center gap-4 text-[11px] font-mono text-muted tracking-label">
        <span className="inline-flex items-center gap-2">
          <span className="inline-block h-3 w-3 bg-acid" />
          RANK 01
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="inline-block h-3 w-3 bg-ink" />
          OTHERS
        </span>
        <span className="ml-auto">SCORE · 0–100</span>
      </div>
    </figure>
  );
}

/* =====================================================================
   RiskBar — micro horizontal chart: each risk = a 16-px tall unit
===================================================================== */
function RiskBar({ count }: { count: number }) {
  if (!count) return null;
  // Show up to 5 units, with a "+N" if over
  const visible = Math.min(5, count);
  return (
    <div className="inline-flex items-center gap-1">
      {Array.from({ length: visible }).map((_, i) => (
        <span
          key={i}
          className="inline-block h-3 w-3 border border-ink"
          style={{ background: i < count ? "#FF4F1A" : "transparent" }}
        />
      ))}
      {count > 5 && (
        <span className="ml-1 font-mono text-[11px] text-muted">
          +{count - 5}
        </span>
      )}
    </div>
  );
}

/* =====================================================================
   ScoreGauge — tight horizontal bar inside each pick card
===================================================================== */
function ScoreGauge({ score, accent = false }: { score: number; accent?: boolean }) {
  const pct = Math.max(0, Math.min(100, score || 0));
  return (
    <div className="w-full">
      <div className="h-1.5 w-full border border-ink">
        <div
          className="h-full"
          style={{
            width: `${pct}%`,
            background: accent ? "#FF4F1A" : "#000",
          }}
        />
      </div>
      <div className="mt-2 flex items-center justify-between font-mono text-[10px] tracking-label text-muted">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>
  );
}

/* =====================================================================
   PickCard — one pick
===================================================================== */
function PickCard({ pick }: { pick: Pick }) {
  const isTop = pick.rank === 1;

  return (
    <article className="tr-card overflow-hidden">
      {/* Header bar — rank + id + score */}
      <div className={`flex items-stretch border-b border-ink`}>
        {/* Rank tile — acid for #1, black for others */}
        <div
          className={`flex items-center justify-center w-[88px] flex-shrink-0 ${
            isTop ? "bg-acid text-ink" : "bg-ink text-paper"
          }`}
        >
          <span className="font-display text-4xl font-semibold leading-none tabular-nums">
            {String(pick.rank).padStart(2, "0")}
          </span>
        </div>

        {/* Identity + why_now */}
        <div className="flex-1 min-w-0 px-5 py-4">
          <div className="font-mono text-[11px] tracking-label text-muted mb-1 truncate">
            {pick.product_id}
          </div>
          <div className="font-display text-lg leading-snug text-ink">
            {pick.why_now}
          </div>
        </div>

        {/* Score */}
        <div className="hidden sm:flex flex-col items-end justify-center px-5 py-4 border-l border-ink min-w-[108px]">
          <div
            className={`font-display text-4xl font-semibold leading-none tabular-nums ${
              isTop ? "text-acid" : "text-ink"
            }`}
          >
            {pick.score ?? "—"}
          </div>
          <div className="mt-1 font-mono text-[10px] tracking-label text-muted">
            SCORE · 100
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-5 space-y-5">
        {/* Score gauge */}
        <div>
          <div className="tr-label text-muted mb-2">A · SIGNAL STRENGTH</div>
          <ScoreGauge score={pick.score ?? 0} accent={isTop} />
        </div>

        {/* Rationale */}
        <div>
          <div className="tr-label text-muted mb-2">B · RATIONALE</div>
          <p className="text-[15px] leading-relaxed text-ink">{pick.rationale}</p>
        </div>

        {/* Risks */}
        {pick.risks && pick.risks.length > 0 && (
          <div>
            <div className="tr-label text-muted mb-2 flex items-center gap-3">
              <span>C · RISKS</span>
              <RiskBar count={pick.risks.length} />
            </div>
            <ul className="space-y-2">
              {pick.risks.map((r, i) => (
                <li
                  key={i}
                  className="relative pl-4 text-[14px] leading-relaxed text-ink"
                >
                  <span
                    className="absolute left-0 top-2.5 h-[2px] w-2.5"
                    style={{ background: "#FF4F1A" }}
                  />
                  {r}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action */}
        {pick.action && (
          <div
            className="bg-ink text-paper p-4"
            style={{ borderRadius: 2 }}
          >
            <div className="tr-label text-acid mb-1.5">D · NEXT ACTION</div>
            <p className="text-[15px] leading-relaxed text-paper">{pick.action}</p>
          </div>
        )}
      </div>
    </article>
  );
}

/* =====================================================================
   Summary strip — acid-accented one-liner from the LLM
===================================================================== */
function SummaryLine({ text }: { text: string }) {
  if (!text) return null;
  return (
    <section className="tr-card p-5 border-t-2 border-acid" style={{ borderRadius: 2 }}>
      <div className="tr-label text-acid mb-2">02 · ONE-LINER</div>
      <p className="font-display text-xl leading-snug text-ink">{text}</p>
    </section>
  );
}

/* =====================================================================
   Main export
===================================================================== */
export function ProductCards({ result }: { result: PickerResult }) {
  const sorted = [...result.picks].sort((a, b) => a.rank - b.rank);

  return (
    <div className="space-y-8">
      {/* 01 · Metrics strip */}
      <section>
        <div className="tr-label mb-3">01 · METRICS</div>
        <SummaryStats picks={sorted} />
      </section>

      {/* 02 · Summary line */}
      {result.summary && <SummaryLine text={result.summary} />}

      {/* 03 · Score chart */}
      {sorted.length > 0 && <ScoreBarChart picks={sorted} />}

      {/* 04 · Pick cards */}
      <section>
        <div className="tr-label mb-3">
          04 · PICKS · <span className="text-muted">RANKED BY SCORE</span>
        </div>
        <div className="space-y-4">
          {sorted.map((p) => (
            <PickCard key={p.product_id} pick={p} />
          ))}
        </div>
      </section>
    </div>
  );
}

/* =====================================================================
   util
===================================================================== */
function truncate(s: string, n: number) {
  if (!s) return "";
  return s.length > n ? s.slice(0, n - 1) + "…" : s;
}
