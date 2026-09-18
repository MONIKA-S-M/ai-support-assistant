from fastapi import FastAPI
from app.query_engine import (
    get_ticket_count,
    get_open_ticket_count,
    get_average_rating,
    get_average_resolution_time,
    get_tickets_by_category,
    get_tickets_by_priority,
    get_tickets_by_status,
    get_top_agent,
)
from app.anomaly_detector import detect_anomalies
from app.query_engine import answer_question


app = FastAPI(
    title="AI Support Ticket Assistant",
    description="REST API for analyzing support tickets and detecting anomalies.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Support Ticket Assistant API is running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/tickets/summary")
def ticket_summary():
    return {
        "total_tickets": get_ticket_count(),
        "open_tickets": get_open_ticket_count(),
        "average_customer_rating": get_average_rating(),
        "average_resolution_time_hrs": get_average_resolution_time(),
        "top_resolving_agent": get_top_agent(),
    }


@app.get("/tickets/by-category")
def tickets_by_category():
    return get_tickets_by_category()


@app.get("/tickets/by-priority")
def tickets_by_priority():
    return get_tickets_by_priority()


@app.get("/tickets/by-status")
def tickets_by_status():
    return get_tickets_by_status()


@app.get("/anomalies")
def anomalies():
    return {
        "count": len(detect_anomalies()),
        "anomalies": detect_anomalies(),
    }

@app.get("/ask")
def ask(question: str):
    return {
        "question": question,
        "answer": answer_question(question),
    }