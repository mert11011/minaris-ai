import React, { useState } from "react";
import "./App.css";

// CHANGE THIS WHEN SWITCHING BETWEEN LOCAL & PRODUCTION
// LOCAL development:
const API_URL = "http://localhost:8001/analyze";

// PRODUCTION deployment (Render):
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
      console.error(error);
      setResponse("❌ Error connecting to backend.");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Minaris Triage Assistant</h1>

      <textarea
        placeholder="Ask a question..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button onClick={sendMessage} disabled={loading}>
        {loading ? "Analyzing..." : "Send"}
      </button>

      {response && (
        <div className="response-box">
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;

