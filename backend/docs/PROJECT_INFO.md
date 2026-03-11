# CRE Lease Abstraction AI - Project Structure

## Overview
This project provides an AI-powered system for extracting structured data from Commercial Real Estate lease documents.

## Project Files

### Core Modules
- **lease_extractor.py** - Main extraction engine with AI and rule-based modes, supports PDF and text files
- **lease_extractor_with_ocr.py** - Extended extractor with OCR support for scanned PDFs
- **schema_validator.py** - Comprehensive schema validation for extracted data
- **batch_processor.py** - Process multiple lease files and export results

### Scripts
- **quick_start.py** - User-friendly interface for quick extractions
- **test_extraction.py** - Comprehensive test suite demonstrating all features
- **test_pdf.py** - Quick utility to test if PDFs have extractable text

### Examples
- **examples/sample_lease_nnn.txt** - Triple Net lease with complex clauses
- **examples/sample_lease_modified_gross.txt** - Modified Gross lease example
- **leases/** - Folder for your PDF lease files

### Documentation
- **README.md** - Complete documentation and usage guide
- **SCANNED_PDF_GUIDE.md** - Guide for handling scanned PDF documents
- **PROJECT_INFO.md** - This file - project structure overview
- **requirements.txt** - Python package dependencies

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Set API Key (Optional but Recommended)
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

### Run Examples

**Quick Start Interface:**
```bash
python quick_start.py examples/sample_lease_nnn.txt
python quick_start.py leases/lease.pdf
```

**Batch Process All Leases:**
```bash
python batch_processor.py leases
```

**Test Suite:**
```bash
python test_extraction.py
```

**Direct Usage:**
```bash
python lease_extractor.py examples/sample_lease_nnn.txt
python lease_extractor.py leases/lease.pdf
```

**OCR for Scanned PDFs:**
```bash
python lease_extractor_with_ocr.py leases/scanned_lease.pdf
```

## Python API Usage

```python
from lease_extractor import LeaseExtractor
from schema_validator import SchemaValidator
import json

# Extract from file
extractor = LeaseExtractor()
result = extractor.extract_from_file('lease.txt')

# Validate
is_valid, errors = SchemaValidator.validate(result)

# Use the data
if is_valid:
    print(json.dumps(result, indent=2))
```

## Features

✓ AI-powered extraction using GPT-4o
✓ PDF support (text-based PDFs)
✓ OCR support for scanned PDFs (optional)
✓ Batch processing of multiple files
✓ Export to JSON and CSV formats
✓ Fallback rule-based extraction (no API key needed)
✓ Comprehensive JSON schema validation
✓ Automatic format conversions (dates, currencies, numbers)
✓ Confidence scoring
✓ Risk flag detection
✓ Renewal and termination option parsing
✓ Multiple rent period handling

## Extracted Data Points

- **Lease Identification**: Execution date, lease type
- **Parties**: Landlord, tenant, guarantor information
- **Premises**: Address, description, square footage
- **Lease Term**: Commencement, expiration, rent start dates
- **Financial Terms**: 
  - Base rent schedule with multiple periods
  - Rent escalation type
  - Security deposit
  - Pro rata share
  - Operating expense pass-through structure
- **Options**: Renewal and termination rights
- **Risk Flags**: Co-tenancy, exclusive use, SNDA

## Supported Lease Types

- **Full Service** - Landlord pays all operating expenses
- **Modified Gross** - Base year expense structure
- **Triple Net (NNN)** - Tenant pays taxes, insurance, CAM
- **Absolute NNN** - Tenant pays all expenses including structural

## Operating Modes

### AI Mode (Recommended)
- Requires OpenAI API key
- Uses GPT-4o for intelligent extraction
- High accuracy (80-95% confidence)
- Handles complex lease language
- Can infer lease types and structures

### Rule-Based Mode (Fallback)
- No API key required
- Uses pattern matching
- Moderate accuracy (30-50% confidence)
- Best for structured documents
- Free to use

## Validation

The schema validator checks:
- Data types (strings, numbers, booleans, dates)
- Date formats (ISO 8601: YYYY-MM-DD)
- Enumerated values (lease types, escalation types, etc.)
- Logical relationships (expiration after commencement)
- Required vs optional fields
- Numeric ranges and constraints

## Confidence Scoring

- **85-100**: High confidence - ready for production use
- **70-84**: Moderate confidence - spot check recommended
- **Below 70**: Low confidence - manual review required

## Best Practices

1. **Use AI Mode** for production systems (much higher accuracy)
2. **Validate All Data** before storing or processing
3. **Review Low Confidence** extractions manually
4. **Clean Input Text** for best results (remove OCR errors)
5. **Handle Nulls Gracefully** - not all leases contain all fields

## Error Handling

The system gracefully handles:
- Missing or incomplete data (returns null)
- Various date formats
- Textual number representations
- Multiple rent periods
- Complex clause structures

## Output Format

All output is valid JSON conforming to the defined schema. Fields not found in the source document are set to `null` rather than omitted.

## Version

Current Version: 1.0.0
Python: 3.7+
Last Updated: February 2026

## Support

For detailed documentation, see README.md
For examples, run test_extraction.py
For quick usage, run quick_start.py
