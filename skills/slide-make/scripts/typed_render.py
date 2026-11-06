"""
typed_render.py — タイプD: plan.tsv に従って画像を生成する（cockpit gen-image）

使い方:
    python3 typed_render.py <type_d> --stage calibration        # 画風の見本
    python3 typed_render.py <type_d> --stage boards             # 一覧画像
    python3 typed_render.py <type_d> --stage slides --slides "4"   # 基準スライドを先に1枚
    python3 typed_render.py <type_d> --stage slides --jobs 3    # 残りをまとめて
    python3 typed_render.py <type_d> --stage slides --slides "2 5" --force   # 作り直し（旧版は old/ へ）
    python3 typed_render.py <type_d> --fix 5 --fix-prompt fix.txt   # 部分修正（旧版は old/ へ）
    python3 typed_render.py <type_d> --review                   # 確認用JPEGと一覧を作る

成功の判定は終了コードではなく、画像ファイルの実在で行う。
Cockpit が無い環境では plan.tsv のプロンプトと参照画像を、使える画像生成ツールに同じ順で渡す。
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def find_cockpit():
    found = shutil.which("cockpit")
    fallback = os.path.expanduser("~/.agi-tools/bin/cockpit")
    if found:
        return found
    if os.access(fallback, os.X_OK):
        return fallback
    sys.exit("cockpit CLI が見つかりません。plan.tsv のプロンプトと参照画像を、使える画像生成ツールに渡してください。")


def load_plan(type_d):
    rows = []
    with open(os.path.join(type_d, "plan.tsv"), encoding="utf-8") as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 4:
                rows.append({"id": fields[0], "size": fields[1], "prompt": fields[2], "png": fields[3], "refs": fields[4:]})
    return rows


def load_meta(type_d):
    with open(os.path.join(type_d, "meta.json"), encoding="utf-8") as f:
        return json.load(f)


def archive(path, type_d):
    if os.path.exists(path):
        old_dir = os.path.join(type_d, "old")
        os.makedirs(old_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(path))[0]
        target = os.path.join(old_dir, f"{stem}.{time.strftime('%Y%m%d-%H%M%S')}.png")
        shutil.move(path, target)
        return target
    return None


def generate(cockpit, type_d, prompt, png, size, refs):
    missing = [r for r in refs if not os.path.isfile(r)]
    if missing:
        print(f"NG {os.path.basename(png)}: 参照画像がありません: {missing}", flush=True)
        return False
    command = [cockpit, "gen-image", "--stdin", "--out", png, "--size", size, "--json"]
    for ref in refs:
        command += ["--reference", ref]
    started = time.time()
    print(f"生成 {os.path.basename(png)} 参照{len(refs)}枚", flush=True)
    with open(prompt, encoding="utf-8") as stdin, open(os.path.join(type_d, "render.log"), "a", encoding="utf-8") as log:
        subprocess.run(command, stdin=stdin, stdout=log, stderr=log, check=False)
    ok = os.path.isfile(png) and os.path.getsize(png) > 0
    print(f"{'OK' if ok else 'NG'} {os.path.basename(png)} {time.time() - started:.0f}秒", flush=True)
    return ok


def ensure_panels(type_d, meta):
    """切り出し済みでなければ一覧画像からコマを切り出す。"""
    panels_dir = meta["panels_dir"]
    for board in meta["boards"]:
        last = os.path.join(panels_dir, f"p{board['start'] + board['count'] - 1:02d}.png")
        if os.path.isfile(last):
            continue
        if not os.path.isfile(board["png"]):
            sys.exit(f"一覧画像がありません: {board['png']}（先に --stage boards）")
        subprocess.run([sys.executable, os.path.join(HERE, "typed_split_board.py"), board["png"], panels_dir,
                        "--cols", str(board["cols"]), "--rows", str(board["rows"]),
                        "--start", str(board["start"]), "--count", str(board["count"])], check=True)


def check_duplicates(images_dir):
    """取り違え（同じ絵）の検出。同一ファイルがあれば番号を返す。"""
    seen = {}
    duplicates = []
    for name in sorted(os.listdir(images_dir)):
        if name.startswith("slide_") and name.endswith(".png"):
            with open(os.path.join(images_dir, name), "rb") as f:
                digest = hashlib.md5(f.read()).hexdigest()
            if digest in seen:
                duplicates.append((seen[digest], name))
            seen.setdefault(digest, name)
    return duplicates


def run_stage(args, type_d, rows, meta, cockpit):
    prefix = {"calibration": "calibration", "boards": "board-", "slides": "slide-"}[args.stage]
    selected = [r for r in rows if r["id"].startswith(prefix)]
    if args.stage == "slides":
        ensure_panels(type_d, meta)
        if args.slides:
            wanted = {f"slide-{int(n):02d}" for n in args.slides.split()}
            selected = [r for r in selected if r["id"] in wanted]

    todo = []
    for row in selected:
        if os.path.isfile(row["png"]) and not args.force:
            print(f"飛ばす {os.path.basename(row['png'])}（既にあります）")
            continue
        if args.force:
            archive(row["png"], type_d)
        todo.append(row)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(lambda r: generate(cockpit, type_d, r["prompt"], r["png"], r["size"], r["refs"]), todo))

    failed = [r["id"] for r, ok in zip(todo, results) if not ok]
    if args.stage == "slides":
        duplicates = check_duplicates(meta["images_dir"])
        for a, b in duplicates:
            print(f"★取り違え {a} = {b}。該当の番号を作り直してください")
        if duplicates:
            failed.append("duplicates")
    if failed:
        print(f"未完了: {failed}")
        return 1
    print("完了。検品表 text_checklist.md と照合してください。")
    return 0


def run_fix(args, type_d, rows, cockpit):
    row = next((r for r in rows if r["id"] == f"slide-{args.fix:02d}"), None)
    if row is None or not os.path.isfile(row["png"]):
        sys.exit(f"スライド {args.fix} の画像がありません")
    if not args.fix_prompt or not os.path.isfile(args.fix_prompt):
        sys.exit("--fix-prompt <ファイル> が必要です")
    temp = row["png"] + ".fix.png"
    if not generate(cockpit, type_d, args.fix_prompt, temp, row["size"], [row["png"]]):
        return 1
    previous = archive(row["png"], type_d)
    shutil.move(temp, row["png"])
    print(f"修正しました: {row['png']}（旧版: {previous}）")
    return 0


def run_review(type_d, rows):
    from PIL import Image

    review_dir = os.path.join(type_d, "review")
    os.makedirs(review_dir, exist_ok=True)
    slides = [r["png"] for r in rows if r["id"].startswith("slide-") and os.path.isfile(r["png"])]
    tile_w, tile_h, gap, cols = 640, 360, 8, 3
    grid_rows = (len(slides) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w + (cols + 1) * gap, grid_rows * tile_h + (grid_rows + 1) * gap), "#3a3a3a")
    for i, png in enumerate(slides):
        image = Image.open(png).convert("RGB")
        full = image.resize((1024, round(image.height * 1024 / image.width)))
        full.save(os.path.join(review_dir, os.path.basename(png).replace(".png", ".jpg")), quality=86)
        tile = image.resize((tile_w, tile_h))
        sheet.paste(tile, (gap + (i % cols) * (tile_w + gap), gap + (i // cols) * (tile_h + gap)))
    sheet.save(os.path.join(review_dir, "contact_sheet.jpg"), quality=88)
    print(f"確認用画像を作りました: {review_dir}（{len(slides)}枚）")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("type_d")
    parser.add_argument("--stage", choices=["calibration", "boards", "slides"])
    parser.add_argument("--slides", help='作るスライド番号（例: "4" や "2 5"）')
    parser.add_argument("--jobs", type=int, default=1, help="同時に生成する枚数（3枚までで実証済み）")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--fix", type=int)
    parser.add_argument("--fix-prompt")
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()

    type_d = os.path.abspath(args.type_d)
    rows = load_plan(type_d)
    if args.review:
        return run_review(type_d, rows)
    cockpit = find_cockpit()
    if args.fix:
        return run_fix(args, type_d, rows, cockpit)
    if not args.stage:
        parser.error("--stage、--fix、--review のいずれかが必要です")
    return run_stage(args, type_d, rows, load_meta(type_d), cockpit)


if __name__ == "__main__":
    sys.exit(main())
