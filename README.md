# Slide Kit

Claude Code / Codex で、**構成をつくる → スライドにする** の二段階でスライドを作るキット。

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

**Claude Code と Codex のどちらでも使えます。** 同じリポジトリで両対応しています。

### Claude Code の場合

```
/plugin marketplace add tamkai/slide-kit
/plugin install slide-kit@slide-kit
```

画像スライド（タイプA）を使うなら、これも:

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
```

### Codex の場合

```bash
codex plugin marketplace add tamkai/slide-kit --ref main
codex plugin add slide-kit@slide-kit
```

画像生成は Codex に組み込みなので、追加のプラグインは要りません。

> **Codex はサンドボックスが既定でネットワークを遮断します。** `slide-setup` が
> フォント（56MB）を落とすときに承認を求めるので、許可してください。
> 許可できない場合の手動導入手順も案内されます。

## 使い方

覚えるのは2つだけです。

```
この原稿からスライド構成を作って     ← 構成が出てくる。ここで直す
これをスライドにして                ← タイプA/Bを聞かれる
```

**原稿がなくても始められます。** 素材が足りなければ、いくつか質問されるので答えるだけです
（`slide-ask` が動きますが、覚える必要はありません）。

うまく動かないときは `/slide-setup` と打つと、環境を診断して自動で直します。

## 中身

| スキル | 役割 |
|---|---|
| `slide-ask` | 第0段階。短い質問と調べもので原稿ブリーフ（`deck_brief.md`）を作る。素材が薄いとき slide-plan が自動で呼ぶ |
| `slide-plan` | 第1段階。構成JSON（`deck_structure.json`）を作る |
| `slide-make` | 第2段階。タイプA/Bを選んでスライド化＋PPTX化 |
| `slide-setup` | 環境の準備・診断。通常は自動で走る |

## 必要なもの

- **Claude Code** または **Codex CLI**（どちらでも動く。同じ SKILL.md を両対応マニフェストで配布）
- **Node.js 18以上** — エージェントが動いていれば大抵入っています
- **Python 3** — タイプB（編集できるスライド）で使います
- **画像生成（タイプAのみ）** — Codex の画像生成を使います。有料プランが必要です。
  Claude Code から使う場合は `openai/codex-plugin-cc` プラグインが要ります

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
