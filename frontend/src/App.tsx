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

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const newMessages = [...messages, { role: "user" as const, content: message }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8001/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();
      console.log("🧠 Backend raw data:", data);

      const reply =
        data.reply ||
        data.answer ||
        "⚠️ No valid response field received from backend.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant" as const, content: reply },
      ]);
    } catch (error) {
      console.error("🚨 Frontend fetch error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant" as const,
          content:
            "⚠️ Error: could not reach backend. Ensure backend is running on port 8001.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col relative">
      {/* 🔹 Header changed: black bg + white text */}
      <header className="flex items-center justify-center py-6 bg-black shadow-sm border-b border-gray-900 relative">
        <h1 className="text-[17px] font-normal text-white tracking-wide">
          Minaris AI
        </h1>
      </header>

      <main className="flex-1 flex flex-col overflow-y-auto transition-all duration-500 ease-in-out">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center flex-1 text-center text-gray-700 px-8 animate-fadeIn">
            <img
              src="/assets/minaris-logo.png"
              alt="Minaris Logo"
              className="h-20 w-auto mb-6 object-contain"
            />
            <p className="max-w-2xl leading-relaxed text-[16.5px] text-[#1a1f2e]">
              This AI analyzes historical triage data across all Minaris programs.  
              Enter the program/client and describe what occurred for event classification —  
              or ask general triage-related questions.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4 py-6 animate-fadeIn">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} role={msg.role} content={msg.content} />
            ))}
            {loading && (
              <div className="flex justify-start px-8 text-gray-400 italic animate-pulse">
                Analyzing triage context...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        )}
      </main>

      <footer className="border-t border-gray-200 bg-white py-6 px-8 relative">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
        </div>
        {/* Enlarged footer credit */}
        <span className="absolute right-8 bottom-2 text-[10px] text-gray-400 italic font-light">
          by MERT TUZ
        </span>
      </footer>
    </div>
  );
}
