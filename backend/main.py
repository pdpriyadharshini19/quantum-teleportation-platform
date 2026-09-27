"""
FastAPI backend for the AI-Based Interactive Quantum Algorithm Learning Platform.

Current scope (first working demo): Quantum Teleportation.
  - /api/teleport   runs the simulation and returns a step-by-step trace
  - /api/chat       rule-based tutor answers questions about the protocol
  - /api/suggested-questions  chips for the frontend to show

Run with:  uvicorn main:app --reload --port 8000
"""
import math

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from teleportation import run_teleportation
from tutor import explain_step, answer_question, SUGGESTED_QUESTIONS

app = FastAPI(title="Quantum Algorithm Learning Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_INV_SQRT2 = 1 / math.sqrt(2)


class TeleportRequest(BaseModel):
    alpha_real: float = Field(default=_INV_SQRT2)
    alpha_imag: float = Field(default=0.0)
    beta_real: float = Field(default=_INV_SQRT2)
    beta_imag: float = Field(default=0.0)


class ChatRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/teleport")
def teleport(req: TeleportRequest):
    alpha = complex(req.alpha_real, req.alpha_imag)
    beta = complex(req.beta_real, req.beta_imag)
    result = run_teleportation(alpha, beta)
    for step in result["steps"]:
        step["explanation"] = explain_step(step["id"])
    return result


@app.get("/api/suggested-questions")
def suggested_questions():
    return {"questions": SUGGESTED_QUESTIONS}


@app.post("/api/chat")
def chat(req: ChatRequest):
    return {"answer": answer_question(req.question)}
