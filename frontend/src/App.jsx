import { useEffect, useRef, useState } from "react";

const PRESETS = [
  { label: "|0>", theta: 0 },
  { label: "|1>", theta: 90 },
  { label: "|+>", theta: 45 },
  { label: "|->", theta: 45, negative: true },
];

function amplitudeToString({ real, imag }) {
  const r = Math.abs(real) < 1e-4 ? 0 : real;
  const i = Math.abs(imag) < 1e-4 ? 0 : imag;
  if (i === 0) return r.toFixed(3);
  if (r === 0) return `${i.toFixed(3)}i`;
  return `${r.toFixed(3)}${i >= 0 ? "+" : ""}${i.toFixed(3)}i`;
}

function StateVector({ terms }) {
  if (!terms || terms.length === 0) return null;
  return (
    <div className="ket-line">
      {terms.map((t, idx) => (
        <span key={t.label}>
          {idx > 0 && <span className="ket-plus"> + </span>}
          <span className="ket-amp">{amplitudeToString(t.amplitude)}</span>
          <span className="ket-label">{t.label}</span>
        </span>
      ))}
    </div>
  );
}

function CircuitDiagram({ highlightStep }) {
  const groups = {
    prep: ["initial_state"],
    bell: ["bell_pair"],
    alice: ["alice_operations"],
    measure: ["measurement"],
    correct: ["bob_before_correction", "correction", "final_state"],
  };
  const active = (key) => (groups[key].includes(highlightStep) ? "active" : "");

  return (
    <svg viewBox="0 0 640 210" className="circuit" role="img" aria-label="Teleportation circuit diagram">
      {/* wires */}
      <line x1="30" y1="40" x2="610" y2="40" className="wire" />
      <line x1="30" y1="105" x2="610" y2="105" className="wire" />
      <line x1="30" y1="170" x2="610" y2="170" className="wire" />
      <text x="8" y="45" className="wire-label">q0</text>
      <text x="8" y="110" className="wire-label">q1</text>
      <text x="8" y="175" className="wire-label">q2</text>

      {/* bell pair creation */}
      <g className={active("bell")}>
        <rect x="90" y="88" width="34" height="34" className="gate" />
        <text x="107" y="110" textAnchor="middle" className="gate-label">H</text>
        <line x1="107" y1="122" x2="107" y2="170" className="wire" />
        <circle cx="107" cy="170" r="6" className="cnot-target" />
        <line x1="98" y1="170" x2="116" y2="170" className="cnot-cross" />
        <line x1="107" y1="164" x2="107" y2="176" className="cnot-cross" />
      </g>

      {/* alice entangles */}
      <g className={active("alice")}>
        <line x1="220" y1="40" x2="220" y2="105" className="wire" />
        <circle cx="220" cy="40" r="6" className="cnot-dot" />
        <circle cx="220" cy="105" r="6" className="cnot-target" />
        <line x1="211" y1="105" x2="229" y2="105" className="cnot-cross" />
        <line x1="220" y1="99" x2="220" y2="111" className="cnot-cross" />

        <rect x="270" y="23" width="34" height="34" className="gate" />
        <text x="287" y="45" textAnchor="middle" className="gate-label">H</text>
      </g>

      {/* measurement */}
      <g className={active("measure")}>
        <rect x="350" y="23" width="40" height="34" className="gate meter" />
        <text x="370" y="45" textAnchor="middle" className="gate-label">M</text>
        <rect x="350" y="88" width="40" height="34" className="gate meter" />
        <text x="370" y="110" textAnchor="middle" className="gate-label">M</text>
      </g>

      {/* classical wires to correction */}
      <g className={active("correct")}>
        <line x1="390" y1="40" x2="390" y2="190" className="classical-wire" />
        <line x1="392" y1="40" x2="392" y2="190" className="classical-wire" />
        <line x1="390" y1="190" x2="480" y2="190" className="classical-wire" />
        <line x1="392" y1="190" x2="480" y2="190" className="classical-wire" />

        <line x1="370" y1="105" x2="370" y2="150" className="classical-wire" />
        <line x1="372" y1="105" x2="372" y2="150" className="classical-wire" />
        <line x1="370" y1="150" x2="450" y2="150" className="classical-wire" />
        <line x1="372" y1="150" x2="450" y2="150" className="classical-wire" />

        <rect x="450" y="132" width="40" height="34" className="gate" />
        <text x="470" y="154" textAnchor="middle" className="gate-label">X</text>
        <rect x="500" y="153" width="40" height="34" className="gate" />
        <text x="520" y="175" textAnchor="middle" className="gate-label">Z</text>
      </g>

      <text x="570" y="175" className="wire-label out">|psi&gt;</text>
    </svg>
  );
}

