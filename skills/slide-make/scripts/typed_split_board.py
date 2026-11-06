"""
typed_split_board.py — タイプD: 一覧画像をコマごとに切り分ける

一覧画像のコマ境界は均一ではない（2026-11-06 実測で最大30px前後ずれた）。
等分で切ると隣のコマが混ざるので、期待位置の近くで「最も色が揃った線」を探して切る。
切り出したコマは清書の参照に使う。スライドの完成画像としては使わない。

使い方:
    python3 typed_split_board.py <board.png> <panels_dir> [--cols 3 --rows 3 --start 1 --count 9]

出力:
    <panels_dir>/pNN.png （NN はスライド番号）
"""
import argparse
import os
import sys

from PIL import Image, ImageStat

SEARCH_RATIO = 0.07   # 期待位置から前後に探す幅（コマ幅に対する比率ではなく全体に対する比率）
RUN_TOLERANCE = 1.15  # 最小のばらつきの何倍までを「境界の帯」とみなすか


def line_spread(gray, position, vertical):
    """指定した1列（または1行）の明るさのばらつきを返す。境界の帯ほど小さい。"""
    width, height = gray.size
    box = (position, 0, position + 1, height) if vertical else (0, position, width, position + 1)
    return ImageStat.Stat(gray.crop(box)).stddev[0]


def find_boundary(gray, expected, length, vertical):
    """expected の近くで最も色が揃った帯の中心を返す。"""
    reach = max(2, int(length * SEARCH_RATIO))
    low, high = max(1, expected - reach), min(length - 2, expected + reach)
    spreads = {p: line_spread(gray, p, vertical) for p in range(low, high + 1)}
    smallest = min(spreads.values())
    limit = smallest * RUN_TOLERANCE + 0.5
    best_run, run = [], []
    for p in range(low, high + 1):
        if spreads[p] <= limit:
            run.append(p)
        else:
            if len(run) > len(best_run):
                best_run = run
            run = []
    if len(run) > len(best_run):
        best_run = run
    return best_run[len(best_run) // 2]


def boundaries(gray, count, length, vertical):
    edges = [0]
    for i in range(1, count):
        edges.append(find_boundary(gray, round(length * i / count), length, vertical))
    edges.append(length)
    return edges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board")
    parser.add_argument("out_dir")
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--start", type=int, default=1, help="1コマ目のスライド番号")
    parser.add_argument("--count", type=int, help="切り出すコマ数（既定は cols x rows）")
    args = parser.parse_args()

    image = Image.open(args.board).convert("RGB")
    scale = 2  # 境界探しだけ縮小して速くする
    gray = image.resize((image.width // scale, image.height // scale)).convert("L")
    xs = [x * scale for x in boundaries(gray, args.cols, gray.width, True)]
    ys = [y * scale for y in boundaries(gray, args.rows, gray.height, False)]
    xs[-1], ys[-1] = image.width, image.height

    total = args.count or args.cols * args.rows
    os.makedirs(args.out_dir, exist_ok=True)
    index = 0
    for r in range(args.rows):
        for c in range(args.cols):
            if index >= total:
                break
            panel = image.crop((xs[c], ys[r], xs[c + 1], ys[r + 1]))
            path = os.path.join(args.out_dir, f"p{args.start + index:02d}.png")
            panel.save(path)
            print(f"{path} {panel.width}x{panel.height}")
            index += 1
    print(f"縦の境界: {xs}")
    print(f"横の境界: {ys}")


if __name__ == "__main__":
    sys.exit(main())
