# CRE Lease Abstraction AI System

Enterprise-grade Commercial Real Estate lease document extraction and analysis system.

## Overview

This system automatically extracts structured data from CRE lease documents using OCR and optional AI-powered extraction with OpenAI GPT-4.

### Features

- **PDF Text Extraction**: Handles both digital and scanned PDFs
- **OCR Support**: Automatic OCR using Tesseract for scanned documents
- **AI Extraction**: Optional OpenAI GPT-4 integration for intelligent data extraction
- **Schema Validation**: Comprehensive validation of extracted lease data
- **Batch Processing**: Process multiple documents efficiently
- **Enterprise Architecture**: Modular, maintainable, and scalable design
- **Comprehensive Logging**: Detailed logs for debugging and auditing
- **Single Command Execution**: Run the entire pipeline with one command

## Quick Start

### Prerequisites

- Python 3.8+
- Tesseract OCR installed (for scanned PDFs)
- OpenAI API key (optional, for AI extraction)

### Installation

1. **Clone or download the repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set OpenAI API key (optional):**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

### Usage

#### Process all PDFs in `data/input/` (OCR only):
```bash
python main.py
```

#### Process with AI extraction:
```bash
python main.py --use-ai
```

#### Process specific file:
```bash
python main.py --file "data/input/mylease.pdf" --use-ai
```

#### Use existing raw text files (skip OCR):
```bash
python main.py --skip-ocr --use-ai
```

#### Enable debug logging:
```bash
python main.py --log-level DEBUG
```

## Project Structure

```
lease_project/
├── main.py                 # Single entry point - run this!
├── requirements.txt        # Python dependencies
├── src/                    # Source code
│   ├── config/            # Configuration
│   │   └── settings.py    # Centralized settings
│   ├── extractors/        # Data extraction
│   │   ├── ocr_processor.py      # PDF OCR
│   │   └── lease_extractor.py    # AI extraction
│   ├── validators/        # Data validation
│   │   └── schema_validator.py
│   ├── processors/        # Batch processing
│   │   └── batch_processor.py
│   └── utils/             # Utilities
│       └── logger.py      # Logging setup
├── data/
│   ├── input/            # Place PDF files here
│   └── output/           # Extracted text and JSON
├── logs/                 # Application logs
├── docs/                 # Documentation
└── tests/               # Test files

```

## Workflow

The system follows a clear pipeline:

1. **Input**: Place PDF lease documents in `data/input/`
2. **OCR Extraction**: Extract text from PDFs (handles both digital and scanned)
3. **AI Extraction**: (Optional) Use OpenAI to extract structured data
4. **Validation**: Validate extracted data against schema
5. **Output**: Save results to `data/output/`
   - `*_raw.txt`: Raw extracted text
   - `*.json`: Structured lease data (if AI extraction used)

## Configuration

Edit `src/config/settings.py` to customize:

- Input/output directories
- OpenAI model and parameters
- OCR settings (DPI, language)
- Logging configuration
- Retry and batch settings

## Extracted Data Schema

The system extracts comprehensive lease information:

- **Lease Identification**: Execution date, lease type
- **Parties**: Landlord, tenant, guarantor
- **Premises**: Property address, square footage, parking
- **Term**: Start date, end date, duration
- **Financial Terms**: Base rent, security deposit, rent escalations
- **Operating Expenses**: Passthroughs, expense stops
- **Options**: Renewal, expansion, termination, purchase
- **Maintenance**: Repair responsibilities
- **Insurance & Risk**: Coverage requirements, liability
- **Default & Remedies**: Events of default, cure periods

See `docs/PROJECT_INFO.md` for complete schema details.

## Output Files

After processing, you'll find in `data/output/`:

- `Commercial_Lease_Agreement_1_raw.txt` - Raw extracted text
- `Commercial_Lease_Agreement_1.json` - Structured data (if AI used)

Logs are saved in `logs/` directory.

## Troubleshooting

### Tesseract Not Found
- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- Update path in `src/config/settings.py` if installed elsewhere

### OpenAI API Errors
- Verify API key is set: `echo $env:OPENAI_API_KEY` (Windows)
- Check API key has sufficient credits
- Verify network connectivity

### No Text Extracted
- Ensure PDF is not corrupted
- For scanned PDFs, verify Tesseract is installed
- Check logs in `logs/` directory for details

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Extractors
1. Create new extractor in `src/extractors/`
2. Import in `src/extractors/__init__.py`
3. Update `main.py` to use new extractor

## Documentation

Additional documentation in `docs/`:

- `PROJECT_INFO.md` - Detailed project information
- `SCANNED_PDF_GUIDE.md` - Guide for handling scanned PDFs
- `PDF_EXTRACTION_SETUP.md` - Detailed setup instructions

## License

Proprietary - Internal use only

## Support

For issues or questions, contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: February 2026
