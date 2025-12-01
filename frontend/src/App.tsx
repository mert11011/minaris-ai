import { useState, useEffect, useRef } from "react";
import { ChatInput } from "./components/ChatInput";
import { ChatMessage } from "./components/ChatMessage";

type Message = { role: "user" | "assistant"; content: string };

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const BACKEND_URL = "http://localhost:8001/analyze";

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = { role: "user", content: message };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      const reply =
        data.reply ||
        data.answer ||
        data.output ||
        "⚠️ No valid response received.";

      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Error contacting backend. Please ensure server is running.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#f6f8fc] flex flex-col">
      
      {/* HEADER — increased text size by ~10% */}
      <header className="bg-black py-4 flex justify-center shadow">
        <h1 className="text-white text-base tracking-wide font-normal">
          Minaris AI
        </h1>
      </header>

      {/* MAIN SECTION */}
      <main className="flex-1 flex flex-col items-center px-6">

        {/* CENTERED WELCOME AREA */}
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col justify-center items-center text-center mt-4">
            <img
              src="/assets/minaris-logo.png"
              alt="Minaris Logo"
              className="h-20 mb-8"
            />

            <p className="max-w-2xl text-[16.5px] text-[#1a1f2e] leading-relaxed">
              This AI analyzes historical triage data across all Minaris programs.  
              Enter the program/client and describe what occurred for event classification —  
              or ask general triage-related questions.
            </p>
          </div>
        )}

        {/* CHAT MESSAGES */}
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

      {/* FOOTER */}
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
