# 図解の型を選ぶ

図解は「見た目の種類」ではなく「**伝えたい関係の種類**」から選ぶ。
タイプD（図解スライド）を作るときに使う。ほかのタイプでも型を考える役に立つ。

## 図解にするかを決める

全スライドを図解にしない。**1枚の主張に関係の構造があるとき**だけ図解にする。
扉、問いかけ、物語の場面は、図にしない方が強いことが多い。

## 関係から型を選ぶ

候補を**2つ以上**比べ、選んだ理由を `diagram.why` に書く。

| 見せたい関係 | 第一候補 | 比べる候補 | 分かれ目 | 分類 |
|---|---|---|---|---|
| 共通部分に価値がある | ベン図 | 左右比較 | 重なりが主張なら、ベン図 | image |
| 2つの違い | 左右比較 | 比較表 | 比べる軸が多ければ、比較表 | image |
| 変化の前後 | ビフォーアフター | 左右比較 | 時間の変化があるなら、前後 | image |
| 順番に進む | 直線フロー | ステップ図 | 上達や深化なら、ステップ図 | image |
| 終わりなく繰り返す | 循環図 | フロー | 最後が最初に戻るなら、循環 | image |
| 条件で分かれる | 分岐フロー | 意思決定ツリー | 分岐が多ければ、枚数を分ける | strict |
| 誰が何をするか | スイムレーン | フロー | 担当が主題なら、スイムレーン | strict |
| 中心から広がる | マインドマップ | ハブとスポーク | 中心とのやり取りなら、ハブ | image |
| 土台の上に積み重なる | ピラミッド | レイヤー図 | 優劣を含めたくなければ、レイヤー | image |
| 全員が同じ傾きの上にいる | 勾配図（坂の比喩） | ピラミッド | 段に分かれないなら、坂 | image |
| 内側に含まれる | 入れ子 | 同心円 | 中心との距離なら、同心円 | image |
| 要素に分解する | ロジックツリー | ピラミッド | 枝が多ければ、枚数を分ける | strict |
| 2つの軸で位置づける | 2軸マップ | 比較表 | 定性の位置づけなら、2軸 | strict |
| 原因が結果を生む | 因果ループ | なぜなぜ、魚の骨 | 循環するなら、因果ループ | strict |
| いつ何が起きるか | タイムライン | ロードマップ | 計画なら、ロードマップ | strict |
| 関係者のつながり | 相関図 | ネットワーク図 | 関係に名前があるなら、相関図 | strict |
| 量を比べる、割合、推移 | 棒、円、折れ線 | | 数値が主張なら、タイプBで作る | exact |

手元に図解100選（`$SLIDE_KIT_PACKS/diagrams/diagram_100_knowledge_base.md`、既定は `~/product/slide-kit-packs/`）があれば、「V. 型の選び方」から読む。全部は読まない。

**優先順位:** 伝えたいメッセージ ＞ 関係の意味 ＞ データの形 ＞ 画風 ＞ 見た目の派手さ。
1枚に複数の関係が混ざるなら、詰めずに枚数を分ける。

## `precision`（分類）

| 値 | 意味 | 扱い |
|---|---|---|
| `image` | 言葉の指示で描ける概念の図 | タイプDで作る |
| `strict` | つながりや要素が多い図 | タイプDで作れるが、要素を減らし、検品を厳しくする。実証は分岐フローのみ |
| `exact` | 数値、座標、比率が主張の図 | 言葉の指示では正確に描けない。タイプBで作る |

実証済みの型は、ベン図、直線フロー、循環図、マインドマップ、ピラミッド、左右比較、勾配図、分岐フローの8つ（2026-11-06。それぞれ少数の例での確認）。

## 構成JSONに書く

スライドに次の欄を足す。

```json
{
  "n": 4,
  "title": "人とAI、それぞれの強みの重なりが新しい価値を生む。",
  "visual_brief": "The person sits above the left set and the AI companion above the right set.",
  "diagram": {
    "type": "ベン図",
    "why": "共通部分に価値があるという主張なので、左右比較ではなくベン図",
    "alternatives": ["左右比較"],
    "contract": "EXACTLY TWO large overlapping sets and one shared overlap. No third set. Sizes are not data.",
    "precision": "image"
  },
  "on_slide": [
    {"where": "タイトル（2行）", "text": "人とAI、それぞれの強みの重なりが / 新しい価値を生む。"},
    {"where": "左の集合の見出し", "text": "人の強み"},
    {"where": "重なりの見出し", "text": "共創価値"},
    {"where": "右の集合の見出し", "text": "AIの強み"}
  ]
}
```

- **`contract`** は絶対に変えない構造を英語で書く。数、向き、つながり、「増やさない」こと
- **`on_slide`** は画像に載せる文字の全リスト。`/` は改行。ここに無い文字は描かれない。`lead_B` や `body_B` を載せたいときも、ここに書く
- 登場人物はデッキ全体の `cast` に書く。画風には書かない

## 構造の書き方の例

| 型 | contract の例 |
|---|---|
| ベン図 | EXACTLY TWO overlapping sets and one shared overlap. No third set. Sizes are not data. |
| 直線フロー | EXACTLY FOUR steps connected left to right. No fifth step, no return arrow. Keep the numbers. |
| 循環図 | EXACTLY FOUR stages in ONE CLOCKWISE closed loop. EXACTLY FOUR arrows, all clockwise. The center is a label and not a fifth stage. |
| マインドマップ | ONE central node and EXACTLY SEVEN branches, one level deep. No links between branches. No branch implies rank or order. |
| ピラミッド | EXACTLY FOUR stacked layers. The bottom is the foundation. Layer sizes are not data. |
| 左右比較 | EXACTLY TWO models side by side, using the same roles on both sides. The right model is larger. No third model. |
| 勾配図 | EXACTLY ONE continuous slope with ONE summit. Everyone stands on this slope and nobody stands off it. |
| 分岐フロー | EXACTLY ONE start, ONE decision and TWO outcomes, connected by one-way arrows. No loop, no third branch. State which label leads to which outcome. |

## 事実を守る

分からない因果、割合、関係の強さを勝手に決めない。足りないものは本人に聞く。仮の例は仮の例と明記する。
