import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.database import save_audit_log

logger = logging.getLogger(__name__)


class AgentExecutionTracker:
    
    def __init__(self, project_name: str, request_id: str):
        self.project_name = project_name
        self.request_id = request_id
        self.traces: List[Dict[str, Any]] = []
        self._current_agent: Optional[str] = None
        self._current_step: Optional[str] = None
        self._start_time: Optional[float] = None
        self._start_time_str: Optional[str] = None

    def start_trace(self, step_name: str, agent_role: str):
        self._current_step = step_name
        self._current_agent = agent_role
        self._start_time = time.time()
        self._start_time_str = datetime.utcnow().isoformat() + "Z"
        logger.info(f"[{self.request_id}] >>> Started agent role: {agent_role} for workflow step: {step_name}")

    def end_trace(self, output_text: str, input_text: Optional[str] = None, status: str = "Success") -> Dict[str, Any]:
        if self._start_time is None or self._current_agent is None or self._current_step is None:
            logger.warning("Trace ended without matching start_trace.")
            return {}
            
        end_time = time.time()
        end_time_str = datetime.utcnow().isoformat() + "Z"
        duration = end_time - self._start_time
        output_summary = output_text[:180] + "..." if len(output_text) > 180 else output_text
        output_summary = output_summary.replace("\n", " ").strip()
        
        trace_record = {
            "agent_role": self._current_agent,
            "step_name": self._current_step,
            "status": status,
            "start_time": self._start_time_str,
            "end_time": end_time_str,
            "duration_seconds": round(duration, 3),
            "output_summary": output_summary
        }
        
        self.traces.append(trace_record)
        logger.info(f"[{self.request_id}] <<< Ended agent role: {self._current_agent} (Duration: {trace_record['duration_seconds']}s, Status: {status})")
        try:
            save_audit_log(
                project_name=self.project_name,
                request_id=self.request_id,
                step_name=self._current_step,
                agent_role=self._current_agent,
                input_data=input_text or "",
                output_data=output_text,  # Save full output to DB for audit credibility
                duration=duration,
                status=status
            )
        except Exception as e:
            logger.error(f"Failed to persist audit trail record: {type(e).__name__} - {str(e)}")
        self._current_step = None
        self._current_agent = None
        self._start_time = None
        self._start_time_str = None
        
        return trace_record
