# Create project views with columns
$gh = "C:\Program Files\GitHub CLI\gh.exe"
$base = "users/anbx-Hayate/projectsV2/3/views"
$headers = @("-H", "Accept: application/vnd.github+json", "-H", "X-GitHub-Api-Version: 2026-03-10")

$visibleAll = @(
    355341676, 355341677, 355341678, 355341679, 355341844,
    355341845, 355341846, 355341847, 355341848, 355341849,
    355341850, 355341852, 355341853, 355341854, 355341685
)

$views = @(
    @{
        file = "view_board.json"
        body = @{
            name = "全体ボード"
            layout = "board"
            visible_fields = $visibleAll
        }
    },
    @{
        file = "view_large_task.json"
        body = @{
            name = "大タスク一覧"
            layout = "table"
            filter = 'label:"大タスク"'
            visible_fields = @(355341676, 355341678, 355341844, 355341845, 355341852, 355341854)
        }
    },
    @{
        file = "view_small_task.json"
        body = @{
            name = "今週の作業"
            layout = "board"
            filter = 'label:"小タスク"'
            visible_fields = @(355341676, 355341678, 355341844, 355341848, 355341845, 355341846, 355341847)
        }
    },
    @{
        file = "view_time.json"
        body = @{
            name = "工数・振り返り"
            layout = "table"
            visible_fields = @(355341676, 355341678, 355341848, 355341849, 355341850, 355341853, 355341844)
        }
    }
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($view in $views) {
    $path = Join-Path $scriptDir $view.file
    $view.body | ConvertTo-Json -Depth 5 | Set-Content -Path $path -Encoding UTF8
    Write-Host "Creating $($view.body.name)..."
    & $gh api -X POST @headers $base --input $path
    Write-Host ""
}
