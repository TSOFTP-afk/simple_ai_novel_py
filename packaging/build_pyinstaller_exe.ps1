param(
    [string]$Version = "v0.1.0",
    [string]$AppName = "SimpleAINovelApp"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$BuildTools = Join-Path $ProjectRoot ".build_tools"
$VendorDir = Join-Path $ProjectRoot "vendor"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$BuildRoot = Join-Path $ProjectRoot "build\pyinstaller"
$SpecRoot = Join-Path $ProjectRoot "build\spec"
$DistRoot = Join-Path $ProjectRoot "dist"
$ExeName = "$AppName-$Version"
$OutputExe = Join-Path $ReleaseRoot "$ExeName.exe"

if (-not (Test-Path -LiteralPath $BuildTools)) {
    throw "Missing .build_tools. Run: python -m pip install pyinstaller -t .build_tools"
}

if (-not (Test-Path -LiteralPath $VendorDir)) {
    throw "Missing vendor directory. Run: python -m pip install -r requirements.txt -t vendor"
}

New-Item -ItemType Directory -Path $ReleaseRoot, $BuildRoot, $SpecRoot -Force | Out-Null

$env:PYTHONPATH = "$BuildTools;$VendorDir"

$IconPath = Join-Path $ProjectRoot "packaging\app_icon.ico"
$AddDataIcon = "${IconPath};packaging"

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onefile `
    --name $ExeName `
    --icon $IconPath `
    --add-data $AddDataIcon `
    --paths $VendorDir `
    --collect-all PIL `
    --distpath $ReleaseRoot `
    --workpath $BuildRoot `
    --specpath $SpecRoot `
    (Join-Path $ProjectRoot "main.py")

if (-not (Test-Path -LiteralPath $OutputExe)) {
    throw "PyInstaller did not create $OutputExe"
}

$Hash = Get-FileHash -LiteralPath $OutputExe -Algorithm SHA256
$SizeMb = [Math]::Round((Get-Item -LiteralPath $OutputExe).Length / 1MB, 2)
Write-Output "Built: $OutputExe"
Write-Output "SizeMB: $SizeMb"
Write-Output "SHA256: $($Hash.Hash)"
