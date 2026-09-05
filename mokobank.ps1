# Define the mapping of Mojibake to proper Myaamia characters
$mappings = @{
    'Å¡' = 'š'
    'Å ' = 'š'
    'Å«' = 'ū'
    'Ã¢' = 'â'
    'Ãª' = 'ê'
    'Ã®' = 'î'
    'Ã´' = 'ô'
}

# Get all relevant files recursively
$files = Get-ChildItem -Path "." -Recurse -Include *.csv, *.json, *.tmx, *.eaf , *.sfm

foreach ($file in $files) {
    Write-Host "🧼 Cleaning: $($file.FullName)"
    
    # Read as UTF8
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Loop through the map and replace
    foreach ($bad in $mappings.Keys) {
        $content = $content.Replace($bad, $mappings[$bad])
    }
    
    # Write back with UTF8 Encoding (No BOM)
    [System.IO.File]::WriteAllText($file.FullName, $content, (New-Object System.Text.UTF8Encoding($false)))
}

Write-Host "✅ Dataset is now sanitized for training!" -ForegroundColor Green