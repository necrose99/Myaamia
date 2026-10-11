# helpers/trimfont.ps1
$OutputEncoding = [System.Text.Encoding]::UTF8

$StaticDir = "C:\Users\black\GitHub\Myaamia\Algic-Etamology-Flask\static"

if (-not (Test-Path $StaticDir)) {
    Write-Warning "Primary path structure unmapped, falling back to local context script root."
    $StaticDir = Join-Path $PSScriptRoot "..\static"
}

Push-Location $StaticDir
Write-Host "Processing web-font transformation loop inside: $StaticDir" -ForegroundColor Cyan

# Global layout optimization flags
$SharedFlags = @('--flavor=woff2', '--glyph-names', '--no-hinting', '--ignore-missing-glyphs')

# 1. Processing for Archival GLAS (Catrinity Workaround)
if (Test-Path "Catrinity.otf") {
    Write-Host "-> Optimizing Archival GLAS matrix (Catrinity-PUA)..." -ForegroundColor Yellow
    try {
        pyftsubset "Catrinity.otf" --unicodes="U+0000-007F,U+E480-E4BF" --layout-features="" --output-file="Catrinity-GLAS.woff2" $SharedFlags
        Write-Host "   ✔ Successfully packed web asset: Catrinity-GLAS.woff2" -ForegroundColor Green
    }
    catch {
        Write-Warning "Linguistic table crash detected on Catrinity config structure: $_"
    }
} else {
    Write-Warning "Source asset 'Catrinity.otf' was missing from directory frame."
}

# 2. Dynamic Weight Mapping for System Fonts
$FontAssets = Get-ChildItem -Path . -Include *.ttf, *.otf -Recurse

foreach ($Font in $FontAssets) {
    $Name = $Font.Name.ToLower()
    $Unicodes = $null
    
    if ($Name -like "*catrinity-glas*" -or $Name -eq "catrinity.otf" -or $Name -like "*.woff2") { continue }
    
    if ($Name -like "*cree*" -or $Name -like "*canadian*") {
        $Unicodes = "U+0000-007F,U+1400-167F,U+18B0-18FF"
    }
    elseif ($Name -like "*cherokee*") {
        $Unicodes = "U+0000-007F,U+13A0-13FF,U+AB70-ABBF"
    }

    if ($Unicodes) {
        # Dynamically change suffix to keep weights isolated (e.g., NotoSansCherokee-Thin.woff2)
        $OutputFile = [io.path]::ChangeExtension($Font.Name, ".woff2")
        Write-Host "-> Subset parsing layout for [$($Font.Name)] -> [$OutputFile]..." -ForegroundColor Yellow
        try {
            pyftsubset $Font.Name --unicodes=$Unicodes --layout-features="kern,liga,calt" --output-file=$OutputFile $SharedFlags
            Write-Host "   ✔ Generated web file asset: $OutputFile" -ForegroundColor Green
        }
        catch {
            Write-Warning "Skipping structural compilation error on [$($Font.Name)]: Malformed table structure."
        }
    }
}

Pop-Location
Write-Host "Font asset compilation workflow completed." -ForegroundColor Green
