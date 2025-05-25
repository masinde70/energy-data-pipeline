#!/usr/bin/env python3
"""
Data models for the energy-data-pipeline.

This module defines Pydantic models for validating ENTSO-E electricity load data.
When Pydantic is installed, it provides advanced validation and schema enforcement.
When Pydantic is not available, the module provides fallback mechanisms that mimic
the core functionality while maintaining API compatibility.

Data Model Features:
    - Type validation for all fields
    - Domain-specific validation (e.g., load must be positive)
    - Logical validation (e.g., timestamps cannot be in the future)
    - Batch processing capabilities with statistics

Design Decisions:
    - Graceful degradation when dependencies are missing
    - Consistent API regardless of available packages
    - Clear error messages with installation instructions
    - Data validation even without Pydantic through manual checks

For more information on Pydantic, refer to Context7 documentation.
"""
# =========================================================================
# IMPORT SECTION
# =========================================================================

# Import standard library modules
from typing import List, Optional, Dict, Any  # Type hints for better code documentation
from datetime import datetime  # For timestamp handling and validation against current time
import sys  # For system-specific parameters and functions (primarily for error reporting)

# =========================================================================
# PYDANTIC IMPORT WITH GRACEFUL FALLBACK
# =========================================================================

# Try to import Pydantic for advanced data validation, with graceful fallback if not available
try:
    # Import Pydantic components for robust data validation
    from pydantic import BaseModel, Field, field_validator
    
    # Flag to indicate Pydantic is available and will be used
    # This flag controls conditional behavior throughout the module
    USING_PYDANTIC = True
    
except ImportError:
    # Provide informative message to guide users when Pydantic is missing
    # These messages appear only once during import, not during runtime execution
    print("Note: Pydantic is not installed. Using basic data classes without advanced validation.")
    print("For comprehensive data validation, install pydantic: pip install pydantic")
    print("Refer to Context7 documentation for more details on Pydantic's benefits.")
    
    # =====================================================================
    # FALLBACK IMPLEMENTATION SECTION
    # =====================================================================
    
    # Create simple fallback classes that mimic Pydantic behavior
    # This ensures the rest of the code can run without modification
    class BaseModel:
        """Simple BaseModel fallback when Pydantic is not available.
        
        This class provides a minimal implementation that maintains API compatibility
        with Pydantic's BaseModel, supporting attribute setting and dictionary conversion.
        It doesn't perform validation like Pydantic would.
        """
        
        def __init__(self, **kwargs):
            """Initialize object by setting attributes from keyword arguments.
            
            Args:
                **kwargs: Key-value pairs to set as object attributes
            """
            # Set each provided keyword argument as an attribute on this object
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def model_dump(self) -> Dict[str, Any]:
            """Return a dictionary of all the model's attributes.
            
            This mimics Pydantic's model_dump method (formerly dict() in Pydantic v1)
            for API compatibility.
            
            Returns:
                Dictionary with attribute names as keys and their values, excluding private attributes
            """
            # Convert object to dict, excluding private attributes (those starting with '_')
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    # Simple placeholder for Field - used when Pydantic is not installed
    def Field(**kwargs):
        """Placeholder for Pydantic Field function.
        
        In Pydantic, Field() provides validation and metadata. This version
        ignores validation parameters but maintains API compatibility so code
        using Field() will still run without modification.
        
        Args:
            **kwargs: Field constraints that would normally be applied by Pydantic
                      (e.g., gt=0 for values greater than zero)
        
        Returns:
            None, as we can't enforce field constraints without Pydantic
        """
        # Return None as we can't enforce field constraints without Pydantic
        return None
    
    # Simple placeholder for field_validator - used when Pydantic is not installed
    def field_validator(*args, **kwargs):
        """Placeholder for Pydantic field_validator decorator.
        
        In Pydantic, field_validator decorates functions that validate specific fields.
        This version creates a no-op decorator to maintain API compatibility so code
        using @field_validator will still run without modification.
        
        Args:
            *args: Positional arguments that would be passed to field_validator
            **kwargs: Keyword arguments that would be passed to field_validator
        
        Returns:
            A decorator function that returns the original function unchanged
        """
        # Return a decorator that doesn't modify the function (no-op)
        def decorator(func):
            return func  # Just return the original function unchanged
        return decorator
    
    # Flag to indicate we're using the fallback implementation
    # This flag controls conditional behavior throughout the module
    USING_PYDANTIC = False

