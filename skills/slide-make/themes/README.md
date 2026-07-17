# slide-make themes

**ビジュアル層のテーマディレクトリ。** レイアウトパターン（`references/patterns.md`）はテーマを知らず、色・フォント・テクスチャはすべてここで定義する。

## 全体方針

slide-make は「レイアウト層」と「ビジュアル層」を分離する設計に移行中。

- **レイアウト層** = `references/patterns.md`（DOM構造と意味クラス名のみ、色・フォント直書き禁止）
- **ビジュアル層** = `themes/{name}/`（CSS変数と意味クラスの実装、テクスチャ、装飾タイポ、プレースホルダ）

生成時は選択されたテーマの `theme.css` と `fonts.html` を各スライドHTMLの `<head>` に差し込み、`_base/` の共通CSSと合成する。


## ディレクトリ構造

```
themes/
├── README.md                ← このファイル
├── _base/                   ← 全テーマ共通
│   ├── semantic-classes.css ← .bg-brand-*, .text-brand-*, .font-*, ジャンプ率 など
│   └── placeholder.css      ← .photo-placeholder, .figure-placeholder
└── {theme-name}/
    ├── theme.css            ← CSS変数＋意味クラスの実装＋装飾＋テクスチャ
    ├── theme.md             ← Voice / パレット意図 / 使い分け / 禁則
    ├── fonts.html           ← <link> タグ片（head に差し込む Google Fonts 等）
    └── assets/              ← SVG / ロゴ等のテーマ固有画像
```

## 新しいテーマを追加する手順

> **対話で作るなら** `CREATE_THEME_GUIDE.md` を使う。Claude がユーザーに
> 質問しながら(Voice → 軸 → パレット → 背景設計 → 試作 → 生成)テーマを
> 1つ完成させる進め方。下記 Step 1-8 は「型の仕様」、CREATE_THEME_GUIDE は
> 「対話での埋め方」。役割が違うので両方を使う。

### 前提: slide-plan の設計哲学 を先に読む

テーマはビジュアル実装層。**色・フォント・禁則を決める前に、まず `<plugin>/skills/slide-plan/references/` を読んで設計哲学を理解すること**。特に：

- `PRINCIPLES.md` — 希少性の三原則（色・レイアウト・記号を 99% 抑え 1% を効かせる）
- `MODES.md` — Document↔Workshop 連続軸。このテーマが想定する位置を決める
- `ACCENT_PLACEMENT.md` — アクセント色は「どこで効かせるか」が本質

哲学層を無視してパレットから入ると、赤を広く塗ったり太字を多用して AI 生成っぽくなる。**必ず原理から入る**こと。

### Step 1: Voice を 1 文で書く

`theme.md` の冒頭に、このテーマの Voice（声）を 1 文で言語化する。これがテーマの全ての判断の軸になる。

```
例（standard）: 「内容を主役にする」— 白地に濃紺、青の一点だけで導線を作る
```

Voice が書けないテーマは作らない。パレットから入らず、言葉から入る。

### Step 2: `themes/{theme-name}/` ディレクトリ作成

```
themes/{theme-name}/
├── theme.css      # CSS 変数 + 意味クラス実装
├── theme.md       # Voice / パレット意図 / 使い分け / 禁則
├── fonts.html     # Google Fonts 等の <link> タグ
└── assets/        # ロゴ / SVG 等（テーマ固有画像）
```

### Step 3: `theme.css` を書く

必須で定義すべき CSS 変数：

- **色**: `--brand-ink` / `--brand-paper` / `--brand-accent` / `--brand-muted` / `--brand-subtle`
- **フォントファミリ**: `--font-display` / `--font-body` / `--font-accent`
- **ジャンプ率**: `--text-xs` / `--text-sm` / `--text-md` / `--text-lg` / `--text-xl` / `--text-2xl` / `--text-hero`
- **プレースホルダ上書き**: `--placeholder-border-color` / `--placeholder-hatch-color-a` / `--placeholder-hatch-color-b`

**ルール**:
- ハードコード色は `--brand-*` の定義箇所だけ。意味クラス（`.bg-brand-accent` 等）は変数参照のみ
- Tailwind 既定カラー（`bg-red-500`, `text-blue-700`）を書かない
- `--text-hero` は `--text-sm` の 8 倍以上（ジャンプ率の担保）

### Step 4: `theme.md` を書く

**必須セクション**（`standard/theme.md` を複製して埋める）:

1. **Voice** — Step 1 で書いた 1 文
2. **カラー意図** — なぜこのパレットか、各色の役割
3. **タイポ使い分け** — `.text-2xl`, `.text-hero` の使いどころ
4. **禁則** — やってはいけないこと（アクセント色の面積上限、同時使用禁止の組み合わせ等）
5. **得意 / 不向き** — このテーマが機能するプレゼン種別 / 相性の悪いプレゼン種別
6. **実装チェックリスト** — 自己監査用

