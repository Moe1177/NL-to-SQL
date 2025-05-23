import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

from models.schemas import (
    FileUploadResponse,
    QueryRequest,
    QueryResponse,
)
from services.database_manager import DatabaseManager
from services.file_processor import FileProcessor
from services.llm_service import LLMService


# Add a request model for JSON uploads
class JsonUploadRequest(BaseModel):
    json_data: list
    filename: str


app = FastAPI(
    title="Natural Language to SQL API",
    description="Upload CSV/Excel files and query them using natural language",
    version="1.0.0",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Initialize services
file_processor = FileProcessor()
db_manager = DatabaseManager()
llm_service = LLMService()


@app.post("/upload-json", response_model=FileUploadResponse)
async def upload_json_data(request: JsonUploadRequest):
    """
    Upload JSON data and create a SQLite table from it.
    Returns table info and column details for context.
    """
    try:
        # Process JSON data
        table_info = await file_processor.process_json_data(
            request.json_data, request.filename
        )
        
        print(f"Upload JSON - Generated table name: {table_info['table_name']}")  # Debug log

        return FileUploadResponse(
            success=True,
            table_name=table_info["table_name"],
            columns=table_info["columns"],
            sample_data=table_info["sample_data"],
            row_count=table_info["row_count"],
        )

    except Exception as e:
        print(f"Upload JSON Error: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest):
    """
    Process a natural language query and return SQL results.
    Uses RAG to provide context to LLM for SQL generation.
    """
    try:
        print(f"Query - Received table name: {request.table_name}")  # Debug log
        
        # Step 1: Get table context for RAG
        table_context = db_manager.get_table_context(request.table_name)
        print(f"Query - Table context retrieved for: {request.table_name}")  # Debug log

        # Step 2: Generate SQL using LLM with RAG context
        sql_query = await llm_service.generate_sql(
            natural_language_query=request.query, table_context=table_context
        )
        print(f"Query - Generated SQL: {sql_query}")  # Debug log

        # Step 3: Execute SQL query on the data
        results = db_manager.execute_query(sql_query, request.table_name)
        print(f"Query - Executed query successfully")  # Debug log
        
        return QueryResponse(
            success=True,
            generated_sql=sql_query,
            results=results["data"],
            row_count=results["row_count"],
            columns=results["columns"],
        )

    except Exception as e:
        print(f"Query Error: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/tables")
async def list_tables():
    """List all available tables (uploaded files)"""
    try:
        tables = db_manager.list_tables()
        return {"success": True, "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")


@app.delete("/tables/{table_name}")
async def delete_table(table_name: str):
    """Delete a table (cleanup uploaded file data)"""
    try:
        db_manager.delete_table(table_name)
        return {"success": True, "message": f"Table {table_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting table: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Natural Language to SQL API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
