#!/usr/bin/env python3
"""
ENTSO-E Data Exploration Script

This script loads and explores ENTSO-E electricity load data.
It performs basic exploratory data analysis on the dataset.

Dependencies:
- pandas: For data manipulation
- matplotlib: For data visualization
- loguru (optional): For enhanced logging (install with: pip install loguru)
- pydantic (optional): For data validation (install with: pip install pydantic)

For more information on these libraries, refer to Context7 documentation.

Note: You may see hashlib warnings about blake2b/blake2s, these can be safely
ignored as they don't affect the functionality of this script.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Filter out hashlib warnings for a cleaner output
warnings.filterwarnings("ignore", message=".*blake2.*")
warnings.filterwarnings("ignore", category=UserWarning)

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

def load_and_validate_data(file_path: Path) -> Optional[ENTSOEBatch]:
    """
    Load and validate the ENTSO-E electricity load data.
    
    Args:
        file_path: Path to the CSV data file
    
    Returns:
        ENTSOEBatch object if validation succeeds, None otherwise
    """
    try:
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
        
        # Create ENTSOELoadData objects
        records = []
        validation_errors = 0
        
        for idx, row in df.iterrows():
            try:
                record = ENTSOELoadData(
                    timestamp=row['timestamp'],
                    load_mw=row['load_mw'],
                    region=row['region']
                )
                records.append(record)
            except Exception as e:
                validation_errors += 1
                logger.warning(f"Validation error in row {idx}: {e}")
        
        if validation_errors > 0:
            logger.warning(f"Found {validation_errors} invalid records that were excluded")
            
        if not records:
            logger.error("No valid records found in the dataset")
            return None
            
        # Create batch
        batch_id = f"batch_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        batch = ENTSOEBatch(records=records, batch_id=batch_id)
        logger.success(f"Successfully loaded and validated {len(records)} records")
        
        return batch
        
    except Exception as e:
        logger.exception(f"Error loading data: {e}")
        return None

def explore_data():
    """
    Load and explore the ENTSO-E electricity load data.
    """
    # Define the data file path
    data_file = project_root / "data" / "entsoe_load.csv"
    
    # Check if file exists
    if not os.path.exists(data_file):
        logger.error(f"Data file not found at {data_file}")
        logger.info("Please download the ENTSO-E data first and save it to data/entsoe_load.csv")
        sys.exit(1)
    
    # Load and validate the data
    batch = load_and_validate_data(data_file)
    if not batch:
        logger.error("Failed to load valid data. Exiting.")
        sys.exit(1)
        
    # Get raw dataframe for analysis
    logger.info("Converting validated data back to DataFrame for analysis")
    df = pd.DataFrame([record.model_dump() for record in batch.records])
    
    # Basic exploration
    logger.info("--- Data Overview ---")
    logger.info(f"Shape: {df.shape}")
    logger.info("--- First 5 rows ---")
    logger.info(f"\n{df.head().to_string()}")
    
    logger.info("--- Data Types ---")
    logger.info(f"\n{df.dtypes.to_string()}")
    
    logger.info("--- Summary Statistics ---")
    logger.info(f"\n{df.describe().to_string()}")
    
    logger.info("--- Null Values ---")
    logger.info(f"\n{df.isnull().sum().to_string()}")
    
    # Show time range
    logger.info("--- Time Range ---")
    time_range = f"{df['timestamp'].min()} to {df['timestamp'].max()}"
    logger.info(f"Time range: {time_range}")
    
    # Compute batch statistics
    stats = batch.get_statistics()
    logger.info("--- Batch Statistics ---")
    logger.info(f"Count: {stats['count']}")
    logger.info(f"Average load: {stats['avg_load']:.2f} MW")
    logger.info(f"Min load: {stats['min_load']:.2f} MW")
    logger.info(f"Max load: {stats['max_load']:.2f} MW")
    
    # Visualize data
    logger.info("--- Creating visualization ---")
    plt.figure(figsize=(14, 8))
    plt.plot(df['timestamp'], df['load_mw'], 'b-', linewidth=2, marker='o', markersize=4)
    
    # Add grid and better formatting
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title(f'Electricity Load in {df.iloc[0]["region"]} - {df["timestamp"].min().strftime("%Y-%m-%d")}', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Load (MW)', fontsize=12)
    
    # Add data min/max annotations
    min_load = df['load_mw'].min()
    max_load = df['load_mw'].max()
    min_idx = df['load_mw'].idxmin()
    max_idx = df['load_mw'].idxmax()
    
    plt.annotate(f'Min: {min_load:.1f} MW',
                xy=(df.iloc[min_idx]['timestamp'], min_load),
                xytext=(-20, -30), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))
    
    plt.annotate(f'Max: {max_load:.1f} MW',
                xy=(df.iloc[max_idx]['timestamp'], max_load),
                xytext=(-20, 30), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))
    
    # Add average line
    avg_load = df['load_mw'].mean()
    plt.axhline(y=avg_load, color='r', linestyle='-', alpha=0.7, label=f'Average: {avg_load:.1f} MW')
    plt.legend(loc='lower right')
    
    plt.tight_layout()
    
    # Save plot
    plot_path = project_root / "data" / "load_visualization.png"
    plt.savefig(plot_path, dpi=300)  # Higher resolution
    logger.success(f"Plot saved to {plot_path}")
    
    # Save validated data as JSON
    json_path = project_root / "data" / "validated_load_data.json"
    with open(json_path, 'w') as f:
        json.dump(batch.model_dump(), f, default=str, indent=2)
    logger.success(f"Validated data saved to {json_path}")
    
    # Show plot
    plt.show()

if __name__ == "__main__":
    explore_data()
