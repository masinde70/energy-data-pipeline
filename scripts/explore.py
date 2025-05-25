#!/usr/bin/env python3
"""
ENTSO-E Data Exploration Script

This script loads and explores ENTSO-E electricity load data.
It performs basic exploratory data analysis on the dataset.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

def explore_data():
    """
    Load and explore the ENTSO-E electricity load data.
    """
    # Define the data file path
    data_file = project_root / "data" / "entsoe_load.csv"
    
    # Check if file exists
    if not os.path.exists(data_file):
        print(f"Error: Data file not found at {data_file}")
        print("Please download the ENTSO-E data first and save it to data/entsoe_load.csv")
        sys.exit(1)
    
    # Load the data
    print(f"Loading data from {data_file}...")
    df = pd.read_csv(data_file)
    
    # Basic exploration
    print("\n--- Data Overview ---")
    print(f"Shape: {df.shape}")
    print("\n--- First 5 rows ---")
    print(df.head())
    
    print("\n--- Data Types ---")
    print(df.dtypes)
    
    print("\n--- Summary Statistics ---")
    print(df.describe())
    
    print("\n--- Null Values ---")
    print(df.isnull().sum())
    
    # Check for timestamps
    if 'timestamp' in df.columns:
        print("\n--- Converting timestamps to datetime ---")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Visualize data if load_mw column exists
    if 'load_mw' in df.columns:
        print("\n--- Creating basic visualization ---")
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['load_mw'])
        plt.title('Electricity Load Over Time')
        plt.xlabel('Time')
        plt.ylabel('Load (MW)')
        plt.tight_layout()
        
        # Save plot
        plot_path = project_root / "data" / "load_visualization.png"
        plt.savefig(plot_path)
        print(f"Plot saved to {plot_path}")
        
        # Show plot
        plt.show()

if __name__ == "__main__":
    explore_data()
