---
name: slide-setup
description: Slide Kit を使う準備をする。フォントの自動導入、Node/Python/Playwright/Codexの確認、Windowsでの画像生成の疎通テストを行い、結果を ~/.slide-kit-ready に記録する。通常は初回に1度だけ自動で走るので、利用者が覚える必要はない。うまく動かないときの診断にも使う。"slide-setup", "スライドの準備", "セットアップ", "スライドが作れない", "動かない" で発動。
---

# slide-setup — 使う準備をする

**ユーザーとのやり取りは必ず日本語で行う。**

Slide Kit が動く状態を作り、結果を `~/.slide-kit-ready` に記録する。

## このスキルの立ち位置

- **通常は初回に1度だけ**、slide-plan / slide-make から自動で呼ばれる。**利用者は存在を知らなくてよい**
- 明示的に呼ばれるのは「**動かないとき**」。そのときは診断ツールとして働く
- **できるだけ自動で直す。** 利用者に手順を読ませない。詰まったところだけ、日本語で「何をすればいいか」を1つだけ伝える

## 実行の原則

- **黙って進める。** 各項目の途中経過を逐一報告しない。最後にまとめて1回報告する
- **失敗しても止まらない。** 全項目を試してから、まとめて結果を出す（1つコケたら全部止まる、が一番つらい）
- 30秒以上かかりそうな処理（フォントDL・Playwright導入）は、始める前に一言添える

## Codex で動かす場合の注意（重要）

**Codex のサンドボックスは既定でネットワークを遮断する。** このスキルは
フォント（56MB）と Playwright（Chromium）をダウンロードするので、**そのままだと黙って失敗する。**

対処:

1. ダウンロードを伴う処理の前に、**ネットワークアクセスの承認を明示的に求める**
2. 承認が得られない/失敗する場合は、利用者にこう伝える:

   > フォントのダウンロードにネットワーク接続が必要です。許可をお願いします。
   > 許可できない場合は、下のURLから手動でダウンロードして、
   > フォントファイルをダブルクリックでインストールしてください。
   > https://github.com/yamatoiizuka/gen-interface-jp/releases/tag/v0.8.0

3. ファイル書き込みはワークスペース内に限られる。`~/Library/Fonts` や
   `%LOCALAPPDATA%` への書き込みが拒否される場合は、上記の手動導入に切り替える

**Claude Code ではこの制約はない。** Codex のときだけ気にする。

なお `codex plugin add` によるスキル導入自体は問題なく動く（実機検証済み）。
制約がかかるのは**スキルが実行するスクリプト**の方。

## チェック項目

### 1. Node.js

```bash
node -v
```

無ければ案内する（Claude Code 自体が Node で動いていることが多いので、通常はある）。
v18以上が必要。

### 2. PPTX組み立ての依存（pptxgenjs）

```bash
cd <plugin>/skills/slide-make/scripts && npm ci
```

**このキットは自前で `node_modules` を持つ**（他のスキルから借りない）。
初回は数十秒かかる。`node_modules` はリポジトリに入っていないので、各自の環境で必ず1度必要。

`npm install` ではなく **`npm ci`** を使う。`package-lock.json` に書かれた
バージョンとハッシュのとおりに入るので、**全員が同じものを使う**状態になる。
`npm install` は解決をやり直すため、上流が差し替わったものをそのまま拾ってしまう。
（`npm ci` が使えない古い npm の場合だけ `npm install` でよい）

### 3. Python 3

```bash
python3 --version    # Windows は py --version または python --version
```

タイプB（編集できるスライド）の抽出とPPTX修正に必要。

**Windowsで無い場合**は入れる:
```powershell
winget install --id Python.Python.3.12 -e --source winget
```

### 4. Playwright（タイプBのみ）

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

Chromiumのダウンロードで1〜2分かかる。**始める前に一言伝える。**

`pip` が「externally-managed-environment」で拒否する場合は、
`python3 -m pip install --user playwright` か、venvを作って入れる。

### 5. フォント（Gen Interface JP）

