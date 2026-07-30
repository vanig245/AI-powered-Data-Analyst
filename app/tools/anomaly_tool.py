import json
import pandas as pd
from langchain_core.tools import tool
from app.data_loader import data_loader

@tool
def detect_anomalies(sql_query: str, column_name: str) -> str:
    """
    Executes a SQL query to fetch data, then detects statistical anomalies (outliers) 
    in the specified numeric column using the Z-score method.
    Use this tool when the user asks to find anomalies, outliers, or unusual patterns in the data.
    Returns the anomalous rows and statistical context so you can explain why they are flagged.
    """
    try:
        df = data_loader.conn.execute(sql_query).df()
        
        if df.empty:
            return "Error: The query returned no data to analyze."
            
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found in the query results."
            
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            return f"Error: Column '{column_name}' is not numeric. Anomaly detection requires numeric data."

        mean_val = df[column_name].mean()
        std_dev = df[column_name].std()
        
        if std_dev == 0:
            return "No anomalies detected. All values in the column are exactly identical."

        df['z_score'] = (df[column_name] - mean_val) / std_dev
        anomalies = df[df['z_score'].abs() > 3].copy()
        
        if anomalies.empty:
            return f"No anomalies detected in '{column_name}'. The data falls within normal statistical ranges (mean: {mean_val:.2f}, std dev: {std_dev:.2f})."

        if len(anomalies) > 50:
            anomalies = anomalies.head(50)
            truncation = "\n... (Anomalies truncated to top 50 rows to save context space)"
        else:
            truncation = ""

        context = {
            "statistical_context": {
                "mean": round(mean_val, 2),
                "standard_deviation": round(std_dev, 2),
                "threshold_used": "Z-score > 3 or < -3 (Values further than 3 standard deviations from the mean are flagged)"
            },
            "anomalies_found": len(anomalies),
            "anomalous_data": anomalies.to_dict(orient="records")
        } 
        return json.dumps(context, indent=2) + truncation
        
    except Exception as e:
        return f"Error detecting anomalies: {str(e)}\nPlease check your SQL query and column name."