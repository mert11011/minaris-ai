import { useState, useEffect, useRef } from "react";
import { ChatInput } from "./components/ChatInput";
import { ChatMessage } from "./components/ChatMessage";

type Message = { role: "user" | "assistant"; content: string };

export default function App() {
  // --- PASSWORD GATE ---
  const [password, setPassword] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const PASSWORD = "MINARIS";

  // --- CHAT STATE ---
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // --- BACKEND URL ---
  const BACKEND_URL =
    process.env.NODE_ENV === "production"
      ? "https://minaris-ai-backend.onrender.com/analyze"
      : "http://localhost:8001/analyze";

  // --- AUTO-SCROLL ---
  useEffect(() => {
    if (authorized) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, authorized]);

  // --- SEND MESSAGE ---
  const handleSendMessage = async (message: string) => {
    if (!authorized || !message.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setLoading(true);

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`);
      }

      const data = await res.json();
      const reply =
        data.reply || data.answer || data.output || "⚠️ Backend returned no message.";

      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠️ Error contacting backend. Backend may be waking up — try again in 5–10 seconds.",
        },
      ]);
    }

    setLoading(false);
  };

  // --- PASSWORD SCREEN ---
  if (!authorized) {
    return (
      <div className="min-h-screen bg-[#f6f8fc] flex flex-col items-center justify-center">
        <h2 className="text-xl mb-6 text-black">Enter Password</h2>

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border border-gray-400 px-3 py-2 rounded w-64 text-center"
          placeholder="Password"
        />

        <button
          onClick={() => {
            if (password === PASSWORD) setAuthorized(true);
            else alert("Incorrect password");
          }}
          className="mt-4 bg-black text-white px-4 py-2 rounded"
        >
          Enter
        </button>
      </div>
    );
  }

  // --- MAIN CHAT UI ---
  return (
    <div className="min-h-screen bg-[#f6f8fc] flex flex-col">
      <header className="bg-black py-4 flex justify-center shadow">
        <h1 className="text-white text-base tracking-wide font-normal">
          Minaris AI
        </h1>
      </header>

      <main className="flex-1 flex flex-col items-center px-6">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col justify-center items-center text-center mt-4">
            <img
              src="/assets/minaris-logo.png"
              alt="Minaris Logo"
              className="h-20 mb-8"
            />

            <p className="max-w-2xl text-[16.5px] text-[#1a1f2e] leading-relaxed">
              This AI analyzes historical triage data across all Minaris
              programs. Enter the program/client and describe what occurred for
              event classification — or ask general triage-related questions.
            </p>
          </div>
        )}

        <div className="w-full max-w-2xl py-6 space-y-4">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} role={msg.role} content={msg.content} />
          ))}

          {loading && (
            <p className="text-gray-500 italic animate-pulse">
              Analyzing triage context…
            </p>
          )}

          <div ref={chatEndRef} />
        </div>
      </main>

      <footer className="bg-white border-t py-6 relative">
        <div className="max-w-2xl mx-auto px-6">
          <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
        </div>

        <p className="text-[10px] italic text-gray-400 absolute bottom-2 right-4">
          by MERT TUZ
        </p>
      </footer>
    </div>
  );
}
