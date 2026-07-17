/**
 * CSSの font-weight / font-family → PPTXに書くフォント名 への変換。
 *
 * ■ なぜこのファイルが要るのか（重要・非自明）
 *
 * Gen Interface JP は「4スタイルリンクモデル」で命名されている。
 * つまり Regular と Bold だけが `Gen Interface JP` ファミリーに収まり、
 * それ以外のウェイトは **独立したファミリー** として登録される。
 *
 *   font-weight: 500 → ファミリー名 "Gen Interface JP Medium" / Subfamily "Regular"
 *
 * そのため CSS の font-weight:500 を見て素直に
 *   { fontFace: "Gen Interface JP", bold: false }
 * と書くと、PowerPoint では **Regular に落ちる**（Mediumにならない）。
 * ウェイトごとに別のフォント名を指定する必要がある。これがこの表の役目。
 *
 * ※ Typographic Family (nameID 16) は "Gen Interface JP" に統一されているので、
 *   Adobe系など対応アプリでは1ファミリーにまとまる。PowerPoint は非対応。
 *
 * 参照: https://github.com/yamatoiizuka/gen-interface-jp
 */

const BASE_TEXT = "Gen Interface JP";
const BASE_DISPLAY = "Gen Interface JP Display";

// ウェイト → [フォント名サフィックス, bold属性]
// Regular(400) と Bold(700) だけがベースファミリー内のスタイルリンクで表現される。
const WEIGHT_MAP = {
  100: ["Thin", false],
  200: ["ExtraLight", false],
  300: ["Light", false],
  400: [null, false], // ベースファミリーそのもの
  500: ["Medium", false],
  600: ["SemiBold", false],
  700: [null, true], // ベースファミリー + bold属性
  800: ["ExtraBold", false],
  900: ["ExtraBold", false], // 900は存在しないので800に丸める
};

/** CSSのfont-weight文字列を100刻みの数値に正規化する */
function normalizeWeight(cssWeight) {
  if (cssWeight === "normal") return 400;
  if (cssWeight === "bold") return 700;
  const n = parseInt(cssWeight, 10);
  if (!n || Number.isNaN(n)) return 400;
  // 未定義のウェイトは最も近い定義済みウェイトに丸める
  const defined = Object.keys(WEIGHT_MAP).map(Number);
  return defined.reduce((a, b) => (Math.abs(b - n) < Math.abs(a - n) ? b : a));
}

/** font-family文字列が見出し用(Display)を指しているか */
function isDisplay(fontFamily) {
  return /Display/i.test(fontFamily || "");
}

/**
 * CSSのスタイルから、PPTXに渡す { fontFace, bold } を返す。
 *
 * @param {string} cssWeight  getComputedStyle().fontWeight の値（"500" 等）
 * @param {string} fontFamily getComputedStyle().fontFamily の値
 * @returns {{fontFace: string, bold: boolean}}
 */
function resolveFont(cssWeight, fontFamily) {
  const weight = normalizeWeight(cssWeight);
  const [suffix, bold] = WEIGHT_MAP[weight] || [null, false];
  const base = isDisplay(fontFamily) ? BASE_DISPLAY : BASE_TEXT;
  return {
    fontFace: suffix ? `${base} ${suffix}` : base,
    bold,
  };
}

/** slide-setup がインストールを確認すべきフォント名の一覧 */
function requiredFontNames() {
  const names = new Set();
  for (const base of [BASE_TEXT, BASE_DISPLAY]) {
    for (const [suffix] of Object.values(WEIGHT_MAP)) {
      names.add(suffix ? `${base} ${suffix}` : base);
    }
  }
  return [...names];
}

module.exports = { resolveFont, normalizeWeight, isDisplay, requiredFontNames,
                   BASE_TEXT, BASE_DISPLAY };
