#!/usr/bin/env bash
# Gen Interface JP を macOS / Linux にユーザー単位でインストールする。
# 管理者権限は不要。
#
# 使い方: bash install_fonts.sh [--all]
#   --all を付けると全8ウェイトを入れる（既定は5ウェイト）
#
# ライセンス: SIL OFL 1.1（自動ダウンロード・再配布とも可）
# https://github.com/yamatoiizuka/gen-interface-jp

set -euo pipefail

VERSION="0.8.0"
URL="https://github.com/yamatoiizuka/gen-interface-jp/releases/download/v${VERSION}/GenInterfaceJP-${VERSION}.zip"

# 既定で入れるウェイト。全16ウェイトで約99MBあるので、使うものだけ入れる。
WEIGHTS=("Regular" "Medium" "SemiBold" "Bold" "ExtraBold")
if [[ "${1:-}" == "--all" ]]; then
  WEIGHTS=("Thin" "ExtraLight" "Light" "Regular" "Medium" "SemiBold" "Bold" "ExtraBold")
fi

case "$(uname -s)" in
  Darwin) FONT_DIR="$HOME/Library/Fonts" ;;
  Linux)  FONT_DIR="$HOME/.local/share/fonts" ;;
  *) echo "このスクリプトは macOS / Linux 用です。Windows は install_fonts.ps1 を使ってください。" >&2; exit 1 ;;
esac

mkdir -p "$FONT_DIR"

# 既に入っているなら何もしない（毎回56MB落とさない）
already=0
for w in "${WEIGHTS[@]}"; do
  [[ -f "$FONT_DIR/GenInterfaceJP-${w}.ttf" ]] || { already=1; break; }
  [[ -f "$FONT_DIR/GenInterfaceJPDisplay-${w}.ttf" ]] || { already=1; break; }
done
if [[ $already -eq 0 ]]; then
  echo "Gen Interface JP は既にインストール済みです（${FONT_DIR}）"
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Gen Interface JP v${VERSION} をダウンロードしています（約56MB）..."
curl -fsSL --retry 3 -o "$TMP/font.zip" "$URL"

echo "展開しています..."
unzip -qo "$TMP/font.zip" -d "$TMP"
SRC="$TMP/GenInterfaceJP-${VERSION}"
[[ -d "$SRC" ]] || { echo "展開に失敗しました: $SRC がありません" >&2; exit 1; }

installed=0
for w in "${WEIGHTS[@]}"; do
  for pair in "Gen Interface JP/GenInterfaceJP-${w}.ttf" \
              "Gen Interface JP Display/GenInterfaceJPDisplay-${w}.ttf"; do
    if [[ -f "$SRC/$pair" ]]; then
      cp -f "$SRC/$pair" "$FONT_DIR/"
      installed=$((installed + 1))
    else
      echo "警告: 見つかりません: $pair" >&2
    fi
  done
done

# ライセンス全文を同梱する（OFLの要件）
cp -f "$SRC/OFL.txt" "$FONT_DIR/GenInterfaceJP-OFL.txt" 2>/dev/null || true

# Linux はフォントキャッシュの更新が要る
if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f >/dev/null 2>&1 || true
fi

echo "完了: ${installed} 個のフォントを ${FONT_DIR} にインストールしました"
