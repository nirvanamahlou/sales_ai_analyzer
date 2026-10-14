import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from arq import create_pool
from sqlalchemy import select

from app.api.schemas import (
    CallResponse,
    DynamicsWebhookRequest,
    HealthResponse,
    QueueResponse,
)
from app.core.config import settings
from app.core.security import require_api_key
from app.crm.dynamics import fetch_recent_calls_from_crm, download_audio_from_crm
from app.db.database import engine, AsyncSessionLocal
from app.db.models import CallAnalysisRecord
from app.ai.agents import run_call_analysis

logging.basicConfig(level=logging.INFO)

redis_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_pool
    
    
    redis_pool = await create_pool(settings.redis_settings())
    logging.info("🔗 Connected to Redis Task Queue")

    yield

    await redis_pool.close()
    await engine.dispose()

app = FastAPI(title="Sales Call Analyzer API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/api/webhook/dynamics",
    response_model=QueueResponse,
    dependencies=[Depends(require_api_key)],
)
async def receive_dynamics_webhook(call_data: DynamicsWebhookRequest):
    await redis_pool.enqueue_job(
        "process_call_task",
        call_data.call_id,
        str(call_data.audio_url),
        _job_id=f"call:{call_data.call_id}",
    )
    return {
        "status": "success",
        "message": f"Task for {call_data.call_id} securely added to queue",
    }


# ==========================================
# روت تستی اضافه شده برای تست هوش مصنوعی (بدون CRM)
# ==========================================
class MockCallRequest(BaseModel):
    transcript: str

@app.post("/api/test-analysis")
async def test_ai_analysis(request: MockCallRequest, db=Depends(get_db)):
    """
    روت تستی: یک متن خام می‌گیرد و مستقیما به هوش مصنوعی می‌فرستد
    و در دیتابیس ذخیره می‌کند
    """
    try:
       
        analysis_result = await run_call_analysis(request.transcript)
        
        
        fake_crm_id = f"test_{uuid.uuid4().hex[:8]}"
        new_record = CallAnalysisRecord(
            crm_activity_id=fake_crm_id,
            transcript=request.transcript,
            lead_score=analysis_result.get("lead_score", 0),
            agent_performance=analysis_result.get("agent_performance", "نامشخص"),
            strengths=analysis_result.get("strengths", []),
            weaknesses=analysis_result.get("weaknesses", [])
        )
        db.add(new_record)
        await db.commit()
        
        return {
            "status": "success", 
            "message": "تحلیل با موفقیت انجام و ذخیره شد",
            "data": analysis_result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
# ==========================================


@app.get("/api/calls/recent", response_model=list[CallResponse])
async def get_recent_calls(db=Depends(get_db)):
    """
    دریافت ۲۰ تماس آخر تحلیل شده از دیتابیس واقعی PostgreSQL
    """
   
    query = select(CallAnalysisRecord).order_by(CallAnalysisRecord.created_at.desc()).limit(20)
    result = await db.execute(query)
    calls = result.scalars().all()
    
   
    response = []
    for call in calls:
        response.append({
            "id": str(call.id), 
            "crm_activity_id": call.crm_activity_id,
            "date": call.created_at,
            "customer_phone": None,
            "lead_score": call.lead_score,
            "agent_performance": call.agent_performance,
            "strengths": call.strengths,
            "weaknesses": call.weaknesses
        })
        
    return response


@app.post(
    "/api/sync-crm",
    response_model=QueueResponse,
    dependencies=[Depends(require_api_key)],
)
async def sync_calls_from_crm():
    """
    اتصال به مایکروسافت داینامیکس، دریافت لیست تماس‌ها و ارسال به صف پردازش
    """
    try:
       
        recent_calls = await fetch_recent_calls_from_crm(limit=5)
        
        if not recent_calls:
            return {"status": "success", "message": "تماس جدیدی در CRM یافت نشد."}
            
        queued_count = 0
        Path(settings.audio_directory).mkdir(parents=True, exist_ok=True)
        
        async with AsyncSessionLocal() as db:
            for call in recent_calls:
                activity_id = call["activityid"]
                existing = await db.execute(
                    select(CallAnalysisRecord.id).where(
                        CallAnalysisRecord.crm_activity_id == activity_id
                    )
                )
                if existing.scalar_one_or_none():
                    continue
                save_path = str(Path(settings.audio_directory) / f"{activity_id}.wav")

                has_audio = await download_audio_from_crm(activity_id, save_path)

                if has_audio:
                    await redis_pool.enqueue_job(
                        "process_call_task",
                        activity_id,
                        save_path,
                        _job_id=f"call:{activity_id}",
                    )
                    queued_count += 1
                
        return {
            "status": "success", 
            "message": f"{queued_count} تماس با موفقیت از CRM دریافت و وارد صف پردازش هوش مصنوعی شد."
        }
        
    except Exception:
        logging.exception("Dynamics synchronization failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Dynamics synchronization failed",
        )