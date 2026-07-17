/**
 * extract_html.py の出力から「編集可能PPTX」を組み立てる。
 *
 * タイプB（編集可能スライド）のステップ2。
 *   - 背景  : flat_NN.png（文字を透明化した2倍解像度PNG）を16:9全面に貼る
 *             → カード・図・装飾はピクセル一致で再現される
 *   - 文字  : structure.json の実座標に編集可能テキストボックスを重ねる
 *             → PowerPointで文言を直せる
 *
 * 使い方:
 *   node build_pptx_from_html.js <extract_dir> <out.pptx> [deck_structure.json]
 *
 * 第3引数に構成JSONを渡すと、speaker_note をスピーカーノートに埋め込む。
 *
 * 生成後は必ず fix_pptx.py を通すこと（PptxGenJSの既知バグ修正）。
 */
const path = require("path");
const fs = require("fs");
const PptxGenJS = require("pptxgenjs");
const { resolveFont } = require("./fonts");

const [, , EXTRACT_DIR, OUT_PPTX, DECK_JSON] = process.argv;
if (!EXTRACT_DIR || !OUT_PPTX) {
  console.error("使い方: node build_pptx_from_html.js <extract_dir> <out.pptx> [deck_structure.json]");
  process.exit(1);
}

const structurePath = path.join(EXTRACT_DIR, "structure.json");
if (!fs.existsSync(structurePath)) {
  console.error(`structure.json がありません: ${structurePath}`);
  console.error("先に extract_html.py を実行してください。");
  process.exit(1);
}
const DATA = JSON.parse(fs.readFileSync(structurePath, "utf8"));

// deck_structure.json は {deck_title, audience, style_ref, slides:[...]} という
// ラッパー形式。スライド番号 n の昇順で並べ、抽出結果と同じ順序に揃える。
let DECK_SLIDES = null;
if (DECK_JSON && fs.existsSync(DECK_JSON)) {
  const deck = JSON.parse(fs.readFileSync(DECK_JSON, "utf8"));
  const slides = Array.isArray(deck) ? deck : deck.slides;
  if (Array.isArray(slides)) {
    DECK_SLIDES = [...slides].sort((a, b) => (a.n || 0) - (b.n || 0));
    if (DECK_SLIDES.length !== DATA.length) {
      console.warn(`注意: 構成JSONは ${DECK_SLIDES.length} 枚、HTMLは ${DATA.length} 枚。`
                 + `枚数が違うのでノートがずれる可能性があります。`);
    }
  }
}

// --- 単位変換: HTML 1280x720 -> PPT 13.333x7.5 inch (96dpi) ---
const PX = 1 / 96;
const px = (v) => v * PX;            // 座標・サイズ
const pt = (cssPx) => cssPx * 0.75;  // CSS px フォント -> pt

// 日本語は欧文より字幅が広く、PowerPointの折返し計算がCSSと一致しない。
// テキストボックス幅に余裕を持たせないと意図しない位置で折り返す（+15%ルール）。
const WIDTH_MARGIN_PX = 18;

function rgbToHex(rgb) {
  const m = rgb && rgb.match(/\d+/g);
  if (!m) return null;
  return m.slice(0, 3)
    .map((n) => parseInt(n).toString(16).padStart(2, "0")).join("").toUpperCase();
}

/**
 * runs（太字/アクセント）から addText 用の text 配列を作る。
 * 重要: \n は消さない。PptxGenJS は文字列内の \n を改行として扱う。
 * 重要: runs を落とすとアクセント色・太字・サイズ差がベースに潰れる。
 */
function buildRuns(block) {
  const full = block.text;
  const base = resolveFont(block.fontWeight, block.fontFamily);
  const baseColor = rgbToHex(block.color) || "333333";
  const runs = (block.runs || []).slice().sort((a, b) => a.start - b.start);
  if (runs.length === 0) {
    return [{ text: full, options: { ...base, color: baseColor, fontSize: pt(block.fontSize) } }];
  }
  const out = [];
  let cur = 0;
  for (const r of runs) {
    if (r.start > cur) {
      out.push({
        text: full.slice(cur, r.start),
        options: { ...base, color: baseColor, fontSize: pt(block.fontSize) },
      });
    }
    const runFont = resolveFont(r.fontWeight || block.fontWeight, block.fontFamily);
    out.push({
      text: full.slice(r.start, r.end),
      options: {
        ...runFont,
        color: rgbToHex(r.color) || baseColor,
        fontSize: pt(r.fontSize || block.fontSize),
      },
    });
    cur = Math.max(cur, r.end);
  }
  if (cur < full.length) {
    out.push({
      text: full.slice(cur),
      options: { ...base, color: baseColor, fontSize: pt(block.fontSize) },
    });
  }
  return out;
}

function addBlock(slide, block) {
  const b = block.box;
  const base = resolveFont(block.fontWeight, block.fontFamily);
  slide.addText(buildRuns(block), {
    x: px(b.x), y: px(b.y),
    w: px(b.w + WIDTH_MARGIN_PX), h: px(b.h) + 0.06,
    fontFace: base.fontFace,
    fontSize: pt(block.fontSize),
    color: rgbToHex(block.color) || "333333",
    bold: base.bold,
    align: block.textAlign === "center" ? "center"
         : block.textAlign === "right" ? "right" : "left",
    valign: "top",
    margin: 0,
    lineSpacingMultiple: 1.0,   // CSS line-height より小さめに
    autoFit: false,
    wrap: true,
  });
}

// --- PPTX 構築 ---
const pptx = new PptxGenJS();
pptx.defineLayout({ name: "W16x9", width: 13.333, height: 7.5 });
pptx.layout = "W16x9";

let noteCount = 0;
DATA.forEach((page, i) => {
  const slide = pptx.addSlide();

  // 1. フラット背景（デザインはここでピクセル一致）
  const flatPath = path.join(EXTRACT_DIR, page.flat);
  if (fs.existsSync(flatPath)) {
    slide.addImage({ path: flatPath, x: 0, y: 0, w: 13.333, h: 7.5 });
  } else {
    console.warn(`背景PNGが見つかりません（背景なしで続行）: ${page.flat}`);
  }

  // 2. 編集可能テキスト（実座標で重ねる）
  for (const block of page.blocks || []) addBlock(slide, block);

  // 3. スピーカーノート（構成JSONがあれば）
  if (DECK_SLIDES && DECK_SLIDES[i]) {
    const d = DECK_SLIDES[i];
    const note = [
      `［${d.n}］${d.title || ""}`,
      "",
      d.key_message || "",
      "",
      d.speaker_note || "",
    ].join("\n").trim();
    if (note) { slide.addNotes(note); noteCount++; }
  }
});

pptx.writeFile({ fileName: OUT_PPTX }).then(() => {
  console.log(`書き出し完了: ${OUT_PPTX}`);
  console.log(`  スライド ${DATA.length} 枚 / ノート ${noteCount} 枚`);
  console.log(`次は: python3 fix_pptx.py "${OUT_PPTX}"`);
});
