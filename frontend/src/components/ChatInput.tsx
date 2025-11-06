import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea height as user types
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    onSendMessage(message);
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // prevent newline default
      handleSubmit(e);
    }
    // Shift+Enter now allows a newline (no submission)
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end w-full bg-white rounded-full shadow-sm border border-gray-200 px-5 py-4 h-auto"
    >
      {/* Auto-expanding textarea instead of single-line input */}
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message here..."
        rows={1}
        className="flex-1 resize-none bg-transparent focus:outline-none text-gray-700 text-[15px] placeholder-gray-400 leading-relaxed"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="ml-3 bg-[#9bd6f5] hover:bg-[#80c8ef] text-[#0a1628] font-semibold py-3 px-6 rounded-full flex items-center justify-center transition-all duration-200 ease-in-out shadow-sm"
      >
        Send
        <Send className="w-4 h-4 ml-2" />
      </button>
    </form>
  );
}