export default function App() {
  const [theta, setTheta] = useState(45);
  const [negative, setNegative] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeStepId, setActiveStepId] = useState(null);

  const [suggested, setSuggested] = useState([]);
  const [messages, setMessages] = useState([
    { role: "tutor", text: "Ask me anything about the teleportation protocol, or run the simulation and I'll explain each step as it happens." },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetch("/api/suggested-questions")
      .then((r) => r.json())
      .then((d) => setSuggested(d.questions || []))
      .catch(() => setSuggested([]));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    const rad = (theta * Math.PI) / 180;
    const alpha_real = Math.cos(rad);
    const beta_real = negative ? -Math.sin(rad) : Math.sin(rad);
    try {
      const res = await fetch("/api/teleport", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ alpha_real, alpha_imag: 0, beta_real, beta_imag: 0 }),
      });
      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();
      setResult(data);
      setActiveStepId(data.steps[0]?.id ?? null);
    } catch (e) {
      setError("Couldn't reach the backend. Is uvicorn running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  const sendQuestion = async (question) => {
    const q = (question ?? input).trim();
    if (!q || sending) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setSending(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      setMessages((m) => [...m, { role: "tutor", text: data.answer }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "tutor", text: "Couldn't reach the tutor backend just now." }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1>Quantum Teleportation</h1>
        <p className="subtitle">An interactive first module of the Quantum Algorithm Learning Platform</p>
      </header>

      <main className="layout">
        <section className="panel simulation-panel">
          <div className="input-row">
            <div className="presets">
              {PRESETS.map((p) => (
                <button
                  key={p.label + (p.negative ? "-" : "")}
                  className="preset-btn"
                  onClick={() => {
                    setTheta(p.theta);
                    setNegative(!!p.negative);
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
            <div className="slider-row">
              <label htmlFor="theta">
                custom mix: alpha = cos({theta}°), beta = {negative ? "-" : ""}sin({theta}°)
              </label>
              <input
                id="theta"
                type="range"
                min="0"
                max="90"
                value={theta}
                onChange={(e) => setTheta(Number(e.target.value))}
              />
            </div>
            <button className="run-btn" onClick={runSimulation} disabled={loading}>
              {loading ? "Running..." : "Run teleportation"}
            </button>
          </div>

          {error && <p className="error-text">{error}</p>}

          <CircuitDiagram highlightStep={activeStepId} />

          <div className="timeline">
            {result ? (
              result.steps.map((step, idx) => (
                <button
                  key={step.id}
                  className={`step ${activeStepId === step.id ? "step-active" : ""}`}
                  onClick={() => setActiveStepId(step.id)}
                >
                  <div className="step-head">
                    <span className="step-index">{idx + 1}</span>
                    <span className="step-title">{step.title}</span>
                  </div>
                  {step.measured_bits && (
                    <p className="measured-bits">
                      measured: m0={step.measured_bits.m0}, m1={step.measured_bits.m1}
                    </p>
                  )}
                  <StateVector terms={step.state} />
                  {step.gates_applied && (
                    <p className="gates-applied">correction gates: {step.gates_applied.join(", ")}</p>
                  )}
                  {typeof step.fidelity_to_original === "number" && (
                    <p className="fidelity">fidelity to original state: {step.fidelity_to_original}</p>
                  )}
                  <p className="step-explanation">{step.explanation}</p>
                </button>
              ))
            ) : (
              <p className="empty-state">
                Pick a state above and run the simulation to see the protocol unfold step by step.
              </p>
            )}
          </div>
        </section>

        <aside className="panel tutor-panel">
          <h2>Tutor</h2>
          <div className="chat-log">
            {messages.map((m, i) => (
              <div key={i} className={`bubble bubble-${m.role}`}>
                {m.text}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="suggested">
            {suggested.map((q) => (
              <button key={q} className="chip" onClick={() => sendQuestion(q)} disabled={sending}>
                {q}
              </button>
            ))}
          </div>

          <form
            className="chat-input-row"
            onSubmit={(e) => {
              e.preventDefault();
              sendQuestion();
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about entanglement, classical bits..."
              disabled={sending}
            />
            <button type="submit" disabled={sending}>
              Send
            </button>
          </form>
        </aside>
      </main>
    </div>
  );
}
