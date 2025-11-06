import { Trash2, Plus } from "lucide-react";
import { Button } from "./ui/button";

interface ChatSidebarProps {
  chats: { id: string; title: string }[];
  currentChatId: string | null;
  onNewChat: () => void;
  onSelectChat: (id: string) => void;
  onDeleteChat: (id: string) => void;
}

export function ChatSidebar({
  chats,
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
}: ChatSidebarProps) {
  return (
    <div className="flex flex-col h-full bg-[#0a1628] text-white">
      <div className="p-4 border-b border-white/10 flex justify-between items-center">
        <h2 className="text-lg font-semibold">Conversations</h2>
        <Button
          variant="ghost"
          size="icon"
          className="hover:bg-white/10"
          onClick={onNewChat}
        >
          <Plus className="w-5 h-5 text-white" />
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`flex items-center justify-between p-2 rounded-lg mb-2 cursor-pointer ${
              currentChatId === chat.id
                ? "bg-gradient-to-r from-[#38bdf8] to-[#9ef01a] text-[#0a1628]"
                : "hover:bg-white/10"
            }`}
          >
            <span className="truncate text-sm">{chat.title}</span>
            <Button
              variant="ghost"
              size="icon"
              className="hover:bg-white/10"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
            >
              <Trash2 className="w-4 h-4 text-white" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
