# CRE Lease Abstraction AI

A sophisticated AI-powered system for extracting structured data from Commercial Real Estate (CRE) lease documents. This tool converts unstructured lease text into standardized JSON format, making lease data easy to analyze, store, and integrate with other systems.

## Features

- **AI-Powered Extraction**: Uses OpenAI GPT-4o for intelligent lease data extraction
- **PDF Support**: Extracts from both text-based and scanned PDF files
- **Batch Processing**: Process multiple lease files at once
- **Fallback Rule-Based Extraction**: Works without API access using pattern matching
- **Comprehensive Schema**: Extracts all critical lease terms including:
  - Lease identification and type
  - Party information (landlord, tenant, guarantor)
  - Premises details
  - Lease term dates
  - Financial terms and rent schedules
  - Options (renewal, termination)
  - Risk flags (co-tenancy, exclusive use, SNDA)
- **Schema Validation**: Ensures extracted data conforms to strict JSON schema
- **Automatic Conversions**:
  - Textual numbers → numeric values
  - Various date formats → ISO format (YYYY-MM-DD)
  - $/SF/year → annual and monthly rent
- **Confidence Scoring**: Provides reliability indicator for extractions
- **Multiple Export Formats**: JSON and CSV output

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up OpenAI API key (optional, but recommended for best results):
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage - Extract from File

```python
from lease_extractor import LeaseExtractor

# Initialize extractor
extractor = LeaseExtractor()

# Extract from file
result = extractor.extract_from_file('path/to/lease.txt')

# Print as JSON
import json
print(json.dumps(result, indent=2))
```

### Extract from Text String

```python
from lease_extractor import LeaseExtractor

lease_text = """
COMMERCIAL LEASE AGREEMENT
Date: January 15, 2024
Landlord: ABC Properties LLC
Tenant: XYZ Corporation
...
"""

extractor = LeaseExtractor()
result = extractor.extract(lease_text)
```

### Command Line Usage

```bash
# Extract from text file
python lease_extractor.py examples/sample_lease_nnn.txt

# Extract from PDF file
python lease_extractor.py leases/lease.pdf

# Run with built-in example
python lease_extractor.py
```

### PDF File Support

The system automatically handles both text-based and scanned PDF files:

```python
from lease_extractor import LeaseExtractor

extractor = LeaseExtractor()

# Works with both .txt and .pdf files
result = extractor.extract_from_file('lease.pdf')
```

**Important Note for Scanned PDFs:**
If your PDFs are scanned images (no searchable text), you'll need to:
1. Use OCR to convert them first (see `SCANNED_PDF_GUIDE.md`)
2. Or use the OCR-enabled extractor (see below)

Quick test to check if your PDF has text:
```bash
python test_pdf.py
```

### Batch Processing Multiple Files

Process all lease files in a folder:

```bash
# Process all PDFs and TXT files in the leases folder
python batch_processor.py leases

# Export options:
# - Single JSON file with all results
# - Individual JSON files per lease
# - CSV summary
# - All formats
```

Example in Python:
```python
from batch_processor import BatchLeaseProcessor

# Initialize processor
processor = BatchLeaseProcessor()

# Process folder
results = processor.process_folder('leases/')

# Export results
processor.export_to_json('all_leases.json')
processor.export_summary_csv('lease_summary.csv')
processor.export_individual_files('output/')
```

### With Validation

```python
from lease_extractor import LeaseExtractor
from schema_validator import SchemaValidator

# Extract lease data
extractor = LeaseExtractor()
result = extractor.extract_from_file('lease.txt')

# Validate the result
is_valid, errors = SchemaValidator.validate(result)

if is_valid:
    print("✓ Extraction successful and valid")
else:
    print("✗ Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

## Output Schema

The system returns JSON in the following format:

```json
{
  "leaseIdentification": {
    "leaseExecutionDate": "2024-01-15",
    "leaseType": "Triple Net"
  },
  "parties": {
    "landlordName": "ABC Properties LLC",
    "tenantName": "XYZ Corporation",
    "guarantorName": "John Smith",
    "isGuaranteed": true
  },
  "premises": {
    "propertyAddress": "450 Technology Drive, San Francisco, CA 94107",
    "premisesDescription": "Suite 300, Third Floor",
    "rentableSquareFeet": 8500
  },
  "leaseTerm": {
    "commencementDate": "2024-02-01",
    "expirationDate": "2031-01-31",
    "rentCommencementDate": "2024-04-01"
  },
  "financialTerms": {
    "baseRentSchedule": [
      {
        "startDate": "2024-04-01",
        "endDate": "2026-03-31",
        "annualRent": 382500,
        "monthlyRent": 31875,
        "currency": "USD"
      }
    ],
    "rentEscalationType": "Fixed Percentage",
    "securityDeposit": 63750,
    "proRataShare": 17.89,
    "operatingExpensePassThrough": "NNN"
  },
  "options": {
    "hasRenewalOption": true,
    "renewalNoticePeriodDays": 270,
    "renewalRentBasis": "FMV",
    "hasTerminationOption": true
  },
  "riskFlags": {
    "coTenancyClause": true,
    "exclusiveUseClause": true,
    "sndaInPlace": true
  },
  "confidenceScore": 92
}
```

## Field Definitions

### Lease Types
- **Full Service**: Landlord pays all operating expenses
- **Modified Gross**: Some operating expenses passed through to tenant above base year
- **Triple Net (NNN)**: Tenant pays proportionate share of taxes, insurance, and CAM
- **Absolute NNN**: Tenant pays all expenses including structural repairs

### Operating Expense Pass-Through Types
- **NNN**: Tenant pays proportionate share of all operating expenses
- **Base Year**: Expenses over base year amount passed to tenant
- **Expense Stop**: Expenses over fixed cap passed to tenant
- **Gross**: No pass-through to tenant

### Rent Escalation Types
- **Fixed Percentage**: Rent increases by set percentage
- **CPI**: Rent tied to Consumer Price Index
- **FMV**: Fair Market Value adjustments
- **Fixed Increase**: Rent increases by fixed dollar amount

### Renewal Rent Basis
- **FMV**: Fair Market Value at renewal
- **Fixed**: Predetermined rent amount
- **CPI**: Based on Consumer Price Index
- **Percentage of Market**: Percentage of market rate

## Examples

See the `examples/` directory for sample lease documents:

- `sample_lease_nnn.txt` - Triple Net lease with co-tenancy and SNDA
- `sample_lease_modified_gross.txt` - Modified Gross lease with base year

## Validation

The `schema_validator.py` module provides comprehensive validation:

```python
from schema_validator import SchemaValidator

