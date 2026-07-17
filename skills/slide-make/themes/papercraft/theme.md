# papercraft theme

slide-make のビジュアル層テーマ。紙とハサミの手仕事感のあるテイスト。
セミナー教材・配布資料・落ち着いた説明資料向け。

## Voice / Personality

- **アトリエの朝** — 紙とハサミの手仕事感。静かで温かく、急かさない声
- **ペーパークラフトの質感** — 背景は紙テクスチャ。図解は切り絵コラージュ。デジタルだが手触りがある
- **抑制的なジャンプ率** — 極端な対比はしない。読み物として落ち着くサイズ感
- **役割を持った余白** — 背景の装飾は四隅・上下に寄せ、中央は読むための余白として空ける
- **メタ情報を見せない** — 「Day 1」「Block」等の運用メタ情報は画面に出さない(教材のページ番号は別。下記参照)

## Color palette

papercraft 固有変数(`--ink` 系)が正典。`theme.css` 冒頭で共通の
`--brand-*` にブリッジ済み(パターン互換のため)。

| トークン | 値 | 役割 |
|---------|----|------|
| `--ink` | `#3A3F38` | 主役テキスト。柔らかい墨グリーン寄り |
| `--ink-soft` | `#6E6A60` | 補助テキスト |
| `--ink-muted` | `#9A9384` | 控えめテキスト |
| `--sage` / `--sage-deep` | `#8B9A7D` / `#6F7E63` | アクセント1。帯・ルール・1軸目 |
| `--gold` / `--gold-deep` | `#C4A057` / `#A8863F` | アクセント2。ハイライト下線・2軸目 |
| `--terracotta` | `#C77B57` | アクセント3。3軸目・差し色 |
| `--cream` | `#F3EEE3` | 地の色 |
| `--card` | `#FBF8F1` | カード面 |

**意図**: クリーム紙の上に sage / gold / terracotta の3アクセント。彩度を抑えた
自然色で、長時間読んでも疲れない。柔らかい構図。

## Typography

| ファミリ | 変数 | 用途 |
|---------|------|------|
| Noto Sans JP | `--font-display` / `--font-body` | 和文見出し・本文。Weight 900 で display、400 で body |
| Inter | `--font-accent` | 欧文ラベル(eyebrow)・章番号。letter-spacing 広め |

### ジャンプ率スケール

| クラス | サイズ | 想定用途 |
|--------|--------|---------|
| `--text-xs` | 0.78rem | eyebrow ラベル、ページ番号 |
| `--text-sm` | 1rem | 本文 |
| `--text-md` | 1.3rem | 本文強調・サブタイトル |
| `--text-lg` | 2.2rem | セクション見出し |
| `--text-xl` | 3.2rem | スライドタイトル |
| `--text-2xl` | 4.6rem | 表紙タイトル級 |
| `--text-hero` | 8rem | 章扉の決め言葉 |

**抑制方針**: テキストブック(配布教材)用途が主なので、standard の hero
12rem より控えめな 8rem。読み物として落ち着くことを優先する。

## 背景画像 — 役割別の4種

papercraft の肝。**万能な1枚ではなく、役割別に複数種を使い分ける**。
背景は CSS の `background-image`(`<img>` ではない)。`assets/backgrounds/` に
JPEG 最適化版を同梱(生成元プロンプトは下記)。

| bg-* クラス | 画像 | 装飾の配置 | 用途 |
|---|---|---|---|
| `.bg-cover` | bg_01_cover.jpg | 上下帯+左下に葉 / 中央広い | 表紙・章扉・キービジュアル |
| `.bg-corners` | bg_03_content_corners.jpg | 四隅に極小装飾 / 中央最大に空く | 本文・3軸・グリッド・比較・split |
| `.bg-wrap` | bg_04_wrap.jpg | 下部に帯 / 上80%は空く | 章まとめ・巻末 |
| `.bg-minimal` | bg_05_minimal.jpg | ほぼ無地の紙テクスチャ | キーメッセージ・対句 |

**背景生成**: `references/background-generation.md` の手順で jinn-image を使う。
共通プロンプト方針 — 「papercraft / cut-paper texture / cream・sage・gold・
terracotta に strictly limited / no text / 装飾は端に寄せ中央は空ける」。
役割ごとに「装飾をどこに置くか」だけ変える。

## 2つのモード — v3 トークガイド / v4 テキストブック

papercraft は用途の異なる2モードを持つ。

| | v3 トークガイド | v4 テキストブック |
|---|---|---|
| 役割 | 講師の語りの伴奏(投影用) | 参加者が手元で読む配布教材 |
| 1枚の中身 | キーフレーズ + 講師が肉付け | 見出し + 説明文 + 要点(読んで追える) |
| CSS | `theme.css` のみ | `theme.css` + `textbook.css` を併用(順に読む) |
| ページ番号 | 出さない | 右下に `.tb-pageno` で出す(教材なので可) |
| 主なクラス | `.title` `.card` `.compare` `.icon-wrap` 等 | `.tb-head` `.tb-body` `.tb-split` `.tb-points` `.tb-figure` 等 |
| レイアウト | ATL-1〜8 の7パターン | 本文/章扉/コラム/まとめ/表紙/目次/巻末 |

