from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.config import settings


class CallAnalysisState(TypedDict):
    transcript: str
    lead_score: int
    agent_performance: str
    strengths: List[str]
    weaknesses: List[str]


class LeadAnalysis(BaseModel):
    lead_score: int = Field(ge=0, le=100)


class SalesAgentAnalysis(BaseModel):
    agent_performance: str
    strengths: list[str]
    weaknesses: list[str]


def get_llm() -> ChatOpenAI:
   
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API KEY is not configured in .env file")
       
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,      
        temperature=0,                    
    )


async def analyze_lead_node(state: CallAnalysisState):
    transcript = state["transcript"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "شما یک تحلیلگر ارشد فروش هستید. بر اساس متن مکالمه، میزان تمایل و کیفیت مشتری (Lead) را از 0 تا 100 ارزیابی کنید. خروجی فقط یک عدد صحیح باشد."),
        ("user", "متن مکالمه:\n{transcript}")
    ])
    
    chain = prompt | get_llm().with_structured_output(LeadAnalysis)
    response = await chain.ainvoke({"transcript": transcript})
    return {"lead_score": response.lead_score}


async def analyze_sales_agent_node(state: CallAnalysisState):
    transcript = state["transcript"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """شما یک مربی فروش هستید. عملکرد کارشناس فروش را در این مکالمه ارزیابی کنید.
        خروجی باید دقیقا یک فایل JSON با این سه کلید باشد:
        - agent_performance: یک کلمه (عالی، خوب، نیازمند بهبود)
        - strengths: آرایه‌ای از نقاط قوت (رشته)
        - weaknesses: آرایه‌ای از نقاط ضعف (رشته)"""),
        ("user", "متن مکالمه:\n{transcript}")
    ])
    
    chain = prompt | get_llm().with_structured_output(SalesAgentAnalysis)
    analysis = await chain.ainvoke({"transcript": transcript})
    return analysis.model_dump()


workflow = StateGraph(CallAnalysisState)


workflow.add_node("lead_analyzer", analyze_lead_node)
workflow.add_node("agent_analyzer", analyze_sales_agent_node)


workflow.set_entry_point("lead_analyzer")
workflow.add_edge("lead_analyzer", "agent_analyzer")
workflow.add_edge("agent_analyzer", END)


call_analysis_app = workflow.compile()


async def run_call_analysis(transcript: str) -> dict:
    """این تابع از بیرون صدا زده می‌شود تا کل جریان اجرا شود"""
    initial_state = {
        "transcript": transcript,
        "lead_score": 0,
        "agent_performance": "",
        "strengths": [],
        "weaknesses": []
    }
    
    # اجرای گراف
    final_state = await call_analysis_app.ainvoke(initial_state)
    return final_state
