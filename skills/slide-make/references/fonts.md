# フォント — Gen Interface JP

このキットの標準フォントは **Gen Interface JP**（作者: 飯塚大和 / [GitHub](https://github.com/yamatoiizuka/gen-interface-jp)）。slide-setup が自動導入する。

## なぜこのフォントなのか

| 理由 | 中身 |
|---|---|
| **PPTXに埋め込める** | 全ウェイトの OS/2 `fsType = 0`（Installable Embedding＝無制限）。**フォントを入れていない第三者に配っても崩れない** |
| **Mac / Windows 両方に入る** | 静的TTF。OS分岐が不要になる |
| **HTMLとPPTXで同じ字面** | 中身が Inter（欧文）+ Noto Sans JP（和文）の混植。Webフォント版もあるので、ブラウザで見た通りがPPTXに来る |
| **ライセンスが自由** | SIL OFL 1.1。商用利用可・再配布可・自動ダウンロード可 |
| **見出し用が別にある** | `Gen Interface JP Display` は字間を詰めた見出し用。本文は `Gen Interface JP` |

## 落とし穴: 4スタイルリンクモデル（必ず読む）

**Gen Interface JP は、Regular と Bold だけが `Gen Interface JP` ファミリーに収まり、それ以外のウェイトは独立したファミリーとして登録される。**

実測すると、例えば Medium はこうなっている:

```
Family (nameID 1)      : "Gen Interface JP Medium"   ← 独立ファミリー扱い
Subfamily (nameID 2)   : "Regular"
Typographic Family (16): "Gen Interface JP"          ← 対応アプリだけがこれを見る
```

PowerPoint は Typographic Family に対応していないため、フォント一覧には
`Gen Interface JP` / `Gen Interface JP Medium` / `Gen Interface JP SemiBold` … と**別々に並ぶ**。

### 何が起きるか

CSSの `font-weight: 500` を見て素直にこう書くと:

```js
{ fontFace: "Gen Interface JP", bold: false }   // ✗ Regular に落ちる
```

**Medium にならず Regular で表示される。** 見た目が痩せて再現度が落ちる。

正しくはこう:

```js
{ fontFace: "Gen Interface JP Medium", bold: false }   // ○
```

### 対応表

| CSS font-weight | PPTXに書くフォント名 | bold属性 |
|---|---|---|
| 100 | `Gen Interface JP Thin` | false |
| 200 | `Gen Interface JP ExtraLight` | false |
| 300 | `Gen Interface JP Light` | false |
| **400** | `Gen Interface JP` | false |
| **500** | `Gen Interface JP Medium` | false |
| **600** | `Gen Interface JP SemiBold` | false |
| **700** | `Gen Interface JP` | **true** |
| 800 | `Gen Interface JP ExtraBold` | false |

見出し用（`font-family` に `Display` を含む場合）は、ベースを `Gen Interface JP Display` に読み替えて同じ規則を適用する。

### 実装

**この表を手で書かない。** `scripts/fonts.js` の `resolveFont()` を使う:

```js
const { resolveFont } = require("./fonts");
const { fontFace, bold } = resolveFont(block.fontWeight, block.fontFamily);
```

`build_pptx_from_html.js` は既にこれを通している。新しく変換スクリプトを書く場合も必ず通すこと。

## その他の注意

- **バージョンを固定する**。v0.8.0（2026-07-17時点の最新）を使う。まだ v1.0 前で、将来メトリクスが変わるとPPTXの字送りがズレる可能性がある。slide-setup はバージョン固定でダウンロードする
- **全16ウェイトで約99MB**。必要なウェイトだけ入れる（既定: Regular / Medium / SemiBold / Bold / ExtraBold）
- **丸ゴシックの代替にはならない**。丸ゴを使うテーマがある場合は別途フォントが要る
- 系譜は Noto Sans JP 派生（そのため著作権表記に Adobe の Reserved Font Name `Source` が残っている）。**`Source` を含む名前での改変再配布は不可**。そのまま同梱・配布するのは OFL 全文を添えれば可

## PowerPoint でフォントを埋め込む手順（利用者に案内する）

`fsType = 0` なので拒否されない。

- **Windows**: ファイル > オプション > 保存 > 「ファイルにフォントを埋め込む」
- **Mac**: PowerPoint > 環境設定 > 保存 > 「フォントをファイルに埋め込む」

これをやっておくと、フォント未インストールの相手に渡しても見た目が保たれる。
