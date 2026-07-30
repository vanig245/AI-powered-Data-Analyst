from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage

from app.config import settings
from app.data_loader import data_loader
from app.session_manager import session_manager
from app.tools.sql_tools import execute_sql
from app.tools.chart_tool import generate_chart
from app.tools.anomaly_tool import detect_anomalies

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL_NAME,
    temperature=0
)

tools = [execute_sql, generate_chart, detect_anomalies]
system_prompt = """You are an expert AI Data Analyst. Your goal is to help the user analyze their dataset.
You have access to a DuckDB database containing the user's data.

Here is the schema for the active dataset:
{schema}

CRITICAL INSTRUCTIONS FOR TOOL CALLING:
1. When you need to query the database, you MUST use the `execute_sql` tool. Pass ONLY a valid SQL SELECT statement.
2. When asked for visualizations, use the `generate_chart` tool. 
3. EXTREMELY IMPORTANT FOR CHARTS: When the `generate_chart` tool returns a markdown link (e.g., `![img](/static/charts/...)`), YOU MUST COPY AND PASTE THAT EXACT MARKDOWN LINK INTO YOUR FINAL RESPONSE. Do not just describe the chart. If you do not include the exact `![img](...)` syntax in your final message, the user will not be able to see the image.
4. When asked to find anomalies, use the `detect_anomalies` tool and explain the statistical reasoning based on its output.
5. Answer directly and professionally based ONLY on the data returned by the tools.
"""

def get_agent_response(session_id: str, user_query: str) -> str:
    """
    Core function to process user queries. Fetches context, runs the agent, and manages history.
    """
    active_table = session_manager.get_active_table(session_id)
    if not active_table:
        return "Please upload a CSV file first before asking questions about the data."
    
    schema = data_loader.get_schema(active_table)
    history = session_manager.get_history(session_id)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True
    )

    session_manager.add_message(session_id, HumanMessage(content=user_query))

    try:
        response = agent_executor.invoke({
            "input": user_query,
            "schema": schema,
            "chat_history": history
        })
        output = response["output"]
        session_manager.add_message(session_id, AIMessage(content=output))
        return output
        
    except Exception as e:
        error_msg = f"An error occurred while analyzing the data: {str(e)}"
        session_manager.add_message(session_id, AIMessage(content=error_msg))
        return error_msg