import type { Message } from "../../types";
import { memo, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";
import { Pencil, Trash2, Info, SmilePlus } from "lucide-react";

const REACTION_EMOJIS = ["👍", "❤️", "😂", "😮", "😢", "🙏", "🔥", "👏"]; 

type MessageBubbleProps = {
  message: Message;
  onEdit?: (msg: Message) => void;
  onDelete?: (msg: Message) => void;
  onReact?: (msg: Message, emoji: string) => void;
};

function MessageBubbleComponent({ message, onEdit, onDelete, onReact }: MessageBubbleProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [reactionMenuOpen, setReactionMenuOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const isOwnMessage = message.sender === "Me";
  const hasReactions = !message.isDeleted && (message.reactionSummary?.length ?? 0) > 0;

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setMenuOpen(true);
  };

  const handleEdit = () => {
    setMenuOpen(false);
    if (onEdit) onEdit(message);
  };

  const handleDelete = () => {
    setMenuOpen(false);
    if (onDelete) onDelete(message);
  };

  const handleReactionSelect = (emoji: string) => {
    setReactionMenuOpen(false);
    setMenuOpen(false);
    onReact?.(message, emoji);
  };

  const handleReactionChipClick = (emoji: string) => {
    onReact?.(message, emoji);
  };

  useEffect(() => {
    if (!menuOpen) {
      setReactionMenuOpen(false);
    }
  }, [menuOpen]);

  return (
    <div className={`flex flex-col gap-1 ${isOwnMessage ? "items-end" : "items-start"}`}>
      <DropdownMenu open={menuOpen} onOpenChange={setMenuOpen}>
        <DropdownMenuTrigger asChild>
          <div
            ref={triggerRef}
            onContextMenu={handleContextMenu}
            className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${isOwnMessage ? 'bg-[rgb(var(--primary-bright))]/10 self-end' : 'bg-[rgb(var(--background))] self-start'}`}
          >
            {message.isDeleted ? (
              <div className="italic text-[rgb(var(--muted-foreground))]">
                {isOwnMessage ? 'You deleted this message' : 'This message was deleted'}
              </div>
            ) : (
              <>
                <div className="font-semibold text-xs text-[rgb(var(--muted-foreground))] mb-1">{message.sender}</div>
                <div className="prose prose-sm max-w-none text-[rgb(var(--foreground))]">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
                </div>
                <div className="text-xs text-[rgb(var(--muted-foreground))] mt-1 text-right flex items-center gap-1 justify-end">
                  <span>{message.time}</span>
                  {message.isEdited ? <span className="italic">· Edited</span> : null}
                  {isOwnMessage && (
                    <span aria-label={message.status === 'seen' ? 'Seen' : message.status === 'delivered' ? 'Delivered' : 'Sent'}>
                      {message.status === 'seen' ? '✓✓' : message.status === 'delivered' ? '✓' : '✓'}
                    </span>
                  )}
                </div>
              </>
            )}
          </div>
        </DropdownMenuTrigger>

        <DropdownMenuContent side="right" align="start">
        <DropdownMenuSub>
          <DropdownMenuSubTrigger className="flex items-center gap-2">
            <Info className="w-4 h-4 mr-2" /> Message info
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent className="w-56 text-[0.7rem] space-y-1">
            <div className="font-semibold text-xs">Details</div>
            <div>Sent: {message.time}</div>
            {message.deliveredAt && <div>Delivered: {message.deliveredAt}</div>}
            {message.seenAt && (
              <div>
                {message.sender === 'Me'
                  ? `Seen by you: ${message.seenAt}`
                  : `Seen: ${message.seenAt}`}
              </div>
            )}
          </DropdownMenuSubContent>
        </DropdownMenuSub>
        {!message.isDeleted && (
          <>
            <DropdownMenuSub open={reactionMenuOpen} onOpenChange={setReactionMenuOpen}>
              <DropdownMenuSubTrigger className="flex items-center gap-2">
                <SmilePlus className="w-4 h-4 mr-2" /> React
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent className="py-2 px-3">
                <div className="flex gap-2">
                  {REACTION_EMOJIS.map((emoji) => (
                    <button
                      key={emoji}
                      type="button"
                      onClick={() => handleReactionSelect(emoji)}
                      className="text-xl leading-none transition hover:scale-110"
                      aria-label={`React with ${emoji}`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            {isOwnMessage && (
              <>
                <DropdownMenuItem onClick={handleEdit} className="flex items-center gap-2">
                  <Pencil className="w-4 h-4 mr-2" /> Edit
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDelete} className="flex items-center gap-2 text-red-600 focus:text-red-600">
                  <Trash2 className="w-4 h-4 mr-2" /> Delete
                </DropdownMenuItem>
              </>
            )}
          </>
        )}
        </DropdownMenuContent>
      </DropdownMenu>

      {hasReactions && (
        <div className={`flex flex-wrap gap-1 text-xs ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
          {message.reactionSummary?.map((reaction) => (
            <button
              key={reaction.emoji}
              type="button"
              onClick={() => handleReactionChipClick(reaction.emoji)}
              className={`flex items-center gap-1 rounded-full border px-2 py-0.5 shadow-sm transition ${
                reaction.reactedByMe
                  ? 'border-[rgb(var(--primary))] bg-[rgb(var(--primary))]/15'
                  : 'border-transparent bg-[rgb(var(--background))]/60'
              }`}
              aria-pressed={reaction.reactedByMe}
            >
              <span>{reaction.emoji}</span>
              {/* <span>{reaction.count}</span> */}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

const MessageBubble = memo(MessageBubbleComponent);
MessageBubble.displayName = "MessageBubble";

export default MessageBubble;
