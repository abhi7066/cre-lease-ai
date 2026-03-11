"""
Batch Processor for CRE Lease Abstraction
Processes multiple lease files (PDF or TXT) from a folder and exports results
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from lease_extractor import LeaseExtractor
from schema_validator import SchemaValidator


class BatchLeaseProcessor:
    """Process multiple lease files in batch and export results."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the batch processor.
        
        Args:
            api_key: OpenAI API key (optional)
        """
        self.extractor = LeaseExtractor(api_key=api_key)
        self.results = []
    
    def process_folder(self, folder_path: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Process all lease files in a folder.
        
        Args:
            folder_path: Path to folder containing lease files
            file_types: List of file extensions to process (default: ['.pdf', '.txt'])
            
        Returns:
            List of extraction results with metadata
        """
        if file_types is None:
            file_types = ['.pdf', '.txt']
        
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        # Find all lease files
        lease_files = []
        for ext in file_types:
            lease_files.extend(folder.glob(f"*{ext}"))
        
        if not lease_files:
            print(f"No lease files found in {folder_path}")
            return []
        
        print(f"Found {len(lease_files)} lease file(s) to process")
        print("=" * 80)
        
        results = []
        for i, file_path in enumerate(lease_files, 1):
            print(f"\n[{i}/{len(lease_files)}] Processing: {file_path.name}")
            print("-" * 80)
            
            try:
                # Extract lease data
                start_time = datetime.now()
                result = self.extractor.extract_from_file(str(file_path))
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Validate
                is_valid, errors = SchemaValidator.validate(result)
                
                # Add metadata
                extraction_result = {
                    "metadata": {
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "processed_at": datetime.now().isoformat(),
                        "processing_time_seconds": round(processing_time, 2),
                        "validation_status": "PASSED" if is_valid else "FAILED",
                        "validation_errors": errors if not is_valid else []
                    },
                    "lease_data": result
                }
                
                results.append(extraction_result)
                
                # Print summary
                print(f"✓ Extraction complete in {processing_time:.2f}s")
                if is_valid:
                    print("✓ Validation passed")
                else:
                    print(f"⚠ Validation issues: {len(errors)} error(s)")
                
                # Print key info
                parties = result.get('parties', {})
                premises = result.get('premises', {})
                print(f"  Landlord: {parties.get('landlordName', 'N/A')[:50]}")
                print(f"  Tenant: {parties.get('tenantName', 'N/A')[:50]}")
                print(f"  Size: {premises.get('rentableSquareFeet', 'N/A')} SF" if premises.get('rentableSquareFeet') else "  Size: N/A")
                print(f"  Confidence: {result.get('confidenceScore', 0)}/100")
                
            except Exception as e:
                print(f"✗ Error processing {file_path.name}: {str(e)}")
                extraction_result = {
                    "metadata": {
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "processed_at": datetime.now().isoformat(),
                        "processing_time_seconds": 0,
                        "validation_status": "ERROR",
                        "validation_errors": [str(e)]
                    },
                    "lease_data": None
                }
                results.append(extraction_result)
        
        self.results = results
        return results
    
    def export_to_json(self, output_file: str = None, pretty: bool = True):
        """
        Export all results to a single JSON file.
        
        Args:
            output_file: Output file path (default: results_TIMESTAMP.json)
            pretty: Whether to format JSON with indentation
        """
        if not self.results:
            print("No results to export")
            return
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"lease_extraction_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(self.results, f, indent=2)
            else:
                json.dump(self.results, f)
        
        print(f"\n✓ Results exported to: {output_file}")
    
    def export_individual_files(self, output_folder: str = "output"):
        """
        Export each lease extraction to a separate JSON file.
        
        Args:
            output_folder: Folder to save individual JSON files
        """
        if not self.results:
            print("No results to export")
            return
        
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)
        
        for result in self.results:
            filename = result['metadata']['filename']
            base_name = os.path.splitext(filename)[0]
            output_file = output_path / f"{base_name}_extracted.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
        
        print(f"\n✓ {len(self.results)} file(s) exported to: {output_folder}/")
    
    def export_summary_csv(self, output_file: str = None):
        """
        Export a summary CSV with key lease information.
        
        Args:
            output_file: Output CSV file path (default: lease_summary_TIMESTAMP.csv)
        """
        if not self.results:
            print("No results to export")
            return
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"lease_summary_{timestamp}.csv"
        
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Filename',
                'Landlord',
                'Tenant',
                'Property Address',
                'Square Feet',
                'Lease Type',
                'Commencement Date',
                'Expiration Date',
                'Security Deposit',
                'Operating Expense Type',
                'Renewal Option',
                'Confidence Score',
                'Validation Status'
            ])
            
            # Data rows
            for result in self.results:
                metadata = result['metadata']
                lease_data = result.get('lease_data')
                
                if lease_data:
                    parties = lease_data.get('parties', {})
                    premises = lease_data.get('premises', {})
                    lease_id = lease_data.get('leaseIdentification', {})
                    term = lease_data.get('leaseTerm', {})
                    financial = lease_data.get('financialTerms', {})
                    options = lease_data.get('options', {})
                    
                    writer.writerow([
                        metadata['filename'],
                        parties.get('landlordName', ''),
                        parties.get('tenantName', ''),
                        premises.get('propertyAddress', ''),
                        premises.get('rentableSquareFeet', ''),
                        lease_id.get('leaseType', ''),
                        term.get('commencementDate', ''),
                        term.get('expirationDate', ''),
                        financial.get('securityDeposit', ''),
                        financial.get('operatingExpensePassThrough', ''),
                        'Yes' if options.get('hasRenewalOption') else 'No',
                        lease_data.get('confidenceScore', 0),
                        metadata['validation_status']
                    ])
                else:
                    writer.writerow([
                        metadata['filename'],
                        'ERROR', '', '', '', '', '', '', '', '', '', 0,
                        metadata['validation_status']
                    ])
        
        print(f"✓ Summary exported to: {output_file}")
    
    def print_summary(self):
        """Print a summary of processing results."""
        if not self.results:
            print("No results available")
            return
        
        print("\n" + "=" * 80)
        print(" BATCH PROCESSING SUMMARY")
        print("=" * 80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['metadata']['validation_status'] == 'PASSED')
        failed = sum(1 for r in self.results if r['metadata']['validation_status'] == 'FAILED')
        errors = sum(1 for r in self.results if r['metadata']['validation_status'] == 'ERROR')
        
        print(f"\nTotal Files Processed: {total}")
        print(f"  ✓ Validation Passed: {passed}")
        print(f"  ⚠ Validation Issues: {failed}")
        print(f"  ✗ Processing Errors: {errors}")
        
        if self.results:
            successful_results = [r for r in self.results if r['lease_data']]
            if successful_results:
                avg_confidence = sum(
                    r['lease_data'].get('confidenceScore', 0) 
                    for r in successful_results
                ) / len(successful_results)
                
                print(f"\nAverage Confidence Score: {avg_confidence:.1f}/100")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point for batch processing."""
    import sys
    
    print("=" * 80)
    print(" CRE LEASE ABSTRACTION - BATCH PROCESSOR")
    print("=" * 80)
    print()
    
    # Check for API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print("✓ OpenAI API key detected - using AI mode (high accuracy)")
    else:
        print("⚠ No OpenAI API key - using rule-based mode (limited accuracy)")
        print("  Set OPENAI_API_KEY environment variable for better results")
    
    print()
    
    # Get folder path
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = "leases"
        print(f"No folder specified. Using default: {folder_path}/")
    
    print()
    
    # Process leases
    processor = BatchLeaseProcessor()
    
    try:
        results = processor.process_folder(folder_path)
        
        if results:
            # Print summary
            processor.print_summary()
            
            # Ask for export options
            print("\nExport Options:")
            print("  1. Single JSON file with all results")
            print("  2. Individual JSON files per lease")
            print("  3. CSV summary")
            print("  4. All of the above")
            print("  5. Skip export")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                processor.export_to_json()
            elif choice == '2':
                processor.export_individual_files()
            elif choice == '3':
                processor.export_summary_csv()
            elif choice == '4':
                processor.export_to_json()
                processor.export_individual_files()
                processor.export_summary_csv()
            else:
                print("Skipping export")
            
            print("\n✓ Batch processing complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
