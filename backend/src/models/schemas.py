from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for natural language queries"""

    query: str
    table_name: str


class QueryResponse(BaseModel):
    """Response model for query results"""

    success: bool
    generated_sql: str
    results: List[Dict[str, Any]]
    row_count: int
    columns: List[str]
    error_message: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response model for file upload"""

    success: bool
    table_name: str
    columns: List[str]
    sample_data: List[Dict[str, Any]]
    row_count: int
    error_message: Optional[str] = None


class TableInfo(BaseModel):
    """Model for table information"""

    table_name: str
    columns: List[Dict[str, str]]  # [{"name": "col1", "type": "TEXT"}, ...]
    sample_data: List[Dict[str, Any]]
    row_count: int
