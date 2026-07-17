# Gen Interface JP を Windows にユーザー単位でインストールする。
# 管理者権限は不要（%LOCALAPPDATA% + HKCU レジストリに登録する方式）。
#
# 使い方:
#   powershell -ExecutionPolicy Bypass -File install_fonts.ps1
#   powershell -ExecutionPolicy Bypass -File install_fonts.ps1 -All
#
# ライセンス: SIL OFL 1.1（自動ダウンロード・再配布とも可）
# https://github.com/yamatoiizuka/gen-interface-jp

param(
  [switch]$All
)

$ErrorActionPreference = "Stop"

$Version = "0.8.0"
$Url = "https://github.com/yamatoiizuka/gen-interface-jp/releases/download/v$Version/GenInterfaceJP-$Version.zip"

# 既定で入れるウェイト。全16ウェイトで約99MBあるので、使うものだけ入れる。
$Weights = @("Regular", "Medium", "SemiBold", "Bold", "ExtraBold")
if ($All) {
  $Weights = @("Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold")
}

# ユーザー単位のフォント置き場（管理者権限が要らないのがここ）
$FontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$RegPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"

New-Item -ItemType Directory -Force -Path $FontDir | Out-Null
if (-not (Test-Path $RegPath)) { New-Item -Path $RegPath -Force | Out-Null }

# 既に入っているなら何もしない（毎回56MB落とさない）
$missing = $false
foreach ($w in $Weights) {
  foreach ($f in @("GenInterfaceJP-$w.ttf", "GenInterfaceJPDisplay-$w.ttf")) {
    if (-not (Test-Path (Join-Path $FontDir $f))) { $missing = $true; break }
  }
  if ($missing) { break }
}
if (-not $missing) {
  Write-Host "Gen Interface JP は既にインストール済みです ($FontDir)"
  exit 0
}

$Tmp = Join-Path $env:TEMP ("slidekit-font-" + [System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

try {
  Write-Host "Gen Interface JP v$Version をダウンロードしています (約56MB)..."
  $zip = Join-Path $Tmp "font.zip"
  # Invoke-WebRequest は既定の進捗表示が遅いので切る
  $ProgressPreference = "SilentlyContinue"
  Invoke-WebRequest -Uri $Url -OutFile $zip -UseBasicParsing

  Write-Host "展開しています..."
  Expand-Archive -Path $zip -DestinationPath $Tmp -Force
  $Src = Join-Path $Tmp "GenInterfaceJP-$Version"
  if (-not (Test-Path $Src)) { throw "展開に失敗しました: $Src がありません" }

  # ファイル名 -> レジストリに登録する表示名（nameID 4 の Full Name）
  # 注意: Regular と Bold だけがベースファミリーのスタイルリンクで、
  #       それ以外は独立ファミリーになる。表示名はいずれも Full Name を使う。
  function Get-FullName($family, $weight) {
    if ($weight -eq "Regular") { return "$family Regular" }
    return "$family $weight"
  }

  $installed = 0
  foreach ($w in $Weights) {
    $items = @(
      @{ Sub = "Gen Interface JP";         File = "GenInterfaceJP-$w.ttf";        Full = (Get-FullName "Gen Interface JP" $w) },
      @{ Sub = "Gen Interface JP Display"; File = "GenInterfaceJPDisplay-$w.ttf"; Full = (Get-FullName "Gen Interface JP Display" $w) }
    )
    foreach ($it in $items) {
      $srcFile = Join-Path $Src (Join-Path $it.Sub $it.File)
      if (-not (Test-Path $srcFile)) {
        Write-Warning "見つかりません: $($it.File)"
        continue
      }
      $dst = Join-Path $FontDir $it.File
      Copy-Item -Path $srcFile -Destination $dst -Force

      # レジストリに登録しないとアプリのフォント一覧に出てこない
      New-ItemProperty -Path $RegPath -Name "$($it.Full) (TrueType)" `
                       -PropertyType String -Value $dst -Force | Out-Null
      $installed++
    }
  }

  # ライセンス全文を同梱する（OFLの要件）
  $ofl = Join-Path $Src "OFL.txt"
  if (Test-Path $ofl) {
    Copy-Item -Path $ofl -Destination (Join-Path $FontDir "GenInterfaceJP-OFL.txt") -Force
  }

  Write-Host "完了: $installed 個のフォントを $FontDir にインストールしました"
  Write-Host "※ 既に起動中の PowerPoint がある場合は、一度終了して開き直してください"
}
finally {
  Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
