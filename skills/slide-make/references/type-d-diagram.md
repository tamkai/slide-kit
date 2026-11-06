# タイプD — 図解スライド（図・絵・文字を丸ごと画像生成 → PPTX）

図解を主役にしたスライドを、**図・絵・日本語をひとつの画像として生成**して作る。
図が画風の世界の中に描かれるので、文字と絵が一体に見える。文字はあとから直せない。

```
画風を決める → 一覧画像で世界観を確かめる → 1枚ずつ清書 → 検品 → PPTX
```

| 向いている | 向いていない |
|---|---|
| 概念の図（ベン図、フロー、循環、マップ、ピラミッド） | 正確な数値の図（棒、折れ線、円、ガント）→ タイプB |
| 世界観の強い講演資料 | 直前まで文言を直す資料 → タイプC |

## なぜ、この作り方か（2026-11-06 の実証）

- 図を別に描いて後から合成すると、絵と文字が一体にならない。切り抜きの縁がぼやけ、文字が図に重なる
- 一覧画像は世界観を決めるのに強い。全コマが同じ手で描かれる
- ただし一覧画像はそのまま使えない。コマの境界が不均一で、細部が甘く、小さい文字に誤りが出る
- 一覧のコマを参照に清書すると、構図を保ったまま文字の誤りも直る

## 前提

- **`cockpit gen-image`（codex / gpt-image-2）を使う。** 実寸の 2560x1440 で出力でき、参照画像も渡せる（1枚 約1〜1.5分）
- Cockpit が無い環境では、`plan.tsv` のプロンプトと参照画像を、使える画像生成ツールに同じ順で渡す
- スクリプトに Pillow が要る
- 使用量を多く消費する。一覧1枚と見本1枚で方向を確かめてから清書に進むのは、そのため

## 手順

### Step 1: 構成を確かめる

`slide-plan` の構成JSONに次が入っていること。無ければ補ってから進む。

- 全スライド: `on_slide`（画像に載せる文字の全リスト）、`visual_brief`
- 図解スライド: `diagram`（型、選んだ理由、変えてはいけない構造）
- デッキ全体: `cast`（任意。登場人物。画風ではなく内容なのでここに書く）

`diagram.precision` が `exact` のスライドは言葉の指示では正確に描けない。本人に伝え、タイプBで作るか、図を変えるかを決める。

### Step 2: 画風を決める

既存のパックを使うか、渡された画風を受け取ってパックを作る → **`type-d-style-intake.md`**

パックの場所: `$SLIDE_KIT_PACKS/styles/`（既定は `~/product/slide-kit-packs/styles/`）。

### Step 3: プロンプトを作る

```bash
python3 <plugin>/skills/slide-make/scripts/typed_build_prompts.py \
  --deck deck_structure.json --style <パックID> --out type_d --anchor <基準にするスライド番号>
```

`--anchor` は質感の基準になる1枚。情報量の多い図解スライドを選ぶ（省略すると最初の図解スライド）。

### Step 4: 一覧画像を作り、**本人に見せて止まる**

```bash
python3 <plugin>/skills/slide-make/scripts/typed_render.py type_d --stage boards
```

9枚で1枚の一覧になる。ここで見るのは世界観と各コマの構図だけで、文字の細部は見ない。
Cockpit 内なら `cockpit ask --media` で見せる。OK が出るまで清書に進まない。

> 9枚を超えるデッキは一覧が複数になり、2枚目以降は1枚目を参照する。この経路は未検証。1枚目を見てから進める。

### Step 5: 基準スライドを清書し、見せて止まる

```bash
python3 <plugin>/skills/slide-make/scripts/typed_render.py type_d --stage slides --slides "<基準の番号>"
```

コマの切り出しは自動で行う。残りの全スライドがこの1枚の質感に揃うので、ここで検品（Step 7）して本人の OK を取る。

### Step 6: 残りを清書する

```bash
python3 <plugin>/skills/slide-make/scripts/typed_render.py type_d --stage slides --jobs 3
```

同時生成は3枚までで実証済み。既にある画像は飛ばす。同じ画像が2枚できる取り違えも検出する。

### Step 7: 全枚を検品する（省略しない）

**`type-d-qa.md`** と `type_d/text_checklist.md` を使い、全枚を実際に開いて確かめる。

```bash
python3 <plugin>/skills/slide-make/scripts/typed_render.py type_d --review
```

`type_d/review/` に確認用JPEG（幅1024）と一覧ができる。

### Step 8: 問題の枚だけ直す

**部分修正**（文字1か所など）は、変える所と保つ所を絞った指示をファイルに書いて渡す。旧版は `type_d/old/` に残る。

```bash
python3 <plugin>/skills/slide-make/scripts/typed_render.py type_d --fix <番号> --fix-prompt fix.txt
```

修正指示の形:

```text
Edit the attached slide. Change ONLY this: the label 「ベインドマップ」 must read 「マインドマップ」.
Keep everything else exactly as it is: composition, characters, colors, texture and all other text.
```

**構造の間違い**や、部分修正で2回直らないものは作り直す（`--stage slides --slides "<番号>" --force`）。

> 部分修正は 2026-11-06 に実際の画像で1回確認した（吹き出しの尾を直した。61秒）。人物の位置や文字は保たれ、質感の細部だけわずかに変わった。直したあとも検品表で全項目を見直す。

### Step 9: PPTX にする

```bash
node <plugin>/skills/slide-make/scripts/build_pptx_from_images.js deck_structure.json images <out.pptx>
python3 <plugin>/skills/slide-make/scripts/fix_pptx.py <out.pptx>
```

画像が16:9全面に入り、ノートに title、key_message、speaker_note が入る。
`<out.pptx>` を PDF にして全ページを見てから渡す。
PNG のまま入るので、9枚で約43MBになる（実測）。配布するときは PowerPoint の画像圧縮を使う。

## 出力

```text
<デッキ>/
├── deck_structure.json
├── images/slide_NN.png     清書（PPTXに入る）
└── type_d/
    ├── board-01.png        一覧画像
    ├── panels/pNN.png      切り出したコマ（清書の参照。完成品として使わない）
    ├── *.prompt.txt        各画像のプロンプト（再生成に使える）
    ├── plan.tsv            生成の計画
    ├── text_checklist.md   検品表
    ├── review/             確認用JPEG
    └── old/                作り直す前の版
```

## 報告するとき

- 画像に焼き込まれた文字は直せないことを、納品時にもう一度伝える
- 検品の結果を、確かめた項目と確かめていない項目に分けて書く
