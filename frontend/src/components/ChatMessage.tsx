type ChatMessageProps = {
  role: "user" | "assistant";
  content: string;
};

export const ChatMessage = ({ role, content }: ChatMessageProps) => {
  const isUser = role === "user";

  return (
    <div
      className={`flex items-start gap-3 px-8 ${
        isUser ? "justify-start" : "justify-start"
      }`}
    >
      {/* Neutral circular icons */}
      <div
        className={`flex items-center justify-center w-12 h-12 rounded-full shadow-sm ${
          isUser
            ? "bg-[#f4ebde]" // beige tone for user
            : "bg-gradient-to-br from-sky-300 to-green-300"
        }`}
      >
        {/* Neutral outline icons */}
        {isUser ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="black"
            className="w-6 h-6 opacity-80"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 7.5a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 19.5a8.25 8.25 0 0 1 15 0"
            />
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="white"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9.75 4.5v15m4.5-15v15m4.5-7.5H5.25"
            />
          </svg>
        )}
      </div>

      {/* Message Bubble */}
      <div
        className={`max-w-2xl px-5 py-3 rounded-2xl text-[16px] leading-relaxed whitespace-pre-line ${
          isUser
            ? "bg-white border border-gray-200 text-[#0a1628]"
            : "bg-white border border-gray-100 text-[#0a1628]"
        }`}
      >
        {content}
      </div>
    </div>
  );
};
