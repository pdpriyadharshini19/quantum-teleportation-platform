"""
Manual statevector simulation of the 3-qubit quantum teleportation protocol.

Built directly on numpy (no Qiskit/Cirq dependency) so the whole platform
installs with a single `pip install -r requirements.txt` and has zero
external API/cloud dependency - important for a live 36-hour hackathon demo.

Qubit ordering (index 0 = most significant bit of the 8-dim statevector):
  q0 - Alice's qubit carrying the unknown state |psi> = alpha|0> + beta|1>
  q1 - Alice's half of an entangled Bell pair
  q2 - Bob's half of the entangled Bell pair (ends up holding |psi>)
"""
import math
import random

import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)


def _kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def _gate_on(qubit_index: int, gate: np.ndarray) -> np.ndarray:
    """Embed a single-qubit gate into the full 3-qubit (8x8) space."""
    mats = [I2, I2, I2]
    mats[qubit_index] = gate
    return _kron3(*mats)


def _cnot(control: int, target: int) -> np.ndarray:
    """Build an 8x8 CNOT for the given control/target qubit indices (0,1,2)."""
    dim = 8
    result = np.zeros((dim, dim), dtype=complex)
    for basis in range(dim):
        bits = [(basis >> (2 - i)) & 1 for i in range(3)]  # bits[0] = q0 (MSB)
        new_bits = bits[:]
        if bits[control] == 1:
            new_bits[target] ^= 1
        new_basis = (new_bits[0] << 2) | (new_bits[1] << 1) | new_bits[2]
        result[new_basis, basis] = 1
    return result


def _ket_label(index: int) -> str:
    return "|" + format(index, "03b") + ">"


def _state_terms(vec: np.ndarray, threshold: float = 1e-6):
    """Human-readable list of nonzero basis components of a statevector."""
    terms = []
    for i, amp in enumerate(vec):
        if abs(amp) > threshold:
            terms.append({
                "label": _ket_label(i),
                "amplitude": {"real": round(float(amp.real), 4), "imag": round(float(amp.imag), 4)},
                "probability": round(float(abs(amp) ** 2), 4),
            })
    return terms


def _qubit2_reduced_state(vec: np.ndarray, m0: int, m1: int):
    """
    After q0 and q1 collapse to classical bits m0,m1, extract q2's
    (still-normalized) 2-dim state from the 8-dim vector.
    """
    out = np.zeros(2, dtype=complex)
    for i, amp in enumerate(vec):
        bits = [(i >> (2 - k)) & 1 for k in range(3)]
        if bits[0] == m0 and bits[1] == m1:
            out[bits[2]] = amp
    norm = np.linalg.norm(out)
    if norm > 1e-9:
        out = out / norm
    return out


def run_teleportation(alpha: complex, beta: complex) -> dict:
    """
    Run the full teleportation protocol for an input state
    |psi> = alpha|0> + beta|1> and return a step-by-step trace
    suitable for driving a UI timeline.
    """
    norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    if norm < 1e-9:
        alpha, beta = 1.0, 0.0
        norm = 1.0
    alpha, beta = alpha / norm, beta / norm

    steps = []

    # Step 0: initial state |psi>_0 (x) |0>_1 (x) |0>_2
    psi0 = np.array([alpha, beta], dtype=complex)
    zero = np.array([1, 0], dtype=complex)
    state = _kron3(psi0, zero, zero)
    steps.append({
        "id": "initial_state",
        "title": "Prepare the unknown state",
        "state": _state_terms(state),
    })

    # Step 1: create Bell pair between q1 and q2 -> H(q1) then CNOT(1->2)
    state = _gate_on(1, H) @ state
    state = _cnot(1, 2) @ state
    steps.append({
        "id": "bell_pair",
        "title": "Entangle Alice's and Bob's shared qubits",
        "state": _state_terms(state),
    })

    # Step 2: Alice entangles her data qubit with her half of the pair
    state = _cnot(0, 1) @ state
    state = _gate_on(0, H) @ state
    steps.append({
        "id": "alice_operations",
        "title": "Alice entangles her qubit with the state to teleport",
        "state": _state_terms(state),
    })

    # Step 3: measure q0 and q1 in the computational basis
    probs = {}
    for m0 in (0, 1):
        for m1 in (0, 1):
            p = sum(
                abs(state[i]) ** 2
                for i in range(8)
                if (i >> 2) & 1 == m0 and (i >> 1) & 1 == m1
            )
            probs[(m0, m1)] = p

    outcomes = list(probs.keys())
    weights = [probs[o] for o in outcomes]
    m0, m1 = random.choices(outcomes, weights=weights, k=1)[0]

    steps.append({
        "id": "measurement",
        "title": "Alice measures her two qubits",
        "measured_bits": {"m0": m0, "m1": m1},
        "outcome_probabilities": [
            {"m0": o[0], "m1": o[1], "probability": round(probs[o], 4)} for o in outcomes
        ],
    })

    # Step 4: Bob's qubit before correction (still entangled/unknown to him)
    bob_before = _qubit2_reduced_state(state, m0, m1)
    steps.append({
        "id": "bob_before_correction",
        "title": "Bob's qubit collapses to a related, but not identical, state",
        "state": _state_terms(bob_before),
    })

    # Step 5: Bob applies the classical correction X^m1 Z^m0
    corrected = bob_before.copy()
    if m1 == 1:
        corrected = X @ corrected
    if m0 == 1:
        corrected = Z @ corrected

    steps.append({
        "id": "correction",
        "title": "Bob applies a correction based on Alice's classical bits",
        "gates_applied": (["X"] if m1 == 1 else []) + (["Z"] if m0 == 1 else []) or ["none needed"],
        "state": _state_terms(corrected),
    })

    fidelity = round(float(abs(np.vdot(psi0, corrected)) ** 2), 6)
    steps.append({
        "id": "final_state",
        "title": "Bob now holds the original unknown state",
        "state": _state_terms(corrected),
        "fidelity_to_original": fidelity,
    })

    return {
        "input_state": {
            "alpha": {"real": round(alpha.real, 4), "imag": round(alpha.imag, 4)},
            "beta": {"real": round(beta.real, 4), "imag": round(beta.imag, 4)},
        },
        "steps": steps,
    }
