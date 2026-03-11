#!/usr/bin/env python
"""
CRE Lease Abstraction System - Main Entry Point
Run the complete lease extraction pipeline with a single command
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import Settings
from src.utils.logger import setup_logger, get_logger
from src.extractors.ocr_processor import OCRProcessor
from src.extractors.lease_extractor import LeaseExtractor
from src.validators.schema_validator import SchemaValidator


def main():
    """Main entry point for the application"""
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="CRE Lease Abstraction AI - Extract structured data from lease documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in data/input/
  python main.py
  
  # Process specific file
  python main.py --file "data/input/lease.pdf"
  
  # Process with OpenAI extraction
  python main.py --use-ai
  
  # Batch process with CSV export
  python main.py --export-csv
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Process specific PDF file (default: process all files in data/input/)'
    )
    
    parser.add_argument(
        '--use-ai',
        action='store_true',
        help='Use OpenAI for extraction (requires OPENAI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--export-csv',
        action='store_true',
        help='Export summary CSV file'
    )
    
    parser.add_argument(
        '--skip-ocr',
        action='store_true',
        help='Skip OCR step (use existing raw text files)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Update log level from args
    Settings.LOG_LEVEL = args.log_level
    
    # Setup logger
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("CRE Lease Abstraction System")
    logger.info("=" * 80)
    
    # Ensure directories exist
    Settings.ensure_directories()
    
    # Validate configuration
    logger.info("\nValidating configuration...")
    Settings.validate()
    
    # Initialize components
    try:
        ocr_processor = OCRProcessor() if not args.skip_ocr else None
        lease_extractor = LeaseExtractor(api_key=Settings.OPENAI_API_KEY) if args.use_ai else None
        
        # Determine input files
        if args.file:
            input_files = [Path(args.file)]
            if not input_files[0].exists():
                logger.error(f"File not found: {args.file}")
                return 1
        else:
            input_files = sorted(Settings.INPUT_DIR.glob("*.pdf"))
            if not input_files:
                logger.warning(f"No PDF files found in {Settings.INPUT_DIR}")
                return 0
        
        logger.info(f"\nFound {len(input_files)} file(s) to process")
        
        # Process files
        results = []
        for pdf_file in input_files:
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing: {pdf_file.name}")
            logger.info(f"{'='*80}")
            
            try:
                # Step 1: OCR extraction
                output_raw = Settings.OUTPUT_DIR / f"{pdf_file.stem}_raw.txt"
                
                if not args.skip_ocr and ocr_processor:
                    logger.info("Step 1: Extracting text from PDF...")
                    text, _ = ocr_processor.process_file(pdf_file, output_raw)
                elif output_raw.exists():
                    logger.info("Step 1: Loading existing raw text...")
                    text = output_raw.read_text(encoding='utf-8')
                else:
                    logger.error(f"No raw text file found: {output_raw}")
                    continue
                
                # Step 2: AI extraction (if enabled)
                if args.use_ai and lease_extractor:
                    logger.info("Step 2: Extracting structured data with AI...")
                    
                    extracted_data = lease_extractor.extract_with_ai(text)
                    
                    # Validate
                    validator = SchemaValidator()
                    is_valid, errors = validator.validate(extracted_data)
                    
                    if not is_valid:
                        logger.warning(f"Validation errors: {len(errors)}")
                        for error in errors[:5]:  # Show first 5 errors
                            logger.warning(f"  - {error}")
                    
                    # Save JSON
                    output_json = Settings.OUTPUT_DIR / f"{pdf_file.stem}.json"
                    output_json.write_text(
                        json.dumps(extracted_data, indent=2),
                        encoding='utf-8'
                    )
                    logger.info(f"✓ Saved JSON: {output_json}")
                    
                    results.append({
                        'file': pdf_file.name,
                        'status': 'success',
                        'valid': is_valid,
                        'errors': len(errors) if not is_valid else 0
                    })
                else:
                    logger.info("Step 2: AI extraction skipped (use --use-ai to enable)")
                    results.append({
                        'file': pdf_file.name,
                        'status': 'text_extracted',
                        'raw_text': str(output_raw)
                    })
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}", exc_info=True)
                results.append({
                    'file': pdf_file.name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("PROCESSING SUMMARY")
        logger.info(f"{'='*80}")
        
        successful = sum(1 for r in results if r['status'] in ['success', 'text_extracted'])
        failed = sum(1 for r in results if r['status'] == 'failed')
        
        logger.info(f"Total files: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        
        if args.use_ai:
            valid = sum(1 for r in results if r.get('valid', False))
            logger.info(f"Valid extractions: {valid}")
        
        logger.info(f"\nOutput directory: {Settings.OUTPUT_DIR}")
        logger.info(f"Log directory: {Settings.LOGS_DIR}")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
