#!/usr/bin/env python3
"""タイプC: deck_structure.json → slides_c/NNN.html (背景=images_c/bg_NN.png, 文字=HTMLテキスト)

使い方: このファイルを成果物ディレクトリにコピーし、TWEAK を案件に合わせて書き換えて実行する。
TWEAK の例は type-c-hybrid.md を参照。フォント・タイポは案件のスタイルに合わせて TPL を調整してよい。
"""
import json, pathlib

BASE = pathlib.Path(__file__).parent
deck = json.load(open(BASE / "deck_structure.json"))

# スライド別の微調整（見て直す用）。既定: 左テキスト・幅560・top150
# title: 改行位置を明示指定（不自然な自動折返しの回避）
TWEAK = {
    # 例:
    # 1:  {"top": 150, "width": 700, "title_size": 66, "title": "長いタイトルは、<br>改行位置を明示"},
    # 5:  {"body_mt": 26},                # 背景の装飾と本文の衝突を逃がす
    # 14: {"width": 470, "body": "...", "extra": '<div style="position:absolute;...">1万人</div>'},
}

TPL = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gen-interface-jp@0.8.0/cdn/400.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gen-interface-jp@0.8.0/cdn/500.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gen-interface-jp@0.8.0/cdn/700.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gen-interface-jp@0.8.0/cdn/display-600.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gen-interface-jp@0.8.0/cdn/display-700.css" />
<style>
body{{margin:0}}
.slide{{
  width:1280px;height:720px;position:relative;overflow:hidden;
  background-color:#F2F2F2;
  background-image:url("../images_c/bg_{nn}.png");
  background-size:cover;background-position:center;
  font-family:"Gen Interface JP",sans-serif;
  color:#121212;
}}
.txt{{position:absolute;left:72px;top:{top}px;width:{width}px;display:flex;flex-direction:column;gap:24px}}
.furi{{font-weight:500;font-size:18px;line-height:1.6;color:#4F4F4F;margin:0 0 -6px}}
.title{{font-family:"Gen Interface JP Display",sans-serif;font-weight:700;font-size:{title_size}px;line-height:1.32;letter-spacing:.01em;margin:0}}
.lead{{font-weight:700;font-size:25px;line-height:1.5;margin:0}}
.body{{font-weight:400;font-size:16.5px;line-height:1.9;color:#4F4F4F;margin:0;margin-top:{body_mt}px}}
.meta{{position:absolute;left:72px;bottom:46px;font-size:12px;color:#8A8A8A;letter-spacing:.18em}}
</style>
</head>
<body>
<div class="slide">
  <div class="txt">
    {furi_html}<h1 class="title">{title}</h1>
    <p class="lead">{lead}</p>
    <p class="body">{body}</p>
  </div>
  <div class="meta">{caption}</div>
  {extra}
</div>
</body>
</html>
"""

out = BASE / "slides_c"
out.mkdir(exist_ok=True)
for s in deck["slides"]:
    n = s["n"]
    t = TWEAK.get(n, {})
    html = TPL.format(
        nn=f"{n:02d}",
        top=t.get("top", 150),
        width=t.get("width", 640),
        title_size=t.get("title_size", 62),
        body_mt=t.get("body_mt", 0),
        title=t.get("title", s["title"]),
        furi_html=(f'<p class="furi">{s["furi"]}</p>' if s.get("furi") else ""),
        lead=s["lead_B"],
        body=t.get("body", s["body_B"].replace("\\n", "<br>").replace("\n", "<br>")),
        caption=s.get("caption", ""),
        extra=t.get("extra", ""),
    )
    (out / f"{n:03d}.html").write_text(html)
    print(f"{n:03d}.html")
print("done")
