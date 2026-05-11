param(
    [string]$Version = "v0.1.0",
    [string]$AppName = "SimpleAINovelApp"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$BuildRoot = Join-Path ([System.IO.Path]::GetTempPath()) "$AppName-release-build"
$PayloadRoot = Join-Path $BuildRoot "payload"
$PayloadApp = Join-Path $PayloadRoot "app"
$PayloadPython = Join-Path $PayloadRoot "python"
$IExpressRoot = Join-Path $BuildRoot "iexpress"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$OutputExe = Join-Path $ReleaseRoot "$AppName-$Version.exe"
$TempOutputExe = Join-Path $BuildRoot "$AppName-$Version.exe"
$PayloadZip = Join-Path $IExpressRoot "app.zip"
$LauncherSource = Join-Path $ProjectRoot "packaging\Launcher.cs"
$LauncherConfig = Join-Path $BuildRoot "LauncherConfig.cs"
$AppIcon = Join-Path $ProjectRoot "packaging\app_icon.ico"

function Reset-Directory([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
}

function Copy-Directory([string]$Source, [string]$Destination) {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null
Reset-Directory $BuildRoot
New-Item -ItemType Directory -Path $PayloadRoot, $PayloadApp, $PayloadPython, $IExpressRoot -Force | Out-Null

$PythonExe = (Get-Command python.exe).Source
$PythonRoot = Split-Path -Parent $PythonExe

Copy-Item -LiteralPath (Join-Path $ProjectRoot "main.py") -Destination $PayloadApp -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination $PayloadApp -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "requirements.txt") -Destination $PayloadApp -Force
Copy-Directory (Join-Path $ProjectRoot "novel_app") (Join-Path $PayloadApp "novel_app")
Copy-Directory (Join-Path $ProjectRoot "vendor") (Join-Path $PayloadApp "vendor")

Copy-Item -LiteralPath (Join-Path $PythonRoot "python.exe") -Destination $PayloadPython -Force
Copy-Item -LiteralPath (Join-Path $PythonRoot "pythonw.exe") -Destination $PayloadPython -Force
Copy-Item -LiteralPath (Join-Path $PythonRoot "python3.dll") -Destination $PayloadPython -Force
Copy-Item -LiteralPath (Join-Path $PythonRoot "python313.dll") -Destination $PayloadPython -Force
Copy-Item -LiteralPath (Join-Path $PythonRoot "vcruntime140.dll") -Destination $PayloadPython -Force
Copy-Item -LiteralPath (Join-Path $PythonRoot "vcruntime140_1.dll") -Destination $PayloadPython -Force
Copy-Directory (Join-Path $PythonRoot "DLLs") (Join-Path $PayloadPython "DLLs")
Copy-Directory (Join-Path $PythonRoot "Lib") (Join-Path $PayloadPython "Lib")
Copy-Directory (Join-Path $PythonRoot "tcl") (Join-Path $PayloadPython "tcl")

Get-ChildItem -Path $PayloadRoot -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path $PayloadRoot -Recurse -Include "*.pyc","*.pyo" | Remove-Item -Force
Get-ChildItem -Path (Join-Path $PayloadPython "Lib") -Directory -Filter "site-packages" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path (Join-Path $PayloadPython "Lib") -Directory -Filter "test" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path (Join-Path $PayloadPython "Lib") -Directory -Filter "ensurepip" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

Compress-Archive -Path (Join-Path $PayloadRoot "*") -DestinationPath $PayloadZip -Force

$EscapedAppName = $AppName.Replace("\", "\\").Replace('"', '\"')
$EscapedVersion = $Version.Replace("\", "\\").Replace('"', '\"')
@"
namespace SimpleAINovelAppLauncher
{
    internal static class LauncherConfig
    {
        public const string AppName = "$EscapedAppName";
        public const string Version = "$EscapedVersion";
    }
}
"@ | Set-Content -LiteralPath $LauncherConfig -Encoding UTF8

$CscCandidates = @(
    (Join-Path $env:SystemRoot "Microsoft.NET\Framework64\v4.0.30319\csc.exe"),
    (Join-Path $env:SystemRoot "Microsoft.NET\Framework\v4.0.30319\csc.exe")
)
$Csc = $CscCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $Csc) {
    throw "Could not find .NET Framework csc.exe"
}

& $Csc `
    /nologo `
    /target:winexe `
    /optimize+ `
    /win32icon:"$AppIcon" `
    /out:$TempOutputExe `
    /resource:"$PayloadZip,payload.zip" `
    /reference:System.IO.Compression.dll `
    /reference:System.IO.Compression.FileSystem.dll `
    /reference:System.Windows.Forms.dll `
    $LauncherSource `
    $LauncherConfig

if (-not (Test-Path -LiteralPath $TempOutputExe)) {
    throw "Launcher compiler did not create $TempOutputExe"
}

Copy-Item -LiteralPath $TempOutputExe -Destination $OutputExe -Force
$Hash = Get-FileHash -LiteralPath $OutputExe -Algorithm SHA256
$SizeMb = [Math]::Round((Get-Item -LiteralPath $OutputExe).Length / 1MB, 2)
Write-Output "Built: $OutputExe"
Write-Output "SizeMB: $SizeMb"
Write-Output "SHA256: $($Hash.Hash)"
