$ErrorActionPreference = "Stop"

# Absolute Windows path to this script's folder
$WorkDir = $PSScriptRoot
Set-Location $WorkDir

Write-Host "Working directory: $WorkDir"
Write-Host ""

function Check-DockerStatus {
    param (
        [string]$Step
    )

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: $Step failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }

    Write-Host "Success!" -ForegroundColor Green
    Write-Host ""
}

function Validate-Yaml {
    Write-Host "---- Validating profile.yaml ----"

    if (-not (Test-Path "$WorkDir\profile.yaml")) {
        Write-Host "ERROR: profile.yaml not found." -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }

    docker pull jrvs/yamale
    Check-DockerStatus "Pulling Yamale"

    docker pull mikefarah/yq:3.3.4
    Check-DockerStatus "Pulling yq"

    docker run --rm `
        -v "$($WorkDir):/workdir" `
        jrvs/yamale `
        yamale -s /schema/profile_schema.yaml profile.yaml

    Check-DockerStatus "YAML validation"
}

function Get-ProfileName {
    Write-Host "---- Parsing metadata ----"

    $rawName = docker run --rm `
        -v "$($WorkDir):/workdir" `
        mikefarah/yq:3.3.4 `
        yq r profile.yaml name

    Check-DockerStatus "Reading profile name"

    $script:ProfileName = $rawName.Trim() -replace '\s+', '_'
    $script:ProfilePrefix = "jarvis_profile_$ProfileName"

    Write-Host "Profile name: $ProfileName"
    Write-Host "PDF name: $ProfilePrefix.pdf"
    Write-Host ""
}

function Convert-YamlToJson {
    Write-Host "---- Converting YAML to JSON ----"

    # Let Docker write directly into the mounted folder.
    # This avoids PowerShell output encoding/redirection issues.
    docker run --rm `
        -v "$($WorkDir):/workdir" `
        mikefarah/yq:3.3.4 `
        sh -c "yq r -j --prettyPrint profile.yaml > profile.json"

    Check-DockerStatus "YAML to JSON conversion"

    if (Test-Path "$WorkDir\profile.json") {
        Write-Host "Updated: $WorkDir\profile.json"
    }
    else {
        Write-Host "ERROR: profile.json was not created." -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }

    Write-Host ""
}

function Render-Markdown {
    Write-Host "---- Rendering profile.md ----"

    docker pull jrvs/render_profile_md
    Check-DockerStatus "Pulling Markdown renderer"

    docker run --rm `
        -v "$($WorkDir):/workdir" `
        jrvs/render_profile_md `
        profile.yaml profile.md

    Check-DockerStatus "Rendering Markdown"

    if (-not (Test-Path "$WorkDir\profile.md")) {
        Write-Host "ERROR: profile.md was not created." -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }
}

function Render-Pdf {
    Write-Host "---- Rendering PDF ----"

    $outputPdf = "$ProfilePrefix.pdf"

    docker pull pandoc/latex:2.9.2.1
    Check-DockerStatus "Pulling Pandoc"

    docker run --rm `
        -v "$($WorkDir):/data" `
        pandoc/latex:2.9.2.1 `
        profile.md `
        -f markdown `
        -t pdf `
        -s `
        --pdf-engine=xelatex `
        -V pagestyle=empty `
        -V fontsize=8pt `
        -V "geometry:top=1.75cm,bottom=1.75cm,left=1.5cm,right=1.5cm" `
        -o $outputPdf

    Check-DockerStatus "Rendering PDF"

    if (Test-Path "$WorkDir\$outputPdf") {
        Write-Host "Updated: $WorkDir\$outputPdf" -ForegroundColor Green
    }
    else {
        Write-Host "ERROR: PDF was not created." -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }

    Write-Host ""
}

try {
    Validate-Yaml
    Get-ProfileName
    Convert-YamlToJson
    Render-Markdown
    Render-Pdf

    Write-Host "===================================="
    Write-Host "DONE" -ForegroundColor Green
    Write-Host "JSON: $WorkDir\profile.json"
    Write-Host "PDF : $WorkDir\$ProfilePrefix.pdf"
    Write-Host "===================================="
}
catch {
    Write-Host ""
    Write-Host "PowerShell error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Read-Host "Press Enter to close"