import json
from langchain_core.tools import tool
from app.data_loader import data_loader

@tool
def execute_sql(query: str) -> str:
    """
    Executes a SQL SELECT query against the DuckDB database and returns the results.
    Use this tool to fetch data to answer the user's analytical questions.
    Input MUST be a valid SQL query string.
    """
    try:
        df = data_loader.conn.execute(query).df()
        if len(df) > 100:
            df = df.head(100)
            truncation_warning = "\n... (Results truncated to top 100 rows)"
        else:
            truncation_warning = ""
        result_str = df.to_json(orient="records", date_format="iso")
        
        return result_str + truncation_warning

    except Exception as e:

        return f"Error executing SQL query: {str(e)}\nPlease check your SQL syntax and try again."