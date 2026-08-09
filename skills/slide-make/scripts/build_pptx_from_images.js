/**
 * build_pptx_from_images.js — 画像スライド → PPTX 生成（スピーカーノート埋め込み）
 *
 * タイプA（画像スライド）のPPTX化。画像を16:9全面に貼り、各スライドのノートに
 * deck_structure.json の「title + key_message + speaker_note」を入れる。
 *
 * 使い方:
 *   node build_pptx_from_images.js <deck_structure.json> <images_dir> <out.pptx>
 * 例:
 *   node build_pptx_from_images.js ./deck_structure.json ./images   ./Deck_A.pptx
 *   node build_pptx_from_images.js ./deck_structure.json ./images_B ./Deck_B.pptx
 *
 * 依存: このスクリプトと同じディレクトリで一度だけ `npm ci` する。
 */
const path = require('path');
const fs = require('fs');
const { resolveFont } = require('./fonts');

let PptxGenJS;
try {
  PptxGenJS = require('pptxgenjs');
} catch (e) {
  console.error('pptxgenjs が見つかりません。次を実行してください:');
  console.error(`  cd "${__dirname}" && npm ci`);
  process.exit(1);
}

const args = process.argv.slice(2);
const READABLE = args.includes('--readable');
const [deckPath, imgDir, outFile] = args.filter((a) => !a.startsWith('--'));
if (!deckPath || !imgDir || !outFile) {
  console.error('使い方: node build_pptx_from_images.js <deck_structure.json> <images_dir> <out.pptx> [--readable]');
  console.error('  --readable : 画像の上に「編集可能なタイトル＋リード文」を重ねる（読み物型）');
  process.exit(1);
}

const raw = JSON.parse(fs.readFileSync(path.resolve(deckPath), 'utf-8'));
// {deck_title, slides:[...]} 形式。素の配列で渡された場合も受ける。
const deck = Array.isArray(raw) ? { slides: raw } : raw;
if (!Array.isArray(deck.slides)) {
  console.error('構成JSONに slides 配列がありません: ' + deckPath);
  process.exit(1);
}

// ===== 読み物型（--readable）のタイトル／リード文の版面 =====
// 画像の上部18%は白の安全領域として空けてある前提。そこにテキストを重ねる。
// この座標は全スライドで固定する（ページ間で動くと読み手の目が迷う）。
const TITLE_BOX = { x: 0.46, y: 0.10, w: 12.42, h: 0.48 };
const LEAD_BOX  = { x: 0.48, y: 0.60, w: 12.36, h: 0.68 };
const TITLE_COLOR = '14243A';
const LEAD_COLOR  = '40536A';
const TITLE_PT = 28.2;
const TITLE_PT_MIN = 27.4;   // 1行に収まらないときだけここまで縮める
const LEAD_PT = 15.8;        // リード文は自動縮小しない（収まらなければ推敲する）

// 日本語1文字を全角1、半角を0.5として概算の表示幅を測る
function visualLen(s) {
  let n = 0;
  for (const ch of s) n += /[\x00-\xFF｡-ﾟ]/.test(ch) ? 0.5 : 1;
  return n;
}

// タイトルを1行に収める。まず字間を詰め、それでも溢れるときだけ縮小する。
function fitTitle(text) {
  const capacity = 24.5;           // 28.2pt で TITLE_BOX に収まる全角換算の目安
  const len = visualLen(text);
  if (len <= capacity) return { fontSize: TITLE_PT, charSpacing: 0 };
  if (len <= capacity * 1.03) return { fontSize: TITLE_PT, charSpacing: -0.4 };
  return { fontSize: TITLE_PT_MIN, charSpacing: -0.4 };
}

const pptx = new PptxGenJS();
pptx.defineLayout({ name: 'W16x9', width: 13.333, height: 7.5 });
pptx.layout = 'W16x9';
pptx.title = deck.deck_title || 'Deck';

const slides = [...deck.slides].sort((a, b) => a.n - b.n);
const missing = [];
const longLeads = [];
const shrunkTitles = [];

for (const s of slides) {
  const img = path.join(path.resolve(imgDir), `slide_${String(s.n).padStart(2, '0')}.png`);
  const slide = pptx.addSlide();
  if (fs.existsSync(img) && fs.statSync(img).size > 0) {
    slide.addImage({ path: img, x: 0, y: 0, w: 13.333, h: 7.5 });
  } else {
    missing.push(s.n);
    slide.addText(`【画像未配置】slide_${String(s.n).padStart(2, '0')}.png\n${s.title || ''}`, {
      x: 0.5, y: 3, w: 12.3, h: 1.5, fontSize: 24, align: 'center', color: 'AA3333',
    });
  }

  // 読み物型: タイトルとリード文を編集可能テキストとして重ねる
  if (READABLE) {
    const title = s.title || '';
    if (title) {
      const fit = fitTitle(title);
      if (fit.fontSize < TITLE_PT) shrunkTitles.push(s.n);
      slide.addText(title, {
        ...TITLE_BOX,
        ...resolveFont('700'),          // Gen Interface JP + bold
        fontSize: fit.fontSize,
        charSpacing: fit.charSpacing,
        color: TITLE_COLOR,
        align: 'left', valign: 'top', margin: 0,
        lineSpacingMultiple: 1.0,
        autoFit: false, wrap: false,    // 1行厳守
      });
    }
    // リード文は「それだけ読めば主張が分かる」文章。lead_B を使う。
    const lead = s.lead_B || s.key_message || '';
    if (lead) {
      if (visualLen(lead) > 105) longLeads.push(s.n);
      slide.addText(lead, {
        ...LEAD_BOX,
        ...resolveFont('600'),          // Gen Interface JP SemiBold
        fontSize: LEAD_PT,
        color: LEAD_COLOR,
        align: 'left', valign: 'top', margin: 0,
        lineSpacingMultiple: 1.08,
        autoFit: false, wrap: true,     // 自動折り返しに任せる
      });
    }
  }

  const note = [
    `［${s.n}］${s.title || ''}`,
    '',
    s.key_message || '',
    '',
    s.speaker_note || '',
  ].join('\n');
  slide.addNotes(note);
}

pptx.writeFile({ fileName: path.resolve(outFile) }).then(() => {
  console.log(`書き出し完了: ${path.basename(outFile)}（${slides.length} 枚${READABLE ? ' / 読み物型' : ''}）`);
  if (missing.length) {
    console.log(`  [要対応] 画像未配置: ${missing.join(', ')}`);
  }
  if (shrunkTitles.length) {
    console.log(`  [注意] タイトルが長く ${TITLE_PT_MIN}pt に縮小: ${shrunkTitles.join(', ')}`);
    console.log(`         縮小より推敲を優先したい場合は、その番号のタイトルを短くする`);
  }
  if (longLeads.length) {
    console.log(`  [注意] リード文が105字を超過: ${longLeads.join(', ')}`);
    console.log(`         フォントは縮小しない方針。冗長な表現を削って推敲する`);
  }
  console.log(`次は: python3 fix_pptx.py "${outFile}"`);
});
