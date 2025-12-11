import type { Message } from "../../types";
import { memo, useRef, useState } from "react";
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
import { Pencil, Trash2, Info, SmilePlus  } from "lucide-react";

type MessageBubbleProps = {
  message: Message;
  onEdit?: (msg: Message) => void;
  onDelete?: (msg: Message) => void;
};

function MessageBubbleComponent({ message, onEdit, onDelete }: MessageBubbleProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);

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

  return (
    <DropdownMenu open={menuOpen} onOpenChange={setMenuOpen}>

      <DropdownMenuTrigger asChild>
        <div
          ref={triggerRef}
          onContextMenu={handleContextMenu}
          className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${message.sender === 'Me' ? 'bg-[rgb(var(--primary-bright))]/10 self-end' : 'bg-[rgb(var(--background))] self-start'}`}
        >
          {message.isDeleted ? (
            <div className="italic text-[rgb(var(--muted-foreground))]">
              {message.sender === 'Me' ? 'You deleted this message' : 'This message was deleted'}
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
                {message.sender === 'Me' && (
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
            <DropdownMenuItem className="flex items-center gap-2">
              <SmilePlus className="w-4 h-4 mr-2" /> React
            </DropdownMenuItem>
            {message.sender === 'Me' && (
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
  );
}

const MessageBubble = memo(MessageBubbleComponent);
MessageBubble.displayName = "MessageBubble";

export default MessageBubble;
