# CRE Lease Abstraction - Enterprise Setup Guide

## Directory Structure

```
lease_project/
│
├── main.py                 ⭐ SINGLE COMMAND ENTRY POINT
├── run.ps1                 🚀 Windows startup script
├── requirements.txt        📦 Dependencies
├── README.md               📖 Full documentation
├── .gitignore              📝 Git configuration
│
├── src/                    💻 Source code (organized modules)
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py     ⚙️ Centralized configuration
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── ocr_processor.py        🖼️ OCR extraction
│   │   └── lease_extractor.py      🤖 AI extraction
│   ├── validators/
│   │   ├── __init__.py
│   │   └── schema_validator.py     ✓ Data validation
│   ├── processors/
│   │   ├── __init__.py
│   │   └── batch_processor.py      ⚡ Batch processing
│   └── utils/
│       ├── __init__.py
│       └── logger.py               📋 Logging setup
│
├── data/                   📂 Data directories
│   ├── input/              📥 Place PDF files here
│   │   └── .gitkeep
│   └── output/             📤 Extracted results
│       └── .gitkeep
│
├── logs/                   📊 Application logs
│   └── .gitkeep
│
├── docs/                   📚 Documentation
│   ├── README.md
│   ├── PROJECT_INFO.md
│   ├── SCANNED_PDF_GUIDE.md
│   ├── PDF_EXTRACTION_SETUP.md
│   └── START_HERE.txt
│
└── tests/                  🧪 Test files (future)
```

## Quick Start

### Option 1: PowerShell Script (Windows)
```powershell
.\run.ps1
```
This validates everything and runs the pipeline.

### Option 2: Direct Command Line

**Basic OCR extraction:**
```bash
python main.py
```

**With AI extraction:**
```bash
python main.py --use-ai
```

**Specific file:**
```bash
python main.py --file "data/input/lease.pdf" --use-ai
```

**Help:**
```bash
python main.py --help
```

## Configuration

All configuration is centralized in `src/config/settings.py`:

- **Directories**: Input/output paths
- **OpenAI**: Model, temperature, token limits
- **OCR**: Tesseract path, DPI, language
- **Logging**: Level, format, location
- **Processing**: Batch size, retries, timeouts

## Workflow

1. **Add PDFs** → Place files in `data/input/`
2. **Run command** → Execute `python main.py`
3. **Results** → Check `data/output/`
   - `*.txt` - Raw extracted text
   - `*.json` - Structured lease data (if AI used)
4. **Logs** → Debug in `logs/` directory

## Features

✅ **Enterprise Architecture**
- Modular, well-organized code
- Separation of concerns (config, extractors, validators, processors)
- Professional logging and error handling
- Fully documented

✅ **PDF Processing**
- Digital PDF text extraction
- Scanned PDF OCR with Tesseract
- Automatic fallback from direct text to OCR

✅ **Single Command Execution**
- All logic controlled via `main.py`
- CLI arguments for different modes
- Minimal setup required

✅ **Flexible Operation**
- OCR-only mode (text extraction)
- AI mode (structured data with OpenAI)
- Batch or single file processing
- Pluggable components

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Verify Tesseract: Check `src/config/settings.py` path
3. (Optional) Set OpenAI key: `$env:OPENAI_API_KEY="your-key"`
4. Run: `python main.py` or `.\run.ps1`
5. Check results: `data/output/`

## Troubleshooting

**Module not found error?**
- Ensure you're running from project root directory
- Check `src/` folder contains all modules

**Tesseract error?**
- Install from: https://github.com/UB-Mannheim/tesseract/wiki
- Update path in `src/config/settings.py`

**No files processed?**
- Add PDFs to `data/input/` folder
- Check folder path in `src/config/settings.py`

**API errors?**
- Set OPENAI_API_KEY environment variable
- Run `python main.py` without `--use-ai` to test OCR

## Project Evolution

This started as a simple lease extraction script and has evolved into an enterprise-grade system with:
- ✓ Modular architecture
- ✓ Configuration management
- ✓ Professional logging
- ✓ Error handling
- ✓ CLI interface
- ✓ Batch processing capability
- ✓ Single command execution

**All functionality accessible via one command: `python main.py`**

---

Ready to extract leases! 🎉
