# Quantum Teleportation - Interactive Learning Platform (SIH26140 prototype)

First working module for "AI-Based Interactive Quantum Algorithm Learning
Platform": a from-scratch (numpy-only, no Qiskit) simulation of quantum
teleportation, a step-by-step visual timeline, and a tutor chat panel.

## Run the backend (FastAPI)

```powershell
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run the frontend (React + Vite)

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173). The dev server
proxies `/api/*` to the backend on port 8000, so no CORS config is needed
locally.

## What's real vs. what's a placeholder

- **Simulation is genuine physics**: full 8-dimensional statevector, real
  random measurement outcomes weighted by actual quantum probabilities,
  and the correction step is verified to reach fidelity 1.0 regardless of
  which of the four measurement outcomes occurs.
- **Tutor is currently rule-based**, not a live LLM call: it matches
  keywords (Bell pair, no-cloning, classical bits, faster-than-light,
  fidelity) to written explanations. This keeps the demo dependency-free
  and immune to Wi-Fi/API outages during judging. `backend/tutor.py` has
  a `get_ai_explanation()` stub ready for you to wire up a real LLM call
  if you want genuinely open-ended Q&A - worth doing before the finale
  since judges in 2026 expect visible AI, and a rule-based matcher alone
  may read as a lookup table rather than "AI".

## Extending to other algorithms

`teleportation.py`'s pattern (build gates as numpy matrices, embed with
`_gate_on`/`_cnot`, return a `steps` list) generalizes directly to
Deutsch-Jozsa, Grover's, or Bernstein-Vazirani if you want to grow this
into the full "learning platform" the problem statement describes -
each would be a new sibling module plus a matching STEP_EXPLANATIONS
block in `tutor.py`.
