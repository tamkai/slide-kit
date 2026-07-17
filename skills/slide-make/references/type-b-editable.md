# タイプB — 編集できるスライド（HTML → PPTX）

構成JSONから **1枚=1ファイルのHTML** を作り、ブラウザで確認しながら固め、
最後に **「見た目そのまま＋文字は編集可能」なPPTX** に変換する。

## 仕組み（なぜこの方式か）

PPTXを最初から手で組む（python-pptxで座標を打つ）方式は**再現度が低く、却下されている**。
座標がズレて意図した見た目にならない。

代わりに使うのが **抽出型** の2枚重ね:

```
  完成HTML
     │
     ├─→ ① 文字だけを透明化してレンダリング → フラット背景PNG（2倍解像度）
     │      カード・図・装飾・グラデーションがピクセルそのまま残る
     │
     └─→ ② 各テキスト要素の実座標(getBoundingClientRect)・スタイル・runを抽出
            
  PPTX = ①を全面背景に敷く + ②を編集可能テキストボックスとして重ねる
       = デザインはピクセル一致 / 文言は編集可
```

装飾や図の座標を個別に拾う必要がないので、HTMLの構造に依存しにくいのが利点。

## 手順

### Step 1: HTMLを作る

`themes/` からテーマを選び、構成JSONの各スライドを **1280x720px** のHTMLにする。

- 1スライド = 1ファイル（`slides/001.html` 〜）
- スライドのルート要素は `.slide`（抽出スクリプトの既定セレクタ）
- 太字・アクセントは `<b>` / `<strong>` / `class="accent"` で表現する（run として抽出される）
- レイアウトパターンのカタログ → `type-b-patterns.md`
- 制約・禁則 → `type-b-pptx-rules.md`
- 反復して直すときの作法 → `type-b-html-loop.md`

`references/index-template.html` を使うと、全スライドをめくって見られるビューアが作れる。

### Step 2: ブラウザで見てもらう（**ここが要**）

**HTMLができたら必ず一度止めて、ユーザーに見てもらう。**

```
open slides/index.html          # Mac
start slides\index.html         # Windows
```

タイプBの最大の利点は**この確認ループが速いこと**。PPTXにしてから直すより圧倒的に安い。
勝手にPPTXまで走り抜けない。

> ブラウザで開いて見てください。直したいところがあれば言ってください。
> ここで直す方が、PowerPointにしてから直すより速いです。

反復編集で確認してもらうときは、**ブラウザのキャッシュに注意**する。
`file://` で見えないときや古い表示が残るときは、no-cache配信 + シークレットウィンドウが確実。

### Step 3: 抽出する

```bash
python3 <plugin>/skills/slide-make/scripts/extract_html.py "slides/*.html" dist/extract
```

出力: `dist/extract/flat_01.png` … と `dist/extract/structure.json`

スライドのルート要素が `.slide` でない場合は `--slide-sel` で指定する。

### Step 4: PPTX化する

```bash
cd <plugin>/skills/slide-make/scripts && npm install    # 初回のみ
node <plugin>/skills/slide-make/scripts/build_pptx_from_html.js \
     dist/extract dist/deck.pptx deck_structure.json
```

第3引数に構成JSONを渡すと、`speaker_note` がスピーカーノートに入る。

**フォントのウェイトは `fonts.js` の `resolveFont()` が解決する。**
自前でフォント名を書かないこと。理由 → `fonts.md`

### Step 5: fix_pptx.py を通す（必須）

```bash
python3 <plugin>/skills/slide-make/scripts/fix_pptx.py dist/deck.pptx
```

PptxGenJS の既知バグを修正する。**飛ばすと壊れたPPTXが出る。**

### Step 6: 検証する

```bash
soffice --headless --convert-to pdf dist/deck.pptx   # LibreOfficeがあれば
pdftoppm -png deck.pdf preview
```

生成PDFを数枚 Read で目視し、以下を確認する:

- 文字が意図した位置にあるか（背景の文字跡と重なっているか）
- **フォントが明朝等に化けていないか**（化けていたらフォント未インストール → slide-setup）
- 折り返しが意図しない位置で起きていないか

## よくある不具合

| 症状 | 原因 | 対処 |
|---|---|---|
| 文字が二重に見える | フラット背景に文字が焼かれている | 透明化CSSが効いていない。`--slide-sel` がルート要素と一致しているか確認 |
| 太字・アクセント色が全部消えた | `runs` が抽出/適用されていない | `extract_html.py` の `--run-sel` を確認。ここは実際にハマった箇所 |
| 文字が痩せて見える | ウェイトがRegularに落ちている | `resolveFont()` を通していない → `fonts.md` |
| 意図しない位置で折り返す | 日本語の字幅 | テキストボックス幅の余裕（`WIDTH_MARGIN_PX`）を増やす |
| フォントが明朝になる | フォント未インストール | slide-setup を実行 |
