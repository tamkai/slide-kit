---
name: slide-make
description: 構成JSON（deck_structure.json）から実際のスライドを作る第2段階。タイプA（Codexで画像生成した見た目重視のスライド）とタイプB（HTMLから作る、あとでPowerPointで文字を直せるスライド）を選べる。どちらも最終形はスピーカーノート入りPPTX。"slide-make", "スライドにして", "スライド化", "画像スライド", "編集できるスライド", "PPTXにして" で発動。前段は slide-plan。
---

# slide-make — 構成をスライドにする（第2段階）

**ユーザーとのやり取りは必ず日本語で行う。**

slide-plan が作った構成JSON（`deck_structure.json`）から、実際のスライドとPPTXを作る。

## 最初に必ず聞くこと

構成JSONを受け取ったら、**作り始める前にこれだけ聞く**:

> どちらで作りますか？
>
> **A. 画像スライド** — AIイラストで世界観が強い。**あとから文字を直せません**（文字が絵に焼き込まれるため）
> **B. 編集できるスライド** — PowerPointであとから文字を直せます。まずブラウザで確認しながら作ります
>
> 迷ったら B。あとで直したくなる可能性があるなら B が安全です。

**この2択以外の質問を最初にしない。** テーマや色の話は、選択後に必要なら聞く。

**Aが選ばれたときだけ**、続けてもう1つ聞く:

> その資料は、どちらに近いですか？
>
> **A-1. 発表者が話す** — タイトル・結論ひとこと・短い本文2〜3行を焼き込みます（Bと同等の情報量が基本）
> **A-2. 読んで分かる必要がある**（配布資料・報告書） — 文章をさらに厚くし、**タイトルとリード文だけは直せる**ようにします

**A-1でも「文字少・図だけ」を既定にしない。** 図だけのスライドは話者が説明しないと成立せず、聞き手も置いていかれやすい。タイトル+lead_B+body_B を焼くのが基本形で、文字を削って図で見せるのはクライマックス等、意図した枚だけに使う（Tension Map で判断）。

| | A-1 講演用 | A-2 読み物 | B 編集できる |
|---|---|---|---|
| 作り方 | Codexで画像生成 | Codexで画像生成＋テキスト重ね | HTML→PPTX変換 |
| 想定 | 話者が喋る | **単体で読める** | 回覧・修正前提 |
| 文字量 | 中（title+lead+本文2〜3行） | 多い（ビジーで可） | 中 |
| タイトル/リード | 画像に焼く | **編集可能** | 編集可能 |
| 本文 | 画像に焼く | 画像に焼く | 編集可能 |
| 使用量 | 多い（3〜5倍速く消費） | 多い | 少ない |
| 手順書 | `references/type-a-image.md` | `references/type-a-readable.md` | `references/type-b-editable.md` |

**A-2 は情報密度を高く取る**（1スライド1メッセージを意図的に外す）。
これは矛盾ではなく Document↔Workshop 連続軸の Document 側に振った状態
（`../slide-plan/references/design-modes.md`）。どちらの端を狙うかを案件ごとに決める。

## Step 0: 環境チェック（初回のみ・自動）

`~/.slide-kit-ready` が存在しなければ、slide-setup の手順を実行してから続行する。存在すれば黙って次へ進む。**利用者に環境の話をさせない。**

タイプAを選ばれた場合、`~/.slide-kit-ready` の中身を読み、`image_gen: ok` でなければ**作業を始める前に**こう伝える:

> このパソコンでは画像生成（タイプA）が動かないことが確認されています。タイプB（編集できるスライド）で作りますか？

## 出力先のルール（重要）

成果物は**作業プロジェクト配下**に作る。**プラグイン配下（このスキルのディレクトリ）や `~/.claude/` には絶対に書かない** — タイプAで使う codex がそこに書けず、後段で必ず詰まる。

```
<作業プロジェクト>/<デッキ名>/
├── deck_structure.json   （slide-plan の出力）
├── images/               （タイプA: 生成画像）
├── slides/               （タイプB: HTML）
├── dist/                 （PPTX・中間物）
└── styles/               （タイプA: 使うスタイル定義のコピー）
```

## タイプA: 画像スライド

→ A-1なら **`references/type-a-image.md`**、A-2なら **`references/type-a-readable.md`** を読んで、そこの手順に従う。

要点だけ:
1. `styles/` からスタイルを選ぶ（既定は `isometric.txt`）
2. **まず代表3枚だけ試作**して世界観・文字描画を目視確認する。使用量を無駄にしないための必須手順
3. 固まってから全枚を並列生成
4. `collect_images.py` で回収・配置・**重複チェック**（codexは隣のスライドと同じ絵を作ることがある）
5. `build_pptx_from_images.js` でPPTX化（スピーカーノート入り）

## タイプB: 編集できるスライド

→ **`references/type-b-editable.md` を読んで、そこの手順に従う。**

要点だけ:
1. `themes/` からテーマを選び、構成JSONから1枚1ファイルのHTMLを作る（1280x720px）
2. **ブラウザで見てもらい、直しを受ける**（ここが速いのがタイプBの利点。活かすこと）
3. 固まったら `extract_html.py` で「フラット背景PNG＋テキスト構造」を抽出
4. `build_pptx_from_html.js` でPPTX化
5. `fix_pptx.py` を**必ず**通す

## フォント（両タイプ共通）

このキットは **Gen Interface JP**（SIL OFL 1.1）を標準フォントとする。slide-setup が自動導入する。

**タイプBでは、ウェイトの扱いに固有の落とし穴がある。** CSSの `font-weight: 500` をそのまま `Gen Interface JP` + bold=false と書くとRegularに落ちる。必ず `scripts/fonts.js` の `resolveFont()` を通すこと。詳細と理由 → `references/fonts.md`

## バンドル資源

| ファイル | 用途 |
|---|---|
| `scripts/collect_images.py` | タイプA: codex生成画像の回収・配置・**ハッシュ重複チェック** |
| `scripts/build_pptx_from_images.js` | タイプA: 画像→PPTX（ノート埋め込み）。`--readable` でタイトル/リードを重ねる |
| `scripts/wf_generate_template.js` | タイプA: 並列生成ワークフローの雛形 |
| `scripts/extract_html.py` | タイプB: HTML→フラット背景PNG＋テキスト構造JSON |
| `scripts/build_pptx_from_html.js` | タイプB: 抽出結果→編集可能PPTX |
| `scripts/fonts.js` | タイプB: ウェイト→フォント名マッピング（**必読**） |
| `scripts/fix_pptx.py` | 両タイプ: 生成後の必須修正 |
| `styles/*.txt` | タイプA: 差し替え可能なスタイル定義。`infographic-readable.txt` はA-2専用（上部18%安全領域） |
| `themes/` | タイプB: HTMLテーマ |
| `references/type-b-patterns.md` | タイプB: レイアウトパターンカタログ |

## 前段

構成JSONは **slide-plan** で作る。構成JSONがない状態でこのスキルが呼ばれたら、先に slide-plan を案内する。