### Step 5: L1-L6 講演パターン対応（必須）

**本スキルの講演モードでは L1-L6 パターンを使う。新テーマは L1-L6 が機能するよう実装すること（全テーマ必須）**。具体的には：

- **L1 Full-Color Single Word** — 画面全体を `--brand-accent` または `--brand-ink` で塗って 1 語配置。テーマ固有の「1 色塗りに耐える色」を選ぶ
- **L2 Photo Full-bleed + Overlay** — 写真＋半透明オーバーレイの色味はテーマのインク色
- **L3 Black Slide** — 完全黒（または `--brand-ink`）で暗転
- **L4 Split Color** — 2 色分割。`--brand-ink` と `--brand-paper`、または `--brand-ink` と `--brand-accent` の組み合わせを決める
- **L5 Number Impact** — 巨大数字（画面 60%）。`--text-hero` のさらに 1.5 倍相当のサイズが映えるか確認
- **L6 Transition Slide** — 微かな色面（`--brand-subtle` or `--brand-muted` ベース）

`theme.md` に **「L1-L6 の実装方針」** セクションを追加し、各パターンでどの変数・どの配色を使うか明記すること。

### Step 6: `fonts.html` に Google Fonts 等の `<link>` を書く

各スライド HTML の `<head>` に差し込まれる。Preconnect と font-display: swap を忘れずに。

### Step 7: `assets/` に必要な SVG / ロゴ等を置く

テーマ固有の画像（ロゴ、装飾モチーフ）。PNG は PPTX 変換で画像として埋め込まれるため、高解像度を用意する。

### Step 8: 動作検証

1. 7 枚程度の小デッキを新テーマで生成（Cover / Section Divider / Text-Heavy / Visual-Hero / Quote / L1 or L5 / Closing）
2. ブラウザで表示し、Voice と一致しているか視覚確認
3. 希少性原則チェック: アクセント色が広く塗られていないか、装飾が均等に付いていないか
4. Phase 7 で PPTX 変換し、`pptx-conversion-rules.md` のフォント pt 対応表に沿った見た目になるか確認

## テーマ作成時のチェックリスト

- [ ] Voice が 1 文で言語化できている
- [ ] slide-plan の設計哲学 の PRINCIPLES.md / MODES.md / ACCENT_PLACEMENT.md を読んだ
- [ ] `bg-red-500` のような Tailwind 既定カラーを theme.css に書いていない
- [ ] ハードコード色は `--brand-*` の定義箇所だけ。意味クラスは変数参照のみ
- [ ] `--text-hero` が本文（`--text-sm`）の少なくとも 8 倍以上（ジャンプ率の担保）
- [ ] アクセント色の使用上限を theme.md に明記
- [ ] 写真プレースホルダ色（`--placeholder-*`）を上書き定義
- [ ] "得意／不向き／禁則" が theme.md に書かれている
- [ ] **L1-L6 の実装方針が theme.md に明記されている（必須）**
- [ ] 7 枚小デッキで動作検証し、Voice との一致を視覚確認した

## 既存テーマ

- **standard** — **既定テーマ。迷ったらこれ。** 白地＋濃紺グレー＋青アクセント1色。用途を選ばない中立的な見た目。フォントは Gen Interface JP
- **papercraft** — 紙の質感。クリーム紙＋sage/gold/terracotta。セミナー教材・配布資料向け。トークガイド / テキストブックの2モードを持つ（`theme.css` + `textbook.css`）。役割別の背景4種を同梱

## テーマを足す2つの経路

slide-make にはビジュアル言語を足す経路が **2 系統** ある。用途が違うのでバッティングしない。

| 経路 | 入口 | 出口 | いつ使う |
|---|---|---|---|
| **themes/**（設計ルート） | 言葉（Voice）+ 原則 | `themes/{name}/` 配下一式 | ゼロから **設計する** とき。哲学・色・タイポ・禁則を原理から定義する |
| **slidekit-templ**（模倣ルート） | PDF | `slide-templates/{nickname}/001-NNN.html` + `references/templates/{nickname}/` | 既存デッキを **再現する** とき。クライアントのブランド PDF やリファレンスを HTML 化する |

### 使い分けルール

- **PPTX 編集可能が必要 → themes/ 一択**。slidekit-templ の出力は HTML のみで、PPTX 変換用の `gen_*.js` は付属しない
- **L1-L6 講演パターンを使う → themes/ 一択**。slidekit-templ 出力には L1-L6 相当のレイアウトが含まれない
- **クライアントブランドの一発再現 → slidekit-templ**。PDF を投入して HTML を返してもらい、`references/templates/` に配置してそのデッキ専用に使う
- **自分の新しい汎用デザイン言語 → themes/**。複数案件で使い回したいなら themes/ に骨格を作る

### 注意

- **slidekit-templ 出力は themes/ 統合されない**。CSS 変数化されず、HTML に色・フォントがハードコードされる。一時利用が前提

