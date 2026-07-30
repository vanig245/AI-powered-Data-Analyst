import os
import pandas as pd
import duckdb
from fastapi import UploadFile, HTTPException
from app.config import settings

class DataLoader:
    def __init__(self):
        self.db_path = os.path.join(settings.DATA_DIR, "analyst.db")
        self.conn = duckdb.connect(self.db_path)

    def save_and_validate_csv(self, file: UploadFile) -> str:
        """
        Saves the uploaded CSV to the data directory and ensures it is valid.
        Returns the absolute file path of the saved CSV.
        """
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported.")

        file_path = os.path.join(settings.DATA_DIR, file.filename)
        
        try:
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            df = pd.read_csv(file_path)
            if df.empty:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
            
            return file_path
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    def load_csv_to_duckdb(self, table_name: str, file_path: str) -> bool:
        """
        Loads a valid CSV file directly into a DuckDB table.
        """
        try:
            query = f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}');"
            self.conn.execute(query)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load data into database: {str(e)}")
            
    def get_schema(self, table_name: str) -> str:
        """
        Retrieves the table schema to feed to the LLM so it knows what columns exist.
        """
        try:
            result = self.conn.execute(f"DESCRIBE {table_name}").df()
            
            schema_str = f"Table: '{table_name}'\nColumns:\n"
            for _, row in result.iterrows():
                schema_str += f"- {row['column_name']} ({row['column_type']})\n"
                
            return schema_str
        except Exception as e:
            return f"Error retrieving schema: {str(e)}"
data_loader = DataLoader()