
import MessageBubble from "./MessageBubble";
import type { Message } from "../../types";

type MessagesListProps = {
  messages: Message[];
  onEdit?: (msg: Message) => void;
};

export default function MessagesList({ messages, onEdit }: MessagesListProps) {
  return (
    <div className="flex flex-col gap-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} onEdit={onEdit} />
      ))}
    </div>
  );
}
