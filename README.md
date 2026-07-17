# Slide Kit

Claude Code で、**構成をつくる → スライドにする** の二段階でスライドを作るキット。

はじめての方は **[docs/quickstart.html](docs/quickstart.html)** をブラウザで開いてください。
（このページは読まなくて大丈夫です）

## 何ができるか

原稿やネタを渡すと、まず**構成**（何枚・各枚に何を言うか）が出てきます。
そこを直してから、スライドにします。最終形はスピーカーノート入りの PowerPoint です。

スライドは2種類から選べます。

| | タイプA: 画像スライド | タイプB: 編集できるスライド |
|---|---|---|
| 見た目 | AIイラストで世界観が強い | 崩れない・端正 |
| あとから文字を直す | **できない** | **できる** |
| 確認方法 | 生成された画像を見る | ブラウザで見る |

## 入れ方

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex

/plugin marketplace add <あなたのGitHubアカウント>/slide-kit
/plugin install slide-kit@slide-kit
```

上2行は画像スライド（タイプA）を使う場合だけ必要です。

## 使い方

覚えるのは2つだけです。

```
この原稿からスライド構成を作って     ← 構成が出てくる。ここで直す
これをスライドにして                ← タイプA/Bを聞かれる
```

うまく動かないときは `/slide-setup` と打つと、環境を診断して自動で直します。

## 中身

| スキル | 役割 |
|---|---|
| `slide-plan` | 第1段階。構成JSON（`deck_structure.json`）を作る |
| `slide-make` | 第2段階。タイプA/Bを選んでスライド化＋PPTX化 |
| `slide-setup` | 環境の準備・診断。通常は自動で走る |

## 必要なもの

- **Claude Code**（このプラグインの土台）
- **Node.js 18以上** — Claude Code が動いていれば大抵入っています
- **Python 3** — タイプB（編集できるスライド）で使います
- **Codex CLI** — タイプA（画像スライド）で使います。画像生成は有料プランが必要です

不足していれば `slide-setup` が自動で入れるか、入れ方を案内します。

## フォント

**Gen Interface JP**（SIL OFL 1.1 / [作者リポジトリ](https://github.com/yamatoiizuka/gen-interface-jp)）を
`slide-setup` が自動でインストールします（管理者権限は不要）。

PPTXに埋め込めるので、**フォントを入れていない相手にPowerPointを渡しても崩れません**。
埋め込み方は `skills/slide-make/references/fonts.md` を参照。

## ライセンス

このリポジトリのスキル・スクリプト・ドキュメントは社内利用を想定しています。
同梱していないもの（フォント本体・ウェブのスタイルギャラリー）は、
それぞれの配布元のライセンスに従ってください。
