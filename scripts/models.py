#!/usr/bin/env python3
"""
Data models for the energy-data-pipeline.

This module defines Pydantic models for validating energy data.
For more information on Pydantic, refer to Context7 documentation.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys

# Try to import Pydantic, provide fallback if not available
try:
    from pydantic import BaseModel, Field, field_validator
    USING_PYDANTIC = True
except ImportError:
    print("Note: Pydantic is not installed. Using basic data classes without validation.")
    print("For data validation, install pydantic: pip install pydantic")
    print("Refer to Context7 documentation for more details on Pydantic.")
    
    # Create simple fallback classes that mimic Pydantic behavior
    class BaseModel:
        """Simple BaseModel fallback when Pydantic is not available."""
        
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def model_dump(self) -> Dict[str, Any]:
            """Return a dictionary of all the model's attributes."""
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    # Simple placeholder for Field
    def Field(**kwargs):
        """Placeholder for Pydantic Field."""
        return None
    
    # Simple placeholder for field_validator
    def field_validator(*args, **kwargs):
        """Placeholder for Pydantic field_validator."""
        def decorator(func):
            return func
        return decorator
    
    USING_PYDANTIC = False

class ENTSOELoadData(BaseModel):
    """Model for ENTSO-E load data."""
    
    def __init__(self, timestamp: datetime, load_mw: float, region: str, **kwargs):
        """Initialize with validation if Pydantic is available."""
        # Perform basic validations even without Pydantic
        if load_mw <= 0:
            raise ValueError("load_mw must be positive")
            
        if timestamp > datetime.now():
            raise ValueError("Timestamp cannot be in the future")
            
        # Set attributes
        super().__init__(timestamp=timestamp, load_mw=load_mw, region=region, **kwargs)
    
    if USING_PYDANTIC:
        # These annotations are only used if Pydantic is available
        timestamp: datetime
        load_mw: float = Field(gt=0)  # Positive-only value
        region: str
        
        @field_validator('timestamp')
        @classmethod
        def check_timestamp_not_future(cls, value):
            """Validate that timestamp is not in the future."""
            if value > datetime.now():
                raise ValueError("Timestamp cannot be in the future")
            return value

class ENTSOEBatch(BaseModel):
    """Batch of load data records."""
    
    def __init__(self, records: List[ENTSOELoadData], batch_id: str, processed_at: Optional[datetime] = None, **kwargs):
        """Initialize batch with records."""
        super().__init__(records=records, batch_id=batch_id, processed_at=processed_at, **kwargs)
    
    if USING_PYDANTIC:
        # These annotations are only used if Pydantic is available
        records: List[ENTSOELoadData]
        batch_id: str
        processed_at: Optional[datetime] = None
    
    def mark_processed(self):
        """Mark this batch as processed with current timestamp."""
        self.processed_at = datetime.now()
        
    def get_statistics(self):
        """Get basic statistics about the batch."""
        if not self.records:
            return {"count": 0, "avg_load": 0, "min_load": 0, "max_load": 0}
        
        loads = [record.load_mw for record in self.records]
        return {
            "count": len(loads),
            "avg_load": sum(loads) / len(loads),
            "min_load": min(loads),
            "max_load": max(loads)
        }