**textbook.css** は v4 専用。`.tb-*` クラス群(見出し・本文・図解プレースホルダ・
要点ボックス・章構成・コラム・目次)を定義。v4 を作るときだけ `theme.css` の
後に読み込む。

## レイアウトパターン(v3 トークガイド)

| パターン | 背景 | 構成 |
|---|---|---|
| 章扉 | bg-cover | eyebrow + 大タイトル + サブ + title-rule.center + progress-dots |
| キービジュアル | bg-cover | 大タイトル中央 + サブ題。図解は背景で代替 |
| キーメッセージ・対句 | bg-minimal | quote-mark + 大タイトル + サブ + 補助行。文字主役 |
| 3軸 | bg-corners | タイトル + 3カード(card-no + icon-wrap + 名称 + rule + 説明 + tag) |
| グリッド | bg-corners | タイトル + 4×4等。各セルは小カード or テキスト+icon-dot |
| 比較2列 | bg-corners | タイトル + .compare(左右 compare-col) |
| split | bg-corners | 左に画像エリア + 右に解説 |

## カラーの使い分け

- 3軸の軸1/2/3 = sage / gold / terracotta(`.blob-sage/gold/terracotta`)
- 比較の「望ましくない側」= ink-soft 寄り / 「望ましい側」= sage
- 帯・補助 = sage 系
- ハイライト下線 = gold(`.accent`)

## 得意なプレゼン種別

- **セミナー・研修の配布教材** — テキストブックモードが本領
- **落ち着いた説明資料** — 紙の質感が「急かさない」読み心地を作る
- **ワークショップの伴奏スライド** — トークガイドモード
- **長めの読み物デッキ** — 抑制的なジャンプ率が長時間の読みに向く

## 苦手 / 不向き

- ピッチデック等の「強度で押す」プレゼン — standard の方が向く
- データ密度の高いダッシュボード — 紙の余白美学と相性が悪い
- 派手な訴求が要るマーケ資料 — 彩度を抑えた自然色は静かすぎる

## 禁則(Don'ts)

1. **アクセント色は1スライド原則2色まで** — 3軸カードの識別目的のみ3色OK
2. **メタ情報(Day/Block/イントロ等)を画面に出さない** — eyebrow は英語の内容ラベルのみ可。v4 のページ番号は例外
3. **背景の中央に装飾を侵食させない** — 中央は読むための余白。装飾は端へ
4. **box-shadow を印刷で残さない** — `@media print` で影オフ済み。個別CSSで影を足したら印刷時の挙動を確認
5. **`overflow-wrap: anywhere` を日本語に使わない** — 語の途中で折れる。`break-word` + 用語名は `white-space:nowrap`
6. **背景画像を `<img>` で置かない** — `background-image`。図解(切り絵コラージュ)だけ `<img>`

## L1-L6 講演パターン実装方針

slide-make の講演モード(L1-L6)を papercraft 色で使う場合の方針。

- **L1 Full-Color Single Word** — 画面全体を `--sage` または `--ink` で塗り1語。
  紙テクスチャ背景(bg-minimal)の上に色面を重ねてもよい
- **L2 Photo Full-bleed + Overlay** — 切り絵コラージュ図解を全面 + `--ink` 半透明オーバーレイ
- **L3 Black Slide** — `--ink`(完全な黒は使わない。墨グリーン)で暗転
- **L4 Split Color** — `--ink` と `--cream`、または `--sage` と `--cream` の2分割
- **L5 Number Impact** — 巨大数字。`--text-hero`(8rem)の1.5倍相当。`--gold` で
- **L6 Transition Slide** — bg-minimal の紙テクスチャに `--sage` の微かな帯

## アセット

`themes/papercraft/assets/backgrounds/` に背景4種(JPEG 最適化版):
- `bg_01_cover.jpg` / `bg_03_content_corners.jpg` / `bg_04_wrap.jpg` / `bg_05_minimal.jpg`

図解(切り絵コラージュ挿絵)はテーマに同梱しない。案件ごとに
`references/background-generation.md` の手順で jinn-image 生成する。

## 実装チェックリスト

- [ ] アクセント色が1スライド2色以内(3軸カードのみ3色可)
- [ ] メタ情報(Day/Block 等)が画面に出ていない
- [ ] 背景クラス(bg-cover/corners/wrap/minimal)が用途どおり
- [ ] 背景中央に装飾が侵食していない(中央は読む余白)
- [ ] 図解は `<img>`、背景は `background-image`
- [ ] v4 なら `theme.css` → `textbook.css` の順で読み込み
- [ ] 1280×720 に収まり、はみ出しがない
- [ ] 印刷(PDF)で box-shadow が四角いベタ面にならない

## 関連リファレンス

- `../README.md` — テーマ追加の型(Step 1-8)
- `../CREATE_THEME_GUIDE.md` — ゼロからテーマを作る対話ガイド
- `../../references/background-generation.md` — 役割別背景画像の生成ワークフロー
- `../../references/html-build-loop.md` — チェックしながら HTML を量産する手順
- `../../references/pptx-conversion-rules.md` — PPTX 変換(抽出型 / 手組み型)
