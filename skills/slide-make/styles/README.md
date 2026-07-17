# styles/ — 差し替え可能なスタイル定義

各 `*.txt` が1つのビジュアルスタイル（世界観）を定義する。slide-make はこのファイルを
各生成プロンプトの冒頭に差し込み、全スライドの世界観を揃える。**スタイルを足せば、同じ
構成JSONから別の見た目のデッキを作れる**（アイソメ / ペーパークラフト / グラレコ等）。

## 同梱スタイル

- `isometric.txt` — アイソメ・クレイ調。warm parchment背景 / sage green / warm goldタグ / deep forest文字。落ち着いた編集デザイン調（第1号・実証済み）
- `editorial-grid.txt` — エディトリアル・グリッド。2x2グリッド + 大きな弧/円のオーバーレイ + サンドイッチ・レイヤリング（被写体が幾何ブロックの前後に重なる）+ ソフィスティケイテッド・ミュート配色（dusty rose / sage / slate blue 等のくすみ色）+ マットフラット + スタジオ照明。1ブロックをタイトル帯に。商品ビジュアル系の高級感
- `handdrawn-warm.txt` — 手描き温かみ系。明るい白ベース + ティール/イエロー/オレンジ/コーラルの差し色 + 手描き線画イラスト（家族・人物・ロボットマスコット）+ 吹き出し/スクリブル/ドット等の装飾パーツ。親しみやすい家族向けトーン。「Agent for Family」デザインシステムが原型（背景はクリーム→白基調に調整）

## ウェブのスタイルギャラリーから持ってくる（いちばん手軽）

**[NotebookLM Slide Style Library](https://notebooklm-slide-gallery.shirakippt.chatgpt.site/)**（制作: KUMIKO SHIRAKI）に、
160種類のスライドスタイルがYAML形式で公開されている。ビジネス / エディトリアル / ミニマル /
アイソメトリック / インフォグラフィック / レトロ など、カテゴリから選べる。

**取り込み方**:

1. ギャラリーで好みのデザインを選び、「YAMLをコピー」する
2. **成果物プロジェクトの `styles/` に** `<好きな名前>.txt` として貼り付ける
   （このプラグイン配下ではなく、作業中のプロジェクト側に置く）
3. 末尾に必ずこの1行を足す:
   ```
   ## Content to visualize (per-slide concept follows):
   ```
4. slide-make にそのスタイル名を伝える

YAMLはそのまま画像生成プロンプトの前置きとして機能する（構造化された指示なので、
image_gen は素直に従う）。日本語テキストの扱いだけ弱いことがあるので、
うまく効かないときは同梱スタイルの `TEXT RULE` セクションを足すとよい。

**注意すべきこと**:

- **このギャラリーはNotebookLM向け**。画像生成（タイプA）にはほぼそのまま使えるが、
  HTMLテーマ（タイプB）に使うには色・フォントを `themes/` の変数に翻訳する作業が要る
- **ライセンス表記がサイトに見当たらない**（2026-07時点）。**個人の制作物なので、
  取り込んだYAMLをこのリポジトリに同梱して再配布しない**。各自がその都度コピーして使う
- 商用案件で使うなら、事前に制作者に確認するのが安全

## 新しいスタイルの作り方（ゼロから書く）

`isometric.txt` を雛形にコピーして、以下を書き換える:

1. **冒頭の出力指定**: 「16:9 widescreen presentation slide」は維持
2. **Visual Style**: 画風（例: layered papercraft / hand-drawn graphic recording / flat editorial）
3. **Color Palette**: 配色を HEX で具体的に（背景・主・副・アクセント・文字）。`use these EXACTLY` と書く
4. **Cross-slide consistency**: 全スライドで同じ質感・線幅・彩度・ライティング・カメラ角度を保つルール
5. **TEXT RULE**: 日本語テキストの扱い（GPT-Image2は実用十分。指定文以外は描かない、を明記）
6. **Layout**: ONE focal idea・余白・タイトル帯を残す等

末尾は `## Content to visualize (per-slide concept follows):` で終え、その後に各スライドの
中身がプロンプトで連結される前提にする。

## 使い方

slide-make の手順内で、生成プロンプトに `styles/<name>.txt` の全文を読み込んで先頭に置く。
ユーザーがスタイルを指定しなければ `isometric.txt` を既定にするか、どのスタイルにするか尋ねる。
