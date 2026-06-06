import os
import shutil
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.graph.workflow import graph
from backend.graph.state import BRDState
from backend.database import save_brd, get_all_brds, get_brd_by_id

app = FastAPI(title="BRD Genie Backend API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

class ClarifyRequest(BaseModel):
    state: Dict[str, Any]
    answers: List[str]

@app.post("/api/start")
async def start_session(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    language: str = Form("English")
):
    """
    Start a BRD generation session using either audio input or raw text input.
    """
    if not file and not raw_text:
        raise HTTPException(status_code=400, detail="Either file or raw_text must be provided.")

    state_input: BRDState = {
        "raw_input": "",
        "cleaned_input": "",
        "structured_data": {},
        "questions": [],
        "answers": [],
        "brd_draft": "",
        "final_brd": "",
        "language": language,
        "localized_brd": ""
    }

    if file:
        # Save the uploaded audio file to the temp directory
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        state_input["raw_input"] = file_path
    else:
        state_input["raw_input"] = raw_text

    try:
        # Run the graph from the start (input node)
        print("--- Initiating LangGraph Execution ---")
        final_state = graph.invoke(state_input)
        
        # Clean up absolute file paths from state returned to client to avoid leaks
        clean_state = dict(final_state)
        if file and clean_state.get("raw_input"):
            clean_state["raw_input"] = os.path.basename(clean_state["raw_input"])
            
        return clean_state
    except Exception as e:
        print(f"Error executing graph: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing graph: {str(e)}")

@app.post("/api/clarify")
async def clarify_session(request: ClarifyRequest):
    """
    Submit answers to the generated questions and resume the LangGraph flow.
    """
    state_input = request.state
    # Ensure answers match questions length or are properly updated
    state_input["answers"] = request.answers

    # If the raw file was saved locally, we restore its temp path if it exists
    if state_input.get("raw_input") and not os.path.exists(state_input["raw_input"]):
        potential_path = os.path.join(TEMP_DIR, state_input["raw_input"])
        if os.path.exists(potential_path):
            state_input["raw_input"] = potential_path

    try:
        print("--- Resuming LangGraph Execution with Answers ---")
        # Invoke the graph again. It will skip clarify generation and continue through generate -> qa -> localize.
        final_state = graph.invoke(state_input)
        
        # Save the resulting BRD to history database
        project_name = final_state.get("structured_data", {}).get("problem", "Software Project").split(".")[0][:50]
        
        brd_id = save_brd(
            project_name=project_name,
            raw_input=final_state.get("raw_input", ""),
            cleaned_input=final_state.get("cleaned_input", ""),
            english_brd=final_state.get("final_brd", ""),
            localized_brd=final_state.get("localized_brd", ""),
            language=final_state.get("language", "English")
        )
        
        # Clean state for return
        clean_state = dict(final_state)
        clean_state["db_id"] = brd_id
        if clean_state.get("raw_input"):
            clean_state["raw_input"] = os.path.basename(clean_state["raw_input"])

        return clean_state
    except Exception as e:
        print(f"Error resuming graph: {e}")
        raise HTTPException(status_code=500, detail=f"Error resuming graph: {str(e)}")

@app.get("/api/history")
def get_history():
    """
    Retrieve list of all past generated BRDs.
    """
    try:
        return get_all_brds()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{brd_id}")
def get_brd(brd_id: int):
    """
    Get detailed records for a specific BRD by ID.
    """
    brd = get_brd_by_id(brd_id)
    if not brd:
        raise HTTPException(status_code=404, detail="BRD record not found")
    return brd
