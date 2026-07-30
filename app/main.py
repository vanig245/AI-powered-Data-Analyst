import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.config import settings
from app.data_loader import data_loader
from app.session_manager import session_manager
from app.agent import get_agent_response

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(settings.BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "charts"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Endpoint to handle CSV uploads.
    Validates the file, loads it into DuckDB, and initializes a new user session.
    """
    try:
        file_path = data_loader.save_and_validate_csv(file)
        table_name = os.path.splitext(file.filename)[0].replace(" ", "_").replace("-", "_").lower()
        data_loader.load_csv_to_duckdb(table_name, file_path)
        session_id = session_manager.create_session()
        session_manager.set_active_table(session_id, table_name)
        
        return {
            "message": "File uploaded and processed successfully",
            "session_id": session_id,
            "table_name": table_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Endpoint to handle user questions.
    Passes the message and session ID to the LangChain agent.
    """
    try:
        response_text = get_agent_response(request.session_id, request.message)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/")
async def serve_frontend():
    """
    Serves the main HTML UI when the user navigates to the root URL (http://localhost:8000).
    """
    from fastapi.responses import FileResponse
    index_path = os.path.join(STATIC_DIR, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "API is running! Please create static/index.html to view the UI."}