class ENTSOELoadData(BaseModel):
    """Model for ENTSO-E load data.
    
    Represents a single electricity load data point with timestamp, load value, and region.
    Includes validation to ensure data quality based on both physical and logical constraints.
    
    Physical constraints:
        - Load values must be positive (electricity consumption is always > 0)
    
    Logical constraints:
        - Timestamps cannot be in the future (we can't have future data)
        
    This class works in two modes:
        1. With Pydantic: Uses schema-based validation with automatic error messages
        2. Without Pydantic: Uses manual validation in __init__ with the same rules
    """
    
    def __init__(self, timestamp: datetime, load_mw: float, region: str, **kwargs):
        """Initialize with validation regardless of whether Pydantic is available.
        
        This constructor ensures core validation rules are applied even without Pydantic.
        When Pydantic is available, these validations happen twice (here and in Pydantic),
        but that's acceptable for ensuring data integrity.
        
        Args:
            timestamp: The date and time when the load was measured
            load_mw: The electricity load in megawatts (must be positive)
            region: The geographic region where the load was measured
            **kwargs: Additional attributes to store (for extensibility)
        
        Raises:
            ValueError: If load_mw is not positive or timestamp is in the future
        """
        # Perform basic validations even without Pydantic
        # These are essential business rules that must be enforced regardless of dependencies
        
        # VALIDATION 1: Ensure load is always positive (basic physics constraint)
        # Electrical load can never be negative or zero in real-world scenarios
        if load_mw <= 0:
            raise ValueError("load_mw must be positive (got {})".format(load_mw))
            
        # VALIDATION 2: Prevent data from the future (logical constraint)
        # We cannot have measurements from times that haven't happened yet
        current_time = datetime.now()
        if timestamp > current_time:
            raise ValueError(
                f"Timestamp cannot be in the future. Current time: {current_time}, got: {timestamp}"
            )
            
        # Once validations pass, set attributes by calling parent class initializer
        # This handles the actual attribute setting differently depending on whether
        # we're using the real Pydantic or our fallback implementation
        super().__init__(timestamp=timestamp, load_mw=load_mw, region=region, **kwargs)
    
    # =====================================================================
    # PYDANTIC SCHEMA DEFINITION
    # =====================================================================
    # This conditional block is only evaluated when Pydantic is available
    # It defines the schema with type annotations and validation rules
    if USING_PYDANTIC:
        # These type annotations with validators are only applied if Pydantic is available.
        # They provide additional schema information, automatic validation, and serialization capabilities.
        # When Pydantic is available, these declarations override the manual validations above.
        
        # The timestamp when the load was measured
        # Type annotation tells Pydantic to expect and validate as datetime object
        timestamp: datetime
        
        # The electricity load in megawatts (must be positive)
        # Field(gt=0) creates a constraint that the value must be greater than 0
        # This will be automatically enforced by Pydantic's validation system
        load_mw: float = Field(
            gt=0,  # Greater than zero constraint
            description="Electricity load in megawatts (must be positive)"
        )
        
        # The geographic region where the load was measured
        # Simple string type without additional constraints
        region: str = Field(
            description="Geographic region identifier for the measurement"
        )
        
        @field_validator('timestamp')
        @classmethod  # Required for Pydantic v2 field validators
        def check_timestamp_not_future(cls, value):
            """Validate that timestamp is not in the future.
            
            This is a Pydantic validator that runs automatically during object creation
            when Pydantic is available. It enforces the business rule that we cannot
            have data from the future.
            
            Args:
                value: The timestamp to validate
                
            Returns:
                The validated timestamp (unchanged if valid)
                
            Raises:
                ValueError: If timestamp is in the future
            """
            current_time = datetime.now()
            if value > current_time:
                raise ValueError(
                    f"Timestamp cannot be in the future. Current time: {current_time}, got: {value}"
                )
            return value

