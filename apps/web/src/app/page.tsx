import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-zinc-50">
      {/* Header */}
      <header className="border-b border-zinc-100">
        <div className="mx-auto max-w-6xl px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-white font-bold text-sm">
              T
            </div>
            <span className="font-semibold text-lg tracking-tight">
              TrendRadar
            </span>
            <span className="text-xs text-zinc-400 font-medium ml-1">
              爆品雷达
            </span>
          </Link>
          <Link
            href="/chat"
            className="text-sm font-medium text-zinc-700 hover:text-black"
          >
            开始选品 →
          </Link>
        </div>
      </header>

      {/* Hero */}
      <main className="mx-auto max-w-4xl px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-50 text-orange-700 text-xs font-medium mb-6 border border-orange-100">
          <span className="h-1.5 w-1.5 rounded-full bg-orange-500 animate-pulse" />
          专为 TikTok Shop 美区卖家打造
        </div>

        <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-zinc-900 mb-6 leading-tight">
          用一句话
          <br />
          <span className="bg-gradient-to-r from-orange-600 to-rose-600 bg-clip-text text-transparent">
            找到下一个爆品
          </span>
        </h1>

        <p className="text-lg text-zinc-600 mb-10 max-w-xl mx-auto leading-relaxed">
          把你的选品需求说给 AI，它会从数百个候选品里挑出 Top 3，
          附带增速、GMV、风险点和下一步动作 ——
          几秒钟完成原本要一上午的工作。
        </p>

        <div className="flex items-center justify-center gap-3 mb-16">
          <Link
            href="/chat"
            className="px-6 py-3 rounded-lg bg-black text-white font-medium hover:bg-zinc-800 transition"
          >
            免费开始选品
          </Link>
          <a
            href="#how"
            className="px-6 py-3 rounded-lg border border-zinc-200 text-zinc-700 font-medium hover:border-zinc-300 transition"
          >
            看看怎么用
          </a>
        </div>

        {/* Example queries */}
        <div className="text-left bg-white border border-zinc-200 rounded-2xl p-6 shadow-sm">
          <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-4">
            试试这些查询
          </div>
          <div className="space-y-2">
            {EXAMPLES.map((ex, i) => (
              <Link
                key={i}
                href={`/chat?q=${encodeURIComponent(ex)}`}
                className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-zinc-50 group transition"
              >
                <span className="text-zinc-400 text-sm">›</span>
                <span className="text-sm text-zinc-700 group-hover:text-black flex-1">
                  {ex}
                </span>
                <span className="text-xs text-zinc-400 group-hover:text-orange-600">
                  使用 →
                </span>
              </Link>
            ))}
          </div>
        </div>
      </main>

      {/* How it works */}
      <section id="how" className="border-t border-zinc-100 bg-white">
        <div className="mx-auto max-w-5xl px-6 py-20">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-3">
            三步找到你的下一个爆品
          </h2>
          <p className="text-zinc-600 text-center mb-14 max-w-xl mx-auto">
            不用刷 FastMoss、不用对比 Kalodata、不用 Excel 算选品分
          </p>
          <div className="grid sm:grid-cols-3 gap-8">
            {STEPS.map((s, i) => (
              <div key={i} className="relative">
                <div className="text-5xl font-bold text-zinc-100 mb-3">
                  0{i + 1}
                </div>
                <h3 className="font-semibold mb-2">{s.title}</h3>
                <p className="text-sm text-zinc-600 leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-100">
        <div className="mx-auto max-w-6xl px-6 py-8 text-xs text-zinc-400 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>© 2026 TrendRadar · 爆品雷达</div>
          <div className="flex items-center gap-4">
            <a
              href="mailto:hello@trendradar.app"
              className="hover:text-zinc-700"
            >
              联系我们
            </a>
            <Link href="/chat" className="hover:text-zinc-700">
              开始选品
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

const EXAMPLES = [
  "给我 3 个美区 30 美金以内、宠物类、增速最快的品",
  "最近 14 天家居类增速 Top 3，但竞争不能太激烈",
  "厨房小工具里单价 15 美金左右、复购率高的品",
];

const STEPS = [
  {
    title: "说出你的需求",
    desc: "用自然语言描述你要找的品 —— 类目、价格、竞争、增速，随便说",
  },
  {
    title: "AI 从候选池筛选",
    desc: "基于 14 天 GMV 增速、达人数、店铺数、复购等信号预筛 50 个候选",
  },
  {
    title: "拿到带推理的 Top 3",
    desc: "每个品都有综合评分、推荐理由、风险提示和下一步动作，直接可执行",
  },
];
