# Session Handover - 2026-07-17 13:43

## Summary

社外の方（IT得意でない・Mac/Windows混在・全員Codex課金あり）に渡すスライド作成キット **Slide Kit** をゼロから構築し、プライベートリポジトリに push した。既存の運用スキル（deck-design / deck-render / slide-build / slide-design-core）を配布物として再編し、Claude Code / Codex の両対応まで完了。

## What We Accomplished

- **リポジトリ構築** `~/product/slide-kit/` → https://github.com/tamkai/slide-kit （private）。コミット3本
- **スキル4本を新設**（既存スキルの再編＋新規）
  - `slide-ask` 第0段階。原稿ブリーフ作成（新規）
  - `slide-plan` 第1段階。構成JSON（旧 deck-design ＋ slide-design-core の哲学層を統合）
  - `slide-make` 第2段階。A-1/A-2/B の3タイプ（旧 deck-render ＋ slide-build を統合）
  - `slide-setup` 環境診断・フォント自動導入（新規）
- **配布物としての毒抜き** — 詳細は後述。ブランド資産・案件名・実在受講者名・絶対パスを全除去
- **フォントを Gen Interface JP に統一** — `fsType=0` で PPTX 埋め込み可・Mac/Win両対応。従来のヒラギノ割当が不要になった
- **タイプA-2（読み物インフォグラフィック）を新設** — ユーザー提供のプロンプトから採用。画像上部18%を白の安全領域にし、そこに編集可能なタイトル/リード文を重ねる
- **Claude Code / Codex 両対応** — 同一 SKILL.md のまま、マニフェストを二枚重ねで実現。実機で全経路検証
- **説明資料** `docs/quickstart.html` — ブラウザで読む1ページ。ライト/ダーク両対応

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| 命名を `slide-plan` / `slide-make` に | Render/Build は中の人の言葉で伝わらない。plan→make なら**順番と役割が名前だけで伝わり**、説明が一行減る（ユーザー選択） |
| 呪文は2つに固定（ask/setup は自動呼び出し） | 覚えることを最小化。setup は「詰まったら唱えるお守り」、ask は slide-plan が素材不足を検知して自動起動 |
| タイプの2択を最初に、A-1/A-2 は後で聞く | 最初に3択を出すと選べない。「あとで文字を直すか」だけで決まる形にした |
| フォントは Gen Interface JP、游ゴシックは不採用 | 当初はMac/Win共通の游ゴシックを検討したが、ユーザー提案の Gen Interface JP が `fsType=0`（埋め込み無制限）で**第三者に配っても崩れない**。上位互換 |
| フォントは同梱せず slide-setup が自動DL | OFLで再配布可だが99MB。リポジトリを軽く保ち、利用者の手作業はゼロにする |
| ブランドテーマを配布物から除去 | 社外の人に渡すと**相手がAFFLATUSロゴ入りスライドを量産できてしまう**。ユーザーも同意 |
| A-2 の「情報密度は高くビジーでも可」を採用 | slide-plan の「1スライド1メッセージ」と衝突して見えるが、**Document↔Workshop 連続軸の Document 端**として整理。矛盾ではなくモード |
| 1リポジトリで Claude/Codex 両対応 | 「伝えている相手の半分がCodexのみ」。マニフェストの置き場所だけが違うので、両方置けば済む |
| A-2 のフォントは Yu Gothic UI でなく Gen Interface JP | 元プロンプトの指定より、埋め込み可・Mac/Win両対応の方が上位。Semibold指定は `Gen Interface JP SemiBold` に解決される |

## Current State

- ブランチ `main`、**未コミットの変更なし**、push 済み（`e760736`）
- リポジトリは **private**。公開化するかは未決（中身に秘密はもう無い）
- **タイプBは実際に動くことを確認済み**。タイプAは codex で一度も実生成していない（**未知数**）
- Codex 検証で使ったローカル登録は**クリーンアップ済み**（`codex plugin marketplace list` に残留なし）
- 元のグローバルスキル（deck-design 等）は `~/.claude/skills/` にそのまま存在。**slide-kit とは独立**

## Key Files Modified

- `skills/*/SKILL.md` — 4スキルの本体
- `skills/slide-make/scripts/fonts.js` — **ウェイト→フォント名マッピング。最重要**
- `skills/slide-make/scripts/extract_html.py` — HTML→フラット背景PNG＋テキスト構造（引数駆動に再構築）
- `skills/slide-make/scripts/build_pptx_from_html.js` — 抽出→編集可能PPTX
- `skills/slide-make/scripts/build_pptx_from_images.js` — 画像→PPTX。`--readable` でA-2のテキスト重ね
- `skills/slide-make/styles/infographic-readable.txt` — A-2用。上部18%安全領域の指示入り
- `skills/slide-make/themes/standard/` — 中立テーマ（新規作成）
- `skills/slide-setup/scripts/install_fonts.{sh,ps1}` — フォント自動導入
- `docs/quickstart.html` — 説明資料
- `.codex-plugin/plugin.json` / `.agents/plugins/marketplace.json` — Codex用マニフェスト