**利用者に手作業をさせない。** OSに応じてスクリプトを実行する:

```bash
# macOS / Linux
bash <plugin>/skills/slide-setup/scripts/install_fonts.sh
```
```powershell
# Windows
powershell -ExecutionPolicy Bypass -File <plugin>\skills\slide-setup\scripts\install_fonts.ps1
```

- 管理者権限は不要（ユーザー単位でインストールする）
- 既に入っていればスキップされる（毎回56MBを落とさない）
- 約56MBのダウンロードがあるので、**始める前に一言伝える**

インストール後、実際に入ったか確認する:

```bash
# macOS
ls ~/Library/Fonts/GenInterfaceJP-*.ttf
```
```powershell
# Windows
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Fonts\GenInterfaceJP-*.ttf"
```

なぜこのフォントなのか、ウェイトの落とし穴 → `<plugin>/skills/slide-make/references/fonts.md`

### 6. Codex（タイプAのみ）

```bash
codex --version
```

無ければ:
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"`
- macOS/Linux: `curl -fsSL https://chatgpt.com/codex/install.sh | sh`

Claude Code から呼ぶには**OpenAI公式プラグイン**も要る:
```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
```

認証は `/codex:setup` で確認する。
**画像生成は Free プランでは使えない**（Go/Plus/Pro/Business/Enterprise、またはAPIキーが必要）。

### 7. 画像生成の疎通テスト（**Windowsでは必須**）

**これがこのスキルの主任務。** Windows には未解決の不具合があり、
「入っているのに画像生成だけ動かない」が起きる:

- [Issue #19133](https://github.com/openai/codex/issues/19133) — `image_gen` ツールがセッションに出てこない
- [Issue #28898](https://github.com/openai/codex/issues/28898) — 画像は出るが保存されず、**保存パスも返らない**

タイプAは「生成 → **パス報告** → 回収」で成り立っているので、後者を踏むと工程ごと壊れる。
**あとで20枚生成してから気づくのが最悪**なので、ここで1枚だけ試す。

手順:

1. codexエージェント（`agentType: 'codex:codex-rescue'`）に、
   **「小さな画像を1枚生成し、保存先の絶対パスを報告せよ」**と指示する
2. 報告されたパスが**実在するファイルか**を確認する
3. 判定:
   - パスが返り、ファイルが実在する → `ok`
   - ツールが無い/パスが返らない/ファイルが無い → `ng`

`ng` の場合、利用者にはこう伝える（issue番号を並べない）:

> このパソコンでは画像スライド（タイプA）が動きませんでした。編集できるスライド（タイプB）は使えるので、そちらで作れます。

## 結果を記録する

全項目が終わったら `~/.slide-kit-ready` を書く。**slide-plan / slide-make はこのファイルの有無で初回判定する。**

```yaml
# Slide Kit セットアップ結果
checked_at: 2026-07-17T11:40:00+09:00
os: darwin            # darwin | win32 | linux
node: v26.3.1
python: 3.12.4
playwright: ok        # ok | ng | skipped
fonts: ok             # ok | ng
codex: ok             # ok | ng | absent
image_gen: ok         # ok | ng | untested   ← タイプAの可否はこれで判断する
type_a: available     # available | unavailable
type_b: available     # available | unavailable
```

`image_gen` が `ok` 以外なら `type_a: unavailable` にする。
slide-make はこれを読んで、タイプAを選ばれたときに先回りして止める。

## 最後の報告（利用者向け）

**技術用語を並べない。** できること/できないことだけを伝える:

> 準備ができました。
>
> - **編集できるスライド**（あとで文字を直せる）: 使えます
> - **画像スライド**（見た目重視）: 使えます
>
> 「この原稿からスライド構成を作って」と話しかけてください。

`type_a: unavailable` の場合:

> 準備ができました。
>
> - **編集できるスライド**（あとで文字を直せる）: 使えます
> - **画像スライド**（見た目重視）: **このパソコンでは使えませんでした**
>
> 編集できるスライドで作れます。「この原稿からスライド構成を作って」と話しかけてください。
