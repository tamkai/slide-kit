# papercraft テーマの背景画像

この4枚は**自前で生成した画像**。第三者の素材ではない。

| ファイル | 役割 |
|---|---|
| `bg_01_cover.jpg` | 上下帯＋左下に葉 / 中央が広く空く。表紙・章扉・キービジュアル |
| `bg_03_content_corners.jpg` | 四隅に極小装飾 / 中央が最大に空く。本文・3軸・グリッド・比較 |
| `bg_04_wrap.jpg` | 下部に帯 / 上80%が空く。章まとめ・巻末 |
| `bg_05_minimal.jpg` | ほぼ無地の紙テクスチャ。キーメッセージ・対句 |

## 出所

`~/.claude/skills/slide-build/themes/papercraft/` で **jinn-image** を使って生成したもの。
生成手順とプロンプトは、そちらの `theme.md` と `references/background-generation.md` にある。

共通のプロンプト方針:

> papercraft / cut-paper texture / cream・sage・gold・terracotta

いずれも 1600×900、JPEG最適化済み。**再配布に制約のある素材は含まれていない。**

## 作り直すとき

このリポジトリでは作らない。`slide-build` 側で生成してからここへコピーする。
中央を広く空け、装飾を四隅・上下に寄せること（中央は読むための余白）。
