$ErrorActionPreference = "Stop"
$main = Join-Path $PSScriptRoot "..\main.py"
$content = Get-Content $main -Raw
if ($content -notmatch 'from seo import configure_seo') { $content = "from seo import configure_seo`n" + $content }
if ($content -notmatch '(?m)^configure_seo\(app\)\s*$') {
  $pattern = '(?m)^(app\s*=\s*FastAPI\([^\r\n]*\)\s*)$'
  if ($content -notmatch $pattern) { throw "No se encontro app = FastAPI(...)" }
  $content = [regex]::Replace($content, $pattern, '${1}' + "`nconfigure_seo(app)", 1)
}
[IO.File]::WriteAllText($main, $content.Replace("`r`n", "`n"), [Text.UTF8Encoding]::new($false))
Write-Host "SEO aplicado a main.py" -ForegroundColor Green
