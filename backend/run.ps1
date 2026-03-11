# CRE Lease Abstraction AI System
# Quick Start Script for Windows

Write-Host "================================" -ForegroundColor Cyan
Write-Host "CRE Lease Abstraction System" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if in correct directory
if (-not (Test-Path "main.py")) {
    Write-Host "✗ Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import fitz, pytesseract, openai" 2>&1 | Out-Null
    Write-Host "✓ All dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Some dependencies missing. Installing..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check Tesseract
Write-Host ""
Write-Host "Checking Tesseract OCR..." -ForegroundColor Yellow
if (Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe") {
    Write-Host "✓ Tesseract found" -ForegroundColor Green
} else {
    Write-Host "⚠ Tesseract not found at default location" -ForegroundColor Yellow
    Write-Host "  Install from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
}

# Check for PDF files
Write-Host ""
Write-Host "Checking for PDF files..." -ForegroundColor Yellow
$pdfCount = (Get-ChildItem "data\input\*.pdf" -ErrorAction SilentlyContinue).Count
if ($pdfCount -gt 0) {
    Write-Host "✓ Found $pdfCount PDF file(s) in data/input/" -ForegroundColor Green
} else {
    Write-Host "⚠ No PDF files found in data/input/" -ForegroundColor Yellow
    Write-Host "  Please add PDF files to data/input/ directory" -ForegroundColor Yellow
}

# Check OpenAI API key
Write-Host ""
Write-Host "Checking OpenAI API key..." -ForegroundColor Yellow
if ($env:OPENAI_API_KEY) {
    $keyPreview = $env:OPENAI_API_KEY.Substring(0, [Math]::Min(10, $env:OPENAI_API_KEY.Length)) + "..."
    Write-Host "✓ API key found: $keyPreview" -ForegroundColor Green
} else {
    Write-Host "⚠ OPENAI_API_KEY not set (OCR-only mode)" -ForegroundColor Yellow
    Write-Host "  Set with: `$env:OPENAI_API_KEY='your-key'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Ready to run!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage:" -ForegroundColor White
Write-Host "  Basic (OCR only):     python main.py" -ForegroundColor White
Write-Host "  With AI extraction:   python main.py --use-ai" -ForegroundColor White
Write-Host "  Help:                 python main.py --help" -ForegroundColor White
Write-Host ""

# Ask to run
$response = Read-Host "Run the extraction now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Starting extraction..." -ForegroundColor Cyan
    Write-Host ""
    
    if ($env:OPENAI_API_KEY) {
        python main.py --use-ai
    } else {
        python main.py
    }
}
