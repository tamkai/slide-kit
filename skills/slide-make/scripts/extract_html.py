"""HTMLスライド群から「フラット背景PNG」と「テキスト構造JSON」を取り出す。

タイプB（編集可能スライド）のステップ1。完成済みのHTMLスライドをPlaywrightで開き、
各ページから2つを取り出す:

  1. flat_NN.png : 文字だけを透明化してレンダリングした2倍解像度のPNG。
                   カード・図・装飾はピクセルそのまま残る。これをPPTXの全面背景にする。
  2. structure.json : テキストブロックの実座標・スタイル・アクセントrun。
                      これをPPTXの編集可能テキストボックスとして重ねる。

この2枚重ねにより「デザインはピクセル一致・文言は編集可」が両立する。
装飾や図の座標を個別に拾う必要がないので、HTMLの構造に依存しにくい。

使い方:
  python3 extract_html.py <slides_glob> <out_dir> [--slide-sel .slide]

例:
  python3 extract_html.py "slides/*.html" dist/extract

依存:
  pip install playwright && playwright install chromium
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse
import glob
import json

# 文字を透明化するCSS。背景PNGに文字を焼かないための肝。
# text-shadow / -webkit-text-stroke も消さないと文字の影が残る。
HIDE_TEXT_CSS = """
  .slide, .slide * {
    color: transparent !important;
    text-shadow: none !important;
    -webkit-text-stroke: 0 !important;
    caret-color: transparent !important;
  }
"""

JS = r"""
(cfg) => {
  const slide = document.querySelector(cfg.slideSel);
  if (!slide) return {error: 'slide element not found: ' + cfg.slideSel};
  const sr = slide.getBoundingClientRect();
  const rel = (el) => {
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.left - sr.left), y: Math.round(r.top - sr.top),
            w: Math.round(r.width), h: Math.round(r.height)};
  };

  // テキストブロック: 「直接の子にテキストノードを持つ」要素を自動収集。
  // クラス名に依存しないので、ページ独自クラスが多くても拾える。
  const blocks = [];
  document.querySelectorAll(cfg.slideSel + ' *').forEach(el => {
    if (['B','I','SPAN','SCRIPT','STYLE','IMG','BR','UL','LI','SVG','PATH'].includes(el.tagName))
      return;
    if (cfg.skipCls.some(c => el.classList.contains(c))) return;
    const hasDirectText = [...el.childNodes].some(
      n => n.nodeType === 3 && n.textContent.trim());
    if (!hasDirectText) return;
    const cs = getComputedStyle(el);
    const full = el.innerText.trim();
    if (!full) return;

    // 太字/アクセントを run(文字範囲)として記録。
    // 重要: runs を入れ忘れると、アクセント色・太字・サブラベルのサイズが
    // すべてベース値に潰れる。実際にハマった箇所なので消さないこと。
    const runs = [];
    [...el.querySelectorAll(cfg.runSel)].forEach(b => {
      const t = b.innerText;
      const idx = full.indexOf(t);
      if (idx < 0) return;
      const bcs = getComputedStyle(b);
      runs.push({
        text: t, start: idx, end: idx + t.length,
        accent: b.classList.contains('accent'),
        color: bcs.color,
        fontSize: parseFloat(bcs.fontSize),
        fontWeight: bcs.fontWeight,
      });
    });

    blocks.push({
      cls: [...el.classList].join(' '),
      text: full,                 // \n を含む。後段で消さないこと
      box: rel(el),
      fontSize: parseFloat(cs.fontSize),
      fontWeight: cs.fontWeight,
      fontFamily: cs.fontFamily,  // ウェイト→フォント名マッピングに使う
      color: cs.color,
      lineHeight: cs.lineHeight,
      textAlign: cs.textAlign,
      runs: runs,                 // 絶対に消さないこと（上のコメント参照）
    });
  });
  return {blocks};
}
"""


def main():
    ap = argparse.ArgumentParser(description="HTMLスライド → フラットPNG + テキスト構造JSON")
    ap.add_argument("slides_glob", help='スライドHTMLのglob（例: "slides/*.html"）')
    ap.add_argument("out_dir", help="出力先ディレクトリ")
    ap.add_argument("--slide-sel", default=".slide", help="スライドのルート要素セレクタ")
    ap.add_argument("--run-sel", default="b, strong, .accent", help="太字/アクセントとしてrun化するセレクタ")
    ap.add_argument("--skip-cls", default="figure-placeholder,fig-label,fig-desc",
                    help="テキスト収集から除外するクラス（カンマ区切り）")
    ap.add_argument("--scale", type=int, default=2, help="背景PNGの解像度倍率")
    args = ap.parse_args()

    pages = sorted(glob.glob(args.slides_glob))
    if not pages:
        raise SystemExit(f"HTMLが1枚も見つかりません: {args.slides_glob}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = {
        "slideSel": args.slide_sel,
        "runSel": args.run_sel,
        "skipCls": [c.strip() for c in args.skip_cls.split(",") if c.strip()],
    }

    result = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 720},
                                  device_scale_factor=args.scale)
        page = ctx.new_page()
        for i, src in enumerate(pages, start=1):
            abs_src = Path(src).resolve()
            page.goto(f"file://{abs_src}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(400)

            # 1. テキスト構造を先に取る（文字が見えている状態で）
            data = page.evaluate(JS, cfg)
            if data.get("error"):
                raise SystemExit(f"{src}: {data['error']}")

            # 2. 文字を透明化してフラット背景を撮る
            page.add_style_tag(content=HIDE_TEXT_CSS.replace(".slide", args.slide_sel))
            page.wait_for_timeout(150)
            flat_name = f"flat_{i:02d}.png"
            page.locator(args.slide_sel).screenshot(path=str(out_dir / flat_name))

            data["name"] = Path(src).stem
            data["flat"] = flat_name
            result.append(data)
            print(f"[{i:2d}/{len(pages)}] {Path(src).name}: "
                  f"blocks={len(data['blocks'])} → {flat_name}")

            # 次のページのために透明化CSSを落とす（goto で新規読込されるが念のため）
            page.reload()

        browser.close()

    out_json = out_dir / "structure.json"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(f"\n完了: {out_json}")
    print(f"      フラット背景 {len(result)} 枚 → {out_dir}")
    print(f"次は: node build_pptx_from_html.js {out_dir} <出力先.pptx>")


if __name__ == "__main__":
    main()
