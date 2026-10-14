import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from sqlalchemy import select

from app.ai.agents import run_call_analysis
from app.core.config import settings
from app.stt.farsava import transcribe_audio_farsava

from app.db.database import AsyncSessionLocal
from app.db.models import CallAnalysisRecord

logging.basicConfig(level=logging.INFO)

async def _resolve_audio_source(call_id: str, audio_source: str) -> str:
    parsed = urlparse(audio_source)
    if parsed.scheme not in {"http", "https"}:
        return audio_source
    if parsed.scheme != "https":
        raise RuntimeError("Remote audio URLs must use HTTPS")
    if (
        not parsed.hostname
        or parsed.hostname.lower() not in settings.audio_url_allowed_hosts
    ):
        raise RuntimeError("Remote audio host is not allowed")

    Path(settings.audio_directory).mkdir(parents=True, exist_ok=True)
    destination = Path(settings.audio_directory) / f"{call_id}.wav"
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=False) as client:
        async with client.stream("GET", audio_source) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if content_type and not content_type.startswith("audio/"):
                raise RuntimeError(f"Unexpected audio content type: {content_type}")
            with destination.open("wb") as audio_file:
                async for chunk in response.aiter_bytes():
                    audio_file.write(chunk)
    return str(destination)


async def process_call_task(ctx, call_id: str, audio_file_path: str):
    logging.info(f"🚀 Task started for Call ID: {call_id}")
    local_audio_path = await _resolve_audio_source(call_id, audio_file_path)
    try:
        logging.info("🎙️ Starting Speech-to-Text with FarsAva...")
        actual_transcript = await transcribe_audio_farsava(local_audio_path)

        logging.info("🧠 Analyzing actual text with AI Multi-Agent Workflow...")
        analysis_result = await run_call_analysis(actual_transcript)

        logging.info("💾 Saving results to PostgreSQL...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(CallAnalysisRecord).where(
                    CallAnalysisRecord.crm_activity_id == call_id
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                record = CallAnalysisRecord(crm_activity_id=call_id)
                db.add(record)
            record.transcript = actual_transcript
            record.lead_score = analysis_result["lead_score"]
            record.agent_performance = analysis_result["agent_performance"]
            record.strengths = analysis_result["strengths"]
            record.weaknesses = analysis_result["weaknesses"]
            await db.commit()
        logging.info(f"🎉 Call {call_id} fully processed and safely stored in DB.")
        return {"status": "success", "call_id": call_id, "data": analysis_result}
    except Exception as e:
        print(f"Error processing call {call_id}: {str(e)}")
        raise e
    finally:
        if success and os.path.exists(file_path):
            os.remove(file_path)

class WorkerSettings:
    functions = [process_call_task]
    redis_settings = settings.redis_settings()
    max_tries = 3
