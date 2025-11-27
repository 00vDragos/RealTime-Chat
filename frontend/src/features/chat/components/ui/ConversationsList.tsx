import { ScrollArea } from '@/components/ui/scroll-area';
import type { Chat } from "../../types";

import ConversationCard from "./ConversationCard";

type ConversationsListProps = {
  chats: Chat[];
  selectedChatId: number | null;
  setSelectedChatId: (id: number) => void;
};

export default function ConversationsList({ chats, selectedChatId, setSelectedChatId }: ConversationsListProps) {
  return (
    <ScrollArea className="flex-1">
      {chats.map((chat) => (
        <ConversationCard
          key={chat.id}
          chat={chat}
          selected={selectedChatId === chat.id}
          onClick={() => setSelectedChatId(chat.id)}
        />
      ))}
    </ScrollArea>
  );
}
