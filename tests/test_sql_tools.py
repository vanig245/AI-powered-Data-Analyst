import pytest
import json
from app.data_loader import data_loader
from app.tools.sql_tools import execute_sql

def test_execute_sql_success():
    """Test that a valid SQL query returns the expected JSON data."""
    data_loader.conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER, name VARCHAR)")
    data_loader.conn.execute("INSERT INTO test_table VALUES (1, 'Alice'), (2, 'Bob')")
    result = execute_sql.invoke({"query": "SELECT * FROM test_table"})

    assert "Alice" in result
    assert "Bob" in result
    data_loader.conn.execute("DROP TABLE test_table")

def test_execute_sql_syntax_error():
    """Test that invalid SQL doesn't crash the app but returns an error string to the LLM."""
    result = execute_sql.invoke({"query": "SELECT * FROM a_table_that_does_not_exist"})
    
    assert "Error executing SQL query" in result