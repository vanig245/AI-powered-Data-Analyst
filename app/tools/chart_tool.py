import os
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_core.tools import tool
from app.data_loader import data_loader
from app.config import settings

CHARTS_DIR = os.path.join(settings.BASE_DIR, "static", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

@tool
def generate_chart(sql_query: str, chart_type: str, x_column: str, y_column: str, title: str) -> str:
    """
    Executes a SQL query to fetch data, generates a visualization, and returns the markdown image link.
    Use this tool when the user asks to visualize data, show a trend, or create a chart.
    Supported chart_type values: 'bar', 'line', 'pie', 'scatter'.
    """
    try:
        df = data_loader.conn.execute(sql_query).df()
        
        if df.empty:
            return "Error: The query returned no data to chart."
        plt.clf()
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        chart_type = chart_type.lower()
        if chart_type == 'bar':
            sns.barplot(data=df, x=x_column, y=y_column)
        elif chart_type == 'line':
            sns.lineplot(data=df, x=x_column, y=y_column)
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x=x_column, y=y_column)
        elif chart_type == 'pie':
            plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')
        else:
            return f"Error: Unsupported chart type '{chart_type}'."
            
        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()

        filename = f"chart_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath)
        plt.close()
        
        return f"Chart generated successfully. Embed this image in your response using markdown: ![img](/static/charts/{filename})"
        
    except Exception as e:
        return f"Error generating chart: {str(e)}\nPlease check your SQL syntax and column names."