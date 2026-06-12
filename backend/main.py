import os
import re
import shutil
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FastAPI")

try:
    from backend.graph.workflow import graph
    from backend.graph.state import BRDState
    AGENTS_READY = True
    logger.info("AI agents loaded successfully.")
except (ImportError, Exception) as e:
    AGENTS_READY = False
    logger.warning(f"AI agents not available: {type(e).__name__}")

from backend.database import save_brd, get_all_brds, get_brd_by_id

app = FastAPI(title="BRD Genie Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a"}
ALLOWED_TEXT_EXTENSIONS = {".txt", ".pdf", ".docx"}
ALLOWED_EXTENSIONS = ALLOWED_AUDIO_EXTENSIONS | ALLOWED_TEXT_EXTENSIONS

_executor = ThreadPoolExecutor(max_workers=4)


def _run_graph_sync(state_input: dict) -> dict:
    """Run graph.invoke in a fresh thread with its own event loop so crewai sync API works."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return graph.invoke(state_input)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


async def run_graph(state_input: dict) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run_graph_sync, state_input)


def secure_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w.\-]", "_", filename)
    return filename or "upload"


def safe_file_path(filename: str) -> str:
    name = secure_filename(filename)
    path = os.path.realpath(os.path.join(TEMP_DIR, name))
    if not path.startswith(os.path.realpath(TEMP_DIR)):
        raise ValueError("Invalid file path.")
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type '{ext}' is not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    return path


@app.get("/api/health")
def health():
    return {"status": "ok", "agents_ready": AGENTS_READY}


class ClarifyRequest(BaseModel):
    state: Dict[str, Any]
    answers: List[str]


@app.post("/api/start")
async def start_session(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    language: str = Form("English")
):
    if not AGENTS_READY:
        raise HTTPException(status_code=503, detail="AI agents not available. Please set GROQ_API_KEY in your .env file and restart the server.")
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
        try:
            file_path = safe_file_path(file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            state_input["raw_input"] = file_path
            logger.info("Audio file saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {type(e).__name__}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file.")
    else:
        state_input["raw_input"] = raw_text

    try:
        logger.info("--- Initiating LangGraph Execution ---")
        final_state = await run_graph(state_input)
        clean_state = dict(final_state)
        if file and clean_state.get("raw_input"):
            clean_state["raw_input"] = os.path.basename(clean_state["raw_input"])
        return clean_state
    except Exception as e:
        logger.error(f"Error executing graph: {type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error executing graph: {str(e)}")


@app.post("/api/clarify")
async def clarify_session(request: ClarifyRequest):
    if not AGENTS_READY:
        raise HTTPException(status_code=503, detail="AI agents not available. Please set GROQ_API_KEY in your .env file and restart the server.")

    state_input = dict(request.state)
    state_input["answers"] = request.answers

    raw_input = state_input.get("raw_input", "")
    if raw_input and not os.path.isabs(raw_input):
        try:
            potential_path = safe_file_path(raw_input)
            if os.path.exists(potential_path):
                state_input["raw_input"] = potential_path
        except ValueError:
            pass

    try:
        logger.info("--- Resuming LangGraph Execution with Answers ---")
        final_state = await run_graph(state_input)

        project_name = final_state.get("structured_data", {}).get("context", "Software Project").split(".")[0][:50].strip() or "Software Project"

        brd_id = save_brd(
            project_name=project_name,
            raw_input=os.path.basename(final_state.get("raw_input", "")),
            cleaned_input=final_state.get("cleaned_input", ""),
            english_brd=final_state.get("final_brd", final_state.get("brd_draft", "")),
            localized_brd=final_state.get("localized_brd", ""),
            language=final_state.get("language", "English")
        )

        clean_state = dict(final_state)
        clean_state["db_id"] = brd_id
        if clean_state.get("raw_input"):
            clean_state["raw_input"] = os.path.basename(clean_state["raw_input"])
        return clean_state
    except Exception as e:
        logger.error(f"Error resuming graph: {type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error resuming graph: {str(e)}")


@app.get("/api/history")
def get_history():
    try:
        return get_all_brds()
    except Exception as e:
        logger.error(f"Error retrieving history: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{brd_id}")
def get_brd(brd_id: int):
    try:
        brd = get_brd_by_id(brd_id)
        if not brd:
            raise HTTPException(status_code=404, detail="BRD record not found")
        return brd
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving BRD: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=str(e))
