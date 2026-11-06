"""
typed_build_prompts.py — タイプD: 構成JSONと画風パックから生成プロンプト一式を作る

使い方:
    # デッキ（一覧画像と清書）
    python3 typed_build_prompts.py --deck deck_structure.json --style <画風> --out type_d [--anchor N] [--with-what]

    # 新しい画風の見本（固定内容を2x2で描く1枚）
    python3 typed_build_prompts.py --calibration --style <画風> --out <出力先> [--with-what]

<画風> に渡せるもの:
    - 画風パックのフォルダ（pack.json がある）
    - パックのID（$SLIDE_KIT_PACKS/styles/<ID>。既定は ~/product/slide-kit-packs）
    - 既存の styles/*.txt（切り分け前の文章として扱い、警告を出す）

出力:
    plan.tsv / 各 *.prompt.txt / meta.json / text_checklist.md
    この後は typed_render.py で生成する。
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_FILE = os.path.join(HERE, "..", "references", "type-d-calibration.txt")
BOARD_SIZE = "3840x2160"
SHEET_SIZE = "2560x1440"
SLIDE_SIZE = "2560x1440"   # 16:9 ちょうどで、両辺が16の倍数
PANELS_PER_BOARD = 9
TITLE_MARKS = ("タイトル", "title", "Title")


def packs_root():
    return os.path.expanduser(os.environ.get("SLIDE_KIT_PACKS", "~/product/slide-kit-packs"))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_style(spec, with_what):
    """画風を読み込む。how=描き方、what=描くもの。生成には既定で how だけを渡す。"""
    path = os.path.expanduser(spec)
    if os.path.isfile(path):
        text = read(path)
        marker = "## Content to visualize"
        if marker in text:
            text = text[: text.index(marker)]
        print(f"[注意] {spec} は切り分け前の文章です。人物や小道具の指定が入っていると内容を押しのけます。"
              "references/type-d-style-intake.md の手順でパックにしてください。", file=sys.stderr)
        return {"how": text.strip(), "what": "", "parts": [], "refs": [], "ref_note": "", "name": spec}

    pack_dir = path if os.path.isdir(path) else os.path.join(packs_root(), "styles", spec)
    pack_file = os.path.join(pack_dir, "pack.json")
    if not os.path.isfile(pack_file):
        sys.exit(f"画風が見つかりません: {spec}")
    pack = json.loads(read(pack_file))
    how = read(os.path.join(pack_dir, pack.get("how_file", "how.txt"))).strip()
    what_path = os.path.join(pack_dir, pack.get("what_file", "what.txt"))
    what = read(what_path).strip() if os.path.isfile(what_path) else ""
    return {
        "how": how,
        "what": what if with_what else "",
        "parts": pack.get("parts", []),
        "refs": [os.path.join(pack_dir, r) for r in pack.get("refs", [])],
        "ref_note": pack.get("ref_note", ""),
        "name": pack.get("name", spec),
    }


def style_block(style):
    lines = ["VISUAL STYLE (how to draw). Apply it to the whole image including the diagrams, not only to characters:",
             style["how"]]
    if style["parts"]:
        lines += ["", "HOW THIS STYLE DRAWS DIAGRAM PARTS:"]
        lines += [f"- {p['en']}" for p in style["parts"]]
    if style["what"]:
        lines += ["", "RECURRING SUBJECT MATTER OF THIS STYLE:", style["what"]]
    return "\n".join(lines)


def reference_note(style):
    if not style["refs"]:
        return ""
    note = ("REFERENCE IMAGES: the attached images define the visual style only: material, light, color and "
            "emptiness. Do not copy their objects or compositions.")
    if style["ref_note"]:
        note += " " + style["ref_note"]
    return note


def cast_block(deck):
    cast = deck.get("cast")
    if cast:
        return f"RECURRING CAST of this deck: {cast}"
    return "PEOPLE are optional. Include them only when they explain an action or a relationship."


def text_items(slide):
    """スライドに載せる文字の全リスト。on_slide が正本で、title と furi を補う。"""
    items = [dict(i) for i in slide.get("on_slide", [])]
    has_title = any(any(mark in i.get("where", "") for mark in TITLE_MARKS) for i in items)
    if not has_title and slide.get("title"):
        items.insert(0, {"where": "タイトル", "text": slide["title"]})
    if slide.get("furi"):
        items.insert(0, {"where": "タイトルの上の小さな1文", "text": slide["furi"]})
    return items


def text_lines(items):
    return [f"- {i['where']}: {i['text']}" for i in items]


TEXT_RULE = ("Render every Japanese string EXACTLY, character for character. Accuracy of Japanese is the top "
             "priority. A slash in a string marks a line break. These strings are required content and they "
             "override any rule in the style about limiting text. Do not add, translate, abbreviate or invent "
             "any other text. No page numbers, no logos, no watermarks.")


def slide_prompt(slide, deck, style, has_anchor):
    diagram = slide.get("diagram") or {}
    refs = [
        "REFERENCE IMAGES:",
        "- The first attached image is the approved thumbnail of this exact slide. Keep its composition, cast "
        "and diagram structure. Redraw it as the final version: cleaner edges, richer texture, generous margins. "
        "The thumbnail may contain wrong characters, so the text list below is the only source of truth for text.",
    ]
    if has_anchor:
        refs.append("- The second attached image is a finished slide from the same deck. Match its finish: "
                    "ground, texture, color, edge quality and typography. Do not copy its diagram, text or layout.")
    parts = [
        "Create ONE SINGLE finished 16:9 presentation slide. This is one complete slide, NOT a grid, NOT a "
        "storyboard, NOT a montage. Illustration, diagram and Japanese typography are drawn together as one image.",
        "\n".join(refs),
    ]
    if diagram.get("contract"):
        parts.append(f"DIAGRAM CONTRACT, non-negotiable: {diagram['contract']}")
    if slide.get("visual_brief"):
        parts.append(f"WHAT TO SHOW: {slide['visual_brief']}")
    parts.append(cast_block(deck))
    parts.append("ALL TEXT. " + TEXT_RULE + "\n" + "\n".join(text_lines(text_items(slide))))
    parts.append(style_block(style))
    return "\n\n".join(parts) + "\n"


def board_prompt(slides, deck, style, cols, rows):
    head = (f"Create ONE single 16:9 image: a finished Japanese presentation deck shown as a precise {cols}x{rows} "
            f"grid of {len(slides)} slides ({rows} rows, {cols} columns). Every panel is exactly 16:9 and the same "
            "size, separated by thin even gutters. Leave any unused panel empty. All slides were made by one art "
            "director, in one hand, as one coherent deck. Illustration, diagram and Japanese typography are drawn "
            "together as one integrated image in each panel. The diagrams belong to the world of the style: they "
            "are not stock shapes with art pasted beside them.")
    parts = [head]
    note = reference_note(style)
    if note:
        parts.append(note)
    parts.append(style_block(style))
    parts.append(cast_block(deck))
    parts.append("TEXT RULES: " + TEXT_RULE)
    body = ["THE SLIDES (left to right, top to bottom):"]
    for i, slide in enumerate(slides, 1):
        lines = [f"Slide {i}."]
        if slide.get("visual_brief"):
            lines.append(slide["visual_brief"])
        contract = (slide.get("diagram") or {}).get("contract")
        if contract:
            lines.append(f"Diagram contract: {contract}")
        lines.append("Text: " + " | ".join(f"{t['where']}: 「{t['text']}」" for t in text_items(slide)))
        body.append(" ".join(lines))
    parts.append("\n\n".join(body))
    parts.append("Composition: vary the slides. Avoid one repeated card layout. Each slide has one clear focal point "
                 "and generous empty space.")
    return "\n\n".join(parts) + "\n"


def calibration_prompt(style):
    head = ("Create ONE single 16:9 image: a style calibration sheet for a Japanese presentation. It shows FOUR "
            "finished slides in a precise 2x2 grid. Every panel is exactly 16:9 and the same size, separated by "
            "thin even gutters. All four come from one deck, drawn by one hand. Illustration, diagram and Japanese "
            "typography are drawn together in each panel.")
    parts = [head]
    note = reference_note(style)
    if note:
        parts.append(note)
    parts.append(style_block(style))
    parts.append(read(CALIBRATION_FILE).strip())
    return "\n\n".join(parts) + "\n"


def write_plan(out_dir, rows):
    with open(os.path.join(out_dir, "plan.tsv"), "w", encoding="utf-8") as f:
        for row in rows:
            f.write("\t".join(row) + "\n")


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def checklist(slides):
    lines = ["# 検品表（生成画像を開いて1項目ずつ照合する）", ""]
    for slide in slides:
        diagram = slide.get("diagram") or {}
        lines.append(f"## スライド {slide['n']} {slide.get('title', '')}")
        if diagram.get("precision") == "exact":
            lines.append("- [ ] **正確な数値が要る図。形と数値を元データと照合する（生成では保証されない）**")
        if diagram.get("contract"):
            lines.append(f"- [ ] 構造: {diagram['contract']}")
        for item in text_items(slide):
            lines.append(f"- [ ] 文字 {item['where']}: {item['text']}")
        lines.append("")
    return "\n".join(lines)


def build_calibration(args, style):
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    prompt_path = os.path.join(out_dir, "calibration.prompt.txt")
    write_text(prompt_path, calibration_prompt(style))
    write_plan(out_dir, [["calibration", SHEET_SIZE, prompt_path, os.path.join(out_dir, "calibration.png")] + style["refs"]])
    write_text(os.path.join(out_dir, "meta.json"), json.dumps({"boards": [], "anchor": None}, ensure_ascii=False, indent=2))
    print(f"見本のプロンプトを作りました: {prompt_path}")
    print(f"次: python3 {HERE}/typed_render.py {out_dir} --stage calibration")


def build_deck(args, style):
    deck_raw = json.loads(read(args.deck))
    deck = {"slides": deck_raw} if isinstance(deck_raw, list) else deck_raw
    slides = sorted(deck["slides"], key=lambda s: s["n"])
    out_dir = os.path.abspath(args.out)
    images_dir = os.path.abspath(args.images or os.path.join(out_dir, "..", "images"))
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for slide in slides:
        if (slide.get("diagram") or {}).get("precision") == "exact":
            print(f"[注意] スライド {slide['n']} は正確な数値が要る図です。言葉の指示だけでは正確に描けません。",
                  file=sys.stderr)

    anchor = args.anchor
    if anchor is None:
        anchor = next((s["n"] for s in slides if s.get("diagram")), slides[0]["n"])

    rows, boards = [], []
    position_of = {}
    for b, start in enumerate(range(0, len(slides), PANELS_PER_BOARD), 1):
        chunk = slides[start:start + PANELS_PER_BOARD]
        cols = 2 if len(chunk) <= 4 else 3
        grid_rows = 2 if len(chunk) <= 4 else 3
        for offset, slide in enumerate(chunk):
            position_of[slide["n"]] = start + offset + 1
        name = f"board-{b:02d}"
        prompt_path = os.path.join(out_dir, f"{name}.prompt.txt")
        write_text(prompt_path, board_prompt(chunk, deck, style, cols, grid_rows))
        png = os.path.join(out_dir, f"{name}.png")
        refs = list(style["refs"])
        if b > 1:
            refs.append(os.path.join(out_dir, "board-01.png"))
        size = BOARD_SIZE if cols == 3 else SHEET_SIZE
        rows.append([name, size, prompt_path, png] + refs)
        boards.append({"id": name, "png": png, "cols": cols, "rows": grid_rows, "start": start + 1, "count": len(chunk)})

    panels_dir = os.path.join(out_dir, "panels")
    anchor_png = os.path.join(images_dir, f"slide_{anchor:02d}.png")
    for slide in slides:
        n = slide["n"]
        has_anchor = n != anchor
        prompt_path = os.path.join(out_dir, f"slide-{n:02d}.prompt.txt")
        write_text(prompt_path, slide_prompt(slide, deck, style, has_anchor))
        png = os.path.join(images_dir, f"slide_{n:02d}.png")
        refs = [os.path.join(panels_dir, f"p{position_of[n]:02d}.png")]
        if has_anchor:
            refs.append(anchor_png)
        rows.append([f"slide-{n:02d}", SLIDE_SIZE, prompt_path, png] + refs)

    write_plan(out_dir, rows)
    write_text(os.path.join(out_dir, "text_checklist.md"), checklist(slides))
    write_text(os.path.join(out_dir, "meta.json"),
               json.dumps({"boards": boards, "anchor": anchor, "images_dir": images_dir, "panels_dir": panels_dir},
                          ensure_ascii=False, indent=2))
    count = math.ceil(len(slides) / PANELS_PER_BOARD)
    print(f"スライド {len(slides)} 枚、一覧画像 {count} 枚、基準スライド {anchor}")
    print(f"次: python3 {HERE}/typed_render.py {out_dir} --stage boards")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--deck")
    parser.add_argument("--style", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--images", help="清書の保存先（既定は <out>/../images）")
    parser.add_argument("--anchor", type=int, help="質感の基準にするスライド番号（既定は最初の図解スライド）")
    parser.add_argument("--with-what", action="store_true", help="画風が持つ題材（what.txt）も生成に渡す")
    parser.add_argument("--calibration", action="store_true", help="画風の見本を作る")
    args = parser.parse_args()

    style = load_style(args.style, args.with_what)
    if args.calibration:
        build_calibration(args, style)
    elif args.deck:
        build_deck(args, style)
    else:
        parser.error("--deck か --calibration のどちらかが必要です")


if __name__ == "__main__":
    main()
