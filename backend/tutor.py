"""
Tutor layer for the learning platform.

For the hackathon prototype this is a deterministic, rule-based explainer:
it never fails, needs no API key, and works fully offline - important
when you're demoing live on a hackathon Wi-Fi network. It is structured
so a real LLM call (Anthropic/OpenAI) can be dropped in later without
touching the frontend: see `get_ai_explanation()` at the bottom.
"""
import re

STEP_EXPLANATIONS = {
    "initial_state": (
        "Alice has a qubit in an unknown state |psi> = alpha|0> + beta|1>. "
        "She doesn't know alpha or beta herself - if she measured the qubit "
        "directly she would destroy the superposition and only recover partial "
        "information. Teleportation lets her send this exact state to Bob "
        "without ever learning or measuring it."
    ),
    "bell_pair": (
        "Before any teleportation happens, Alice and Bob must share one "
        "entangled pair of qubits (a Bell pair), created ahead of time by "
        "applying a Hadamard gate then a CNOT. This is the 'quantum channel' - "
        "it carries no information by itself, but it's what makes teleportation "
        "possible later."
    ),
    "alice_operations": (
        "Alice applies a CNOT from her data qubit onto her half of the Bell "
        "pair, then a Hadamard on her data qubit. This entangles all three "
        "qubits together and rotates the information about alpha and beta "
        "into a form that can be read out by an ordinary measurement."
    ),
    "measurement": (
        "Alice measures her two qubits in the computational basis, getting "
        "two classical bits (m0, m1). This step is genuinely random - the "
        "probabilities shown here come directly from the entangled state, "
        "exactly as quantum mechanics predicts."
    ),
    "bob_before_correction": (
        "The instant Alice measures, Bob's qubit collapses too (that's what "
        "entanglement means). But it's not automatically equal to the "
        "original |psi> - it differs by at most a known X and/or Z flip, "
        "depending on Alice's measurement result."
    ),
    "correction": (
        "Alice sends her two classical bits to Bob over an ordinary channel "
        "(phone, internet, radio - anything classical). Bob uses them to apply "
        "the matching correction: X if m1=1, then Z if m0=1. This classical "
        "communication step is why teleportation can never send information "
        "faster than light."
    ),
    "final_state": (
        "After the correction, Bob's qubit is now in exactly the state "
        "alpha|0> + beta|1> that Alice started with. Alice's original qubit "
        "was destroyed in the measurement (the no-cloning theorem guarantees "
        "there is only ever one copy) - the state was moved, not duplicated."
    ),
}

SUGGESTED_QUESTIONS = [
    "What is a Bell pair?",
    "Why does Alice need to send classical bits?",
    "Is this faster than light communication?",
    "What is the no-cloning theorem?",
    "Why does the measurement collapse Bob's qubit too?",
]

_KNOWLEDGE_BASE = [
    (
        re.compile(r"bell pair|entangle", re.I),
        "A Bell pair is two qubits prepared so that measuring one instantly tells "
        "you about the other, no matter the distance between them. It's created with "
        "a Hadamard gate followed by a CNOT. Teleportation needs one shared Bell pair "
        "between sender and receiver before it can begin.",
    ),
    (
        re.compile(r"faster than light|ftl|instant", re.I),
        "No. Bob's qubit does collapse the instant Alice measures, but his qubit is "
        "still in the wrong state until he applies a correction - and he can only know "
        "which correction to apply once Alice's two classical bits reach him at or "
        "below light speed. No usable information moves faster than light.",
    ),
    (
        re.compile(r"classical bit|classical channel|why.*send", re.I),
        "Alice's measurement produces two classical bits (m0, m1). These tell Bob "
        "exactly which correction (I, X, Z, or XZ) to apply to his qubit to turn it "
        "into the original state. Without these two bits, Bob's qubit is unusable "
        "random noise from his point of view.",
    ),
    (
        re.compile(r"no.?clon", re.I),
        "The no-cloning theorem says you can't make an independent, identical copy "
        "of an unknown quantum state. That's exactly why teleportation destroys "
        "Alice's original qubit during measurement instead of copying it - only one "
        "instance of the state ever exists.",
    ),
    (
        re.compile(r"why.*collapse|measur.*bob", re.I),
        "Because Bob's qubit is entangled with Alice's two qubits before she "
        "measures them. Measuring any qubit in an entangled group forces the whole "
        "group into a consistent joint state - that's the defining feature of "
        "entanglement.",
    ),
    (
        re.compile(r"fidelity", re.I),
        "Fidelity here measures how close Bob's final qubit is to Alice's original "
        "state, from 0 (completely different) to 1 (identical). In an ideal, "
        "noise-free simulation like this one, fidelity should always come out to 1.0.",
    ),
]

_FALLBACK = (
    "I don't have a canned answer for that one yet. Try asking about Bell pairs, "
    "classical bits, the no-cloning theorem, or why teleportation isn't faster-than-light "
    "communication - or click one of the suggested questions."
)


def explain_step(step_id: str) -> str:
    return STEP_EXPLANATIONS.get(step_id, "")


def answer_question(question: str) -> str:
    for pattern, answer in _KNOWLEDGE_BASE:
        if pattern.search(question):
            return answer
    return _FALLBACK


def get_ai_explanation(question: str) -> str:
    """
    Hook for a real LLM call (e.g. the Anthropic Python SDK) to replace the
    rule-based `answer_question` above with genuine open-ended tutoring.
    Left unimplemented so the prototype has zero external dependencies and
    never fails on hackathon Wi-Fi; wire this up if you want free-form Q&A
    beyond the topics in _KNOWLEDGE_BASE.
    """
    raise NotImplementedError("Plug in an LLM API call here for open-ended tutoring.")
