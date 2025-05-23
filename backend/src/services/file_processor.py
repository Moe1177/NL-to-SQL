import os
import tempfile
import uuid
from typing import Any, Dict, List

import pandas as pd
from fastapi import UploadFile

from .database_manager import DatabaseManager


class FileProcessor:
    """Handles file upload and processing for CSV/Excel files"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    async def process_json_data(self, data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """
        Process JSON data from frontend and store in SQLite database.

        Args:
            data: List of dictionaries containing the data
            filename: Original filename for table naming

        Returns:
            Dict containing table info, columns, sample data, etc.
        """
        # Convert JSON data to DataFrame
        df = pd.DataFrame(data)

        # Generate unique table name
        table_name = self._generate_table_name(filename)

        # Store DataFrame in SQLite database
        self.db_manager.create_table_from_dataframe(df, table_name)

        # Prepare response data
        table_info = {
            "table_name": table_name,
            "columns": list(df.columns),
            "sample_data": df.head(50).to_dict("records"),
            "row_count": len(df),
        }

        return table_info

    async def process_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process uploaded CSV or Excel file and store in SQLite database.

        Args:
            file: UploadFile from FastAPI

        Returns:
            Dict containing table info, columns, sample data, etc.
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=self._get_file_extension(file.filename)
        ) as tmp_file:
            # Write uploaded file content to temporary file
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Read file into pandas DataFrame
            df = self._read_file_to_dataframe(tmp_file_path, file.filename)

            # Generate unique table name
            table_name = self._generate_table_name(file.filename)

            # Store DataFrame in SQLite database
            self.db_manager.create_table_from_dataframe(df, table_name)

            # Prepare response data
            table_info = {
                "table_name": table_name,
                "columns": list(df.columns),
                "sample_data": df.head(50).to_dict("records"),  # First 5 rows
                "row_count": len(df),
            }

            return table_info

        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)

    def _read_file_to_dataframe(self, file_path: str, filename: str) -> pd.DataFrame:
        """
        Read CSV or Excel file into pandas DataFrame.

        TODO: Add your custom logic here for:
        - Data cleaning and preprocessing
        - Handling different file encodings
        - Custom column name processing
        - Data type inference and conversion
        """
        if filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

        # Basic cleaning (you can expand this)
        df.columns = df.columns.str.strip()  # Remove whitespace from column names

        return df

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return os.path.splitext(filename)[1]

    def _generate_table_name(self, filename: str) -> str:
        """
        Generate unique table name from filename.

        TODO: Customize this logic based on your needs
        """
        # Remove extension and clean filename
        base_name = os.path.splitext(filename)[0]
        base_name = base_name.replace(" ", "_").replace("-", "_")

        # Add unique identifier
        unique_id = str(uuid.uuid4())[:8]
        table_name = f"{base_name}_{unique_id}"

        return table_name
