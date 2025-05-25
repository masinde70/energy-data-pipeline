#!/usr/bin/env python3
"""
ENTSO-E Data Processing Script

This script processes ENTSO-E electricity load data using Pydantic models for validation
and Loguru for enhanced logging. Both packages are optional but recommended for 
best performance and data quality.

Dependencies:
- pandas: For data manipulation
- loguru (optional): For enhanced logging (install with: pip install loguru)
- pydantic (optional): For data validation (install with: pip install pydantic)

For more information on these libraries, refer to Context7 documentation.
"""

import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

# Check for required dependencies
missing_dependencies = []
try:
    import loguru
except ImportError:
    missing_dependencies.append("loguru")

try:
    import pydantic
except ImportError:
    missing_dependencies.append("pydantic")

if missing_dependencies:
    print(f"Warning: Missing optional dependencies: {', '.join(missing_dependencies)}")
    print("For full functionality, install them with: pip install " + " ".join(missing_dependencies))
    print("Refer to Context7 documentation for more details on these packages.")

# Import custom modules
from logging_setup import setup_logging
from models import ENTSOELoadData, ENTSOEBatch

# Set up logging
logger = setup_logging()

def load_data(file_path: str) -> Optional[ENTSOEBatch]:
    """Load and validate ENTSO-E data from CSV.
    
    Args:
        file_path: Path to the CSV data file
        
    Returns:
        ENTSOEBatch object if validation succeeds, None otherwise
    """
    try:
        # Read the CSV file
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        
        # Check required columns
        required_columns = ['timestamp', 'load_mw', 'region']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return None
            
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Convert DataFrame to list of ENTSOELoadData objects
        records = []
        validation_errors = 0
        
        for idx, row in df.iterrows():
            try:
                record = ENTSOELoadData(
                    timestamp=row['timestamp'],
                    load_mw=float(row['load_mw']),
                    region=row['region']
                )
                records.append(record)
            except Exception as e:
                validation_errors += 1
                logger.warning(f"Validation error in row {idx}: {e}")
        
        if validation_errors > 0:
            logger.warning(f"Found {validation_errors} invalid records out of {len(df)}")
            
        if not records:
            logger.error("No valid records found in the dataset")
            return None
        
        # Create and return a batch
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.success(f"Successfully loaded {len(records)} valid records into batch {batch_id}")
        return ENTSOEBatch(records=records, batch_id=batch_id)
    
    except Exception as e:
        logger.exception(f"Error loading data: {e}")
        return None

def process_batch(batch: ENTSOEBatch) -> bool:
    """Process a batch of ENTSO-E data.
    
    Args:
        batch: The batch of data to process
        
    Returns:
        True if processing succeeded, False otherwise
    """
    try:
        logger.info(f"Processing batch {batch.batch_id} with {len(batch.records)} records")
        
        # Get statistics
        stats = batch.get_statistics()
        logger.info(f"Batch statistics: {stats}")
        
        # Example processing: calculate hourly averages
        df = pd.DataFrame([record.model_dump() for record in batch.records])
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour')['load_mw'].mean()
        
        logger.info("Hourly load averages:")
        for hour, avg_load in hourly_avg.items():
            logger.info(f"Hour {hour}: {avg_load:.2f} MW")
        
        # Mark batch as processed
        batch.mark_processed()
        logger.success(f"Successfully processed batch {batch.batch_id} at {batch.processed_at}")
        return True
    
    except Exception as e:
        logger.exception(f"Error processing batch {batch.batch_id}: {e}")
        return False

def main(file_path: str) -> int:
    """Main function to load and process data.
    
    Args:
        file_path: Path to the input CSV file
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("Starting data processing pipeline")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return 1
    
    # Load and validate data
    batch = load_data(file_path)
    if not batch:
        logger.error("Failed to load valid data")
        return 1
    
    # Process the batch
    success = process_batch(batch)
    if not success:
        logger.error("Failed to process batch")
        return 1
    
    logger.success("Pipeline completed successfully")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Please provide a file path")
        sys.exit(1)
    
    file_path = sys.argv[1]
    exit_code = main(file_path)
    sys.exit(exit_code)
