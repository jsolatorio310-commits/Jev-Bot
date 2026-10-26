import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return (
    <main>
      <p className="eyebrow">Jev Trading Bot</p>
      <h1>Paper trading foundation</h1>
      <p>Phase 0 is running. Market data, strategy, AI, and execution are not enabled.</p>
      <span className="status">PAPER ONLY</span>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);