# Validate data
is_valid, errors = SchemaValidator.validate(data)

# Validate JSON string
is_valid, errors = SchemaValidator.validate_json_string(json_string)
```

Validation checks include:
- Data types (string, number, boolean, date)
- Date format (YYYY-MM-DD)
- Date logical ordering (expiration after commencement)
- Enumerated values (lease types, escalation types, etc.)
- Numeric ranges (confidence score 0-100, positive values)
- Required vs. optional fields

## Working with PDF Files

### Text-Based PDFs
The system automatically extracts text from PDFs with searchable text:
```bash
python lease_extractor.py lease.pdf
python batch_processor.py leases/
```

### Scanned PDFs (Image-Only)
If your PDFs contain scanned images without text, you have several options:

#### Option 1: Online OCR (Easiest - Free)
1. **Google Drive Method** (Recommended):
   - Upload PDF to Google Drive
   - Right-click → Open with Google Docs
   - File → Download → PDF
   - The new PDF will have searchable text

2. **Online Services**:
   - SmallPDF OCR: https://smallpdf.com/ocr-pdf
   - Adobe Online OCR
   - Soda PDF

#### Option 2: Use Python OCR Support (Advanced)
```bash
# Install Tesseract OCR first:
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Install Python packages
pip install pytesseract pdf2image

# Use OCR-enabled extractor
python lease_extractor_with_ocr.py lease.pdf
```

**Check if PDF needs OCR:**
```bash
python test_pdf.py
```

See `SCANNED_PDF_GUIDE.md` for detailed instructions.

## API Modes

### AI Mode (Recommended)
- Requires OpenAI API key
- Uses GPT-4o for intelligent extraction
- High accuracy and confidence scores (typically 80-95%)
- Handles complex lease language and variations
- Can infer lease types and expense structures

### Rule-Based Mode (Fallback)
- No API key required
- Uses pattern matching and regular expressions
- Lower confidence scores (typically 30-50%)
- Best for well-structured, consistent documents
- Free to use

## Requirements

- Python 3.7+
- openai >= 1.12.0 (for AI mode)
- python-dateutil >= 2.8.2 (for date parsing)
- pdfplumber >= 0.10.0 (for PDF extraction)
- PyPDF2 >= 3.0.0 (for PDF extraction fallback)

**Optional for OCR support on scanned PDFs:**
- pytesseract >= 0.3.10
- pdf2image >= 1.16.3
- Tesseract OCR (system installation)

## Best Practices

1. **Document Quality**: Works best with text-based documents. For PDFs, convert to text first using OCR if needed.

2. **API Key**: Use AI mode for production systems - significantly more accurate.

3. **Validation**: Always validate extracted data before storing or processing.

4. **Confidence Scores**: Review extractions with confidence scores below 70%.

5. **Error Handling**: Implement proper error handling for missing or malformed data.

## Troubleshooting

### Low Confidence Scores
- Ensure document text is clean and readable
- Check for OCR errors if converted from PDF
- Verify lease document is in English
- Use AI mode instead of rule-based mode

### Missing Data
- System returns `null` for fields not found in document
- This is expected behavior - not all leases contain all fields
- Do not treat null values as errors

### Date Format Errors
- System attempts to normalize various date formats
- Manual review may be needed for ambiguous dates (e.g., 01/02/2024)
- Validation will flag invalid date formats

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please review the code documentation and examples provided.

## Version

Current Version: 1.0.0
Last Updated: February 2026