## Lessons Learned

### 効いたこと

- **E2Eを実際に回したのが決定的だった。** 構文チェックだけでは3つのバグを全部見逃していた
- **実ファイルをダウンロードして fontTools で検証**したから、4スタイルリンク問題に気づけた。ドキュメントだけ読んでいたら踏んでいた
- **`fc-list` でOSレベルの裏取り**までやったので、マッピングの正しさが実証できた
- Codexは**実機で `codex exec` して自動発動を確認**できた。これがなければ「たぶん動く」で終わっていた

### 踏んだ罠（次回避ける）

- **`runs` の出力し忘れ**。メモ `html-to-pptx-high-fidelity` に「実際にハマった」と書いてあるのに**同じ罠を踏んだ**。抽出スクリプトを書いたら必ず `runs` が出ているか実データで確認する
- **zsh は `$FILES` を単語分割しない**。`for f in $FILES` が黙って1ファイル名として扱われ、置換が全く実行されていなかった（無害だったが気づきにくい）。`tr '\n' '\0' | xargs -0` を使う
- 移植元スクリプトが**`~/.claude/...` の絶対パス直書き**＋**他スキルの node_modules 借用**だった。配布物では必ず切る
- 構成JSONは `{deck_title, slides:[...]}` の**ラッパー形式**。素の配列ではない
- `themes/afflatus` の117MBは**ほぼ node_modules**（しかもMac専用sharpバイナリ）。コピー前にサイズを測る

### 判明した外部事実

- **Codexのサンドボックスは既定でネットワーク遮断**。フォント56MB DLが黙って失敗する。承認が要る
- Codexは未知のfrontmatterフィールドを**拒否せず無視する**ので SKILL.md は無改造で共用できる
- Codexでのスキル名は `slide-kit:slide-plan` と名前空間化される
- 画像生成は**通常の3〜5倍速く使用量を消費**する（公式明記）。「代表3枚から」は財布の話でもある

## Next Steps

- [ ] **Windows実機検証**（最大の残リスク）
  - [ ] `install_fonts.ps1` — レジストリ登録（HKCU）が管理者権限なしで通るか
  - [ ] Codex の画像生成が動くか → [#19133](https://github.com/openai/codex/issues/19133)（image_gen が露出しない）/ [#28898](https://github.com/openai/codex/issues/28898)（保存パスが返らない）。後者はタイプAの工程を丸ごと壊す
  - [ ] 駄目なら「Windowsの方はまずタイプBで」と案内する運用に逃げる（BはOS非依存）
- [ ] **タイプAを codex で実生成する**（3枚だけ。使用量注意）。一度も通していない
- [ ] **別セッションで通し試用**する（このセッションは旧スキルと同居していて発動判定が混ざる）
  - 確認の主眼は**「構成JSONを出して止まるか」**。二段階の生命線
- [ ] リポジトリを公開にするか決める（privateだと相手をコラボレーターに招待する手間が人数分かかる）
- [ ] `standard` テーマで実際にスライドを作ってみる（作ったが未使用）

## Blockers / Open Questions

- **Windows実機がない**（ユーザーに確認したが未回答）。渡す当日に相手のマシンで一緒に確認する案あり
- **プライベートリポの配布性** — Codexからのprivate取得は成功したが、それは自分の認証情報だから。相手はコラボレーター招待＋git認証が必要。公開リポにすれば消える問題
- **スタイルギャラリーのライセンス** — [NotebookLM Slide Style Library](https://notebooklm-slide-gallery.shirakippt.chatgpt.site/)（KUMIKO SHIRAKI氏）にライセンス表記がない。同梱せず各自コピー方針にしたが、商用案件で使うなら制作者確認が要る
- **Gen Interface JP が v1.0 前**（v0.8.0）。メトリクス変更で過去デッキがズレる可能性 → バージョン固定で運用中

## Memory & Decisions Written This Session

- auto-memory: `gen-interface-jp-style-link.md`（新規・reference）— 4スタイルリンク問題の対応表
- auto-memory: `slide-kit-distribution.md`（新規・project）— キットの設計方針と現在地
- auto-memory: `html-to-pptx-high-fidelity.md`（更新）— ヒラギノ割当の記述を除去
- MEMORY.md: 上記2件を索引に追加
- Decisions/: なし（今回の判断はプロジェクト内に閉じるため auto-memory に寄せた）

## User Preferences Noted

- **命名は「伝わるか」で決める。** Render/Build のような内輪の語彙を嫌う。plan/make のような平易な動詞を好む
- **勝手に判断して先に進めるより、判断の理由を示して確認を取る形を評価する**（ブランド除去の報告に「ナイスです」）
- **上位の手段は黙って落とさず、分岐点で提示する**（既存メモ `surface-upper-tier-options` と一致）
- ウェブで見つけた良いプロンプトを持ち込む。**採否と理由を明示すると噛み合う**
- Tier 2（ファイル作成・commit・push）は都度確認を求める。今回は明示承認を得てから実行した
