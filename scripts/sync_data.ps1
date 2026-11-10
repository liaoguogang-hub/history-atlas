<#
.SYNOPSIS
    把历史图鉴的数据 JSON 同步到 Android App 的 assets 目录。

.DESCRIPTION
    源目录 (Source):  C:\Users\guoga\Documents\DSH\data
    目标目录 (Target): C:\Users\guoga\Documents\DSH\history-atlas\app\src\main\assets\data

    拷贝前逐个校验：
      1. 文件存在
      2. 不带 UTF-8 BOM（契约要求 UTF-8 无 BOM）
      3. JSON 可解析
      4. 顶层字段 version / scope / periods / events / figures 齐全

    任意一项不通过即报错退出，不写入任何文件，避免把坏数据打进 APK。

    校验通过后打印每个文件的大小与条数统计（时期 / 事件 / 人物）。

.PARAMETER Source
    源数据目录。默认取脚本所在目录的上级下的 data\ 子目录。

.PARAMETER Target
    目标 assets 数据目录。默认取脚本所在目录的上级下的
    history-atlas\app\src\main\assets\data\ 子目录。

.PARAMETER ValidateOnly
    只校验不拷贝。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\sync_data.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\sync_data.ps1 -Source D:\other\data -Target D:\other\assets\data
#>
[CmdletBinding()]
param(
    [string]$Source,
    [string]$Target,
    [switch]$ValidateOnly
)

$ErrorActionPreference = 'Stop'

# 以脚本自身位置推导默认路径，避免依赖当前工作目录
$RepoRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Source)) {
    $Source = Join-Path $RepoRoot 'data'
}
if ([string]::IsNullOrWhiteSpace($Target)) {
    $Target = Join-Path $RepoRoot 'history-atlas\app\src\main\assets\data'
}

$DataFiles = @('china.json', 'world.json')

function Test-DataFile {
    <#
    .SYNOPSIS 校验单个数据文件，返回其统计信息。
    #>
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Name
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw ("[$Name] 数据文件不存在: $Path`n" +
               "  提示：数据文件需先由数据同事生成到源目录，再执行本脚本。`n" +
               "  若只想校验已有文件，可加 -ValidateOnly 参数。")
    }

    # 契约要求 UTF-8 无 BOM
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        throw "[$Name] 数据文件带 UTF-8 BOM，违反契约 §8: $Path"
    }

    $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "[$Name] 数据文件为空: $Path"
    }

    try {
        $obj = $text | ConvertFrom-Json
    } catch {
        throw "[$Name] JSON 解析失败: $Path -> $($_.Exception.Message)"
    }

    foreach ($field in @('version', 'scope', 'periods', 'events', 'figures')) {
        if ($null -eq $obj.$field) {
            throw "[$Name] 顶层缺少字段 '$field': $Path"
        }
    }

    [pscustomobject]@{
        Name         = $Name
        Path         = $Path
        SizeBytes    = $bytes.Length
        Scope        = [string]$obj.scope
        Periods      = @($obj.periods).Count
        Events       = @($obj.events).Count
        Figures      = @($obj.figures).Count
    }
}

Write-Host "源目录   : $Source"
Write-Host "目标目录 : $Target"
Write-Host ""

# ---------------------------------------------------------------------------
# 1. 校验
# ---------------------------------------------------------------------------
Write-Host "[1/3] 校验数据文件..."
$results = @()
foreach ($name in $DataFiles) {
    $path = Join-Path $Source $name
    $stat = Test-DataFile -Path $path -Name $name
    $results += $stat
    Write-Host ("  OK  {0,-12} {1,10:N0} 字节  scope={2,-6} periods={3,-4} events={4,-4} figures={5}" -f `
        $stat.Name, $stat.SizeBytes, $stat.Scope, $stat.Periods, $stat.Events, $stat.Figures)
}
Write-Host "  校验全部通过。"

if ($ValidateOnly) {
    Write-Host ""
    Write-Host "仅校验模式（-ValidateOnly），未拷贝任何文件。"
    exit 0
}

# ---------------------------------------------------------------------------
# 2. 准备目标目录
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/3] 准备目标目录..."
if (-not (Test-Path -LiteralPath $Target -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Write-Host "  已创建 $Target"
} else {
    Write-Host "  已存在 $Target"
}

# ---------------------------------------------------------------------------
# 3. 拷贝
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[3/3] 拷贝数据文件..."
foreach ($stat in $results) {
    $dest = Join-Path $Target $stat.Name
    Copy-Item -LiteralPath $stat.Path -Destination $dest -Force
    $actual = (Get-Item -LiteralPath $dest).Length
    Write-Host ("  ->  {0,-12} {1,10:N0} 字节  periods={2,-4} events={3,-4} figures={4}" -f `
        $stat.Name, $actual, $stat.Periods, $stat.Events, $stat.Figures)
}

Write-Host ""
Write-Host "同步完成。执行 :app:assembleDebug 即可把新数据打进 APK。"
