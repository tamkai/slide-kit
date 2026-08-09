# タイプA — 画像スライド（Codex画像生成 → PPTX）

構成JSONとスタイル定義から、**codex の `image_gen` で1枚ずつ画像スライドを生成**し、
スピーカーノート入りPPTXに仕上げる。

**文字は絵に焼き込まれるので、あとから直せない。** 直す可能性があるならタイプBを勧める。

## 前提

- **codex CLI が認証済み**であること（`/codex:setup` で確認）
- **画像生成はFreeプランでは使えない**（Go/Plus/Pro/Business/Enterprise、またはAPIキー）
- **Windows では動かない可能性がある**。既知の未解決不具合がある（後述）

### 使用量の注意（利用者に必ず伝える）

> 画像生成は、通常の作業の**3〜5倍の速さで使用量の枠を消費します**。20枚のデッキを一度に作ると枠がごっそり減ります。まず代表3枚で試すのはそのためです。

残量は codex セッション中に `/status` で確認できる。

### Windows の既知の不具合

- [Issue #19133](https://github.com/openai/codex/issues/19133) — 設定を入れても `image_gen` ツールが出てこない
- [Issue #28898](https://github.com/openai/codex/issues/28898) — 画像は生成されるが `.codex\generated_images` に保存されず、**保存パスも返らない**

後者は Step 3-4 の生命線（パス報告 → 回収）を壊す。
slide-setup が疎通テスト済みなら `~/.slide-kit-ready` に `image_gen: ok` が入っている。
入っていなければタイプBを勧めること。

## 手順

### Step 1: スタイルを選ぶ

`styles/` から選ぶ（既定は `isometric.txt`）。

| ファイル | 世界観 |
|---|---|
| `isometric.txt` | アイソメトリックの立体図 |
| `handdrawn-warm.txt` | 手描き・あたたかい |
| `editorial-grid.txt` | エディトリアル・グリッド |

**選んだスタイル定義は成果物ディレクトリの `styles/` にコピーする**（後で何を使ったか分かるように）。
新しいスタイルを足す方法 → `styles/README.md`。ウェブで見つけたプロンプトを貼るだけでよい。

### Step 2: 出力ディレクトリを用意する

**codexが書ける場所**に作る。プラグイン配下や `~/.claude/` は不可。

```
<作業プロジェクト>/<デッキ名>/
├── deck_structure.json
├── styles/<name>.txt
├── images/      （文字少版の出力先）
└── images_B/    （読ませ版を作る場合）
```

### Step 3: まず代表3枚だけ試作する（必須）

**いきなり全枚を回さない。** 世界観・日本語の描画・体裁を目視で確認してから全枚に進む。
手戻りが減るだけでなく、**使用量の無駄が減る**。

`scripts/wf_generate_template.js` を成果物ディレクトリにコピーし、冒頭の CONFIG
（DIR / STYLE / DECK / TYPE / TARGETS / SAMPLES）を埋めて **Workflow** で実行する。

各 codex エージェント（`agentType: 'codex:codex-rescue'`）が image_gen で1枚生成し、
**保存はせず生成パスを報告する**。

- 文字少版（TYPE=A）と 上下分割の読ませ版（TYPE=B）は CONFIG の `TYPE` で切替。両方作るなら2回実行
- レイアウトの詳細・読ませ版が上下分割でなければならない理由 → `type-a-layouts.md`

3枚を Read で目視し、ユーザーにも見せて世界観の合意を取ってから Step 3 を全枚で回す。

### Step 4: 回収・配置・重複チェック（最重要）

エージェントの報告から「n→生成パス」の `mapping.json`（`{"1":"/...png", ...}`）を作り、配置する:

```bash
python3 <plugin>/skills/slide-make/scripts/collect_images.py <images_dir> mapping.json
```

- codexは `~/.codex/generated_images/<uuid>/ig_*.png` に吐く癖があり、`cp` が不安定。**配置はこのスクリプトで行う**
- **このスクリプトは全 slide_NN.png のハッシュ重複を検出する。重複が出たら「取り違え」** — codexはお手本に引きずられ、隣のスライドと同じ絵を作ることがある。その番号だけ再生成する
  - 再生成プロンプトに「前回◯◯と同じ絵を作った。このスライドの主役は△△」と明示すると直る
- 欠落（パスが無い/空）も検出される。欠落番号だけ再生成する

詳細・codexの保存癖 → `type-a-codex.md`

### Step 5: PPTX化する

```bash
cd <plugin>/skills/slide-make/scripts && npm ci    # 初回のみ
node <plugin>/skills/slide-make/scripts/build_pptx_from_images.js \
     deck_structure.json <images_dir> <out.pptx>
```

画像を16:9全面に貼り、各スライドのノートに「title + key_message + speaker_note」を入れる。
文字少版/読ませ版で images_dir と出力名を変えて2回実行する。

### Step 6: 検証する

- 重複チェックが「重複なし」になっていること（Step 4で担保）
- 生成画像を数枚 Read で目視（**日本語の崩れ**・世界観のばらつき・取り違え）
- 問題のある番号だけ再生成して Step 4-5 をやり直す
