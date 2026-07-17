"""
collect_images.py — codex生成画像の回収・重複チェック・配置

codexの image_gen は ~/.codex/generated_images/<uuid>/ig_*.png に固定で吐き、
指定パスへのcpは不安定。このスクリプトは、エージェントが報告した「n→生成パス」の
対応を受け取り、所定の images_dir/slide_NN.png に配置し、全枚のハッシュ重複を検出する。

使い方:
    python3 collect_images.py <images_dir> <mapping.json>

mapping.json の形式:
    {"1": "/Users/.../ig_xxx.png", "2": "/Users/.../ig_yyy.png", ...}
    値は codex の実パス or 既に配置済みのパス。

出力:
    - 配置結果（OK / 失敗）
    - 全 slide_NN.png のハッシュ重複検出（★重複があれば該当番号を表示）
    重複が出たスライドは「取り違え」なので、その番号だけ再生成すること。
"""
import sys
import os
import json
import shutil
import hashlib


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) != 3:
        print("usage: python3 collect_images.py <images_dir> <mapping.json>")
        sys.exit(1)
    images_dir = os.path.abspath(os.path.expanduser(sys.argv[1]))
    os.makedirs(images_dir, exist_ok=True)
    mapping = json.load(open(os.path.expanduser(sys.argv[2]), encoding="utf-8"))

    ok, fail = [], []
    for n, src in sorted(mapping.items(), key=lambda x: int(x[0])):
        src = os.path.expanduser(src)
        dst = os.path.join(images_dir, f"slide_{int(n):02d}.png")
        if os.path.exists(src) and os.path.getsize(src) > 0:
            if os.path.abspath(src) != dst:
                shutil.copy(src, dst)
            ok.append(int(n))
        else:
            fail.append((int(n), src))

    print(f"配置OK: {ok}")
    if fail:
        print(f"★配置失敗（パスが無い/空）: {fail}")

    # 全枚ハッシュ重複チェック（最重要: codex並列生成は隣のスライドと同じ絵を作る取り違えが起きる）
    files = sorted(
        f for f in os.listdir(images_dir)
        if f.startswith("slide_") and f.endswith(".png")
    )
    by_hash = {}
    for f in files:
        h = md5(os.path.join(images_dir, f))
        by_hash.setdefault(h, []).append(f)
    dups = {h: fs for h, fs in by_hash.items() if len(fs) > 1}
    print(f"\n枚数: {len(files)}")
    if dups:
        print("★重複検出（取り違え。該当番号を再生成すること）:")
        for h, fs in dups.items():
            print(f"  {' = '.join(fs)}  (hash {h[:8]})")
        sys.exit(2)
    else:
        print("重複なし ✅ 全スライドユニーク")


if __name__ == "__main__":
    main()
