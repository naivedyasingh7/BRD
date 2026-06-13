import os
import re
import uuid
import shutil
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends

from backend.api.schemas import ClarifyRequest, BRDStateResponse, ProjectHistoryResponse, BRDDetailResponse
from backend.services.config import is_groq_configured, is_sarvam_configured
from backend.graph.state import BRDState
from backend.graph.workflow import graph
from backend.database import save_brd, get_all_brds, get_brd_by_id, get_audit_trail

logger = logging.getLogger(__name__)
router = APIRouter()

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a"}
ALLOWED_TEXT_EXTENSIONS = {".txt", ".pdf", ".docx"}
ALLOWED_EXTENSIONS = ALLOWED_AUDIO_EXTENSIONS | ALLOWED_TEXT_EXTENSIONS
MAX_TEXT_LENGTH = 50_000
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024

_executor = ThreadPoolExecutor(max_workers=4)


def _run_graph_sync(state_input: dict) -> dict:
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


@router.post("/start", response_model=BRDStateResponse)
async def start_session(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    language: str = Form("English")
):
    request_id = f"req-{uuid.uuid4().hex[:8]}"
    logger.info(f"[{request_id}] POST /api/start received (Language: {language})")

    if not is_groq_configured():
        logger.error(f"[{request_id}] GROQ_API_KEY is not configured.")
        raise HTTPException(
            status_code=503, 
            detail="AI agents not available. Please set GROQ_API_KEY in your .env file and restart the server."
        )
        
    if not file and not raw_text:
        raise HTTPException(status_code=400, detail="Either file or raw_text must be provided.")
        
    if raw_text and len(raw_text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"raw_text exceeds maximum allowed length of {MAX_TEXT_LENGTH} characters."
        )

    state_input: BRDState = {
        "raw_input": "",
        "cleaned_input": "",
        "questions": [],
        "answers": [],
        "brd_draft": "",
        "final_brd": "",
        "language": language,
        "localized_brd": "",
        "request_id": request_id,
        "project_name": "",
        "db_id": None,
        "context_analysis": "",
        "extracted_requirements": "",
        "stakeholder_analysis": "",
        "ambiguities_analysis": "",
        "risks_analysis": "",
        "structured_outline": "",
        "qa_review": "",
        "agent_traces": []
    }

    file_path = None
    if file:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file has no filename.")
        try:
            file_path = safe_file_path(file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        try:
            logger.info(f"[{request_id}] Saving uploaded file to {file_path}")
            content = await file.read(MAX_FILE_SIZE_BYTES + 1)
            if len(content) > MAX_FILE_SIZE_BYTES:
                raise HTTPException(status_code=413, detail="File exceeds maximum allowed size of 25MB.")
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            state_input["raw_input"] = file_path
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[{request_id}] Failed to save uploaded file: {type(e).__name__} - {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file.")
    else:
        state_input["raw_input"] = raw_text

    try:
        logger.info(f"[{request_id}] Invoking LangGraph workflow...")
        final_state = await run_graph(state_input)
        clean_state = dict(final_state)
        
        # If execution completes without questions (e.g. state answers already present or none found), save to DB
        questions = clean_state.get("questions", [])
        if not questions:
            project_name = clean_state.get("project_name") or "Software Project"
            logger.info(f"[{request_id}] Generation completed immediately. Saving BRD for project: {project_name}")
            db_id = save_brd(
                project_name=project_name,
                raw_input=os.path.basename(clean_state.get("raw_input", "")),
                cleaned_input=clean_state.get("cleaned_input", ""),
                english_brd=clean_state.get("final_brd", clean_state.get("brd_draft", "")),
                localized_brd=clean_state.get("localized_brd", ""),
                language=clean_state.get("language", "English")
            )
            clean_state["db_id"] = db_id

        if file and clean_state.get("raw_input"):
            clean_state["raw_input"] = os.path.basename(clean_state["raw_input"])
            
        return clean_state
    except Exception as e:
        logger.error(f"[{request_id}] Error executing LangGraph: {type(e).__name__} - {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error processing request: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"[{request_id}] Cleaned up temp file: {file_path}")
            except OSError:
                pass


@router.post("/clarify", response_model=BRDStateResponse)
async def clarify_session(request: ClarifyRequest):
    request_id = request.state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    logger.info(f"[{request_id}] POST /api/clarify received")

    if not is_groq_configured():
        logger.error(f"[{request_id}] GROQ_API_KEY is not configured.")
        raise HTTPException(
            status_code=503, 
            detail="AI agents not available. Please set GROQ_API_KEY in your .env file and restart the server."
        )

    state_input = dict(request.state)
    state_input["answers"] = request.answers

    # Map file input paths correctly if they were trimmed to basenames
    raw_input = state_input.get("raw_input", "")
    if raw_input and not os.path.isabs(raw_input):
        try:
            potential_path = safe_file_path(raw_input)
            if os.path.exists(potential_path):
                state_input["raw_input"] = potential_path
        except ValueError:
            pass

    try:
        logger.info(f"[{request_id}] Resuming LangGraph workflow from clarify...")
        final_state = await run_graph(state_input)
        clean_state = dict(final_state)
        
        project_name = clean_state.get("project_name") or "Software Project"
        
        # Save BRD to DB
        logger.info(f"[{request_id}] Saving generated BRD version for project: {project_name}")
        brd_id = save_brd(
            project_name=project_name,
            raw_input=os.path.basename(clean_state.get("raw_input", "")),
            cleaned_input=clean_state.get("cleaned_input", ""),
            english_brd=clean_state.get("final_brd", clean_state.get("brd_draft", "")),
            localized_brd=clean_state.get("localized_brd", ""),
            language=clean_state.get("language", "English")
        )
        
        clean_state["db_id"] = brd_id
        if clean_state.get("raw_input"):
            clean_state["raw_input"] = os.path.basename(clean_state["raw_input"])
            
        return clean_state
    except Exception as e:
        logger.error(f"[{request_id}] Error resuming LangGraph: {type(e).__name__} - {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error resuming pipeline: {str(e)}")


@router.get("/history", response_model=List[ProjectHistoryResponse])
def get_history():
    logger.info("GET /api/history received")
    try:
        return get_all_brds()
    except Exception as e:
        logger.error(f"Failed to query database history: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history records.")


@router.get("/history/{brd_id}", response_model=BRDDetailResponse)
def get_brd(brd_id: int):
    logger.info(f"GET /api/history/{brd_id} received")
    try:
        brd = get_brd_by_id(brd_id)
        if not brd:
            raise HTTPException(status_code=404, detail="BRD record not found.")
            
        # Enrich history details with audit logs if they exist
        project_name = brd.get("project_name")
        if project_name:
            brd["agent_traces"] = get_audit_trail(project_name)
            
        return brd
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query database record: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve BRD record.")
