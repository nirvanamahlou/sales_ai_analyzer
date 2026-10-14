import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class CallAnalysisRecord(Base):
    __tablename__ = "call_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    crm_activity_id = Column(String, unique=True, index=True, nullable=False)
    
    # داده‌های خام
    transcript = Column(Text, nullable=True)
    
    # خروجی‌های هوش مصنوعی
    lead_score = Column(Integer, default=0)
    agent_performance = Column(String, nullable=True)
    
    # استفاده از قابلیت JSON در پستگرس برای ذخیره آرایه‌ها
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