class ENTSOEBatch(BaseModel):
    """Batch of ENTSO-E electricity load data records.
    
    Groups multiple ENTSOELoadData records together for efficient batch processing.
    Tracks batch processing status and provides statistical methods for analysis.
    
    Key features:
        - Grouping related records for atomic operations
        - Tracking processing status with timestamps
        - Calculating aggregate statistics across multiple records
        - Maintaining data lineage with batch identifiers
    
    Typical usage:
        1. Load and validate multiple ENTSOELoadData records
        2. Group them into a batch with a unique identifier
        3. Process the entire batch as a unit
        4. Mark the batch as processed
        5. Generate statistics for reporting
    """
    
    def __init__(self, records: List[ENTSOELoadData], batch_id: str, 
                 processed_at: Optional[datetime] = None, **kwargs):
        """Initialize a batch with validated records and metadata.
        
        Args:
            records: List of validated ENTSOELoadData objects for batch processing
            batch_id: Unique identifier for this batch (for traceability)
            processed_at: When the batch was processed (None if not processed yet)
            **kwargs: Additional attributes to store (for extensibility)
        
        Note:
            The processed_at attribute starts as None and is set by mark_processed()
            when batch processing completes successfully.
        """
        # Initialize the batch by calling parent class initializer
        # This handles the attribute setting based on whether we're using Pydantic or not
        super().__init__(records=records, batch_id=batch_id, processed_at=processed_at, **kwargs)
    
    # =====================================================================
    # PYDANTIC SCHEMA DEFINITION
    # =====================================================================
    # This conditional block defines the schema when Pydantic is available
    if USING_PYDANTIC:
        # These type annotations are only applied if Pydantic is available
        # They provide schema information, automatic validation, and serialization
        
        # List of validated ENTSOELoadData objects in this batch
        # This creates a relationship between models and validates nested objects
        records: List[ENTSOELoadData] = Field(
            description="List of validated electricity load data records in this batch"
        )
        
        # Unique identifier for this batch
        # Used for tracking and logging purposes
        batch_id: str = Field(
            description="Unique identifier for tracking this batch through the pipeline"
        )
        
        # When the batch was processed (None if not processed yet)
        # This is used to track completion status
        processed_at: Optional[datetime] = Field(
            default=None,
            description="Timestamp when this batch was successfully processed (None if pending)"
        )
    
    def mark_processed(self):
        """Mark this batch as processed with the current timestamp.
        
        Sets the processed_at attribute to the current datetime.
        Used to track when data processing was completed successfully.
        
        This method should be called at the end of successful batch processing
        to maintain an audit trail of data transformations.
        """
        # Update the timestamp to the current time to indicate processing completion
        self.processed_at = datetime.now()
        
    def get_statistics(self):
        """Calculate aggregate statistics for all records in the batch.
        
        Computes summary statistics including count, average, minimum, and maximum 
        load values across all records in the batch. These statistics are useful
        for monitoring, reporting, and data quality assessment.
        
        Returns:
            Dictionary containing:
                - count: Number of records in the batch
                - avg_load: Average electricity load across all records (in MW)
                - min_load: Minimum electricity load observed (in MW)
                - max_load: Maximum electricity load observed (in MW)
                
        Example:
            >>> batch = ENTSOEBatch(records=[...], batch_id="batch_20250101")
            >>> stats = batch.get_statistics()
            >>> print(f"Average load: {stats['avg_load']:.2f} MW")
        """
        # Handle empty batch case to prevent division by zero or min/max errors
        if not self.records:
            # Return zeroed statistics for empty batches
            return {
                "count": 0,
                "avg_load": 0.0,
                "min_load": 0.0,
                "max_load": 0.0
            }
        
        # Extract load values from all records using list comprehension
        # This creates a list containing only the load_mw values from each record
        loads = [record.load_mw for record in self.records]
        
        # Calculate and return statistics in a dictionary
        return {
            "count": len(loads),                  # Number of records in batch
            "avg_load": sum(loads) / len(loads),  # Mean load across all records
            "min_load": min(loads),               # Minimum load value in batch  
            "max_load": max(loads)                # Maximum load value in batch
        }


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
Example usage of this module:

from datetime import datetime
from models import ENTSOELoadData, ENTSOEBatch

# Create individual load data records with validation
try:
    # Valid record
    record1 = ENTSOELoadData(
        timestamp=datetime(2025, 5, 1, 12, 0),  # May 1, 2025 at noon
        load_mw=45000.5,                        # 45,000.5 MW
        region="DE"                             # Germany
    )
    
    # This would fail validation (negative load)
    # record2 = ENTSOELoadData(
    #     timestamp=datetime(2025, 5, 1, 13, 0),
    #     load_mw=-100.0,  # INVALID: negative value
    #     region="FR"
    # )
    
    # This would fail validation (future timestamp)
    # record3 = ENTSOELoadData(
    #     timestamp=datetime(2026, 1, 1, 0, 0),  # INVALID: future date
    #     load_mw=30000.0,
    #     region="ES"
    # )
    
    # Create a batch of records
    batch = ENTSOEBatch(
        records=[record1],
        batch_id="batch_20250501_example"
    )
    
    # Calculate statistics
    stats = batch.get_statistics()
    print(f"Batch statistics: {stats}")
    
    # Mark batch as processed after operations
    batch.mark_processed()
    print(f"Batch processed at: {batch.processed_at}")
    
except ValueError as e:
    print(f"Validation error: {e}")
"""
