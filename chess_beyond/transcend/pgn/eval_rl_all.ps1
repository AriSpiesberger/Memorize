# Every eval.py evaluation of the two rl_pgn_games.py models (-all runs), plus what the starting models
# still need for a side-by-side comparison. Run from chess_beyond/:
#
#     powershell -ExecutionPolicy Bypass -File transcend/pgn/eval_rl_all.ps1
#
# Logs: runs/transcend/eval_logs/<step>.log. Results: results/transcend/eval/<model>-<kind>.json.
# One step failing does not stop the rest. Temperatures 0.001 0.01 0.1 1 throughout.

$ErrorActionPreference = "Continue"
$env:STOCKFISH = (Resolve-Path "tools/fairy-stockfish-largeboard_x86-64.exe").Path   # absolute: relative fails on Windows
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$py = "..\.venv\Scripts\python.exe"
$lr = "results/transcend/eval/level_ratings.json"
$temps = "0.001", "0.01", "0.1", "1"
$logs = "runs/transcend/eval_logs"
New-Item -ItemType Directory -Force $logs | Out-Null

# eval.py overwrites <model>-games.json: keep the starting 1000-1300 model's T = 0.001 and 1 results
$base = "results/transcend/eval/chess-pgn-1000-1300-games.json"
$kept = "results/transcend/eval/chess-pgn-1000-1300-games.T0001-1.json"
if (-not (Test-Path $kept)) { Copy-Item $base $kept }

$steps = @(
    # the RL models: games (all five levels, as for the starting models), positions, puzzles
    @("rl-1000-1300-games",     "games",     "runs/transcend/rl-pgn-1000-1300-all.pt", $temps, "--level-ratings", $lr, "--workers", "24"),
    @("rl-2400-games",          "games",     "runs/transcend/rl-pgn-2400+-all.pt",     $temps, "--level-ratings", $lr, "--workers", "24"),
    @("rl-1000-1300-positions", "positions", "runs/transcend/rl-pgn-1000-1300-all.pt", $temps, "--workers", "24"),
    @("rl-2400-positions",      "positions", "runs/transcend/rl-pgn-2400+-all.pt",     $temps, "--workers", "24"),
    @("rl-1000-1300-puzzles",   "puzzles",   "runs/transcend/rl-pgn-1000-1300-all.pt", $temps, "--strata-dir", "strata-pgn"),
    @("rl-2400-puzzles",        "puzzles",   "runs/transcend/rl-pgn-2400+-all.pt",     $temps, "--strata-dir", "strata-pgn"),
    # the starting models: games at the two temperatures 1000-1300 never had, and positions (never run);
    # their puzzles and the 2400+ games already cover these temperatures
    @("base-1000-1300-games",   "games",     "Arisp/chess-pgn-1000-1300", @("0.01", "0.1"), "--level-ratings", $lr, "--workers", "24"),
    @("base-1000-1300-positions", "positions", "Arisp/chess-pgn-1000-1300", $temps, "--workers", "24"),
    @("base-2400-positions",    "positions", "Arisp/chess-pgn-2400plus",  $temps, "--workers", "24")
)

foreach ($s in $steps) {
    $name, $kind, $model, $t = $s[0], $s[1], $s[2], $s[3]
    $extra = $s[4..($s.Count - 1)]
    $log = "$logs/$name.log"
    Write-Host "$(Get-Date -Format HH:mm)  $name  ->  $log"
    & $py transcend/pgn/eval.py $kind --model $model --temps @t @extra *> $log
    Write-Host "$(Get-Date -Format HH:mm)  $name  exit $LASTEXITCODE"
}
Write-Host "all done"
