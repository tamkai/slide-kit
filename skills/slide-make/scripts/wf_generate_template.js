// slide-make 画像生成ワークフロー テンプレート（タイプA / タイプB 両対応）
// 使い方: このファイルを成果物プロジェクトにコピーし、下の CONFIG を埋めて Workflow で実行する。
// 各 codex エージェントは画像を生成し「n→実パス」を報告する（cpはしない）。
// 戻り値の mapping を scripts/collect_images.py に渡して配置＋重複チェックする。

export const meta = {
  name: 'slide-make-generate',
  description: 'deck_structure.json + スタイル定義から画像スライドを並列生成（codex image_gen）',
  phases: [{ title: 'Generate', detail: 'codexエージェントが各スライドを並列生成し実パス報告' }],
}

// ===== CONFIG（ここを埋める）=====
const DIR = '/ABS/PATH/TO/<project>/<deck-name>'   // 成果物ディレクトリ（codexが書ける場所）
const STYLE = `${DIR}/styles/isometric.txt`          // 使うスタイル定義
const DECK = `${DIR}/deck_structure.json`
const TYPE = 'A'                                      // 'A'=文字少図主役 / 'B'=上下分割読ませ版
const IMG_DIR = TYPE === 'B' ? `${DIR}/images_B` : `${DIR}/images`
const TARGETS = Array.from({ length: 20 }, (_, i) => i + 1)  // 生成対象 n（欠落再生成時は該当番号だけに）
const SAMPLES = [1, 3, 13]                            // 世界観のお手本に使う既完成スライド番号（無ければ[]）
// =================================

const sampleRefs = SAMPLES.map(n => `${IMG_DIR}/slide_${String(n).padStart(2,'0')}.png`).join('\n- ')

function promptFor(n) {
  const layout = TYPE === 'B'
    ? `【レイアウト＝上下2分割（厳守）】
- 上段(約45%)=テキスト主役: 地よりわずかに明るい/縁取りのある横長パネル(角丸・軽い影)の上に文字を載せる(浮かせない)。上から: 小さめタイトル(title) → 大きい結論ひとこと(lead_B) → 小さめ本文2〜3行(body_B)。タイトル<結論<本文 のサイズ階層を明確に。
- 下段(約55%)=横長アイソメ図: 16:9横幅いっぱいの横長ジオラマ(visual_brief)。`
    : `【レイアウト＝講演用（Bと同等の情報量）】テキストゾーン(title特大 + lead_B結論ひとこと + body_B小さめ本文2〜3行 + 小さなキャプション)と図(visual_brief)のゾーンを非対称バランスで。title<lead_B<body_Bのサイズ階層を明確に。たっぷり余白。クライマックス等で文字少・図主役にする枚は、呼び出し側で明示指定した時のみtitleだけに絞る。`

  const textFields = TYPE === 'B'
    ? `title / lead_B / body_B / visual_brief`
    : `title / lead_B / body_B / visual_brief`

  return `あなたはセミナースライドの画像を1枚生成するデザイナー。Codex組み込みの image_gen で描く(ImageMagick等にフォールバックしない)。${TARGETS.length}枚組デッキの1枚で、全枚の世界観を厳密に揃える。

【スタイル定義(厳守)】${STYLE} を読む。配色・質感・トーン・16:9・余白ルールを厳守。横長・ワイド・16:9・landscape widescreen と方向語を重ねる。
${SAMPLES.length ? `【お手本(世界観の基準)】\n- ${sampleRefs}\n同じ質感・配色・体裁に揃える。ただし内容は下記スライドのもので、隣のスライドの絵をコピーしない(取り違え厳禁)。` : ''}
【構成】${DECK} の "n": ${n} を使う。使うフィールド: ${textFields}。labels は画作りのヒント(何を描くか)として使い、**文字としては焼かない**。speaker_noteは画像に入れない。
${layout}
指定した文字以外の文字・段落は描かない。ONE focal idea・余白優先。

【保存】image_genで生成するだけ(cpしない)。生成後、codexが吐いた実ファイルの【絶対パス】を必ず明示報告する。
最終出力は「slide ${n} / 生成された絶対パス / 寸法」だけ。`
}

phase('Generate')
const results = await parallel(TARGETS.map(n => () =>
  agent(promptFor(n), { label: `slide:${n}`, phase: 'Generate', agentType: 'codex:codex-rescue' })
    .then(text => ({ n, text }))))

// 戻り値: 各エージェントの報告テキスト。ここから「n→実パス」を抽出して mapping.json を作り、
// collect_images.py で IMG_DIR に配置＋重複チェックする。
return { type: TYPE, imgDir: IMG_DIR, results: results.filter(Boolean) }
