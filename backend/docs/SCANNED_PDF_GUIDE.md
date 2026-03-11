# Handling Scanned PDF Leases

## Problem
Your PDF lease files contain scanned images rather than searchable text. The system detected this when trying to extract text and found no extractable content.

## Solution Options

### Option 1: Use Online OCR Services (Easiest)
Convert your PDFs to text-searchable PDFs using online tools:

1. **Adobe Acrobat Online** (Free trial)
   - Upload PDF → Select "Edit PDF" → "Recognize Text"
   - Download the OCR'd version

2. **SmallPDF** (https://smallpdf.com/ocr-pdf)
   - Free for small files
   - Upload → Convert → Download

3. **Google Drive** (Free)
   - Upload PDF to Google Drive
   - Right-click → Open with Google Docs
   - File → Download → PDF
   - The downloaded PDF will have OCR'd text

### Option 2: Use Desktop Software

1. **Adobe Acrobat Pro** (Paid)
   - Tools → Enhance Scans → Recognize Text

2. **ABBYY FineReader** (Paid)
   - Professional OCR software

### Option 3: Add Python OCR Support (Advanced)

Install Tesseract OCR and Python packages:

#### Windows:
```powershell
# 1. Install Tesseract OCR
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Run the installer (tesseract-ocr-w64-setup-v5.x.x.exe)
# Note the installation path (e.g., C:\Program Files\Tesseract-OCR)

# 2. Add Tesseract to PATH or set environment variable
$env:PATH += ";C:\Program Files\Tesseract-OCR"

# 3. Install Python packages
pip install pytesseract pdf2image
pip install poppler-utils  # Or download poppler binaries

# 4. Enable OCR in the extractor
python lease_extractor_with_ocr.py leases/
```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils
pip install pytesseract pdf2image

# Mac
brew install tesseract poppler
pip install pytesseract pdf2image
```

### Option 4: Use Commercial API Services

1. **Google Cloud Vision API**
   - High accuracy OCR
   - Pay per use

2. **AWS Textract**
   - Document-specific OCR
   - Good for forms and tables

3. **Microsoft Azure Computer Vision**
   - OCR Read API

## Quick Test After OCR

After converting your PDFs, test them:

```powershell
python test_pdf.py
```

Then run the batch processor:

```powershell
python batch_processor.py leases
```

## Current Workaround

If you cannot perform OCR:

1. **Manual Extraction**: Copy text from PDF viewer and save as .txt file
2. **Use AI with Images**: Upload images to ChatGPT/Claude and ask for extraction
3. **Hire Data Entry**: For large volumes, consider outsourcing

## How to Check if Your PDF is Scanned

```python
import pdfplumber

with pdfplumber.open('your_lease.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    if text and len(text.strip()) > 100:
        print("✓ PDF has searchable text")
    else:
        print("✗ PDF is scanned - needs OCR")
```

## Recommendation

For the 3 PDF files in your leases folder:
- **Lakshya-Lease-deed.pdf**
- **LEASE AGREEMENT.pdf**
- **LEASE DEED SPRCPL WITH SPRGT.pdf**

**Recommended approach:**
1. Upload to Google Drive (free)
2. Open each with Google Docs
3. Download as PDF
4. Replace the original files
5. Run: `python batch_processor.py leases`

This will take about 5-10 minutes and is completely free.

## Prevention for Future

When scanning lease documents:
- Use "OCR" or "Searchable PDF" setting on your scanner
- If using a phone camera, use apps that do automatic OCR (Adobe Scan, Microsoft Lens)
- Request digital/searchable PDFs from landlords/tenants when possible
