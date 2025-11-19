import React, { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8001/analyze";
// const API_URL = "https://minaris-ai-backend.onrender.com/analyze";

function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      setResponse(data.reply || "⚠️ No response received.");
    } catch (error) {
      setResponse("❌ Error connecting to backend.");
    }

    setLoading(false);
  };

  return (
    <div className="app-container">

      <div className="header">
        <img src="/minaris.png" alt="Minaris Logo" className="logo" />
        <h1>Minaris AI</h1>
        <p className="subtitle">
          This AI analyzes historical triage data across all Minaris programs.
          Enter the program/client and describe what occurred for event classification — 
          or ask general triage-related questions.
        </p>
      </div>

      <div className="input-card">
        <textarea
          placeholder="Type your message here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="input-box"
        />

        <button className="send-btn" onClick={sendMessage} disabled={loading}>
          {loading ? "Analyzing..." : "Send"}
        </button>
      </div>

      {response && (
        <div className="response-card">
          <pre>{response}</pre>
        </div>
      )}

      <footer className="footer">Built by MERT TUZ</footer>
    </div>
  );
}

export default App;
