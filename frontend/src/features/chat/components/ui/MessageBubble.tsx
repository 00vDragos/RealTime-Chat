import type { Message } from "../../types";
type MessageBubbleProps = {
  message: Message;
};

export default function MessageBubble({ message }: MessageBubbleProps) {
  return (
    <div
      className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${message.sender === 'Me' ? 'bg-green-100 self-end' : 'bg-white self-start'}`}
    >
      <div className="font-semibold text-xs text-gray-500 mb-1">{message.sender}</div>
      <div>{message.text}</div>
      <div className="text-xs text-gray-400 mt-1 text-right">{message.time}</div>
    </div>
  );
}
