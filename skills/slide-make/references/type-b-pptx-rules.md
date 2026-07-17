# PPTX変換の制約と落とし穴

タイプB（編集できるスライド）でPPTXを組むときの技術ルール。
テーマに依存しない、PptxGenJS 固有の制約と、実際に繰り返し踏んだ罠をまとめる。

通常は `build_pptx_from_html.js` が面倒を見るので、このドキュメントを読む必要はない。
**変換スクリプトを自分で書く/直すときだけ**読む。

## 1. PptxGenJS API の制約

### シェイプ名は定数を使う

```javascript
// ✅ 正しい
pres.shapes.OVAL
pres.shapes.RECTANGLE
pres.shapes.ROUNDED_RECTANGLE

// ❌ 文字列名は無効
"ellipse"  "rect"  "roundedRectangle"
```

### カラーは「#なしの6桁hex」だけ

```javascript
// ✅ 正しい
color: "E85C5C"
fill: { color: "1A1A1A" }

// ❌ ファイルが破損する
color: "#E85C5C"    // # 付き
color: "E85C5C80"   // 8桁hex（アルファ付き）
```

透明度は `transparency` で指定する:
```javascript
fill: { color: "E85C5C", transparency: 50 }
```

### オプションオブジェクトを使い回さない

**PptxGenJSは渡されたオブジェクトを内部で書き換える。** 使い回すと2個目以降が壊れる。

```javascript
// ✅ 毎回新しいオブジェクトを作る
slide.addShape(pres.shapes.RECTANGLE, { shadow: { type: "outer", blur: 4 } });
slide.addShape(pres.shapes.RECTANGLE, { shadow: { type: "outer", blur: 4 } });

// ❌ 壊れる
const shadow = { type: "outer", blur: 4 };
slide.addShape(pres.shapes.RECTANGLE, { shadow });
slide.addShape(pres.shapes.RECTANGLE, { shadow });
```

### テキスト

- `margin: 0` — 全テキストに指定する（図形との位置合わせのため）
- `bullet: true` を使う。Unicode の `•` を自前で書かない
- `breakLine: true` は **改行したい片にだけ**付ける

```javascript
// ✅ breakLine は改行位置だけ
[
  { text: "違い", options: { underline: { style: "heavy", color: "E85C5C" } } },
  { text: "が、", options: { breakLine: true } },   // ここで改行
  { text: "差し出せる場を。" }
]

// ❌ スタイル分割片に breakLine を付けると 1片＝1行になる
[
  { text: "違い", options: { underline: {...}, breakLine: true } },  // ← 意図せず改行
  { text: "が、", options: { breakLine: true } },
]
```

## 2. 単位換算

| 変換 | 式 |
|---|---|
| 座標・サイズ | `1px = 1/96 inch`（HTML 1280x720 → PPT 13.333 x 7.5 inch） |
| フォントサイズ | `pt = px × 0.75` |

**px×0.75 は参考値**。最終的にはPPTX上の見た目で判断する。

## 3. 落とし穴（実際に踏んだもの）

### 行間 — CSSの値をそのまま入れると広がりすぎる

CSSの `line-height` と PPTXの `lineSpacingMultiple` は、同じ数値でも結果が大きく違う。
CSSはフォントのascender/descender込みのem-box基準、PPTXはフォントサイズに対する行送り倍率で、
**PPTXの既定の行間が既にCSSより広い**。同じ値を入れると二重に広がる。

| 用途 | CSS line-height | PPTX lineSpacingMultiple |
|---|---|---|
| タイトル（1〜2行） | 1.2〜1.5 | **1.0〜1.15** |
| 本文（複数行） | 1.7〜1.9 | **1.2〜1.3** |
| キャプション | 1.5〜1.6 | **1.15〜1.2** |

### テキストボックスの幅 — +15%の余裕を取る

HTMLのpx幅をインチ換算しただけでは足りない。
PowerPointは**日本語フォントをブラウザより幅広にレンダリング**し、テキストボックスの内部マージンも加わる。
足りないと意図しない位置で折り返す。

`build_pptx_from_html.js` は `WIDTH_MARGIN_PX`（既定18px）で吸収している。
それでも折り返すなら、この値を増やす。

### 画像のアスペクト比 — 手動計算が必須

`addImage` は指定した `w`/`h` に**ストレッチする**。
HTMLの `object-fit: contain` のような自動維持はしてくれない。
配置前に実ピクセルサイズを確認し、比率を計算してから w/h を決める。

（フラット背景PNGは16:9固定なのでこの問題は起きない。図を個別に貼る場合の話）

### runs を落とすと強調が全部消える

抽出時に `runs`（太字・アクセントの文字範囲）を含め忘れると、
**アクセント色・太字・サブラベルのサイズが全部ベース値に潰れる**。実際にハマった箇所。

`extract_html.py` / `build_pptx_from_html.js` は対応済み。自分で書くときは注意する。

### フォントのウェイトが落ちる

`font-weight: 500` をそのまま `Gen Interface JP` + bold=false と書くとRegularに落ちる。
必ず `scripts/fonts.js` の `resolveFont()` を通す。→ `fonts.md`

## 4. fix_pptx.py は必須

```bash
python3 <plugin>/skills/slide-make/scripts/fix_pptx.py output.pptx
```

PptxGenJS の既知バグを修正する。**飛ばすと壊れたPPTXが出る。**
生成のたびに必ず通すこと。

## 5. 枚数が多いときはバッチ分割する

1回の生成で全スライドを組もうとすると、途中で落ちたときに全部やり直しになる。
枚数が多い場合は分割して組み、最後に結合する。

## 関連

- タイプBの全体手順: `type-b-editable.md`
- レイアウトパターン: `type-b-patterns.md`
- フォントの扱い: `fonts.md`
- 既定テーマの色・禁則: `../themes/standard/theme.md`
- 設計哲学（希少性・連続軸・Tension Map）: `../../slide-plan/references/`
