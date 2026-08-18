# タイプC — ハイブリッド（生成背景 × 編集可能テキスト）

**世界観はタイプA、編集可能性はタイプB。** codex image_gen で「文字なしの背景アート」を生成し、
タイトル・リード・本文・キャプションは HTML テキストとして重ね、タイプBの抽出パイプラインで
「背景ピクセルそのまま＋文字は編集可能」な PPTX に仕上げる。

2026-08-18 の犬飼ゼミ講演デッキ（Neo Museum スタイル・18枚）で実証済み。

## 向き不向き

- ◎ スタイルの世界観を最大化したいが、直前まで文言を直したい講演資料
- ◎ 誤字リスクを構造的に消したい（文字は焼かないので生成時の文字事故が起きない）
- △ 図の中の文字（グラフの数値ラベル等）が多い資料 — 図中文字は背景に焼くか、
  HTML側で座標指定のオーバーレイにするかを枚単位で判断する（例: 特大統計数字は
  HTMLオーバーレイにすると編集可能になり、グラデ下線も CSS で表現できる）

## 手順

### Step 1: 文字なし背景を生成する

各スライドの visual_brief を使い、**「テキストを後から重ねる背景専用」**として生成する。
プロンプトに必ず入れる要素:

- **文字・数字・記号・タグを一切描かない**（タイトルも本文もキャプションも無し）
- **テキストゾーン（通常は左半分〜左2/3）は完全に空のフラットな地色のまま**にする
- アート要素の位置・スケール指定（下段のみ、右2/5のみ、等）
- 既に焼き込み版デッキがある場合は、その画像をお手本に「同じ絵を文字抜きで」と指示すると
  世界観の一貫性が保てる（新規なら代表1枚をアンカーにして残りを揃える）

出力は `images_c/bg_NN.png` に collect（回収・重複チェックはタイプAと同じ
`collect_images.py` を使う）。

### Step 2: HTML テキスト層を組む

`scripts/typec_build_html.py` を成果物ディレクトリにコピーし、CONFIG を埋めて実行する。
deck_structure.json から 1280x720 の HTML（1枚=1ファイル、ルートは `.slide`）を生成する。

- 背景: `background-image: url("../images_c/bg_NN.png")` + `background-size: cover`
- 文字: title（特大・Display）/ lead_B（結論）/ body_B（本文）/ caption（メタ）
- フォントは **Gen Interface JP**（タイプBと同じ。`fonts.md` のウェイト規則に従う）
- **タイトルの改行位置は自動折返しに任せず、TWEAK で `<br>` を明示する**
  （「自分/が動く」のような不自然な折返しが必ず出る。全枚スクリーンショットで検品する）
- 背景のアートとテキストの衝突は、TWEAK の top / width / body_mt で逃がす。
  逃げ切れないときは背景の再生成（ゾーン指定を厳しく）の方が速い

### Step 3: 検品 → 抽出 → PPTX（タイプBと同一）

```bash
# 全枚スクリーンショット → ユーザーにブラウザで見てもらう（必ず止まる）
python3 <plugin>/skills/slide-make/scripts/extract_html.py "slides_c/*.html" dist/extract
node <plugin>/skills/slide-make/scripts/build_pptx_from_html.js dist/extract dist/deck.pptx deck_structure.json
python3 <plugin>/skills/slide-make/scripts/fix_pptx.py dist/deck.pptx
```

検証はタイプBと同じ（soffice→PDF目視、フォント化け、二重文字）。
加えて `ppt/slides/slideN.xml` の `<a:t>` を数えてテキストが編集可能で入っていることを確認する。

## 落とし穴（実証済み）

- **背景生成で「空けて」と言った領域にも装飾が入ることがある** → ゾーンを座標%で明示する
- **お手本参照でも要素の位置は微妙に動く** → テキスト衝突は全枚検品で拾う。直しはHTML側が1秒、背景側は再生成90秒
- 図中に焼いた文字（グラデバー等）と HTML テキストの重なりは body_mt 等で回避
- ファイルサイズ: 背景18枚で PPTX が 30MB 級になる。配布時は PowerPoint の画像圧縮を使う
