import pytest
import json
from app.data_loader import data_loader
from app.tools.anomaly_tool import detect_anomalies

def test_detect_anomalies_finds_outlier():
    """Test that the Z-score logic successfully flags a massive mathematical outlier."""
    data_loader.conn.execute("DROP TABLE IF EXISTS anomaly_test")
    
    data_loader.conn.execute("CREATE TABLE anomaly_test (value INTEGER)")
    normal_data = ", ".join(["(10)"] * 15)
    data_loader.conn.execute(f"INSERT INTO anomaly_test VALUES {normal_data}, (10000)")
    
    result = detect_anomalies.invoke({
        "sql_query": "SELECT * FROM anomaly_test", 
        "column_name": "value"
    })
    
    assert "10000" in result
    assert "statistical_context" in result
    
    parsed_result = json.loads(result)
    assert parsed_result["anomalies_found"] == 1
    assert parsed_result["anomalous_data"][0]["value"] == 10000

    data_loader.conn.execute("DROP TABLE anomaly_test")

def test_detect_anomalies_wrong_column_type():
    """Test that the tool rejects text columns since anomalies require numbers."""
    data_loader.conn.execute("CREATE TABLE IF NOT EXISTS text_test (name VARCHAR)")
    data_loader.conn.execute("INSERT INTO text_test VALUES ('Alice'), ('Bob')")
    
    result = detect_anomalies.invoke({
        "sql_query": "SELECT * FROM text_test", 
        "column_name": "name"
    })
    
    assert "is not numeric" in result
    data_loader.conn.execute("DROP TABLE text_test")