
import MessageBubble from "./MessageBubble";
import type { Message } from "../../types";
import { ScrollArea } from "@/components/ui/scroll-area";

type MessagesListProps = {
  messages: Message[];
  onEdit?: (msg: Message) => void;
  onDelete?: (msg: Message) => void;
};

export default function MessagesList({ messages, onEdit, onDelete }: MessagesListProps) {
  return (
    <ScrollArea className="w-full h-full" type="always">
      <div className="flex flex-col gap-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} onEdit={onEdit} onDelete={onDelete} />
        ))}
      </div>
    </ScrollArea>
  );
}
