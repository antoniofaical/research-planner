$ErrorActionPreference = 'Stop'

$projectRoot = $PSScriptRoot
$versionCheck = 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'
$candidates = @(
    @{ Command = (Join-Path $projectRoot '.venv/Scripts/python.exe'); Prefix = @() },
    @{ Command = (Join-Path $projectRoot '.venv/bin/python'); Prefix = @() },
    @{ Command = 'py'; Prefix = @('-3') },
    @{ Command = 'python3'; Prefix = @() },
    @{ Command = 'python'; Prefix = @() },
    @{ Command = 'python3.14'; Prefix = @() },
    @{ Command = 'python3.13'; Prefix = @() },
    @{ Command = 'python3.12'; Prefix = @() },
    @{ Command = 'python3.11'; Prefix = @() }
)

foreach ($candidate in $candidates) {
    $command = $candidate.Command
    $prefix = $candidate.Prefix
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { continue }
    try {
        & $command @prefix -c $versionCheck 2>$null
        if ($LASTEXITCODE -ne 0) { continue }
    }
    catch { continue }
    & $command @prefix -X utf8 (Join-Path $projectRoot 'scripts/bootstrap.py')
    exit $LASTEXITCODE
}

[Console]::Error.WriteLine('Erro: instale Python 3.11 ou superior com suporte a venv e execute novamente.')
exit 1
