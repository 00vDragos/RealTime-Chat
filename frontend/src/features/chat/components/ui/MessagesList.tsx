
import MessageBubble from "./MessageBubble";
import type { Message } from "../../types";

export default function MessagesList({ messages }: { messages: Message[] }) {
  return (
    <div className="flex flex-col gap-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
    </div>
  );
}
