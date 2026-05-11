Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Action
    Write-Host "OK: $Name" -ForegroundColor Green
}

Push-Location $ProjectRoot
try {
    Invoke-Step "Python version" {
        Invoke-Native python @("--version")
    }

    Invoke-Step "Compile Python files" {
        Invoke-Native python @(
            "-m",
            "compileall",
            "-q",
            "main.py",
            "novel_app",
            "tests",
            "test_core_modules.py",
            "test_database_extensions.py",
            "test_text_importer.py",
            "test_qt_helpers.py"
        )
    }

    Invoke-Step "Run unittest suite" {
        Invoke-Native python @("-m", "unittest", "discover", "-v")
    }

    Invoke-Step "Run pytest suite" {
        Invoke-Native python @("-m", "pytest", "tests", "-q")
    }

    Invoke-Step "Core startup smoke" {
        $oldSmokeExit = $env:SIMPLE_AI_NOVEL_SMOKE_EXIT
        try {
            $env:SIMPLE_AI_NOVEL_SMOKE_EXIT = "1"
            Invoke-Native python @("main.py")
        }
        finally {
            if ($null -eq $oldSmokeExit) {
                Remove-Item Env:\SIMPLE_AI_NOVEL_SMOKE_EXIT -ErrorAction SilentlyContinue
            }
            else {
                $env:SIMPLE_AI_NOVEL_SMOKE_EXIT = $oldSmokeExit
            }
        }
    }

    Invoke-Step "PyQt offscreen smoke" {
        $oldQtOffscreen = $env:SIMPLE_AI_NOVEL_QT_OFFSCREEN
        $oldQtSmoke = $env:SIMPLE_AI_NOVEL_QT_SMOKE
        try {
            $env:SIMPLE_AI_NOVEL_QT_OFFSCREEN = "1"
            $env:SIMPLE_AI_NOVEL_QT_SMOKE = "1"
            Invoke-Native python @("main.py")
        }
        finally {
            if ($null -eq $oldQtOffscreen) {
                Remove-Item Env:\SIMPLE_AI_NOVEL_QT_OFFSCREEN -ErrorAction SilentlyContinue
            }
            else {
                $env:SIMPLE_AI_NOVEL_QT_OFFSCREEN = $oldQtOffscreen
            }

            if ($null -eq $oldQtSmoke) {
                Remove-Item Env:\SIMPLE_AI_NOVEL_QT_SMOKE -ErrorAction SilentlyContinue
            }
            else {
                $env:SIMPLE_AI_NOVEL_QT_SMOKE = $oldQtSmoke
            }
        }
    }

    Write-Host ""
    Write-Host "Health check passed." -ForegroundColor Green
}
finally {
    Pop-Location
}
